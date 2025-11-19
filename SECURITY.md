# Security Policy

## Our Commitment

The IaC Security Guardrails project takes security seriously. We appreciate your efforts to responsibly disclose your findings and will make every effort to acknowledge your contributions.

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

### For Security Researchers

If you believe you've found a security vulnerability in IaC Security Guardrails, please follow these steps:

### 🔒 Private Disclosure (Recommended for Severe Issues)

**For Critical/High Severity Issues:**

1. **DO NOT** create a public GitHub issue
2. Use [GitHub Private Vulnerability Reporting](https://github.com/yourorg/iac-security-guardrails/security/advisories/new)
3. Or email us at: **security@yourorg.com** with:
   - Subject: "[SECURITY] Brief description"
   - Detailed description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

**We commit to:**
- Acknowledge receipt within 48 hours
- Provide a detailed response within 7 days
- Keep you informed of our progress
- Credit you in our security advisories (if desired)

### 📢 Public Disclosure (For Low/Medium Severity)

For lower severity issues or security improvements:

1. Create a [Security Issue](https://github.com/yourorg/iac-security-guardrails/issues/new?template=security_vulnerability.yml)
2. Include all relevant details
3. We'll triage and respond promptly

## Severity Classification

### Critical
- Remote code execution
- Authentication bypass
- Privilege escalation
- Data breach potential
- Complete system compromise

### High
- SQL injection
- Cross-site scripting (XSS)
- Information disclosure (sensitive data)
- Denial of service vulnerabilities

### Medium
- Information disclosure (non-sensitive)
- Security misconfiguration
- Missing security headers
- Weak cryptography

### Low
- Security best practice violations
- Hardening opportunities
- Documentation issues

## Security Best Practices for Users

### When Using IaC Guard

1. **Keep Updated**
   ```bash
   pip install --upgrade iac-guard
   ```

2. **Use Latest Scanners**
   - Update tfsec regularly
   - Update Checkov regularly
   - Update Conftest/OPA regularly

3. **Secure Your Pipeline**
   - Run IaC Guard in isolated CI/CD environments
   - Use read-only credentials when possible
   - Audit IaC Guard configurations

4. **Review Scan Results**
   - Don't ignore security warnings
   - Validate findings before dismissing
   - Track remediation progress

5. **Secure Configuration**
   - Don't commit secrets to Git
   - Use environment variables for sensitive data
   - Enable branch protection rules

### Security Scanner Versions

We test against these versions:

| Scanner  | Minimum Version | Recommended |
|----------|----------------|-------------|
| tfsec    | 1.28.0         | Latest      |
| Checkov  | 3.0.0          | Latest      |
| Conftest | 0.45.0         | Latest      |
| Terraform| 1.0.0          | Latest      |

## Security Features

### Built-in Security

IaC Guard includes these security features:

- ✅ Input validation for all file paths
- ✅ Subprocess timeout enforcement
- ✅ No arbitrary code execution
- ✅ Read-only filesystem operations
- ✅ Secure temporary file handling
- ✅ No network calls without user consent

### Security Scanning

We scan our own code with:

- **tfsec** - For IaC security
- **Checkov** - For policy violations
- **Bandit** - For Python security issues
- **Safety** - For dependency vulnerabilities
- **Trivy** - For container scanning
- **Gitleaks** - For secret detection

## Vulnerability Disclosure Process

### Timeline

1. **Day 0**: Vulnerability reported privately
2. **Day 1-2**: Initial triage and acknowledgment
3. **Day 3-7**: Detailed analysis and assessment
4. **Day 7-30**: Develop and test fix
5. **Day 30-45**: Coordinated disclosure and release
6. **Day 45+**: Public disclosure (if not resolved)

### Responsible Disclosure

We follow a **45-day disclosure policy**:

- We aim to fix vulnerabilities within 30 days
- We'll publish a security advisory within 45 days
- We'll credit researchers (with permission)
- We'll recommend mitigation steps

## Security Advisories

Published security advisories can be found:

- [GitHub Security Advisories](https://github.com/yourorg/iac-security-guardrails/security/advisories)
- [Security Mailing List](https://groups.google.com/g/iac-guard-security)
- [CVE Database](https://cve.mitre.org/)

## Security Hall of Fame

We thank the following security researchers for responsibly disclosing vulnerabilities:

<!-- Add researchers here -->
- *Be the first to contribute!*

## Bug Bounty Program

Currently, we do not offer a paid bug bounty program. However:

- We provide public recognition
- We offer early access to new features
- We're considering a bounty program in the future

## Security Contacts

- **Security Team Email**: security@yourorg.com
- **Security Lead**: @security-lead
- **PGP Key**: [Download](https://yourorg.com/pgp-key.asc)

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## Legal

This security policy is governed by our [Terms of Service](https://yourorg.com/terms) and applicable laws. We reserve the right to modify this policy at any time.

---

**Last Updated**: 2024-01-15
**Version**: 1.0
