#!/bin/bash
# Setup script for IaC Security Guardrails
# This script installs all dependencies and configures the environment

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
echo -e "${CYAN}IaC Security Guardrails - Setup${NC}"
echo -e "${CYAN}======================================${NC}"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${YELLOW}⚠ Terraform is not installed${NC}"
    echo "Installing Terraform..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget -q https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
        unzip -q terraform_1.6.0_linux_amd64.zip
        sudo mv terraform /usr/local/bin/
        rm terraform_1.6.0_linux_amd64.zip
        echo -e "${GREEN}✓ Terraform installed${NC}"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install terraform
            echo -e "${GREEN}✓ Terraform installed${NC}"
        else
            echo -e "${RED}✗ Homebrew not found. Please install Terraform manually${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Please install Terraform manually from https://www.terraform.io/downloads${NC}"
    fi
else
    TERRAFORM_VERSION=$(terraform version -json | grep -o '"terraform_version":"[^"]*' | cut -d'"' -f4 2>/dev/null || terraform version | head -1)
    echo -e "${GREEN}✓ Terraform ${TERRAFORM_VERSION} found${NC}"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
cd "$PROJECT_ROOT"
pip install -r requirements.txt > /dev/null 2>&1 || pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Install tfsec
echo ""
echo "Installing tfsec..."
if command -v tfsec &> /dev/null; then
    echo -e "${GREEN}✓ tfsec already installed${NC}"
else
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
        sudo mv tfsec /usr/local/bin/ 2>/dev/null || mv tfsec /usr/local/bin/
        echo -e "${GREEN}✓ tfsec installed${NC}"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install tfsec
            echo -e "${GREEN}✓ tfsec installed${NC}"
        else
            echo -e "${YELLOW}⚠ Please install tfsec manually: brew install tfsec${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Please install tfsec manually from https://github.com/aquasecurity/tfsec${NC}"
    fi
fi

# Install Checkov
echo ""
echo "Installing Checkov..."
if command -v checkov &> /dev/null; then
    echo -e "${GREEN}✓ Checkov already installed${NC}"
else
    pip install checkov > /dev/null 2>&1 || pip install checkov
    echo -e "${GREEN}✓ Checkov installed${NC}"
fi

# Install Conftest (optional)
echo ""
echo "Installing Conftest (optional)..."
if command -v conftest &> /dev/null; then
    echo -e "${GREEN}✓ Conftest already installed${NC}"
else
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install conftest
            echo -e "${GREEN}✓ Conftest installed${NC}"
        else
            echo -e "${YELLOW}⚠ Conftest installation skipped (optional)${NC}"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        CONFTEST_VERSION=0.45.0
        wget -q "https://github.com/open-policy-agent/conftest/releases/download/v${CONFTEST_VERSION}/conftest_${CONFTEST_VERSION}_Linux_x86_64.tar.gz"
        tar xzf conftest_${CONFTEST_VERSION}_Linux_x86_64.tar.gz
        sudo mv conftest /usr/local/bin/ 2>/dev/null || mv conftest /usr/local/bin/
        rm conftest_${CONFTEST_VERSION}_Linux_x86_64.tar.gz
        echo -e "${GREEN}✓ Conftest installed${NC}"
    else
        echo -e "${YELLOW}⚠ Conftest installation skipped (optional)${NC}"
    fi
fi

# Setup pre-commit hooks
echo ""
echo "Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install > /dev/null 2>&1
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠ pre-commit not found. Run 'pip install pre-commit && pre-commit install'${NC}"
fi

# Create reports directory
mkdir -p "$PROJECT_ROOT/reports"

# Summary
echo ""
echo -e "${CYAN}======================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${CYAN}======================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the README.md for usage instructions"
echo "  2. Run a test scan: make scan"
echo "  3. Test with insecure examples: make scan-insecure"
echo ""
echo "Quick test:"
echo "  python3 iac_guard.py scan --path ./iac/terraform"
echo ""
