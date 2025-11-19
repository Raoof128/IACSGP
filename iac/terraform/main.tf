# Secure AWS Infrastructure Example
# This is a properly configured example that should pass all security checks

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
  region = var.aws_region
}

# Secure S3 Bucket with proper configuration
resource "aws_s3_bucket" "secure_bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = var.bucket_name
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "Terraform"
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "secure_bucket" {
  bucket = aws_s3_bucket.secure_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning
resource "aws_s3_bucket_versioning" "secure_bucket" {
  bucket = aws_s3_bucket.secure_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "secure_bucket" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Secure Security Group with restricted access
resource "aws_security_group" "secure_app" {
  name        = "${var.environment}-secure-app-sg"
  description = "Secure security group with restricted access"
  vpc_id      = var.vpc_id

  # Allow HTTPS from specific CIDR
  ingress {
    description = "HTTPS from corporate network"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.corporate_cidr]
  }

  # Allow HTTP from specific CIDR
  ingress {
    description = "HTTP from corporate network"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.corporate_cidr]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-secure-app-sg"
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "Terraform"
  }
}

# EBS Volume with encryption
resource "aws_ebs_volume" "secure_volume" {
  availability_zone = "${var.aws_region}a"
  size              = 20
  encrypted         = true
  type              = "gp3"

  tags = {
    Name        = "${var.environment}-secure-volume"
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "Terraform"
  }
}

# RDS Instance with encryption
resource "aws_db_instance" "secure_db" {
  identifier             = "${var.environment}-secure-db"
  engine                 = "postgres"
  engine_version         = "15.3"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_encrypted      = true
  db_name                = "securedb"
  username               = var.db_username
  password               = var.db_password
  skip_final_snapshot    = true
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.secure_app.id]

  tags = {
    Name        = "${var.environment}-secure-db"
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "Terraform"
  }
}
