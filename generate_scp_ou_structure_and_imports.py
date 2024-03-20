"""
Summary
    This script is a useful starting point if you have manually-managed SCPs that you want to migrate to IaC.
    This script will parse the OU structure and create SCP JSONs in a local representation of the OU structure.
    It will also generate import files to be used by Terraform, unless specified otherwise.

    This script can also be used to refresh the OU structure to make it easier to add new SCP attachments.
    To run this script to just refresh the OU structure and not make SCP updates or generate imports, run:
    python generate_scp_ou_structure_and_imports.py --skip-import-creation --skip-customer-scp-refresh
"""

import argparse
import boto3
from collections import Counter
import json
import logging
import os
import re

# Set log level to INFO
logging.basicConfig(level=logging.INFO)

# Initialize AWS Organizations client
org_client = boto3.client(
    "organizations",
)

# Define the local folder where you want to save the structure
OUTPUT_FOLDER = "service_control_policies"
IMPORT_POLICY_ATTACHMENTS_TF = "import_policy_attachments.tf"
# SCP_TERRAFORM_MANIFEST = "scp_define_attach.tf"


def get_all_scp_attachments(ou_id):
    """
    Return a list of all SCP attachments, 1 per attachment, to see what should be placed in SHARED.
    """
    list_of_policies_attached = []
    attached_scps = org_client.list_policies_for_target(
        TargetId=ou_id, Filter="SERVICE_CONTROL_POLICY"
    )["Policies"]
    for attached_scp in attached_scps:
        list_of_policies_attached.append(attached_scp["Name"])
    # Don't recurse into accounts
    if not re.match(r"\d{12}", ou_id):
        child_ous = org_client.list_organizational_units_for_parent(ParentId=ou_id)
        for child_ou in child_ous["OrganizationalUnits"]:
            child_attachments = get_all_scp_attachments(child_ou["Id"])
            for child_attachment in child_attachments:
                list_of_policies_attached.append(child_attachment)
        child_accounts = org_client.list_accounts_for_parent(ParentId=ou_id)
        for child_account in child_accounts["Accounts"]:
            child_attachments = get_all_scp_attachments(child_account["Id"])
            for child_attachment in child_attachments:
                list_of_policies_attached.append(child_attachment)
    return list_of_policies_attached


# Function to retrieve all child OUs recursively using NextTokens
def get_all_child_ous(parent_id, org_client, next_token=None, child_ous=[]):
    if next_token:
        response = org_client.list_organizational_units_for_parent(
            ParentId=parent_id, NextToken=next_token
        )
    else:
        response = org_client.list_organizational_units_for_parent(ParentId=parent_id)

    child_ous.extend(response["OrganizationalUnits"])

    if "NextToken" in response:
        get_all_child_ous(parent_id, response["NextToken"], child_ous)

    return child_ous


# Function to retrieve all child accounts recursively using NextTokens
def get_all_child_accounts(parent_id, org_client, next_token=None, child_accounts=[]):
    if next_token:
        response = org_client.list_accounts_for_parent(
            ParentId=parent_id, NextToken=next_token
        )
    else:
        response = org_client.list_accounts_for_parent(ParentId=parent_id)

    child_accounts.extend(response["Accounts"])

    if "NextToken" in response:
        get_all_child_accounts(parent_id, response["NextToken"], child_accounts)

    return child_accounts


def get_child_ou_and_scps(
    ou_id,
    starting_folder,
    all_attachments_counter,
    skip_import_creation,
    skip_customer_scp_refresh,
    attachment_dict: dict = {},
):
    """
    Walks through each OU/account in the Organization and

    This function will write files to disk in the folder structure within service_control_policies directory.


    Returns a dictionary of SCP attachments with each key representing an SCP (an SCP can be attached to multiple OUs).
    This return value can be used for troubleshooting purposes.
    """
    # Get OU Information -- OU here is root, OU, or account
    # Special case for root
    if re.match(r"r-", ou_id):
        ou_info = {}  # Empty dict to avoid KeyError: 'OrganizationalUnit'
        ou_info["OrganizationalUnit"] = {"Name": "ROOT"}
    # Special case for accounts
    elif re.match(r"\d{12}", ou_id):
        account_name = org_client.describe_account(AccountId=ou_id)["Account"]["Name"]
        ou_info = {}  # Empty dict to avoid KeyError: 'OrganizationalUnit'
        ou_info["OrganizationalUnit"] = {"Name": f"{account_name}_ACCOUNT"}
    else:
        ou_info = org_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
    ou_name = ou_info["OrganizationalUnit"]["Name"]
    ou_path = os.path.join(starting_folder, ou_name)

    # Create a folder for the current OU
    os.makedirs(ou_path, exist_ok=True)

    # List attached SCPs for the OU
    attached_scps = org_client.list_policies_for_target(
        TargetId=ou_id, Filter="SERVICE_CONTROL_POLICY"
    )

    # Save attached SCPs as JSON files
    for scp in attached_scps["Policies"]:
        # Skip FullAWSAccess SCP and AWS Guardrails SCPs
        if scp["Name"] == "FullAWSAccess":
            print(f"Adding Full AWS Access placeholder to {ou_path}")
            with open(os.path.join(ou_path, "FullAWSAccess.placeholder"), "w") as f:
                f.write("# Placeholder for FullAWSAccess")
            continue
        scp_id = scp["Id"]
        scp_name = scp["Name"]
        # Get description but fall back to name if blank
        scp_description = scp["Description"]
        if scp_description == "":
            scp_description = scp_name
        if re.match(r"aws-guardrails", scp["Name"]):
            target_path = os.path.join(ou_path, f"{scp_name}.guardrail")
            print(f"Adding Control Tower guardrail placeholder to {target_path}")
            with open(target_path, "w") as f:
                f.write(
                    f"# This is a placeholder for the Control Tower Guardrail SCP {scp_name}"
                )
            continue
        elif (
            scp_name in all_attachments_counter
            and all_attachments_counter[scp_name] > 1
            and not skip_customer_scp_refresh
        ):
            target_path = os.path.join(OUTPUT_FOLDER, "SHARED", f"{scp_name}.json")
            placeholder = os.path.join(ou_path, f"{scp_name}.shared")
            print(f"Adding shared placeholder for {scp_name} to {target_path}")
            with open(placeholder, "w") as f:
                f.write(f"# This is a placeholder for shared SCP {scp_name}")
        else:
            target_path = os.path.join(ou_path, f"{scp_name}.json")
        if skip_customer_scp_refresh:
            continue
        scp_document = org_client.describe_policy(PolicyId=scp_id)["Policy"]["Content"]
        scp_document_to_print = {
            "policy": json.loads(scp_document),
            "description": scp_description,
        }
        scp_json = json.dumps(scp_document_to_print, indent=4)
        print(f"Writing SCP to {target_path}")
        with open(target_path, "w") as f:
            f.write(scp_json)
        if not skip_import_creation:
            with open(IMPORT_POLICY_ATTACHMENTS_TF, "a") as f:
                f.write(
                    f"""
import {{
  to = module.{scp_name}.aws_organizations_policy_attachment.attach_scp["{ou_id}"]
  id = "{ou_id}:{scp_id}"
}}
"""
                )
        if attachment_dict.get(scp_name) is None:
            attachment_dict[scp_name] = {}
            attachment_dict[scp_name] = {
                "scp_name": scp_name,
                "scp_desc": scp_description,
                "target_path": target_path,
                "scp_target_list": [ou_id],
            }
        else:
            attachment_dict[scp_name]["scp_target_list"].append(ou_id)

    # Recursively process child OUs and accounts
    if not re.match(r"\d{12}", ou_id):
        child_ous = get_all_child_ous(ParentId=ou_id, org_client=org_client)
        child_accounts = get_all_child_accounts(ParentId=ou_id, org_client=org_client)
        for child in child_ous["OrganizationalUnits"] + child_accounts["Accounts"]:
            attachment_dict.update(
                get_child_ou_and_scps(
                    child["Id"],
                    starting_folder=ou_path,
                    all_attachments_counter=all_attachments_counter,
                    skip_import_creation=skip_import_creation,
                    skip_customer_scp_refresh=skip_customer_scp_refresh,
                    attachment_dict=attachment_dict,
                )
            )

    return attachment_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate SCP structure and import manifest"
    )
    parser.add_argument(
        "--skip-customer-scp-refresh",
        help="If specified, will leave customer SCPs alone and only refresh the externally managed (Control Tower guardrails and FullAWSAccess) SCPs",
        action="store_true",
    )
    parser.add_argument(
        "--skip-import-creation",
        help="If specified, will not create any import files during the script execution. Useful for refreshes of CT and FullAWSAccess SCPs",
        action="store_true",
    )
    args = parser.parse_args()
    skip_customer_scp_refresh = args.skip_customer_scp_refresh
    skip_import_creation = args.skip_import_creation
    # Create the output folder
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_FOLDER, "SHARED"), exist_ok=True)

    if not skip_import_creation:
        with open(IMPORT_POLICY_ATTACHMENTS_TF, "w") as f:
            f.write(
                f"""# This file was automatically generated by {os.path.basename(__file__)} and may require manual review
    """
            )
    # Get a list of all existing SCPs in the Organization
    response = org_client.list_policies(Filter="SERVICE_CONTROL_POLICY")
    all_policies = response["Policies"]
    # Loop through responses while there is a NextToken
    while "NextToken" in response:
        response = org_client.list_policies(
            Filter="SERVICE_CONTROL_POLICY", NextToken=response["NextToken"]
        )
        all_policies.extend(response["Policies"])
    # Exclude CT-managed (aws-guardrails) and FullAWSAccess
    all_policies = [
        policy
        for policy in all_policies
        if (
            policy["Name"] != "FullAWSAccess"
            and not re.match(r"aws-guardrails", policy["Name"])
        )
    ]

    if not skip_import_creation:
        with open("import_policies.tf", "w") as f:
            logging.info("Generating policy import manifest...")
            for policy in all_policies:
                policy_id = policy["Id"]
                policy_name = policy["Name"]
                module_name = policy_name.replace(" ", "_")
                f.write(
                    f"""
import {{
    to = module.{module_name}.aws_organizations_policy.create_scp
    id = "{policy_id}"
}}
"""
                )

    all_policy_names = [policy["Name"] for policy in all_policies]

    # Get the root of the organization tree
    root_id = org_client.list_roots()["Roots"][0]["Id"]
    all_scp_attachments = get_all_scp_attachments(ou_id=root_id)
    all_attachments_counter = Counter(all_scp_attachments)

    # Start parsing the organization structure
    all_attachments = get_child_ou_and_scps(
        ou_id=root_id,
        starting_folder=OUTPUT_FOLDER,
        skip_import_creation=skip_import_creation,
        skip_customer_scp_refresh=skip_customer_scp_refresh,
        all_attachments_counter=all_attachments_counter,
    )

    if not skip_customer_scp_refresh:
        logging.info("Printing attachment details for customer managed SCPs...")
        logging.info(all_attachments)
    logging.info(f"Organization structure and SCPs saved in {OUTPUT_FOLDER}")
