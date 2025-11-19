# Tagging Policies
# Enforces mandatory tags on cloud resources

package terraform.tagging

import rego.v1

# Define mandatory tags
mandatory_tags := ["Environment", "Owner"]

# Recommended tags
recommended_tags := ["ManagedBy", "Name"]

# List of resource types that require tags
taggable_resources := [
    "aws_s3_bucket",
    "aws_security_group",
    "aws_instance",
    "aws_ebs_volume",
    "aws_db_instance",
    "aws_vpc",
    "aws_subnet",
    "aws_efs_file_system",
    "aws_dynamodb_table",
    "aws_lambda_function",
]

# DENY: Resources must have all mandatory tags
deny_missing_mandatory_tags[msg] {
    resource := input.resource_changes[_]
    resource.type == taggable_resources[_]

    # Get missing mandatory tags
    missing_tags := [tag |
        tag := mandatory_tags[_]
        not resource.change.after.tags[tag]
    ]

    count(missing_tags) > 0

    msg := sprintf("Resource '%s' is missing mandatory tags: %s", [resource.address, concat(", ", missing_tags)])
}

# DENY: Tag values must not be empty
deny_empty_tag_values[msg] {
    resource := input.resource_changes[_]
    resource.type == taggable_resources[_]

    # Check for empty tag values
    tag_key := mandatory_tags[_]
    tag_value := resource.change.after.tags[tag_key]
    tag_value == ""

    msg := sprintf("Resource '%s' has empty value for mandatory tag '%s'", [resource.address, tag_key])
}

# WARN: Resources should have recommended tags
warn_missing_recommended_tags[msg] {
    resource := input.resource_changes[_]
    resource.type == taggable_resources[_]

    # Get missing recommended tags
    missing_tags := [tag |
        tag := recommended_tags[_]
        not resource.change.after.tags[tag]
    ]

    count(missing_tags) > 0

    msg := sprintf("Resource '%s' is missing recommended tags: %s", [resource.address, concat(", ", missing_tags)])
}

# WARN: Environment tag should be valid
warn_invalid_environment[msg] {
    resource := input.resource_changes[_]
    resource.type == taggable_resources[_]

    env := resource.change.after.tags["Environment"]
    not env in ["dev", "development", "staging", "stage", "prod", "production", "test", "qa"]

    msg := sprintf("Resource '%s' has non-standard Environment tag value: '%s'", [resource.address, env])
}
