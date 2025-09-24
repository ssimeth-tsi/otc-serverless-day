variable "function_name_suffix" {
  description = "Suffix to append to function name for PR environments"
  default     = ""
}

locals {
  code_hash = filemd5("${path.module}/../code.zip")
  function_name = "fastapi_function${var.function_name_suffix}"
}

resource "opentelekomcloud_fgs_function_v2" "fastapi_function" {
  name        = local.function_name
  app         = "default"
  agency      = "functiongraph"
  handler     = "index.handler"
  memory_size = 256
  timeout     = 30
  runtime     = "Python3.9"
  vpc_id      = var.vpc_id
  network_id  = var.network_id
  code_type   = "zip"
  func_code   = filebase64("${path.module}/../code.zip")
  
  user_data = jsonencode({
    DATABASE_URL = "sqlite:///tmp/users.db"
  })
  
  lifecycle {
    ignore_changes = [user_data]
  }
}

# Output for Function URN
output "function_urn" {
  value       = opentelekomcloud_fgs_function_v2.fastapi_function.urn
  description = "URN of the deployed Function"
}

output "function_name" {
  value       = opentelekomcloud_fgs_function_v2.fastapi_function.name
  description = "Name of the deployed Function"
}