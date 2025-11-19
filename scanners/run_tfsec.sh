#!/bin/bash
# Run tfsec security scanner on Terraform code
# tfsec is a static analysis security scanner for Terraform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TERRAFORM_DIR="${1:-$PROJECT_ROOT/iac/terraform}"
OUTPUT_FORMAT="${2:-default}"
OUTPUT_FILE="${3:-$PROJECT_ROOT/reports/tfsec-report.json}"

echo "========================================="
echo "Running tfsec Security Scanner"
echo "========================================="
echo "Terraform Directory: $TERRAFORM_DIR"
echo "Output Format: $OUTPUT_FORMAT"
echo ""

# Create reports directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Check if tfsec is installed
if ! command -v tfsec &> /dev/null; then
    echo "ERROR: tfsec is not installed"
    echo "Install with: curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash"
    echo "Or using brew: brew install tfsec"
    exit 1
fi

echo "tfsec version: $(tfsec --version)"
echo ""

# Run tfsec with appropriate format
case $OUTPUT_FORMAT in
    json)
        tfsec "$TERRAFORM_DIR" \
            --format json \
            --out "$OUTPUT_FILE" \
            --soft-fail
        echo "JSON report saved to: $OUTPUT_FILE"
        ;;
    sarif)
        tfsec "$TERRAFORM_DIR" \
            --format sarif \
            --out "$OUTPUT_FILE" \
            --soft-fail
        echo "SARIF report saved to: $OUTPUT_FILE"
        ;;
    junit)
        tfsec "$TERRAFORM_DIR" \
            --format junit \
            --out "$OUTPUT_FILE" \
            --soft-fail
        echo "JUnit report saved to: $OUTPUT_FILE"
        ;;
    checkstyle)
        tfsec "$TERRAFORM_DIR" \
            --format checkstyle \
            --out "$OUTPUT_FILE" \
            --soft-fail
        echo "Checkstyle report saved to: $OUTPUT_FILE"
        ;;
    *)
        # Default output to console + JSON
        tfsec "$TERRAFORM_DIR" \
            --format default \
            --soft-fail

        # Also save JSON for programmatic access
        tfsec "$TERRAFORM_DIR" \
            --format json \
            --out "$OUTPUT_FILE" \
            --soft-fail
        echo ""
        echo "JSON report saved to: $OUTPUT_FILE"
        ;;
esac

echo ""
echo "tfsec scan complete!"
