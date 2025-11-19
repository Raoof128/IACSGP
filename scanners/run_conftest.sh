#!/bin/bash
# Run Conftest with OPA policies on Terraform plans
# Conftest is a utility for testing structured data with OPA

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TERRAFORM_DIR="${1:-$PROJECT_ROOT/iac/terraform}"
POLICY_DIR="${2:-$PROJECT_ROOT/policies/opa}"
OUTPUT_FILE="${3:-$PROJECT_ROOT/reports/conftest-report.json}"

echo "========================================="
echo "Running Conftest/OPA Policy Checker"
echo "========================================="
echo "Terraform Directory: $TERRAFORM_DIR"
echo "Policy Directory: $POLICY_DIR"
echo ""

# Create reports directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_FILE")"
mkdir -p "$PROJECT_ROOT/reports/terraform-plans"

# Check if conftest is installed
if ! command -v conftest &> /dev/null; then
    echo "ERROR: Conftest is not installed"
    echo "Install with: curl -L https://github.com/open-policy-agent/conftest/releases/latest/download/conftest_linux_amd64 -o /usr/local/bin/conftest && chmod +x /usr/local/bin/conftest"
    echo "Or using brew: brew install conftest"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "ERROR: Terraform is not installed"
    echo "Install from: https://www.terraform.io/downloads"
    exit 1
fi

echo "Conftest version: $(conftest --version)"
echo "Terraform version: $(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4)"
echo ""

# Initialize Terraform (if needed)
echo "Initializing Terraform..."
cd "$TERRAFORM_DIR"
terraform init -backend=false -upgrade=false > /dev/null 2>&1 || true

# Generate Terraform plan in JSON format
PLAN_FILE="$PROJECT_ROOT/reports/terraform-plans/tfplan.json"
echo "Generating Terraform plan..."

# Create a dummy tfvars for planning (plan will fail but we can still test the config)
terraform plan -out=tfplan.binary -input=false > /dev/null 2>&1 || {
    echo "NOTE: Terraform plan failed (expected without real AWS credentials)"
    echo "      We'll test the configuration files directly"
}

if [ -f "tfplan.binary" ]; then
    terraform show -json tfplan.binary > "$PLAN_FILE" 2>/dev/null || true
    rm -f tfplan.binary
fi

# If plan failed, create a synthetic plan from the configuration
if [ ! -f "$PLAN_FILE" ] || [ ! -s "$PLAN_FILE" ]; then
    echo "Creating configuration snapshot for policy testing..."
    # For demo purposes, we'll test individual .tf files
    cd "$PROJECT_ROOT"
fi

# Run Conftest on Terraform files
echo ""
echo "Running OPA policies with Conftest..."
echo "--------------------------------------"

# Test all .tf files
FAILED=0
for tf_file in $(find "$TERRAFORM_DIR" -name "*.tf"); do
    echo "Testing: $(basename $tf_file)"

    # Run conftest and capture result
    if conftest test "$tf_file" \
        --policy "$POLICY_DIR" \
        --output json \
        --all-namespaces 2>&1 | tee -a "$OUTPUT_FILE.tmp"; then
        echo "  ✓ Passed"
    else
        echo "  ✗ Failed"
        FAILED=1
    fi
done

# Also test the plan if it exists
if [ -f "$PLAN_FILE" ] && [ -s "$PLAN_FILE" ]; then
    echo ""
    echo "Testing Terraform plan..."
    conftest test "$PLAN_FILE" \
        --policy "$POLICY_DIR" \
        --output json \
        --all-namespaces >> "$OUTPUT_FILE.tmp" 2>&1 || FAILED=1
fi

# Consolidate output
if [ -f "$OUTPUT_FILE.tmp" ]; then
    mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"
    echo ""
    echo "Policy check report saved to: $OUTPUT_FILE"
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "✓ All Conftest policy checks passed!"
    exit 0
else
    echo "✗ Some Conftest policy checks failed!"
    exit 1
fi
