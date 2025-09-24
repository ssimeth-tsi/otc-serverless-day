# ------------------------
## Terraform Configuration

terraform {
  # Backend configuration via CLI parameters
  # Initialize with: terraform init -backend-config=...
  backend "s3" {}

  required_providers {
    opentelekomcloud = {
      source = "opentelekomcloud/opentelekomcloud"
      version = ">=1.36.44"
    }
  }
}

# ------------------------
## Provider Configuration

provider "opentelekomcloud" {
  domain_name = var.domain_name
  tenant_name = var.tenant_name
  # For eu-de & eu_nl
  auth_url    = "https://iam.eu-de.otc.t-systems.com/v3"
  region      = var.region

  # For AK/SK
  access_key  = var.access_key
  secret_key  = var.secret_key
}

# ------------------------
## Variables

variable "domain_name" {
  description = "Name of the Domain (e.g. OTC00000000001000xxxxxx) set as TF_VAR_domain_name"
}

variable "tenant_name" {
  description = "Name of the Tenant (e.g. eu-de,eu-nl,eu-ch2) set as TF_VAR_tenant_name"
}

variable "region" {
  description = "Name of the Region (e.g. eu-de,eu-nl,eu-ch2) set as TF_VAR_region"
}

variable "access_key" {
  description = "Your AK set as TF_VAR_access_key"
}

variable "secret_key" {
  description = "Your SK set as TF_VAR_secret_key"
}

variable "vpc_id" {
  description = "VPC ID where the function will be deployed"
}

variable "network_id" {
  description = "Network ID (subnet) where the function will be deployed"
}

