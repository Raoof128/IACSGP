#!/bin/bash
# Format and validate Terraform code
# This script runs terraform fmt and terraform validate

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TERRAFORM_DIR="${1:-$PROJECT_ROOT/iac/terraform}"

echo "========================================="
echo "Terraform Format and Validation"
echo "========================================="
echo "Terraform Directory: $TERRAFORM_DIR"
echo ""

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "ERROR: Terraform is not installed"
    echo "Install from: https://www.terraform.io/downloads"
    exit 1
fi

echo "Terraform version: $(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4)"
echo ""

cd "$TERRAFORM_DIR"

# Check formatting
echo "Checking Terraform formatting..."
if terraform fmt -check -recursive .; then
    echo "✓ All Terraform files are properly formatted"
else
    echo "✗ Some Terraform files are not properly formatted"
    echo ""
    echo "Run 'terraform fmt -recursive' to fix formatting issues"
    exit 1
fi

echo ""

# Initialize Terraform
echo "Initializing Terraform..."
terraform init -backend=false -upgrade=false > /dev/null 2>&1

echo ""

# Validate configuration
echo "Validating Terraform configuration..."
if terraform validate; then
    echo "✓ Terraform configuration is valid"
else
    echo "✗ Terraform configuration has errors"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ Format and validation checks passed!"
echo "========================================="
