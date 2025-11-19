# Encryption Policies
# Ensures encryption at rest for storage resources

package terraform.encryption

import rego.v1

# EBS Volume encryption check
deny_unencrypted_ebs[msg] {
    ebs := input.resource_changes[_]
    ebs.type == "aws_ebs_volume"

    # Check if encryption is explicitly disabled or not set
    ebs.change.after.encrypted == false

    msg := sprintf("EBS volume '%s' does not have encryption enabled", [ebs.address])
}

deny_unencrypted_ebs[msg] {
    ebs := input.resource_changes[_]
    ebs.type == "aws_ebs_volume"

    # Check if encryption field is not present
    not ebs.change.after.encrypted

    msg := sprintf("EBS volume '%s' does not have encryption configured", [ebs.address])
}

# RDS encryption check
deny_unencrypted_rds[msg] {
    rds := input.resource_changes[_]
    rds.type == "aws_db_instance"

    rds.change.after.storage_encrypted == false

    msg := sprintf("RDS instance '%s' does not have storage encryption enabled", [rds.address])
}

deny_unencrypted_rds[msg] {
    rds := input.resource_changes[_]
    rds.type == "aws_db_instance"

    not rds.change.after.storage_encrypted

    msg := sprintf("RDS instance '%s' does not have storage encryption configured", [rds.address])
}

# EC2 instance root volume encryption
deny_unencrypted_ec2_root[msg] {
    instance := input.resource_changes[_]
    instance.type == "aws_instance"

    root_block := instance.change.after.root_block_device[_]
    root_block.encrypted == false

    msg := sprintf("EC2 instance '%s' root volume is not encrypted", [instance.address])
}

# S3 bucket encryption (complementary to s3_security.rego)
deny_unencrypted_s3_bucket[msg] {
    bucket := input.resource_changes[_]
    bucket.type == "aws_s3_bucket"
    bucket_id := bucket.address

    not has_encryption_config(bucket_id)

    msg := sprintf("S3 bucket '%s' does not have server-side encryption enabled", [bucket_id])
}

# Helper to check for encryption configuration
has_encryption_config(bucket_address) {
    encryption := input.resource_changes[_]
    encryption.type == "aws_s3_bucket_server_side_encryption_configuration"
    bucket_name := split(bucket_address, ".")[1]
    contains(encryption.change.after.bucket, bucket_name)
}

# DynamoDB table encryption
deny_unencrypted_dynamodb[msg] {
    table := input.resource_changes[_]
    table.type == "aws_dynamodb_table"

    # Check if server-side encryption is disabled
    not table.change.after.server_side_encryption

    msg := sprintf("DynamoDB table '%s' does not have server-side encryption enabled", [table.address])
}

# EFS encryption check
deny_unencrypted_efs[msg] {
    efs := input.resource_changes[_]
    efs.type == "aws_efs_file_system"

    efs.change.after.encrypted == false

    msg := sprintf("EFS file system '%s' does not have encryption enabled", [efs.address])
}

# WARN: Resources should use KMS for encryption
warn_no_kms_encryption[msg] {
    ebs := input.resource_changes[_]
    ebs.type == "aws_ebs_volume"
    ebs.change.after.encrypted == true

    not ebs.change.after.kms_key_id

    msg := sprintf("EBS volume '%s' uses default encryption instead of KMS (recommended)", [ebs.address])
}
