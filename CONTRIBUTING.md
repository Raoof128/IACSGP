# Contributing to IaC Security Guardrails

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/your-org/iac-security-guardrails/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Enhancements

1. Check existing [Issues](https://github.com/your-org/iac-security-guardrails/issues) for similar suggestions
2. Create a new issue with:
   - Clear description of the enhancement
   - Use case and benefits
   - Proposed implementation (if you have one)

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/iac-security-guardrails.git
   cd iac-security-guardrails
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-policy
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   # Install development dependencies
   pip install -r requirements.txt
   pre-commit install

   # Run pre-commit checks
   pre-commit run --all-files

   # Run tests (when available)
   pytest tests/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add new security policy for XYZ"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/my-new-policy
   ```

7. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Describe your changes clearly

## Development Setup

### Prerequisites

- Python 3.10+
- Terraform 1.0+
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/your-username/iac-security-guardrails.git
cd iac-security-guardrails

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Install scanners
pip install checkov
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
```

## Code Style

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for formatting (max line length: 100)
- Use [Flake8](https://flake8.pycqa.org/) for linting
- Add type hints where appropriate

```python
def scan_terraform(path: str, severity: Severity) -> ScanResult:
    """Scan Terraform code for security issues.

    Args:
        path: Path to Terraform directory
        severity: Minimum severity threshold

    Returns:
        ScanResult object with findings
    """
    pass
```

### Terraform

- Use `terraform fmt` for formatting
- Add comments for complex logic
- Include examples for new resources

### Rego (OPA Policies)

- Use descriptive rule names
- Add comments explaining the policy
- Include both deny and warn rules where appropriate

```rego
# DENY: S3 buckets must have encryption enabled
deny_unencrypted_s3[msg] {
    bucket := input.resource_changes[_]
    bucket.type == "aws_s3_bucket"
    not has_encryption(bucket)

    msg := sprintf("S3 bucket '%s' does not have encryption enabled", [bucket.address])
}
```

## Adding New Security Policies

### OPA/Rego Policies

1. Create a new `.rego` file in `policies/opa/`
2. Follow the naming convention: `<category>_<subcategory>.rego`
3. Use the package naming: `terraform.<category>`
4. Add both deny and warn rules as needed
5. Test your policy

Example:
```rego
package terraform.networking

import rego.v1

# DENY: VPC must have flow logs enabled
deny_vpc_no_flow_logs[msg] {
    vpc := input.resource_changes[_]
    vpc.type == "aws_vpc"
    vpc_id := vpc.address

    not has_flow_logs(vpc_id)

    msg := sprintf("VPC '%s' does not have flow logs enabled", [vpc_id])
}
```

### tfsec Custom Checks

Add to `.tfsec/custom_checks.yaml`

### Checkov Custom Policies

Add to `policies/checkov/`

## Testing

### Manual Testing

```bash
# Test against secure examples
python3 iac_guard.py scan --path ./iac/terraform

# Test against insecure examples (should fail)
python3 iac_guard.py scan --path ./iac/terraform/examples
```

### Automated Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=iac_guard tests/
```

## Documentation

### README Updates

- Update README.md for major features
- Add examples and usage instructions
- Update the table of contents

### Inline Documentation

- Add docstrings to all functions and classes
- Use clear, concise comments
- Explain the "why" not just the "what"

### Policy Documentation

Update `SECURITY_POLICIES.md` with:
- Rule ID and description
- Rationale
- Compliant and non-compliant examples

## Pull Request Guidelines

### Title

Use clear, descriptive titles:
- ✅ "Add Lambda security policy for reserved concurrency"
- ✅ "Fix S3 encryption detection for KMS keys"
- ❌ "Update code"
- ❌ "Fix bug"

### Description

Include:
- What: What changes are being made
- Why: Why these changes are needed
- How: How the changes work
- Testing: How you tested the changes

### Checklist

Before submitting:
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Pre-commit hooks pass
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts

## Release Process

(For maintainers)

1. Update version in `setup.py` and `iac_guard.py`
2. Update CHANGELOG.md
3. Create a git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release with release notes

## Questions?

- Open an [Issue](https://github.com/your-org/iac-security-guardrails/issues)
- Ask in [Discussions](https://github.com/your-org/iac-security-guardrails/discussions)

---

**Thank you for contributing!** 🎉
