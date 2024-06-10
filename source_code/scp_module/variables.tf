variable "scp_name" {
  description = "Name to be used for the SCP"
  type        = string
}

variable "scp_desc" {
  description = "Description of the SCP"
  type        = string
}

variable "scp_policy" {
  description = "Customer managed SCP policy json to be attached"
  type        = string
  validation {
    condition = (
      length(var.scp_policy) < 5120
    )
    error_message = "Your SCP would exceed the AWS Quota of 5120 characters. Reduce its size."
  }
}

variable "scp_target_list" {
  description = "A list of Target IDs to which the SCP will be attached. It can be the Root OU or individual OUs or individual AWS Account"
  type        = list(string)
  default     = []
}
