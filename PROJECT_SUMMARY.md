# IaC Security Guardrails - Project Summary

## What This Project Does

This is a **production-ready Infrastructure-as-Code (IaC) security pipeline** that automatically scans Terraform projects for security misconfigurations and blocks insecure changes before they reach production.

## Key Components

### 1. Security Scanners (Defense in Depth)
- **tfsec**: Fast Terraform security scanner (500+ checks)
- **Checkov**: Policy-as-code scanner (1000+ policies)
- **Conftest/OPA**: Custom policy enforcement with Rego

### 2. CLI Tool (`iac_guard.py`)
```bash
python3 iac_guard.py scan --path ./terraform --severity-threshold HIGH
```

### 3. CI/CD Integration
- **GitHub Actions**: Automated PR scanning with comments
- **GitLab CI**: Security Dashboard integration
- **Pre-commit Hooks**: Local developer scanning

### 4. Security Policies (OPA/Rego)
Located in `policies/opa/`:
- `s3_security.rego` - S3 bucket security
- `security_groups.rego` - Firewall rules
- `encryption.rego` - Encryption at rest
- `tagging.rego` - Resource tagging
- `secrets.rego` - Secret detection

## File Structure

```
.
├── iac_guard.py                    # Main CLI tool
├── requirements.txt                # Python dependencies
├── .pre-commit-config.yaml         # Pre-commit hooks
├── .gitignore                      # Git ignore rules
│
├── iac/terraform/                  # Terraform examples
│   ├── main.tf                     # Secure infrastructure
│   ├── variables.tf
│   ├── outputs.tf
│   └── examples/
│       └── insecure_example.tf     # Insecure code for testing
│
├── policies/opa/                   # OPA/Rego policies
│   ├── s3_security.rego
│   ├── security_groups.rego
│   ├── encryption.rego
│   ├── tagging.rego
│   └── secrets.rego
│
├── scanners/                       # Scanner wrapper scripts
│   ├── run_tfsec.sh
│   ├── run_checkov.sh
│   └── run_conftest.sh
│
├── scripts/
│   └── format_and_validate.sh
│
├── ci/                             # CI/CD configurations
│   ├── github-actions/
│   │   └── iac-security.yml
│   └── gitlab-ci/
│       └── .gitlab-ci.yml
│
├── reports/                        # Output directory for reports
│
└── Documentation
    ├── README.md                   # Main documentation
    ├── QUICKSTART.md              # Quick start guide
    ├── SECURITY_POLICIES.md       # Policy reference
    ├── CONTRIBUTING.md            # Contribution guidelines
    ├── CHANGELOG.md               # Version history
    └── LICENSE                     # MIT License
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Scanners
```bash
# tfsec
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash

# Checkov
pip install checkov

# Conftest
brew install conftest  # or download from GitHub
```

### 3. Run a Scan
```bash
# Scan secure example (should pass)
python3 iac_guard.py scan --path ./iac/terraform

# Scan insecure example (should fail)
python3 iac_guard.py scan --path ./iac/terraform/examples
```

### 4. Setup CI/CD
```bash
# For GitHub
cp ci/github-actions/iac-security.yml .github/workflows/

# For GitLab
cp ci/gitlab-ci/.gitlab-ci.yml .gitlab-ci.yml
```

### 5. Enable Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

## Security Checks Performed

### Critical Issues (Block Merge)
- ❌ Public S3 buckets
- ❌ Unencrypted storage (S3, EBS, RDS)
- ❌ SSH/RDP from 0.0.0.0/0
- ❌ Hardcoded secrets
- ❌ Publicly accessible databases

### High Severity (Block Merge)
- ❌ Missing encryption
- ❌ Wide port ranges from internet
- ❌ Missing mandatory tags

### Medium/Low (Warn)
- ⚠️ Missing recommended tags
- ⚠️ No versioning on S3
- ⚠️ Missing rule descriptions

## Example Output

### Terminal
```
============================================================
IaC Security Guardrails - Starting Security Scan
============================================================
Target: /path/to/terraform
Severity Threshold: HIGH
Time: 2024-01-15 10:30:45
============================================================

✓ Format and validation passed
✓ tfsec scan completed in 2.34s (5 issues)
✓ Checkov scan completed in 8.12s (12 issues)
✓ Conftest scan completed in 1.45s (3 violations)

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

### Supported Output Formats
- Terminal (colored, human-readable)
- JSON (programmatic access)
- SARIF (GitHub/GitLab Security tab)
- Markdown (PR comments, reports)

## How It Works

### Local Development Flow
```
Developer writes Terraform
    ↓
Pre-commit hook runs
    ↓
Catches issues before commit
    ↓
Developer fixes issues
    ↓
Commit succeeds
```

### CI/CD Flow
```
PR created
    ↓
GitHub Actions/GitLab CI triggered
    ↓
Format & Validate
    ↓
Security Scans (tfsec, Checkov, Conftest)
    ↓
Aggregate Results
    ↓
If HIGH/CRITICAL found → ❌ Block merge
If no issues → ✅ Allow merge
    ↓
Post comment on PR with findings
Upload SARIF to Security tab
```

## Customization

### Change Severity Threshold
```bash
# Only block CRITICAL
python3 iac_guard.py scan --severity-threshold CRITICAL

# Block MEDIUM and above
python3 iac_guard.py scan --severity-threshold MEDIUM
```

### Run Specific Scanners
```bash
# Only tfsec (fastest)
python3 iac_guard.py scan --scanners tfsec

# tfsec + Checkov
python3 iac_guard.py scan --scanners tfsec checkov
```

### Add Custom Policies
Create a new `.rego` file in `policies/opa/`:
```rego
package terraform.custom

import rego.v1

deny_my_custom_check[msg] {
    # Your policy logic
    msg := "Your custom message"
}
```

## Testing

### Test Secure Examples
```bash
python3 iac_guard.py scan --path ./iac/terraform
# Expected: ✅ PASSED
```

### Test Insecure Examples
```bash
python3 iac_guard.py scan --path ./iac/terraform/examples
# Expected: ❌ FAILED with multiple HIGH severity issues
```

## Resume/Portfolio Summary

> "Designed an Infrastructure-as-Code (IaC) security guardrails pipeline that enforces policy-as-code for Terraform in CI/CD, automatically blocking insecure cloud changes before deployment."

### Key Achievements
- ✅ Multi-layer security scanning (tfsec, Checkov, OPA)
- ✅ Custom policy-as-code enforcement with Rego
- ✅ CI/CD integration (GitHub Actions, GitLab CI)
- ✅ Automated PR blocking for security violations
- ✅ SARIF reporting for Security Dashboards
- ✅ Pre-commit hooks for developer experience

### Technologies Used
- **Languages**: Python, Rego (OPA), Bash, HCL (Terraform)
- **Security Tools**: tfsec, Checkov, Conftest/OPA
- **CI/CD**: GitHub Actions, GitLab CI
- **Cloud**: AWS (examples for S3, EC2, RDS, Security Groups)
- **DevOps**: Pre-commit hooks, Infrastructure-as-Code

## Next Steps

1. ✅ Copy this pipeline to your Terraform repositories
2. ✅ Customize policies for your organization
3. ✅ Train your team on security best practices
4. ✅ Monitor security findings in dashboards
5. ✅ Continuously improve policies based on findings

## Support & Documentation

- **Quick Start**: See `QUICKSTART.md`
- **Full Documentation**: See `README.md`
- **Security Policies**: See `SECURITY_POLICIES.md`
- **Contributing**: See `CONTRIBUTING.md`

---

**Built for DevSecOps teams to shift security left** 🛡️
