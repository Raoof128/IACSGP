# 🛡️ IaC Security Guardrails

**Infrastructure-as-Code Security Pipeline for Terraform**

A production-ready security guardrails system that automatically scans Terraform projects for misconfigurations, enforces policy-as-code, and blocks insecure changes in CI/CD pipelines.

> *"Designed an Infrastructure-as-Code (IaC) security guardrails pipeline that enforces policy-as-code for Terraform in CI/CD, automatically blocking insecure cloud changes before deployment."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Terraform](https://img.shields.io/badge/terraform-1.0+-purple.svg)](https://www.terraform.io/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Local CLI](#local-cli)
  - [Pre-commit Hooks](#pre-commit-hooks)
  - [CI/CD Integration](#cicd-integration)
- [Security Policies](#security-policies)
- [Configuration](#configuration)
- [Reports and Outputs](#reports-and-outputs)
- [Extending Policies](#extending-policies)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

IaC Security Guardrails is a comprehensive security scanning pipeline that helps DevOps and Security teams prevent insecure infrastructure from reaching production. It integrates multiple industry-standard security scanners and custom policy-as-code engines to provide defense-in-depth for Terraform projects.

### What It Does

- ✅ **Scans** Terraform code for security misconfigurations
- ✅ **Detects** publicly exposed services, missing encryption, weak security groups
- ✅ **Enforces** policy-as-code using OPA/Rego, tfsec, and Checkov
- ✅ **Blocks** PR merges when critical/high severity issues are found
- ✅ **Generates** human-readable security reports as CI artifacts
- ✅ **Integrates** with GitHub Actions, GitLab CI, and pre-commit hooks

---

## 🚀 Features

### Multi-Layer Security Scanning

| Scanner | Purpose | Coverage |
|---------|---------|----------|
| **tfsec** | Fast Terraform-specific security scanner | AWS, Azure, GCP misconfigurations |
| **Checkov** | Comprehensive policy-as-code scanner | 1000+ built-in policies |
| **Conftest/OPA** | Custom policy enforcement engine | Custom Rego policies |

### Security Checks

- 🔒 **Encryption at Rest**: Ensures S3, EBS, RDS have encryption enabled
- 🌐 **Public Exposure**: Detects publicly accessible S3 buckets and databases
- 🔥 **Firewall Rules**: Identifies unrestricted security groups (0.0.0.0/0 on SSH/RDP)
- 🏷️ **Resource Tagging**: Enforces mandatory tags (Owner, Environment)
- 🔑 **Secret Detection**: Finds hardcoded credentials and API keys
- 📊 **Compliance**: Maps to CIS, NIST, PCI-DSS benchmarks

### Developer Experience

- 🖥️ **CLI Tool**: Run scans locally with `iac-guard scan`
- 🪝 **Pre-commit Hooks**: Catch issues before commit
- 🔄 **CI/CD Integration**: Automated scanning in GitHub Actions and GitLab CI
- 📄 **Multiple Output Formats**: Terminal, JSON, SARIF, Markdown
- 🎯 **Severity Thresholds**: Configurable fail conditions

---

## 🏗️ Architecture

### Security Scanning Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Developer Workflow                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  Local Development (Pre-commit)        │
         │  • terraform fmt                        │
         │  • terraform validate                   │
         │  • iac-guard scan (lightweight)         │
         └────────────────────────────────────────┘
                              │
                              ▼ git push
         ┌────────────────────────────────────────┐
         │  CI/CD Pipeline (GitHub/GitLab)        │
         │  ┌──────────────────────────────────┐  │
         │  │ Step 1: Format & Validation      │  │
         │  └──────────────────────────────────┘  │
         │  ┌──────────────────────────────────┐  │
         │  │ Step 2: Security Scanning        │  │
         │  │  • tfsec                         │  │
         │  │  • Checkov                       │  │
         │  │  • Conftest/OPA                  │  │
         │  └──────────────────────────────────┘  │
         │  ┌──────────────────────────────────┐  │
         │  │ Step 3: Policy Evaluation        │  │
         │  │  • Aggregate findings            │  │
         │  │  • Apply severity threshold      │  │
         │  └──────────────────────────────────┘  │
         │  ┌──────────────────────────────────┐  │
         │  │ Step 4: Report Generation        │  │
         │  │  • JSON, SARIF, Markdown         │  │
         │  │  • PR Comments                   │  │
         │  │  • Security Dashboard Upload     │  │
         │  └──────────────────────────────────┘  │
         └────────────────────────────────────────┘
                              │
                ┌─────────────┴──────────────┐
                ▼                            ▼
         ✅ Pass: Merge                ❌ Fail: Block
         Allowed                       Merge + Notify
```

### Directory Structure

```
iac-security-guardrails/
├── iac/                          # Infrastructure-as-Code
│   └── terraform/
│       ├── main.tf               # Secure example infrastructure
│       ├── variables.tf          # Variable definitions
│       ├── outputs.tf            # Output values
│       └── examples/
│           └── insecure_example.tf  # Intentionally insecure code for testing
│
├── policies/                     # Policy-as-Code
│   └── opa/                      # Open Policy Agent (Rego) policies
│       ├── s3_security.rego      # S3 bucket security policies
│       ├── security_groups.rego  # Security group policies
│       ├── encryption.rego       # Encryption at rest policies
│       ├── tagging.rego          # Resource tagging policies
│       └── secrets.rego          # Secret detection policies
│
├── scanners/                     # Scanner wrapper scripts
│   ├── run_tfsec.sh             # tfsec security scanner
│   ├── run_checkov.sh           # Checkov scanner
│   └── run_conftest.sh          # Conftest/OPA policy checker
│
├── scripts/                      # Utility scripts
│   └── format_and_validate.sh   # Terraform formatting and validation
│
├── ci/                           # CI/CD configurations
│   ├── github-actions/
│   │   └── iac-security.yml     # GitHub Actions workflow
│   └── gitlab-ci/
│       └── .gitlab-ci.yml       # GitLab CI pipeline
│
├── iac_guard.py                 # Main CLI tool
├── requirements.txt             # Python dependencies
├── .pre-commit-config.yaml      # Pre-commit hooks configuration
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd iac-security-guardrails

# Install Python dependencies
pip install -r requirements.txt

# Install scanner tools (choose your platform)
# Linux/macOS:
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
pip install checkov
brew install conftest  # or download from GitHub releases

# Windows (using Chocolatey):
choco install tfsec checkov
```

### 2. Run Your First Scan

```bash
# Scan the secure example
python3 iac_guard.py scan --path ./iac/terraform

# Scan the insecure example (should fail)
python3 iac_guard.py scan --path ./iac/terraform/examples
```

### 3. Setup Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📦 Installation

### Prerequisites

- **Python**: 3.10 or higher
- **Terraform**: 1.0 or higher
- **Git**: 2.0 or higher

### Scanner Installation

#### Option 1: Automated Install (Recommended)

```bash
# Run the installation script
pip install -r requirements.txt
```

#### Option 2: Manual Install

**tfsec**
```bash
# Linux/macOS
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash

# Windows (Chocolatey)
choco install tfsec

# Homebrew
brew install tfsec
```

**Checkov**
```bash
pip install checkov
```

**Conftest**
```bash
# Linux/macOS
CONFTEST_VERSION=0.45.0
wget "https://github.com/open-policy-agent/conftest/releases/download/v${CONFTEST_VERSION}/conftest_${CONFTEST_VERSION}_Linux_x86_64.tar.gz"
tar xzf conftest_${CONFTEST_VERSION}_Linux_x86_64.tar.gz
sudo mv conftest /usr/local/bin/

# Homebrew
brew install conftest

# Windows (Chocolatey)
choco install conftest
```

---

## 💻 Usage

### Local CLI

The `iac_guard.py` CLI is the main interface for running security scans.

#### Basic Scan

```bash
python3 iac_guard.py scan
```

#### Scan Specific Path

```bash
python3 iac_guard.py scan --path ./my-terraform-project
```

#### Set Severity Threshold

```bash
# Only fail on CRITICAL issues
python3 iac_guard.py scan --severity-threshold CRITICAL

# Fail on HIGH and above (default)
python3 iac_guard.py scan --severity-threshold HIGH

# Fail on MEDIUM and above
python3 iac_guard.py scan --severity-threshold MEDIUM
```

#### Output Formats

```bash
# Terminal output (default)
python3 iac_guard.py scan --format terminal

# JSON output
python3 iac_guard.py scan --format json --output reports/scan.json

# SARIF output (for GitHub/GitLab integration)
python3 iac_guard.py scan --format sarif --output reports/scan.sarif

# Markdown report
python3 iac_guard.py scan --format markdown --output reports/scan.md
```

#### Run Specific Scanners

```bash
# Run only tfsec
python3 iac_guard.py scan --scanners tfsec

# Run tfsec and Checkov
python3 iac_guard.py scan --scanners tfsec checkov

# Run all scanners (default)
python3 iac_guard.py scan --scanners all
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit to catch issues early.

#### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# (Optional) Run against all files
pre-commit run --all-files
```

#### What Gets Checked

- ✅ Terraform formatting (`terraform fmt`)
- ✅ Terraform validation (`terraform validate`)
- ✅ Security scans (lightweight tfsec scan)
- ✅ Python code formatting (Black)
- ✅ Trailing whitespace, YAML/JSON syntax
- ✅ Secret detection

#### Skip Hooks (Emergency)

```bash
# Skip pre-commit hooks (not recommended)
git commit --no-verify -m "Emergency fix"
```

### CI/CD Integration

#### GitHub Actions

Copy the workflow file to your repository:

```bash
mkdir -p .github/workflows
cp ci/github-actions/iac-security.yml .github/workflows/
```

The workflow will:
- ✅ Trigger on pull requests to main/master
- ✅ Run all security scanners
- ✅ Upload SARIF to GitHub Security tab
- ✅ Comment on PR with findings
- ✅ Block merge if HIGH/CRITICAL issues found

#### GitLab CI

Copy the GitLab CI configuration:

```bash
cp ci/gitlab-ci/.gitlab-ci.yml .gitlab-ci.yml
```

The pipeline will:
- ✅ Run on merge requests
- ✅ Generate SARIF for GitLab Security Dashboard
- ✅ Create artifacts with reports
- ✅ Fail pipeline on HIGH/CRITICAL issues

---

## 🔐 Security Policies

### Built-in Policies

#### 1. S3 Security (`policies/opa/s3_security.rego`)

- ❌ **DENY**: S3 buckets without encryption
- ❌ **DENY**: Public S3 buckets (block_public_access = false)
- ❌ **DENY**: Public ACLs (public-read, public-read-write)
- ⚠️ **WARN**: S3 buckets without versioning

#### 2. Security Groups (`policies/opa/security_groups.rego`)

- ❌ **DENY**: SSH (port 22) open to 0.0.0.0/0
- ❌ **DENY**: RDP (port 3389) open to 0.0.0.0/0
- ❌ **DENY**: All ports open to 0.0.0.0/0
- ❌ **DENY**: Wide port ranges (>100 ports) from internet
- ⚠️ **WARN**: Missing security group rule descriptions

#### 3. Encryption (`policies/opa/encryption.rego`)

- ❌ **DENY**: Unencrypted EBS volumes
- ❌ **DENY**: Unencrypted RDS instances
- ❌ **DENY**: Unencrypted EC2 root volumes
- ❌ **DENY**: Unencrypted S3 buckets
- ⚠️ **WARN**: Resources not using KMS encryption

#### 4. Tagging (`policies/opa/tagging.rego`)

- ❌ **DENY**: Missing mandatory tags (Environment, Owner)
- ❌ **DENY**: Empty tag values
- ⚠️ **WARN**: Missing recommended tags (ManagedBy, Name)
- ⚠️ **WARN**: Non-standard Environment values

#### 5. Secrets Detection (`policies/opa/secrets.rego`)

- ❌ **DENY**: Hardcoded database passwords
- ❌ **DENY**: Hardcoded AWS access keys
- ❌ **DENY**: Publicly accessible databases
- ⚠️ **WARN**: Unmarked sensitive fields

### Severity Levels

| Level | Description | CI/CD Behavior |
|-------|-------------|----------------|
| 🔴 **CRITICAL** | Immediate security risk, data breach potential | ❌ Block merge |
| 🟠 **HIGH** | Significant security risk, requires immediate action | ❌ Block merge (default) |
| 🟡 **MEDIUM** | Security concern, should be addressed | ⚠️ Warn (configurable) |
| 🔵 **LOW** | Minor security improvement | ℹ️ Inform only |
| ⚪ **INFO** | Best practice recommendation | ℹ️ Inform only |

---

## ⚙️ Configuration

### Severity Threshold

Configure when builds should fail:

```bash
# Only block CRITICAL issues
export IAC_GUARD_THRESHOLD=CRITICAL

# Block HIGH and above (default)
export IAC_GUARD_THRESHOLD=HIGH

# Block MEDIUM and above
export IAC_GUARD_THRESHOLD=MEDIUM
```

### Scanner Selection

Choose which scanners to run:

```bash
# Run all scanners (default)
python3 iac_guard.py scan --scanners all

# Run specific scanners
python3 iac_guard.py scan --scanners tfsec checkov
```

### Custom Terraform Path

```bash
python3 iac_guard.py scan --path /path/to/terraform/code
```

---

## 📊 Reports and Outputs

### Terminal Output

```
============================================================
IaC Security Guardrails - Starting Security Scan
============================================================
Target: /home/user/iac/terraform
Severity Threshold: HIGH
Scanners: tfsec, checkov, conftest
Time: 2024-01-15 10:30:45
============================================================

Step 1: Running Terraform Format & Validation
------------------------------------------------------------
✓ Format and validation passed

Step 2a: Running tfsec Security Scanner
------------------------------------------------------------
✓ tfsec scan completed in 2.34s
  Found 5 issues

Step 2b: Running Checkov Security Scanner
------------------------------------------------------------
✓ Checkov scan completed in 8.12s
  Found 12 issues

Step 2c: Running Conftest/OPA Policy Checker
------------------------------------------------------------
✓ Conftest scan completed in 1.45s
  Found 3 policy violations

============================================================
Scan Results Summary
============================================================
Total Issues Found: 20
  🔴 Critical: 2
  🟠 High:     5
  🟡 Medium:   8
  🔵 Low:      4
  ⚪ Info:     1

❌ FAILED: Found 7 issues at or above HIGH severity
```

### JSON Output

```json
{
  "timestamp": "2024-01-15T10:30:45",
  "terraform_path": "/home/user/iac/terraform",
  "severity_threshold": "HIGH",
  "results": [
    {
      "scanner": "tfsec",
      "success": false,
      "duration": 2.34,
      "findings": [
        {
          "severity": "HIGH",
          "rule_id": "AWS017",
          "title": "S3 bucket does not have encryption enabled",
          "description": "Bucket 'my-bucket' should have encryption configured",
          "file_path": "main.tf",
          "line_number": 42,
          "resource": "aws_s3_bucket.example",
          "remediation": "Add server-side encryption configuration"
        }
      ]
    }
  ]
}
```

### SARIF Output

SARIF (Static Analysis Results Interchange Format) integrates with:
- GitHub Security tab
- GitLab Security Dashboard
- Azure DevOps
- SonarQube

### Markdown Report

Perfect for:
- PR comments
- Email notifications
- Documentation
- Security dashboards

---

## 🔧 Extending Policies

### Adding Custom OPA/Rego Policies

1. Create a new `.rego` file in `policies/opa/`:

```bash
touch policies/opa/my_custom_policy.rego
```

2. Write your policy:

```rego
package terraform.custom

import rego.v1

# DENY: Lambda functions must have reserved concurrent executions
deny_lambda_without_concurrency[msg] {
    lambda := input.resource_changes[_]
    lambda.type == "aws_lambda_function"

    not lambda.change.after.reserved_concurrent_executions

    msg := sprintf("Lambda function '%s' does not have reserved concurrent executions", [lambda.address])
}
```

3. Test your policy:

```bash
python3 iac_guard.py scan --scanners conftest
```

### Customizing tfsec Rules

Create a `.tfsec/config.yml` file:

```yaml
exclude:
  - AWS001  # Exclude specific rules

severity_overrides:
  AWS017: ERROR  # Upgrade severity
  AWS018: WARNING  # Downgrade severity

minimum_severity: MEDIUM
```

### Customizing Checkov Policies

Create a `.checkov.yml` file:

```yaml
skip-check:
  - CKV_AWS_18  # Skip specific checks

framework:
  - terraform

output: compact
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Scanner Not Found

**Error**: `tfsec: command not found`

**Solution**:
```bash
# Install tfsec
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
sudo mv tfsec /usr/local/bin/
```

#### 2. Terraform Validation Fails

**Error**: `Error: Required variable not set`

**Solution**: Create a `terraform.tfvars` file or set `TF_VAR_*` environment variables

#### 3. Pre-commit Hook Fails

**Error**: `[ERROR] conftest is not installed`

**Solution**:
```bash
# Install conftest
brew install conftest
# or download from GitHub releases
```

#### 4. False Positives

**Solution**: Use inline suppressions:

```hcl
# tfsec:ignore:AWS017
resource "aws_s3_bucket" "example" {
  # ... justified use case
}
```

### Debug Mode

```bash
# Enable verbose output
python3 iac_guard.py scan --path . --verbose

# Run specific scanner directly
bash scanners/run_tfsec.sh ./iac/terraform
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-policy`
3. Add your changes
4. Run tests: `pre-commit run --all-files`
5. Commit: `git commit -m "Add new security policy for X"`
6. Push: `git push origin feature/my-new-policy`
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/iac-security-guardrails.git
cd iac-security-guardrails

# Install dev dependencies
pip install -r requirements.txt
pre-commit install

# Run tests
pytest tests/

# Run linters
black iac_guard.py
flake8 iac_guard.py
```

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **tfsec**: [aquasecurity/tfsec](https://github.com/aquasecurity/tfsec)
- **Checkov**: [bridgecrewio/checkov](https://github.com/bridgecrewio/checkov)
- **Conftest**: [open-policy-agent/conftest](https://github.com/open-policy-agent/conftest)
- **Open Policy Agent**: [open-policy-agent/opa](https://github.com/open-policy-agent/opa)

---

## 📞 Support

- 🐛 **Bug Reports**: [Open an issue](https://github.com/your-org/iac-security-guardrails/issues)
- 💡 **Feature Requests**: [Open an issue](https://github.com/your-org/iac-security-guardrails/issues)
- 📖 **Documentation**: This README and inline code comments

---

## 🎓 Learning Resources

- [Terraform Security Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)
- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
- [OPA Policy Language](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)

---

**Built with ❤️ for DevSecOps teams**
