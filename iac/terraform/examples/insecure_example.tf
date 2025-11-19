# INSECURE TERRAFORM EXAMPLE
# This file intentionally contains multiple security violations
# It should be flagged by the IaC security guardrails

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# VIOLATION 1: Public S3 bucket without encryption
resource "aws_s3_bucket" "public_bucket" {
  bucket = "insecure-public-bucket-example"
  # Missing tags: Owner, Environment
}

# VIOLATION 2: S3 bucket allows public access
resource "aws_s3_bucket_public_access_block" "public_bucket" {
  bucket = aws_s3_bucket.public_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# VIOLATION 3: Public read access on bucket
resource "aws_s3_bucket_acl" "public_bucket" {
  bucket = aws_s3_bucket.public_bucket.id
  acl    = "public-read"
}

# VIOLATION 4: Security group with unrestricted SSH access (0.0.0.0/0)
resource "aws_security_group" "insecure_ssh" {
  name        = "insecure-ssh-sg"
  description = "Insecure security group allowing SSH from anywhere"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "RDP from anywhere"
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow all traffic"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Missing mandatory tags
}

# VIOLATION 5: EBS volume without encryption
resource "aws_ebs_volume" "unencrypted" {
  availability_zone = "us-east-1a"
  size              = 10
  encrypted         = false

  # Missing tags
}

# VIOLATION 6: RDS instance without encryption
resource "aws_db_instance" "insecure_db" {
  identifier          = "insecure-database"
  engine              = "mysql"
  engine_version      = "8.0"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  storage_encrypted   = false
  username            = "admin"
  password            = "hardcoded-password-123"  # VIOLATION 7: Hardcoded password
  skip_final_snapshot = true
  publicly_accessible = true  # VIOLATION 8: Publicly accessible database

  # Missing tags
}

# VIOLATION 9: EC2 instance without encryption and IMDSv2
resource "aws_instance" "insecure_instance" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  metadata_options {
    http_tokens = "optional"  # Should be "required" for IMDSv2
  }

  root_block_device {
    encrypted = false
  }

  # Missing tags
}

# VIOLATION 10: Hardcoded secrets in variables (anti-pattern)
variable "api_key" {
  default = "AKIAIOSFODNN7EXAMPLE"  # Hardcoded AWS-like key
}

variable "secret_key" {
  default = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
