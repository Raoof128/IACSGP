# Frequently Asked Questions (FAQ)

## General Questions

### What is IaC Security Guardrails?

IaC Security Guardrails is an automated security scanning pipeline for Terraform projects. It integrates multiple industry-standard security scanners (tfsec, Checkov, Conftest/OPA) to detect misconfigurations, enforce policy-as-code, and block insecure infrastructure changes before they reach production.

### Who should use this tool?

- **DevOps Engineers** - Integrate security into your CI/CD pipelines
- **Security Teams** - Enforce security policies across all infrastructure
- **Platform Engineers** - Standardize security checks organization-wide
- **Cloud Architects** - Prevent misconfigurations from the start
- **Developers** - Catch security issues before code review

### How is this different from just running tfsec or Checkov?

IaC Security Guardrails provides:
- **Unified CLI** - One command to run multiple scanners
- **Consistent Results** - Aggregated, normalized findings
- **Custom Policies** - OPA/Rego policies specific to your organization
- **CI/CD Integration** - Ready-to-use GitHub Actions and GitLab CI
- **Severity Thresholds** - Configurable pass/fail criteria
- **Multiple Report Formats** - JSON, SARIF, Markdown
- **Pre-commit Hooks** - Catch issues before commit

### Is this tool free and open source?

Yes! IaC Security Guardrails is licensed under the **MIT License**, which means:
- ✅ Free for commercial and personal use
- ✅ Modify and distribute freely
- ✅ No warranty or liability
- ✅ Must include copyright notice

---

## Installation

### What are the system requirements?

**Minimum:**
- Python 3.9+
- Terraform 1.0+
- 512MB RAM
- Linux, macOS, or Windows

**Recommended:**
- Python 3.10+
- Terraform 1.5+
- 2GB RAM
- Linux or macOS

### How do I install IaC Guard?

**Quick install:**
```bash
git clone https://github.com/yourorg/iac-security-guardrails
cd iac-security-guardrails
bash scripts/setup.sh
```

**Manual install:**
```bash
pip install -r requirements.txt
# Install scanners (see docs)
```

### Do I need to install all three scanners?

No, but recommended:
- **Minimum**: tfsec (fastest, Terraform-specific)
- **Recommended**: tfsec + Checkov (comprehensive coverage)
- **Maximum**: tfsec + Checkov + Conftest (custom policies)

The tool gracefully skips missing scanners.

### Can I use Docker instead?

Yes! See our [Docker documentation](Dockerfile):
```bash
docker build -t iac-guard .
docker run -v $(pwd)/terraform:/terraform iac-guard scan
```

---

## Usage

### How do I run a basic scan?

```bash
python3 iac_guard.py scan --path ./terraform
```

### How do I change the severity threshold?

```bash
# Only fail on CRITICAL issues
python3 iac_guard.py scan --severity-threshold CRITICAL

# Fail on HIGH and above (default)
python3 iac_guard.py scan --severity-threshold HIGH

# Fail on MEDIUM and above
python3 iac_guard.py scan --severity-threshold MEDIUM
```

### Can I run specific scanners only?

Yes:
```bash
# Only tfsec (fastest)
python3 iac_guard.py scan --scanners tfsec

# tfsec + Checkov
python3 iac_guard.py scan --scanners tfsec checkov

# All available scanners
python3 iac_guard.py scan --scanners all
```

### How do I generate different report formats?

```bash
# JSON report
python3 iac_guard.py scan --format json --output report.json

# SARIF (for GitHub/GitLab Security)
python3 iac_guard.py scan --format sarif --output report.sarif

# Markdown
python3 iac_guard.py scan --format markdown --output report.md

# All formats
python3 iac_guard.py scan --format all
```

### How do I use verbose mode?

```bash
python3 iac_guard.py scan --verbose
```

This shows:
- Detailed scanner output
- Dependency checking results
- Error stack traces
- Debug information

---

## CI/CD Integration

### How do I integrate with GitHub Actions?

Copy our workflow:
```bash
cp ci/github-actions/iac-security.yml .github/workflows/
git add .github/workflows/iac-security.yml
git commit -m "Add IaC security scanning"
git push
```

The workflow runs on:
- Pull requests to main/master
- Pushes to main/master
- Manual trigger

### How do I integrate with GitLab CI?

Copy our configuration:
```bash
cp ci/gitlab-ci/.gitlab-ci.yml .gitlab-ci.yml
git add .gitlab-ci.yml
git commit -m "Add IaC security scanning"
git push
```

### Can I use this with other CI systems?

Yes! The CLI works with any CI system:
- **Jenkins**: Shell script in pipeline
- **CircleCI**: Add step in config.yml
- **Azure DevOps**: Add bash task
- **Travis CI**: Add script in .travis.yml

Example for any CI:
```bash
pip install -r requirements.txt
./scripts/setup.sh  # Install scanners
python3 iac_guard.py scan
```

### How do I setup pre-commit hooks?

```bash
pip install pre-commit
pre-commit install
```

Now scans run automatically before each commit!

---

## Policies

### How do I customize security policies?

**For OPA/Rego policies:**
1. Edit files in `policies/opa/`
2. Add new `.rego` files
3. Follow existing patterns

**For tfsec:**
1. Create `.tfsec/config.yml`
2. Add custom rules

**For Checkov:**
1. Create `.checkov.yml`
2. Configure skip rules

### Can I disable specific rules?

**tfsec inline:**
```hcl
# tfsec:ignore:AWS017
resource "aws_s3_bucket" "example" {
  # ...
}
```

**Checkov inline:**
```hcl
# checkov:skip=CKV_AWS_18:Justified reason
resource "aws_s3_bucket" "example" {
  # ...
}
```

### How do I add mandatory tags?

Edit `policies/opa/tagging.rego`:
```rego
mandatory_tags := ["Environment", "Owner", "CostCenter"]
```

### What policies are included by default?

See [SECURITY_POLICIES.md](SECURITY_POLICIES.md) for complete list:
- S3 bucket security
- Security group restrictions
- Encryption requirements
- Resource tagging
- Secret detection

---

## Troubleshooting

### "Scanner not found" error

**Solution:**
```bash
# Check what's installed
make check-deps

# Install missing scanners
bash scripts/setup.sh
```

### "Terraform validation failed"

**Cause:** Missing variables or invalid configuration

**Solution:**
1. Create `terraform.tfvars` with required variables
2. Or use `terraform.tfvars.example` as template
3. Or set `TF_VAR_*` environment variables

### "Permission denied" errors

**Solution:**
```bash
# Make scripts executable
chmod +x iac_guard.py
chmod +x scripts/*.sh
chmod +x scanners/*.sh
```

### Pre-commit hooks not running

**Solution:**
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Test manually
pre-commit run --all-files
```

### Scans are too slow

**Solutions:**
- Run only tfsec: `--scanners tfsec`
- Skip validation: Edit scripts
- Use parallel execution (future feature)
- Run in Docker with resource limits

### Too many false positives

**Solutions:**
1. Adjust severity threshold: `--severity-threshold HIGH`
2. Disable specific rules (see above)
3. Customize policies for your environment
4. Report false positives as issues

---

## Advanced Usage

### Can I run this in Docker?

Yes:
```bash
docker build -t iac-guard .
docker run -v $(pwd):/work iac-guard scan --path /work/terraform
```

### Can I integrate with Terraform Cloud?

Yes, via:
1. **Sentinel Policies** - Convert our OPA policies
2. **Run Tasks** - Call IaC Guard as external check
3. **VCS Integration** - Run in GitHub Actions on PR

### Can I use this with Terragrunt?

Yes:
```bash
# Scan rendered Terraform
terragrunt plan -out=plan
terragrunt show -json plan > plan.json
python3 iac_guard.py scan --path .
```

### Can I add custom Python checks?

Yes, edit `iac_guard.py`:
```python
def custom_check(self):
    # Your custom logic
    pass
```

### How do I contribute custom policies?

1. Fork the repository
2. Add your policy to `policies/opa/`
3. Add tests
4. Submit pull request

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Performance

### How long does a scan take?

**Typical scan times:**
- Small project (<10 files): 5-10 seconds
- Medium project (10-50 files): 10-30 seconds
- Large project (>50 files): 30-60 seconds

### Which scanner is fastest?

1. **tfsec** - Fastest (Go binary)
2. **Conftest** - Fast (Go binary)
3. **Checkov** - Slower (Python, comprehensive)

### Can I speed up scans?

**Yes:**
- Use only tfsec for speed
- Skip Terraform validation
- Run scanners in parallel (future)
- Use Docker with resource limits
- Cache dependencies in CI

---

## Support

### Where can I get help?

1. **Documentation** - Start with [README.md](README.md)
2. **GitHub Issues** - Report bugs or request features
3. **GitHub Discussions** - Ask questions
4. **Stack Overflow** - Tag: `iac-guard`
5. **Community Slack** - Join our channel

### How do I report a bug?

1. Check existing issues
2. Use bug report template
3. Include version, OS, error logs
4. Provide minimal reproduction

### How do I request a feature?

1. Check existing feature requests
2. Use feature request template
3. Describe use case clearly
4. Explain expected behavior

### How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- Development setup
- Coding standards
- Pull request process

---

## Comparison

### vs. tfsec alone

| Feature | tfsec | IaC Guard |
|---------|-------|-----------|
| Speed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Coverage | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Custom Policies | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| CI Integration | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Reports | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### vs. Checkov alone

| Feature | Checkov | IaC Guard |
|---------|---------|-----------|
| Speed | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Coverage | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Custom Policies | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| CI Integration | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Reports | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### vs. Manual review

| Aspect | Manual | IaC Guard |
|--------|--------|-----------|
| Speed | Slow | Fast |
| Consistency | Variable | Consistent |
| Coverage | Depends on reviewer | Comprehensive |
| Scalability | Poor | Excellent |
| Cost | High | Low |

---

## License & Legal

### What is the license?

MIT License - see [LICENSE](LICENSE)

### Can I use this commercially?

Yes, the MIT License allows commercial use.

### Do I need to credit the project?

The MIT License requires including the copyright notice, but you don't need to actively credit us in your product.

### Can I modify and redistribute?

Yes, under the MIT License terms.

---

**Still have questions?**

- 📖 Check our [comprehensive documentation](README.md)
- 💬 Ask on [GitHub Discussions](https://github.com/yourorg/iac-security-guardrails/discussions)
- 🐛 Report an [issue](https://github.com/yourorg/iac-security-guardrails/issues)

---

*Last Updated: 2024-01-15*
