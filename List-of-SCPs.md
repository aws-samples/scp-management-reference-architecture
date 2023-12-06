# List of Service Control Policies

Here is a list of sample service control policies provided as a prescriptive guidance for you. You can start building SCP management architecture for your organization with these policies.

---

## List of Account Baseline SCPs

All SCP policies that fall under the SCP category - Account Baseline, are defined in the below list

| SCP Name                         | Policy Statements in the SCP                                      | Applicable Resources   | Attached to OUs / Accounts                            | Role / OU Exemptions                                                                                                       | Other Conditions                              |
| -------------------------------- | ----------------------------------------------------------------- | ---------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Account_Baseline_Root            | Prevent organization leave, delete, or remove actions             | All (\*)               | Root                                                  |                                                                                                               |                                               |
|                                  | Prevent Modifications to Specific Lambda Functions                | Currently a place holder | Root                                                  |  |                                               |
|                                  | Prevent account region enable and disable                         | All (\*)               | Root                                                  |                                                                           |                                               |
|                                  | Prevent billing modification                                      | All (\*)               | Root                                                  |                                                                                                                            |                                               |
|                                  | Prevent specific tag modifications                                | All (\*)               | Root                                                  |                                                                                                                            |  |
|
| Account_Baseline_AllowedServices (Multi OU)| Deny any AWS service usage outside the approved list              | All (\*)               | All OUs except Testing OUs (like Sandbox) OU |||
                                
---

## List of Infrastrcuture Baseline SCPs

All SCP policies that fall under the SCP category - Infrastructure Baseline, are defined in the list below.

> NOTE: While designing these SCPs we have considered Infrastcruture OU as the dedicated OU created to host the adminsitrative accounts where networking services are built and managed for the entire organization.

| SCP Name                              | Policy Statements in the SCP                                                                           | Applicable Resources | Applicable OUs / Accounts                                     | Role Exemptions                                                                                                                                                                       | Other Conditions |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Infrastructure_Baseline_Root                 | Prevent Creating Default VPC and Subnet and Classic VPC Links                                          | All (\*)             | Root                                                          |                                                                                                                                                                                       |                  |
|                                       | Enforce use of IMDSv2 for instance creation                                                            | All EC2 Instances    | Root | |                  |
|                                       | Prevent removal of IMDSv2                                                                              | All EC2 Instances    | Root  |   |                  |
|                                       | Prevent VPC privilege actions                                                                          | All (\*)             | Root                                                          | | |
| Infrastructure_Baseline_VPCBoundaries        | Prevent broad list of privilege VPC and EC2 Actions                                                    | All (\*)             | All OUs except Infrastructure OU | | |
|                                       | Prevent write actions for DirectConnect, Global Accelerator, CloudFront, Internet gateway, VPC Peering | All (\*)             | All OUs except Infrastructure OU    |                                                                                                                                                                                       |                  |
| Infrastructure_Baseline_InfrastructureOU | Prevent DHCP options, Subnet CIDR, Network ACLs, Route Table edit actions                              | All (\*)             | Infrastructure OU                                  |  |                  |
|                                       |                                                                                                        |                      |                                                               |                                                                                                                                                                                       |                  |

---

## List of Security Baseline SCPs

All SCP policies that fall under the SCP category - Security Baseline, are defined in the list below

> NOTE: In this solution, we have designed the SCPs for KMS such that KMS Key creation is allowed to all but KMS Key Deletion is only allowed to federated roles (only secuyrity administrator). Since it cannot be anticipated which pipeline roles will be creating amd managing KMS keys hence if any pipeline role is allowed to delete KMS keys then **it would raise a priviledge escalation scenario** hence if you need to delete a KMS key then reach out to the role-taker of the federated role allowed to delete the key, present a valid business case and accordingly get the key deleted.

| SCP Name               | Policy Statements in the SCP                        | Applicable Resources                         | Applicable OUs / Accounts | Role Exemptions                                                                                                                                                                                                                                            | Other Conditions |
| ---------------------- | --------------------------------------------------- | -------------------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Security_Baseline_Root | Prevent Root activities in member accounts          | All (\*)                                     | Root                      |                                                                                                                                                                                                                                                            |                  |
|                        | Prevent KMS Key Deletion                            | All (\*)                                     | Root                      | |                  |
|                        | Prevent IAM User creation                           | All (\*)                                     | Root                      | |                  |
|                        | Prevent IAM User password and access keys creation  | All (\*)                                     | Root                      | |                  |
|                        | Prevent federation write activities through AWS IAM | All (\*)                                     | Root                      | |                  |
|                        | Prevent write actions for privilege IAM roles       | Breakglass-role, place holder for more roles | Root                      | |                  |
|                        | Prevent modification of other Security Services     | All (\*)                                     | Root                      | |                  |
|                        |                                                     |                                              |                           

---

## List of Data Baseline SCPs

> **Pre-requisite** - A service enablement is requested before deploying the data baseline SCPs - **Configure S3 service block public access at account level** so that any bucket created in S3 will have public access blocked by default

All SCP policies that are defined in any of the Data Baseline SCP files, should be defined in the below list

| SCP Name              | Policy Statements in the SCP                         | Applicable Resources                   | Applicable OUs / Accounts | Role Exemptions                                                                                                                                                           | Other Conditions |
| --------------------- | ---------------------------------------------------- | -------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Data_Baseline_Root | Prevent deletion of critical buckets and its objects | Place holder for critical bucket names | Root                      | |                  |
|                       | Prevent S3 public access                             | All (\*)                               | Root                      | |                  |
|                       | Prevent disabling EBS encryption                     | All (\*)                               | Root                      | |                  |
|                       | Prevent creation of unencrypted RDS instances        | All (\*)                               | Root                      | |                  |
|                       |                                                      |                                        |                           |                                                                                                                                                                           |                  |
