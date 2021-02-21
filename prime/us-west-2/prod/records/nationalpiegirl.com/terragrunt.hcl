# Terragrunt will copy the Terraform configurations specified by the source parameter, along with any files in the
# working directory, into a temporary folder, and execute your Terraform commands in that folder.
terraform {
  source = "../module"
}

# Include all settings from the root terragrunt.hcl file
include {
  path = find_in_parent_folders()
}

# These are the variables we have to pass in to use the module specified in the terragrunt configuration above
inputs = {
  soa = "ns-1088.awsdns-08.org. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400"
  dns_zone = "nationalpiegirl.com"
  email = false
  tags = {
    Env = "prod"
  }
}
