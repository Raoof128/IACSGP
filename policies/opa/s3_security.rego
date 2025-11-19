# S3 Bucket Security Policies
# Ensures S3 buckets follow security best practices

package terraform.s3

import rego.v1

# Helper to get all S3 bucket resources
s3_buckets := [bucket |
    bucket := input.resource_changes[_]
    bucket.type == "aws_s3_bucket"
]

# Helper to get S3 public access blocks
public_access_blocks := [block |
    block := input.resource_changes[_]
    block.type == "aws_s3_bucket_public_access_block"
]

# Helper to get S3 bucket ACLs
bucket_acls := [acl |
    acl := input.resource_changes[_]
    acl.type == "aws_s3_bucket_acl"
]

# Helper to get S3 encryption configurations
encryption_configs := [config |
    config := input.resource_changes[_]
    config.type == "aws_s3_bucket_server_side_encryption_configuration"
]

# DENY: S3 buckets must have encryption enabled
deny_unencrypted_s3[msg] {
    bucket := s3_buckets[_]
    bucket_id := bucket.address

    # Check if there's a corresponding encryption config
    not has_encryption_config(bucket_id)

    msg := sprintf("S3 bucket '%s' does not have server-side encryption configured", [bucket_id])
}

# Helper function to check if bucket has encryption
has_encryption_config(bucket_address) {
    encryption := encryption_configs[_]
    # Extract bucket name from address
    bucket_name := split(bucket_address, ".")[1]
    contains(encryption.change.after.bucket, bucket_name)
}

# DENY: S3 buckets must block public access
deny_public_s3[msg] {
    block := public_access_blocks[_]
    block.change.after.block_public_acls == false

    msg := sprintf("S3 bucket public access block '%s' allows public ACLs (block_public_acls must be true)", [block.address])
}

deny_public_s3[msg] {
    block := public_access_blocks[_]
    block.change.after.block_public_policy == false

    msg := sprintf("S3 bucket public access block '%s' allows public policies (block_public_policy must be true)", [block.address])
}

deny_public_s3[msg] {
    block := public_access_blocks[_]
    block.change.after.restrict_public_buckets == false

    msg := sprintf("S3 bucket public access block '%s' does not restrict public buckets (restrict_public_buckets must be true)", [block.address])
}

# DENY: S3 bucket ACL must not be public-read or public-read-write
deny_public_acl[msg] {
    acl := bucket_acls[_]
    acl.change.after.acl == "public-read"

    msg := sprintf("S3 bucket ACL '%s' is set to 'public-read' which is insecure", [acl.address])
}

deny_public_acl[msg] {
    acl := bucket_acls[_]
    acl.change.after.acl == "public-read-write"

    msg := sprintf("S3 bucket ACL '%s' is set to 'public-read-write' which is insecure", [acl.address])
}

# WARN: S3 buckets should have versioning enabled
warn_no_versioning[msg] {
    bucket := s3_buckets[_]
    bucket_id := bucket.address
    not has_versioning(bucket_id)

    msg := sprintf("S3 bucket '%s' does not have versioning enabled (recommended)", [bucket_id])
}

# Helper to check versioning
has_versioning(bucket_address) {
    versioning := input.resource_changes[_]
    versioning.type == "aws_s3_bucket_versioning"
    bucket_name := split(bucket_address, ".")[1]
    contains(versioning.change.after.bucket, bucket_name)
    versioning.change.after.versioning_configuration[_].status == "Enabled"
}
