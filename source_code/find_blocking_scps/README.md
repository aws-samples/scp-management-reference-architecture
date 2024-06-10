# Find SCPs blocking your IAM Actions

*   To identify what SCP is denying your action, use this python script.
*   Add this script to somewhere in your PATH, then provide the target (account, OU, or root), resource, and action, and you'll get a shortlist of which SCPs may be blocking it.

> Note: You need to have permissions for an account that can query SCPs and the OUs they are attached to.

For more details, see the script!

## Example Usage

```bash
scp_block_finder.py --target "999999999999" --action "logs:DescribeLogGroups" --resource "arn:aws:logs:us-west-1:999999999999:log-group::log-stream:" --region "us-east-1"
```
