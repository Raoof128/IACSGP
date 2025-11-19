# Secrets Detection Policies
# Detects hardcoded secrets and credentials in Terraform code

package terraform.secrets

import rego.v1

# Patterns for detecting potential secrets
suspicious_patterns := {
    "aws_access_key": "AKIA[0-9A-Z]{16}",
    "password": "password",
    "secret": "secret",
    "api_key": "api[_-]?key",
}

# Get all resource changes
all_resources := [r | r := input.resource_changes[_]]

# Get all variables
all_variables := [v | v := input.variables[_]]

# DENY: Databases must not have hardcoded passwords
deny_hardcoded_db_password[msg] {
    db := input.resource_changes[_]
    db.type == "aws_db_instance"

    password := db.change.after.password

    # Check if password looks hardcoded (not a variable/reference)
    not startswith(password, "var.")
    not startswith(password, "data.")
    not contains(password, "random_password")

    msg := sprintf("RDS instance '%s' appears to have a hardcoded password - use AWS Secrets Manager or variables instead", [db.address])
}

# DENY: Variables must not have hardcoded AWS access keys
deny_hardcoded_aws_keys[msg] {
    resource := all_resources[_]

    # Convert resource to string for pattern matching
    resource_str := sprintf("%v", [resource.change.after])

    # Check for AWS access key pattern
    regex.match("AKIA[0-9A-Z]{16}", resource_str)

    msg := sprintf("Resource '%s' contains what appears to be a hardcoded AWS access key", [resource.address])
}

# DENY: Check for common password/secret field patterns
deny_suspicious_hardcoded_values[msg] {
    resource := all_resources[_]

    # Check various common secret fields
    suspicious_field := has_suspicious_field(resource)

    msg := sprintf("Resource '%s' may contain hardcoded secrets in field '%s'", [resource.address, suspicious_field])
}

# Helper to check for suspicious fields
has_suspicious_field(resource) := field {
    after := resource.change.after
    field := ["password", "secret_key", "api_key", "access_key", "secret_access_key"][_]
    value := object.get(after, field, "")
    value != ""
    not startswith(value, "var.")
    not startswith(value, "data.")
}

# DENY: EC2 user_data must not contain secrets
deny_secrets_in_userdata[msg] {
    instance := input.resource_changes[_]
    instance.type == "aws_instance"

    user_data := instance.change.after.user_data

    # Check for common secret patterns in user_data
    contains(lower(user_data), "password")
    contains(user_data, "=")

    msg := sprintf("EC2 instance '%s' user_data may contain embedded secrets", [instance.address])
}

# WARN: Sensitive values should use sensitive = true
warn_unmarked_sensitive_fields[msg] {
    resource := all_resources[_]
    resource.type == "aws_db_instance"

    # Password exists but might not be marked sensitive in variables
    resource.change.after.password

    msg := sprintf("RDS instance '%s' has a password field - ensure it's marked as sensitive in variables", [resource.address])
}

# DENY: Public exposure of databases
deny_public_database[msg] {
    db := input.resource_changes[_]
    db.type == "aws_db_instance"

    db.change.after.publicly_accessible == true

    msg := sprintf("RDS instance '%s' is publicly accessible - this is a critical security risk", [db.address])
}

# Helper function to convert to lowercase
lower(str) := lower_str {
    lower_str := lower(str)
}
