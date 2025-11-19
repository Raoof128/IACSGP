#!/bin/bash
# Run Checkov security scanner on Terraform code
# Checkov is a static code analysis tool for IaC

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TERRAFORM_DIR="${1:-$PROJECT_ROOT/iac/terraform}"
OUTPUT_FORMAT="${2:-cli}"
OUTPUT_FILE="${3:-$PROJECT_ROOT/reports/checkov-report.json}"

echo "========================================="
echo "Running Checkov Security Scanner"
echo "========================================="
echo "Terraform Directory: $TERRAFORM_DIR"
echo "Output Format: $OUTPUT_FORMAT"
echo ""

# Create reports directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Check if checkov is installed
if ! command -v checkov &> /dev/null; then
    echo "ERROR: Checkov is not installed"
    echo "Install with: pip install checkov"
    exit 1
fi

echo "Checkov version: $(checkov --version)"
echo ""

# Run Checkov with appropriate format
case $OUTPUT_FORMAT in
    json)
        checkov -d "$TERRAFORM_DIR" \
            --framework terraform \
            --output json \
            --output-file-path "$(dirname "$OUTPUT_FILE")" \
            --soft-fail
        echo "JSON report saved to: $OUTPUT_FILE"
        ;;
    sarif)
        checkov -d "$TERRAFORM_DIR" \
            --framework terraform \
            --output sarif \
            --output-file-path "$(dirname "$OUTPUT_FILE")" \
            --soft-fail
        echo "SARIF report saved to: $OUTPUT_FILE"
        ;;
    junit)
        checkov -d "$TERRAFORM_DIR" \
            --framework terraform \
            --output junitxml \
            --output-file-path "$(dirname "$OUTPUT_FILE")" \
            --soft-fail
        echo "JUnit report saved to: $OUTPUT_FILE"
        ;;
    *)
        # Default CLI output + save JSON
        checkov -d "$TERRAFORM_DIR" \
            --framework terraform \
            --compact \
            --soft-fail

        # Also save JSON for programmatic access
        checkov -d "$TERRAFORM_DIR" \
            --framework terraform \
            --output json \
            --output-file-path "$(dirname "$OUTPUT_FILE")" \
            --soft-fail \
            --quiet
        echo ""
        echo "JSON report saved to: $OUTPUT_FILE"
        ;;
esac

echo ""
echo "Checkov scan complete!"
