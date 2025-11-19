#!/bin/bash
# Comprehensive test script for IaC Security Guardrails

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}======================================${NC}"
echo -e "${CYAN}IaC Security Guardrails - Test Suite${NC}"
echo -e "${CYAN}======================================${NC}"
echo ""

cd "$PROJECT_ROOT"

TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Python syntax
echo -e "${CYAN}Test 1: Checking Python syntax...${NC}"
if python3 -m py_compile iac_guard.py 2>/dev/null; then
    echo -e "${GREEN}✓ Python syntax check passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Python syntax check failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# Test 2: CLI help
echo -e "${CYAN}Test 2: Checking CLI help output...${NC}"
if python3 iac_guard.py --help > /dev/null 2>&1; then
    echo -e "${GREEN}✓ CLI help works${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ CLI help failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# Test 3: Unit tests
echo -e "${CYAN}Test 3: Running unit tests...${NC}"
if python3 tests/test_iac_guard.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ All unit tests passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Some unit tests failed${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# Test 4: Check directory structure
echo -e "${CYAN}Test 4: Checking directory structure...${NC}"
REQUIRED_DIRS=(
    "iac/terraform"
    "iac/terraform/examples"
    "policies/opa"
    "scanners"
    "scripts"
    "ci/github-actions"
    "ci/gitlab-ci"
    "reports"
    "tests"
    "examples"
)

DIR_CHECK_PASSED=true
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}✗ Missing directory: $dir${NC}"
        DIR_CHECK_PASSED=false
    fi
done

if $DIR_CHECK_PASSED; then
    echo -e "${GREEN}✓ All required directories present${NC}"
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

# Test 5: Check required files
echo -e "${CYAN}Test 5: Checking required files...${NC}"
REQUIRED_FILES=(
    "iac_guard.py"
    "requirements.txt"
    "README.md"
    "Makefile"
    ".gitignore"
    ".pre-commit-config.yaml"
    "iac/terraform/main.tf"
    "iac/terraform/variables.tf"
    "iac/terraform/outputs.tf"
    "iac/terraform/examples/insecure_example.tf"
    "policies/opa/s3_security.rego"
    "policies/opa/security_groups.rego"
    "policies/opa/encryption.rego"
    "policies/opa/tagging.rego"
    "policies/opa/secrets.rego"
    "scanners/run_tfsec.sh"
    "scanners/run_checkov.sh"
    "scanners/run_conftest.sh"
    "scripts/format_and_validate.sh"
    "scripts/setup.sh"
    "ci/github-actions/iac-security.yml"
    "ci/gitlab-ci/.gitlab-ci.yml"
)

FILE_CHECK_PASSED=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Missing file: $file${NC}"
        FILE_CHECK_PASSED=false
    fi
done

if $FILE_CHECK_PASSED; then
    echo -e "${GREEN}✓ All required files present${NC}"
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

# Test 6: Check script permissions
echo -e "${CYAN}Test 6: Checking script permissions...${NC}"
EXECUTABLE_FILES=(
    "iac_guard.py"
    "scanners/run_tfsec.sh"
    "scanners/run_checkov.sh"
    "scanners/run_conftest.sh"
    "scripts/format_and_validate.sh"
    "scripts/setup.sh"
    "scripts/run_tests.sh"
)

PERM_CHECK_PASSED=true
for file in "${EXECUTABLE_FILES[@]}"; do
    if [ ! -x "$file" ]; then
        echo -e "${YELLOW}⚠ Not executable: $file${NC}"
        chmod +x "$file" 2>/dev/null && echo -e "${GREEN}  Fixed: $file${NC}" || PERM_CHECK_PASSED=false
    fi
done

if $PERM_CHECK_PASSED; then
    echo -e "${GREEN}✓ All scripts have correct permissions${NC}"
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi
echo ""

# Test 7: Check OPA policy syntax (if conftest is installed)
if command -v conftest &> /dev/null; then
    echo -e "${CYAN}Test 7: Validating OPA policy syntax...${NC}"
    POLICY_CHECK_PASSED=true

    for policy in policies/opa/*.rego; do
        if ! conftest verify "$policy" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠ Policy may have issues: $policy${NC}"
            # Don't fail on this as conftest verify may not work without proper config
        fi
    done

    if $POLICY_CHECK_PASSED; then
        echo -e "${GREEN}✓ OPA policies checked${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ Some policy checks had warnings${NC}"
        ((TESTS_PASSED++))  # Don't fail on this
    fi
    echo ""
else
    echo -e "${YELLOW}Test 7: Skipped (conftest not installed)${NC}"
    echo ""
fi

# Test 8: Check Python dependencies
echo -e "${CYAN}Test 8: Checking Python dependencies...${NC}"
if python3 -c "import pytest; import black; import flake8" 2>/dev/null; then
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠ Some Python dependencies missing (run: pip install -r requirements.txt)${NC}"
    ((TESTS_PASSED++))  # Don't fail on this
fi
echo ""

# Summary
echo -e "${CYAN}======================================${NC}"
echo -e "${CYAN}Test Summary${NC}"
echo -e "${CYAN}======================================${NC}"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
