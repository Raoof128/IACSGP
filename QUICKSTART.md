# Quick Start Guide

Get up and running with IaC Security Guardrails in 5 minutes.

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Security Scanners

**Option A: Quick Install (All Platforms)**
```bash
# Install Checkov (Python-based)
pip install checkov

# Install tfsec
# Linux/macOS:
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
# Move to PATH
sudo mv tfsec /usr/local/bin/

# Install Conftest
# Download latest release from: https://github.com/open-policy-agent/conftest/releases
# Or use Homebrew:
brew install conftest
```

**Option B: Package Managers**
```bash
# macOS (Homebrew)
brew install tfsec checkov conftest

# Linux (apt)
# Note: May need to use pip for checkov
pip install checkov

# Windows (Chocolatey)
choco install tfsec checkov conftest
```

## Basic Usage

### Run a Security Scan

```bash
# Scan the example Terraform code
python3 iac_guard.py scan --path ./iac/terraform

# Expected output: ✅ PASSED (secure example)
```

### Test with Insecure Code

```bash
# Scan the intentionally insecure examples
python3 iac_guard.py scan --path ./iac/terraform/examples

# Expected output: ❌ FAILED (multiple HIGH severity issues)
```

## Setup for Your Project

### 1. Copy the Pipeline

```bash
# For GitHub Actions
mkdir -p .github/workflows
cp ci/github-actions/iac-security.yml .github/workflows/

# For GitLab CI
cp ci/gitlab-ci/.gitlab-ci.yml .gitlab-ci.yml
```

### 2. Add Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Test
pre-commit run --all-files
```

### 3. Customize for Your Terraform

```bash
# Update the Terraform path in your CI config
# GitHub Actions: Edit .github/workflows/iac-security.yml
# GitLab CI: Edit .gitlab-ci.yml

# Change this line:
--path ./iac/terraform

# To your Terraform directory:
--path ./terraform  # or wherever your .tf files are
```

## Common Commands

### Scan with Different Severity Thresholds

```bash
# Only fail on CRITICAL issues
python3 iac_guard.py scan --severity-threshold CRITICAL

# Fail on HIGH and above (default)
python3 iac_guard.py scan --severity-threshold HIGH

# Fail on MEDIUM and above
python3 iac_guard.py scan --severity-threshold MEDIUM
```

### Generate Reports

```bash
# JSON report
python3 iac_guard.py scan --format json --output report.json

# Markdown report
python3 iac_guard.py scan --format markdown --output report.md

# SARIF (for GitHub/GitLab security tab)
python3 iac_guard.py scan --format sarif --output report.sarif
```

### Run Specific Scanners

```bash
# Only tfsec (fastest)
python3 iac_guard.py scan --scanners tfsec

# tfsec + Checkov
python3 iac_guard.py scan --scanners tfsec checkov

# All scanners (default)
python3 iac_guard.py scan --scanners all
```

## Troubleshooting

### "Scanner not found" Error

**Problem**: `tfsec: command not found`

**Solution**:
```bash
# Verify installation
which tfsec
tfsec --version

# If not found, reinstall
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
sudo mv tfsec /usr/local/bin/
```

### Terraform Validation Fails

**Problem**: `Error: Required variable not set`

**Solution**: Create a `terraform.tfvars` file with dummy values:
```hcl
bucket_name = "test-bucket"
vpc_id = "vpc-12345678"
db_username = "admin"
db_password = "dummy-password"
```

### Too Many Findings

**Problem**: Hundreds of findings, hard to fix all at once

**Solution**: Start with HIGH severity only:
```bash
python3 iac_guard.py scan --severity-threshold HIGH
```

Then gradually lower the threshold as you fix issues.

## Next Steps

1. ✅ Review the security policies in `policies/opa/`
2. ✅ Customize policies for your organization
3. ✅ Add to your CI/CD pipeline
4. ✅ Train your team on security best practices
5. ✅ Set up automated scanning on all Terraform repos

## Resources

- **Full Documentation**: See [README.md](README.md)
- **Security Policies**: See `policies/opa/*.rego`
- **CI/CD Examples**: See `ci/` directory
- **Insecure Examples**: See `iac/terraform/examples/`

---

**Questions?** Open an issue or check the [Troubleshooting](README.md#troubleshooting) section.
