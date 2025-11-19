# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added

#### Core Features
- Complete IaC security guardrails pipeline for Terraform
- Python CLI tool (`iac_guard.py`) for running security scans
- Multi-scanner integration (tfsec, Checkov, Conftest/OPA)
- Severity-based threshold enforcement (CRITICAL, HIGH, MEDIUM, LOW, INFO)

#### Security Policies (OPA/Rego)
- S3 bucket security policies (encryption, public access, ACLs)
- Security group policies (SSH, RDP, wide port ranges)
- Encryption policies (EBS, RDS, EC2, S3)
- Resource tagging policies (mandatory and recommended tags)
- Secrets detection policies (hardcoded passwords, AWS keys)

#### CI/CD Integration
- GitHub Actions workflow with PR comments and SARIF upload
- GitLab CI pipeline with Security Dashboard integration
- Automated report generation (JSON, SARIF, Markdown)
- Artifact upload and retention

#### Developer Tools
- Pre-commit hooks configuration
- Format and validation scripts
- Example secure Terraform infrastructure
- Intentionally insecure examples for testing

#### Documentation
- Comprehensive README with architecture diagrams
- Quick start guide
- Security policies reference
- Contributing guidelines
- Troubleshooting guide

#### Infrastructure Examples
- Secure AWS infrastructure (S3, EC2, RDS, Security Groups)
- Insecure examples demonstrating violations
- Terraform variables and outputs

### Features

#### Scanning
- Terraform format checking (`terraform fmt`)
- Terraform validation (`terraform validate`)
- tfsec security scanning with JSON/SARIF output
- Checkov policy scanning with custom rules
- Conftest/OPA policy enforcement

#### Reporting
- Terminal-friendly summary output
- JSON export for programmatic access
- SARIF export for GitHub/GitLab Security tabs
- Markdown reports for PR comments
- Detailed finding information (severity, file, line, remediation)

#### Flexibility
- Configurable severity thresholds
- Scanner selection (run all or specific scanners)
- Custom Terraform path support
- Multiple output formats

### Configuration

- `.pre-commit-config.yaml` - Pre-commit hooks for local development
- `.gitignore` - Comprehensive ignore rules for Python and Terraform
- `requirements.txt` - Python dependencies
- CI/CD workflows for GitHub and GitLab

### Security

#### Policies Enforced
- No public S3 buckets
- No unencrypted storage (S3, EBS, RDS)
- No SSH/RDP from 0.0.0.0/0
- No hardcoded secrets
- No publicly accessible databases
- Mandatory resource tagging

### Developer Experience

- One-command security scanning
- Fast feedback loop with pre-commit hooks
- Clear, actionable error messages
- Exemption support (inline suppressions)

## [Unreleased]

### Planned Features
- [ ] Support for additional cloud providers (Azure, GCP)
- [ ] Terraform Cloud/Enterprise integration
- [ ] Custom policy generator UI
- [ ] Automated remediation suggestions
- [ ] Integration with security scanning tools (Snyk, Aqua)
- [ ] Policy compliance reporting
- [ ] Historical trend analysis
- [ ] Slack/Teams notifications
- [ ] Cost optimization checks
- [ ] Drift detection

---

## Version History

### Version Format
- MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

### Release Notes Format
Each release includes:
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
