# Security Policies Reference

Comprehensive guide to all security policies enforced by IaC Security Guardrails.

## Table of Contents

- [S3 Security](#s3-security)
- [Security Groups](#security-groups)
- [Encryption](#encryption)
- [Resource Tagging](#resource-tagging)
- [Secrets Detection](#secrets-detection)
- [Customization](#customization)

---

## S3 Security

**Policy File**: `policies/opa/s3_security.rego`

### Rules

#### ❌ DENY: S3 Buckets Without Encryption

**Rule ID**: `s3_encryption`

**Description**: All S3 buckets must have server-side encryption enabled.

**Rationale**: Unencrypted data at rest can be accessed if physical storage is compromised.

**Compliant Example**:
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-secure-bucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

**Non-Compliant Example**:
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  # Missing encryption configuration
}
```

#### ❌ DENY: Public S3 Buckets

**Rule ID**: `s3_public_access`

**Description**: S3 buckets must block all public access.

**Rationale**: Publicly accessible buckets can lead to data breaches.

**Compliant Example**:
```hcl
resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

**Non-Compliant Example**:
```hcl
resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id

  block_public_acls       = false  # ❌ Allows public ACLs
  block_public_policy     = false  # ❌ Allows public policies
}
```

#### ❌ DENY: Public ACLs

**Rule ID**: `s3_public_acl`

**Description**: S3 bucket ACLs must not be set to public-read or public-read-write.

**Rationale**: Public ACLs expose data to the internet.

**Non-Compliant Example**:
```hcl
resource "aws_s3_bucket_acl" "example" {
  bucket = aws_s3_bucket.example.id
  acl    = "public-read"  # ❌ Public access
}
```

---

## Security Groups

**Policy File**: `policies/opa/security_groups.rego`

### Rules

#### ❌ DENY: SSH from Internet

**Rule ID**: `sg_ssh_from_internet`

**Description**: Security groups must not allow SSH (port 22) from 0.0.0.0/0.

**Rationale**: Open SSH access is the #1 attack vector for cloud breaches.

**Compliant Example**:
```hcl
resource "aws_security_group" "example" {
  ingress {
    description = "SSH from corporate network only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # ✅ Restricted CIDR
  }
}
```

**Non-Compliant Example**:
```hcl
resource "aws_security_group" "example" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ Open to internet
  }
}
```

#### ❌ DENY: RDP from Internet

**Rule ID**: `sg_rdp_from_internet`

**Description**: Security groups must not allow RDP (port 3389) from 0.0.0.0/0.

**Rationale**: RDP is frequently targeted for brute-force attacks.

#### ❌ DENY: All Ports from Internet

**Rule ID**: `sg_all_ports_from_internet`

**Description**: Security groups must not allow all ports from 0.0.0.0/0.

**Non-Compliant Example**:
```hcl
resource "aws_security_group" "example" {
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ All ports open
  }
}
```

---

## Encryption

**Policy File**: `policies/opa/encryption.rego`

### Rules

#### ❌ DENY: Unencrypted EBS Volumes

**Rule ID**: `ebs_encryption`

**Description**: All EBS volumes must have encryption enabled.

**Compliant Example**:
```hcl
resource "aws_ebs_volume" "example" {
  availability_zone = "us-west-2a"
  size              = 20
  encrypted         = true  # ✅ Encrypted
}
```

**Non-Compliant Example**:
```hcl
resource "aws_ebs_volume" "example" {
  availability_zone = "us-west-2a"
  size              = 20
  encrypted         = false  # ❌ Not encrypted
}
```

#### ❌ DENY: Unencrypted RDS Instances

**Rule ID**: `rds_encryption`

**Description**: All RDS instances must have storage encryption enabled.

**Compliant Example**:
```hcl
resource "aws_db_instance" "example" {
  # ... other config
  storage_encrypted = true  # ✅ Encrypted
}
```

#### ❌ DENY: Unencrypted EC2 Root Volumes

**Rule ID**: `ec2_root_encryption`

**Description**: EC2 instance root volumes must be encrypted.

**Compliant Example**:
```hcl
resource "aws_instance" "example" {
  # ... other config

  root_block_device {
    encrypted = true  # ✅ Encrypted
  }
}
```

---

## Resource Tagging

**Policy File**: `policies/opa/tagging.rego`

### Mandatory Tags

All taggable resources must include:

- **Environment**: dev, staging, prod
- **Owner**: Team or individual responsible

### Recommended Tags

- **ManagedBy**: Terraform, CloudFormation, etc.
- **Name**: Human-readable resource name

### Rules

#### ❌ DENY: Missing Mandatory Tags

**Rule ID**: `tagging_mandatory`

**Description**: All resources must have Environment and Owner tags.

**Compliant Example**:
```hcl
resource "aws_instance" "example" {
  # ... other config

  tags = {
    Name        = "web-server"
    Environment = "prod"
    Owner       = "platform-team"
    ManagedBy   = "Terraform"
  }
}
```

**Non-Compliant Example**:
```hcl
resource "aws_instance" "example" {
  # ... other config

  tags = {
    Name = "web-server"
    # ❌ Missing Environment and Owner
  }
}
```

#### ❌ DENY: Empty Tag Values

**Rule ID**: `tagging_empty_values`

**Description**: Tag values must not be empty strings.

---

## Secrets Detection

**Policy File**: `policies/opa/secrets.rego`

### Rules

#### ❌ DENY: Hardcoded Database Passwords

**Rule ID**: `secrets_db_password`

**Description**: Database passwords must not be hardcoded.

**Compliant Example**:
```hcl
variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "example" {
  password = var.db_password  # ✅ From variable
}
```

**Non-Compliant Example**:
```hcl
resource "aws_db_instance" "example" {
  password = "MyP@ssw0rd123"  # ❌ Hardcoded
}
```

#### ❌ DENY: Hardcoded AWS Keys

**Rule ID**: `secrets_aws_keys`

**Description**: AWS access keys must not be hardcoded.

**Pattern**: `AKIA[0-9A-Z]{16}`

#### ❌ DENY: Publicly Accessible Databases

**Rule ID**: `secrets_public_db`

**Description**: RDS instances must not be publicly accessible.

**Compliant Example**:
```hcl
resource "aws_db_instance" "example" {
  publicly_accessible = false  # ✅ Private
}
```

---

## Customization

### Severity Levels

You can customize severity levels for your organization:

```python
# In iac_guard.py, modify the severity mapping
def _map_tfsec_severity(self, severity_str: str) -> Severity:
    mapping = {
        "CRITICAL": Severity.CRITICAL,
        "HIGH": Severity.HIGH,
        "MEDIUM": Severity.MEDIUM,
        "LOW": Severity.LOW,
    }
    return mapping.get(severity_str.upper(), Severity.INFO)
```

### Adding Custom Policies

Create a new `.rego` file in `policies/opa/`:

```rego
package terraform.custom

import rego.v1

# Example: Deny Lambda without timeout
deny_lambda_no_timeout[msg] {
    lambda := input.resource_changes[_]
    lambda.type == "aws_lambda_function"

    not lambda.change.after.timeout

    msg := sprintf("Lambda '%s' must specify a timeout", [lambda.address])
}
```

### Exemptions

Use inline suppressions for justified exceptions:

```hcl
# tfsec:ignore:AWS017
resource "aws_s3_bucket" "public_website" {
  # Justified: This is intentionally a public website bucket
  bucket = "my-public-website"
}
```

For Checkov:
```hcl
# checkov:skip=CKV_AWS_18:Public bucket required for static website
resource "aws_s3_bucket" "public_website" {
  bucket = "my-public-website"
}
```

---

## Policy Testing

Test your policies work correctly:

```bash
# Test against insecure examples (should fail)
python3 iac_guard.py scan --path ./iac/terraform/examples

# Test against secure examples (should pass)
python3 iac_guard.py scan --path ./iac/terraform
```

---

**Last Updated**: 2024-01-15
