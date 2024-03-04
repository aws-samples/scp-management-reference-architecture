"""
Summary
    This script will walk through the service_control_policies folder and generate SCP attachments based on its contents

Input
    A directory structure containing folders that match your AWS Organization, with JSON files representing SCP attachments.

Output
    A Terraform file that will create the SCP attachments using the `scp_module` like so:
    module "Service_Baseline_Root" {
        source          = "./scp_module"
        ...
    }
"""

import boto3
import glob
import logging
import os
import json
import re

SCP_FOLDER = "service_control_policies"
CHILD_TYPES = ["ORGANIZATIONAL_UNIT", "ACCOUNT"]
ACCOUNT_SUFFIX = "_ACCOUNT"  # Differentiates OU folders vs Account folders
OUTPUT_FILE = "scp_define_attach_auto.tf"
GLOBAL_SCP_NAME_LIST = (
    []
)  # TODO - Implement a check to ensure that same-named policies are not present

logging.basicConfig(level=logging.INFO)


def get_scp_attachments(current_target_id, current_path, data_dict, org_client):
    logging.info(f"Scanning {current_path} for SCP attachments")
    # Count the number of items in the current path and exit if more than 4
    custom_scp_count = 0
    for each_item in os.listdir(current_path):
        if (
            os.path.isfile(os.path.join(current_path, each_item))
            and not re.search(r"\.guardrail$", each_item)
            and not re.search(r"^FullAWSAccess\.placeholder$", each_item)
        ):
            custom_scp_count += 1
        if custom_scp_count > 4:
            raise Exception(
                f"The {current_path} folder has more than 4 attachments, making it invalid. Fix it before continuing."
            )
        if not re.search(r"(ROOT|ACCOUNT)$", current_path) and custom_scp_count > 2:
            raise Exception(
                f"The {current_path} folder is an OU folder with more than 2 custom attachments, making it invalid. Fix it before continuing."
            )
    for json in glob.glob(os.path.join(current_path, "*.json"), recursive=False):
        base_name = os.path.basename(json).replace(".json", "")
        data_dict[base_name] = {
            "path": f"{current_path}/{base_name}.json",
            "targets": [current_target_id],
        }
    # If there are SHARED files in the folder, create Terraform resources that reference their SHARED equivalent.
    for shared_json in glob.glob(os.path.join(current_path, "*.shared")):
        logging.info(
            f"Pulling policy attachment info for {shared_json} within {current_path}"
        )
        base_name = os.path.basename(shared_json).replace(".shared", "")
        if data_dict.get(base_name, ""):
            data_dict[base_name]["targets"].append(current_target_id)
        else:
            data_dict[base_name] = {
                "path": f"{SCP_FOLDER}/SHARED/{base_name}.json",
                "targets": [current_target_id],
            }
    # Get all child OUs and Accounts
    for child_type in CHILD_TYPES:
        if re.match(r"\d{12}", current_target_id):
            # Don't recurse into accounts
            continue
        children = org_client.list_children(
            ParentId=current_target_id, ChildType=child_type
        )
        while "NextToken" in children:
            children.append(
                org_client.list_children(
                    ParentId=current_target_id,
                    ChildType=child_type,
                    NextToken=children["NextToken"],
                )
            )
        for child in children["Children"]:
            object_id = child["Id"]
            if child_type == "ORGANIZATIONAL_UNIT":
                child_path_name = org_client.describe_organizational_unit(
                    OrganizationalUnitId=object_id
                )["OrganizationalUnit"]["Name"]
            else:
                child_path_name = (
                    org_client.describe_account(AccountId=object_id)["Account"]["Name"]
                    + ACCOUNT_SUFFIX
                )
            # Recursive call for each sub-OU
            try:
                data_dict.update(
                    get_scp_attachments(
                        current_target_id=object_id,
                        current_path=os.path.join(current_path, child_path_name),
                        data_dict=data_dict,
                        org_client=org_client,
                    )
                )
            except FileNotFoundError:
                raise FileNotFoundError(
                    "The AWS OU structure contains a resource without a matching file/folder in the SCP repo. To resolve this, run the update_scp_ou_structure workflow."
                )

    return data_dict


def get_terraform_resource_string(
    # Name of the SCP
    scp_name,
    # Path to the SCP JSON file, relative to the SCP_FOLDER
    scp_policy_path,
    # List of targets to attach the SCP to
    scp_target_list,
):
    """
    This function will return a string that represents a Terraform resource
    """
    scp_policy_path = scp_policy_path.replace("\\", "/")
    scp_target_list_string = ", ".join(f'"{s}"' for s in scp_target_list)
    scp_resource_string = f"""
module "{scp_name}" {{
    source          = "./scp_module"
    scp_name        = "{scp_name}"
    scp_desc        = jsondecode(file("./{scp_policy_path}")).description
    scp_policy      = jsonencode(jsondecode(file("./{scp_policy_path}")).policy)
    scp_target_list = [{scp_target_list_string}]
}}

output "{scp_name}_byte_size" {{
    value = module.{scp_name}.scp_byte_size
}}
"""
    return scp_resource_string


def main():
    org_client = boto3.client("organizations")
    root = org_client.list_roots()["Roots"][0]
    root_id = root["Id"]
    # The data dictionary will keep track of SCP name, source path, and targets
    data_dict = {}

    root_path = os.path.join(SCP_FOLDER, "ROOT")
    current_target_id = root_id
    current_path = root_path
    data_dict = get_scp_attachments(
        current_target_id=current_target_id,
        current_path=current_path,
        data_dict=data_dict,
        org_client=org_client,
    )
    # Write the Terraform manifest
    with open(OUTPUT_FILE, "w") as f:
        for scp_entry in data_dict:
            scp_policy_path = data_dict[scp_entry]["path"]
            scp_target_list = data_dict[scp_entry]["targets"]
            f.write(
                get_terraform_resource_string(
                    scp_name=scp_entry,
                    scp_policy_path=scp_policy_path,
                    scp_target_list=scp_target_list,
                )
            )


if __name__ == "__main__":
    main()