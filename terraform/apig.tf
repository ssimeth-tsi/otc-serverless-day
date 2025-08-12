# ------------------------
## API Gateway Configuration

# Variable für die Gateway ID
variable "api_gateway_id" {
  description = "ID of the dedicated API Gateway"
  default     = "ca0329375f9848578a4423f86eff3392"
}

# API erstellen
resource "opentelekomcloud_apigw_api_v2" "user_api" {
  gateway_id             = var.api_gateway_id
  group_id               = opentelekomcloud_apigw_group_v2.user_api_group.id
  name                   = "user-api${var.function_name_suffix}"
  type                   = "Public"
  request_protocol       = "HTTPS"
  request_method         = "ANY"
  request_uri            = "/users"
  match_mode             = "PREFIX"
  
  func_graph {
    function_urn     = opentelekomcloud_fgs_function_v2.fastapi_function.urn
    invocation_type  = "sync"
    timeout          = 30000
    version          = "latest"
  }
}

# Root API für Health Check
resource "opentelekomcloud_apigw_api_v2" "root_api" {
  gateway_id             = var.api_gateway_id
  group_id               = opentelekomcloud_apigw_group_v2.user_api_group.id
  name                   = "root-api${var.function_name_suffix}"
  type                   = "Public"
  request_protocol       = "HTTPS"
  request_method         = "GET"
  request_uri            = "/"
  match_mode             = "EXACT"
  
  func_graph {
    function_urn     = opentelekomcloud_fgs_function_v2.fastapi_function.urn
    invocation_type  = "sync"
    timeout          = 30000
    version          = "latest"
  }
}

# API Group erstellen
resource "opentelekomcloud_apigw_group_v2" "user_api_group" {
  instance_id = var.api_gateway_id
  name        = "user-api-group${var.function_name_suffix}"
  description = "API Group for User Management FastAPI Application"
}

# Verwende das existierende RELEASE Environment
# Die Environment-ID muss manuell ermittelt werden
variable "release_env_id" {
  description = "ID of the existing RELEASE environment"
  default     = "DEFAULT_ENVIRONMENT_RELEASE_ID"  # Diese ID muss aus der Console ermittelt werden
}

# API publizieren im RELEASE Environment
resource "opentelekomcloud_apigw_api_publishment_v2" "user_api_publish" {
  gateway_id     = var.api_gateway_id
  environment_id = var.release_env_id
  api_id         = opentelekomcloud_apigw_api_v2.user_api.id
}

resource "opentelekomcloud_apigw_api_publishment_v2" "root_api_publish" {
  gateway_id     = var.api_gateway_id
  environment_id = var.release_env_id
  api_id         = opentelekomcloud_apigw_api_v2.root_api.id
}



# Outputs
output "api_info" {
  value = {
    message         = "APIs created successfully."
    user_api_url    = format("https://%s.apic.eu-de.otc.t-systems.com%s", opentelekomcloud_apigw_group_v2.user_api_group.id,opentelekomcloud_apigw_api_v2.user_api.request_uri)
    api_group_id    = opentelekomcloud_apigw_group_v2.user_api_group.id
    user_api_id     = opentelekomcloud_apigw_api_v2.user_api.id
    root_api_id     = opentelekomcloud_apigw_api_v2.root_api.id
    gateway_id      = var.api_gateway_id
  }
  description = "API information"
}

# Separate outputs to avoid GitHub masking
output "api_base_url" {
  value = format("https://%s.apic.eu-de.otc.t-systems.com", opentelekomcloud_apigw_group_v2.user_api_group.id)
  description = "Base URL of the API"
}

output "api_endpoints" {
  value = {
    root  = "/"
    users = "/users"
  }
  description = "Available API endpoints"
}