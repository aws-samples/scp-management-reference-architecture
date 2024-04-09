import argparse
import boto3
import json
import logging
import re

"""
Author: Benjamin Morris
"""

def check_conditions(condition, region, principal_arn, account, org_id):
    """
    Helper function that returns whether a condition applies.

    This helper function is EXTREMELY limited and only handles a handful of
    specific operator and condition key combinations.

    Returns False if the SCP's Condition does not apply to the user-provided input
    Returns True if the SCP's Condition does apply to the user-provided input
    """
    # Region allowlist
    try:
        allowed_regions = condition["StringNotEquals"]["aws:RequestedRegion"]
        if region and region in allowed_regions:
            return False
    except KeyError:
        logging.info("No region allowlist condition found.")
    # Principal allowlist
    try:
        allowed_principals = condition["ArnNotLike"]["aws:PrincipalARN"]
        if principal_arn:
            # Operate under the assumption that the condition applies
            # unless an exception is found
            for excluded_principal in allowed_principals:
                if re.search(excluded_principal.replace("*", ".*"), principal_arn):
                    return False
    except KeyError:
        logging.info("No principal allowlist condition found.")
    # Principal blocklist
    try:
        blocked_principals = condition["ArnLike"]["aws:PrincipalARN"]
        if principal_arn:
            # Operate under the assumption that the condition does NOT apply
            # unless an exception is found
            applies = False
            for included_principal in blocked_principals:
                if re.search(included_principal.replace("*", ".*"), principal_arn):
                    applies = True
            if applies is False:
                return False
    except KeyError:
        logging.info("No principal blocklist condition found.")
    # Account allowlist
    try:
        allowed_accounts = condition["StringNotEquals"]["aws:PrincipalAccount"]
        if account and account in allowed_accounts:
            return False
    except KeyError:
        logging.info("No account allowlist condition found.")
    # Org Allowlist
    try:
        allowed_org_id = condition["StringNotEquals"]["aws:PrincipalOrgID"]
        if org_id and org_id == allowed_org_id:
            return False
    except KeyError:
        logging.info("No account allowlist condition found.")
    # If all of the conditions apply, return True: the SCP does apply
    return True


def find_blocking_scp(
    # The account, OU ID, or root ID that you want to query
    target,
    # The action that you want to test for.
    # It must be the full name of the action, no wildcards
    action,
    # The resource that you want to test access to
    # It must be the full ARN of the resource, no wildcards.
    resource,
    # [Optional] The region this request is occurring in
    # (Useful to filter out region-based Denies)
    region="",
    # [Optional] The ARN of the principal making this request
    # (Useful to filter out principal-based Denies)
    principal_arn="",
    # [Optional] The ID of the account making this request
    # (Useful to filter out account-based Denies)
    account="",
    # keyworded variable length of arguments
    **kwargs,
):
    """
    This is a script to help narrow down which SCP is blocking an action.

    Notes:
        This assumes that the SCP is using a default-allow (FullAWSAccess).
        This script will not be useful if you use a default-deny SCP model.
        This script does not handle most conditions currently.
        You will need to check conditions manually.
        The script does a cursory check of common allowlist conditions...
        ...specifically region, account, and principal.

    Example Usage:
    find_blocking_scp(
        target="999999999999",
        action="logs:DescribeLogGroups",
        resource="arn:aws:logs:us-west-1:999999999999:log-group::log-stream:",
    )
    """
    org_client = boto3.client("organizations")
    org_id = org_client.describe_organization()["Organization"]["Id"]
    current_target = target
    ou_stack = [current_target]
    while not re.match(r"r-", current_target):
        parent_resp = org_client.list_parents(ChildId=current_target)
        parent_id = parent_resp["Parents"][0]["Id"]
        ou_stack.append(parent_id)
        current_target = parent_id
    logging.info(ou_stack)
    # Then for each layer, list the policies,
    # then describe the policies so that we can check for the specified action
    for organizations_id in ou_stack:
        policies = org_client.list_policies_for_target(
            TargetId=organizations_id, Filter="SERVICE_CONTROL_POLICY"
        )["Policies"]
        for policy in policies:
            policy_id = policy["Id"]
            policy_response = org_client.describe_policy(PolicyId=policy_id)
            policy_content = policy_response["Policy"]["Content"]
            policy_name = policy_response["Policy"]["PolicySummary"]["Name"]
            policy_arn = policy_response["Policy"]["PolicySummary"]["Arn"]
            logging.warning(f"Querying policy {policy_name} (ARN {policy_arn})...")
            logging.debug(policy_content)
            policy_json = json.loads(policy_content)["Statement"]
            for statement in policy_json:
                if statement["Effect"] == "Deny":

                    # Check for Action value matches ###
                    if statement.get("Action"):
                        action_match = False
                        all_actions = statement["Action"]
                        # Standardize into a list if there's only one action
                        if isinstance(all_actions, str):
                            all_actions = [all_actions]
                        for action_identifier in all_actions:
                            action_identifier = action_identifier.replace("*", ".*")
                            if re.search(action_identifier, action):
                                action_match = True
                                break
                    elif statement.get("NotAction"):
                        action_match = True
                        all_notactions = statement["NotAction"]
                        # Standardize into a list if there's only one action
                        if isinstance(all_notactions, str):
                            all_notactions = [all_notactions]
                        for notaction_identifier in all_notactions:
                            notaction_identifier = notaction_identifier.replace(
                                "*", ".*"
                            )
                            if re.search(notaction_identifier, action):
                                action_match = False
                                break

                    # Check for Resource value matches
                    resource_match = False
                    all_resources = statement["Resource"]
                    # Standardize into a list if there's only one resource
                    if isinstance(all_resources, str):
                        all_resources = [all_resources]
                    for resource_identifier in all_resources:
                        resource_identifier = resource_identifier.replace("*", ".*")
                        if re.search(resource_identifier, resource):
                            resource_match = True
                            break

                    # Check for Conditions (LIMITED FUNCTIONALITY!!!)
                    try:
                        condition_json = statement["Condition"]
                        condition_match = check_conditions(
                            condition_json, region, principal_arn, account, org_id
                        )
                    except KeyError:
                        logging.debug("No Conditions key in statement.")
                        condition_match = True

                    # Filter out non-matching SCP statements
                    if resource_match and action_match and condition_match:
                        pretty_statement = json.dumps(statement, indent=4)
                        logging.warning(
                            f"Found a possibly-blocking SCP in policy {policy_name}:\r\n{pretty_statement}"
                        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCP Block Finder")
    parser.set_defaults(method=find_blocking_scp)
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="The account, OU ID, or root ID that you want to query.",
    )
    parser.add_argument(
        "--action",
        type=str,
        required=True,
        help="The action that you want to test access to. It must be the full name of the action (service:Action), no wildcards.",
    )
    parser.add_argument(
        "--resource",
        type=str,
        required=True,
        help="The resource that you want to test access to. It must be the full ARN of the resource, no wildcards.",
    )
    parser.add_argument(
        "--region",
        type=str,
        required=False,
        help="The region this request is occurring in.",
    )
    parser.add_argument(
        "--principal_arn",
        type=str,
        required=False,
        help="The ARN of the principal making this request.",
    )
    parser.add_argument(
        "--account",
        type=str,
        required=False,
        help="The ID of the account making this request.",
    )
    args = parser.parse_args()
    args.method(**vars(args))
