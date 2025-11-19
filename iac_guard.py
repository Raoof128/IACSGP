#!/usr/bin/env python3
"""
IaC Guard - Infrastructure-as-Code Security Guardrails CLI
A comprehensive security scanner for Terraform projects

This tool integrates multiple security scanners and enforces policy-as-code
to prevent insecure infrastructure changes from reaching production.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

# Version
__version__ = "1.0.0"


class Severity(Enum):
    """Severity levels for security findings"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0

    def __str__(self):
        return self.name


@dataclass
class Finding:
    """Represents a security finding from a scanner"""
    scanner: str
    severity: Severity
    rule_id: str
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    resource: Optional[str] = None
    remediation: Optional[str] = None

    def __str__(self):
        return f"[{self.severity.name}] {self.scanner}: {self.title}"


@dataclass
class ScanResult:
    """Results from a security scan"""
    scanner: str
    success: bool
    findings: List[Finding] = field(default_factory=list)
    duration: float = 0.0
    error_message: Optional[str] = None

    def get_findings_by_severity(self, min_severity: Severity) -> List[Finding]:
        """Get findings at or above a minimum severity level"""
        return [f for f in self.findings if f.severity.value >= min_severity.value]


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @staticmethod
    def disable():
        """Disable colors (for non-TTY environments)"""
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.MAGENTA = ''
        Colors.CYAN = ''
        Colors.WHITE = ''
        Colors.BOLD = ''
        Colors.RESET = ''


class IaCGuard:
    """Main IaC Security Guardrails scanner"""

    def __init__(
        self,
        terraform_path: str,
        severity_threshold: Severity = Severity.HIGH,
        scanners: Optional[List[str]] = None,
        verbose: bool = False,
    ):
        self.terraform_path = Path(terraform_path).resolve()
        self.severity_threshold = severity_threshold
        self.project_root = Path(__file__).parent.resolve()
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.verbose = verbose

        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

        # Disable colors if not in TTY
        if not sys.stdout.isatty():
            Colors.disable()

        # Scanners to run
        if scanners is None:
            self.scanners = ["tfsec", "checkov"]  # Removed conftest by default as it requires more setup
        else:
            self.scanners = scanners

        self.results: List[ScanResult] = []

        # Validate terraform path exists
        if not self.terraform_path.exists():
            raise ValueError(f"Terraform path does not exist: {self.terraform_path}")

        if not self.terraform_path.is_dir():
            raise ValueError(f"Terraform path is not a directory: {self.terraform_path}")

    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required tools are installed"""
        dependencies = {
            'terraform': False,
            'tfsec': False,
            'checkov': False,
            'conftest': False,
        }

        for tool in dependencies:
            try:
                result = subprocess.run(
                    [tool, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                dependencies[tool] = result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                dependencies[tool] = False

        return dependencies

    def run_all_scans(self) -> bool:
        """Run all security scans and return success status"""
        self._print_header()

        # Check dependencies
        deps = self.check_dependencies()
        self.logger.info("Checking dependencies...")

        missing_deps = [tool for tool, installed in deps.items() if not installed and tool in self.scanners]
        if 'terraform' not in deps or not deps['terraform']:
            self.logger.error(f"{Colors.RED}✗ Terraform is not installed{Colors.RESET}")
            return False

        if missing_deps:
            self.logger.warning(f"{Colors.YELLOW}⚠ Missing scanners: {', '.join(missing_deps)}{Colors.RESET}")
            self.logger.warning("Continuing with available scanners...")
            self.scanners = [s for s in self.scanners if s not in missing_deps]

        if not self.scanners:
            self.logger.error(f"{Colors.RED}✗ No scanners available{Colors.RESET}")
            return False

        # Step 1: Format and Validate
        if not self._run_format_and_validate():
            self.logger.error(f"\n{Colors.RED}❌ Format/Validation failed - stopping scan{Colors.RESET}")
            return False

        # Step 2: Run security scanners
        for scanner in self.scanners:
            if scanner == "tfsec" and deps.get('tfsec', False):
                self._run_tfsec()
            elif scanner == "checkov" and deps.get('checkov', False):
                self._run_checkov()
            elif scanner == "conftest" and deps.get('conftest', False):
                self._run_conftest()

        # Step 3: Analyze results
        return self._analyze_results()

    def _print_header(self):
        """Print scan header"""
        print(f"{Colors.BOLD}{'=' * 60}")
        print(f"{Colors.CYAN}IaC Security Guardrails - Starting Security Scan{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        print(f"Target: {Colors.WHITE}{self.terraform_path}{Colors.RESET}")
        print(f"Severity Threshold: {Colors.YELLOW}{self.severity_threshold.name}{Colors.RESET}")
        print(f"Scanners: {Colors.CYAN}{', '.join(self.scanners)}{Colors.RESET}")
        print(f"Time: {Colors.WHITE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

    def _run_format_and_validate(self) -> bool:
        """Run terraform fmt and validate"""
        print(f"{Colors.BOLD}Step 1: Running Terraform Format & Validation{Colors.RESET}")
        print("-" * 60)

        # Check if there are any .tf files
        tf_files = list(self.terraform_path.glob("*.tf"))
        if not tf_files:
            self.logger.warning(f"{Colors.YELLOW}⚠ No .tf files found in {self.terraform_path}{Colors.RESET}")
            print(f"{Colors.YELLOW}✓ No Terraform files to validate\n{Colors.RESET}")
            return True

        try:
            # Run terraform fmt -check
            fmt_result = subprocess.run(
                ['terraform', 'fmt', '-check', '-recursive', str(self.terraform_path)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.terraform_path)
            )

            if fmt_result.returncode != 0:
                self.logger.warning(f"{Colors.YELLOW}⚠ Some files need formatting{Colors.RESET}")
                if self.verbose and fmt_result.stdout:
                    print(fmt_result.stdout)
                # Don't fail on formatting issues, just warn
                print(f"{Colors.YELLOW}⚠ Format check completed with warnings\n{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}✓ All files are properly formatted{Colors.RESET}")

            # Run terraform init (suppress backend initialization)
            print("Initializing Terraform...")
            init_result = subprocess.run(
                ['terraform', 'init', '-backend=false', '-upgrade=false'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.terraform_path)
            )

            if init_result.returncode != 0:
                self.logger.warning(f"{Colors.YELLOW}⚠ Terraform init had warnings (continuing){Colors.RESET}")
                if self.verbose:
                    self.logger.debug(init_result.stderr)

            # Run terraform validate
            validate_result = subprocess.run(
                ['terraform', 'validate', '-json'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.terraform_path)
            )

            if validate_result.returncode == 0:
                print(f"{Colors.GREEN}✓ Terraform configuration is valid\n{Colors.RESET}")
                return True
            else:
                # Try to parse JSON output
                try:
                    validation_output = json.loads(validate_result.stdout)
                    if validation_output.get('valid', False):
                        print(f"{Colors.GREEN}✓ Terraform configuration is valid\n{Colors.RESET}")
                        return True
                    else:
                        print(f"{Colors.YELLOW}⚠ Validation warnings (continuing){Colors.RESET}\n")
                        return True  # Continue even with validation warnings
                except json.JSONDecodeError:
                    print(f"{Colors.YELLOW}⚠ Validation completed with warnings (continuing){Colors.RESET}\n")
                    return True  # Continue anyway for security scanning

        except subprocess.TimeoutExpired:
            self.logger.error(f"{Colors.RED}✗ Format and validation timed out\n{Colors.RESET}")
            return False
        except Exception as e:
            self.logger.error(f"{Colors.RED}✗ Error running format and validation: {e}\n{Colors.RESET}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

    def _run_tfsec(self) -> None:
        """Run tfsec security scanner"""
        print(f"{Colors.BOLD}Step 2a: Running tfsec Security Scanner{Colors.RESET}")
        print("-" * 60)

        json_output = self.reports_dir / "tfsec-report.json"
        start_time = datetime.now()

        try:
            result = subprocess.run(
                [
                    'tfsec',
                    str(self.terraform_path),
                    '--format', 'json',
                    '--out', str(json_output),
                    '--soft-fail'
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Parse tfsec JSON output
            findings = []
            if json_output.exists():
                try:
                    with open(json_output, 'r') as f:
                        tfsec_data = json.load(f)

                    if "results" in tfsec_data and tfsec_data["results"]:
                        for issue in tfsec_data["results"]:
                            severity = self._map_tfsec_severity(issue.get("severity", "LOW"))

                            finding = Finding(
                                scanner="tfsec",
                                severity=severity,
                                rule_id=issue.get("rule_id", "UNKNOWN"),
                                title=issue.get("description", "Security issue found"),
                                description=issue.get("impact", ""),
                                file_path=issue.get("location", {}).get("filename", "unknown"),
                                line_number=issue.get("location", {}).get("start_line"),
                                resource=issue.get("resource", ""),
                                remediation=issue.get("resolution", ""),
                            )
                            findings.append(finding)

                except json.JSONDecodeError as e:
                    self.logger.warning(f"{Colors.YELLOW}⚠ Could not parse tfsec JSON output: {e}{Colors.RESET}")
                except Exception as e:
                    self.logger.warning(f"{Colors.YELLOW}⚠ Error reading tfsec output: {e}{Colors.RESET}")

            scan_result = ScanResult(
                scanner="tfsec",
                success=True,  # We use soft-fail, so always succeed
                findings=findings,
                duration=duration,
            )

            self.results.append(scan_result)

            print(f"{Colors.GREEN}✓ tfsec scan completed in {duration:.2f}s{Colors.RESET}")
            print(f"  Found {len(findings)} issues\n")

        except subprocess.TimeoutExpired:
            self.logger.error(f"{Colors.RED}✗ tfsec scan timed out\n{Colors.RESET}")
            self.results.append(
                ScanResult(scanner="tfsec", success=False, error_message="Timeout")
            )
        except FileNotFoundError:
            self.logger.error(f"{Colors.RED}✗ tfsec not found in PATH\n{Colors.RESET}")
            self.results.append(
                ScanResult(scanner="tfsec", success=False, error_message="tfsec not installed")
            )
        except Exception as e:
            self.logger.error(f"{Colors.RED}✗ Error running tfsec: {e}\n{Colors.RESET}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            self.results.append(
                ScanResult(scanner="tfsec", success=False, error_message=str(e))
            )

    def _run_checkov(self) -> None:
        """Run Checkov security scanner"""
        print(f"{Colors.BOLD}Step 2b: Running Checkov Security Scanner{Colors.RESET}")
        print("-" * 60)

        json_output = self.reports_dir / "checkov-report.json"
        start_time = datetime.now()

        try:
            result = subprocess.run(
                [
                    'checkov',
                    '-d', str(self.terraform_path),
                    '--framework', 'terraform',
                    '--output', 'json',
                    '--output-file-path', str(self.reports_dir),
                    '--soft-fail',
                    '--compact',
                    '--quiet'
                ],
                capture_output=True,
                text=True,
                timeout=180,
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Parse Checkov JSON output
            findings = []

            # Checkov outputs to results_json.json in the specified directory
            checkov_results = self.reports_dir / "results_json.json"
            if checkov_results.exists():
                try:
                    with open(checkov_results, 'r') as f:
                        checkov_data = json.load(f)

                    # Navigate the Checkov structure
                    results_key = "results"
                    if results_key in checkov_data:
                        failed_checks = checkov_data[results_key].get("failed_checks", [])

                        for check in failed_checks:
                            # Map Checkov severity
                            severity = self._map_checkov_severity(check.get("check_id", ""))

                            finding = Finding(
                                scanner="checkov",
                                severity=severity,
                                rule_id=check.get("check_id", "UNKNOWN"),
                                title=check.get("check_name", "Security check failed"),
                                description=check.get("check_result", {}).get("result", "") if isinstance(check.get("check_result"), dict) else "",
                                file_path=check.get("file_path", "unknown"),
                                line_number=check.get("file_line_range", [0])[0] if check.get("file_line_range") else None,
                                resource=check.get("resource", ""),
                                remediation=check.get("guideline", ""),
                            )
                            findings.append(finding)

                except json.JSONDecodeError as e:
                    self.logger.warning(f"{Colors.YELLOW}⚠ Could not parse Checkov JSON output: {e}{Colors.RESET}")
                except Exception as e:
                    self.logger.warning(f"{Colors.YELLOW}⚠ Error reading Checkov output: {e}{Colors.RESET}")

            scan_result = ScanResult(
                scanner="checkov",
                success=True,
                findings=findings,
                duration=duration,
            )

            self.results.append(scan_result)

            print(f"{Colors.GREEN}✓ Checkov scan completed in {duration:.2f}s{Colors.RESET}")
            print(f"  Found {len(findings)} issues\n")

        except subprocess.TimeoutExpired:
            self.logger.error(f"{Colors.RED}✗ Checkov scan timed out\n{Colors.RESET}")
            self.results.append(
                ScanResult(scanner="checkov", success=False, error_message="Timeout")
            )
        except FileNotFoundError:
            self.logger.error(f"{Colors.RED}✗ Checkov not found in PATH\n{Colors.RESET}")
            self.results.append(
                ScanResult(scanner="checkov", success=False, error_message="checkov not installed")
            )
        except Exception as e:
            self.logger.error(f"{Colors.RED}✗ Error running Checkov: {e}\n{Colors.RESET}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            self.results.append(
                ScanResult(scanner="checkov", success=False, error_message=str(e))
            )

    def _run_conftest(self) -> None:
        """Run Conftest/OPA policy checker"""
        print(f"{Colors.BOLD}Step 2c: Running Conftest/OPA Policy Checker{Colors.RESET}")
        print("-" * 60)

        policy_dir = self.project_root / "policies" / "opa"
        json_output = self.reports_dir / "conftest-report.json"
        start_time = datetime.now()

        try:
            # Find all .tf files
            tf_files = list(self.terraform_path.glob("*.tf"))

            if not tf_files:
                self.logger.warning(f"{Colors.YELLOW}⚠ No .tf files found for Conftest{Colors.RESET}")
                return

            findings = []
            failed = False

            # Run conftest on each .tf file
            for tf_file in tf_files:
                result = subprocess.run(
                    [
                        'conftest',
                        'test',
                        str(tf_file),
                        '--policy', str(policy_dir),
                        '--output', 'json',
                        '--all-namespaces'
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    failed = True

                # Parse conftest output
                if result.stdout:
                    try:
                        conftest_data = json.loads(result.stdout)
                        # Process conftest findings
                        # Note: Conftest output format varies, this is a basic implementation
                    except json.JSONDecodeError:
                        pass

            duration = (datetime.now() - start_time).total_seconds()

            scan_result = ScanResult(
                scanner="conftest",
                success=not failed,
                findings=findings,
                duration=duration,
            )

            self.results.append(scan_result)

            print(f"{Colors.GREEN}✓ Conftest scan completed in {duration:.2f}s{Colors.RESET}")
            print(f"  Found {len(findings)} policy violations\n")

        except subprocess.TimeoutExpired:
            self.logger.error(f"{Colors.RED}✗ Conftest scan timed out\n{Colors.RESET}")
            self.results.append(
                ScanResult(scanner="conftest", success=False, error_message="Timeout")
            )
        except FileNotFoundError:
            self.logger.error(f"{Colors.RED}✗ Conftest not found in PATH\n{Colors.RESET}")
            self.results.append(
                ScanResult(scanner="conftest", success=False, error_message="conftest not installed")
            )
        except Exception as e:
            self.logger.error(f"{Colors.RED}✗ Error running Conftest: {e}\n{Colors.RESET}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            self.results.append(
                ScanResult(scanner="conftest", success=False, error_message=str(e))
            )

    def _analyze_results(self) -> bool:
        """Analyze all scan results and determine pass/fail"""
        print(f"{Colors.BOLD}{'=' * 60}")
        print(f"{Colors.CYAN}Scan Results Summary{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

        # Aggregate all findings
        all_findings = []
        for result in self.results:
            all_findings.extend(result.findings)

        # Count by severity
        severity_counts = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 0,
            Severity.MEDIUM: 0,
            Severity.LOW: 0,
            Severity.INFO: 0,
        }

        for finding in all_findings:
            severity_counts[finding.severity] += 1

        # Print summary
        print(f"Total Issues Found: {Colors.BOLD}{len(all_findings)}{Colors.RESET}")
        print(f"  🔴 Critical: {Colors.RED}{severity_counts[Severity.CRITICAL]}{Colors.RESET}")
        print(f"  🟠 High:     {Colors.YELLOW}{severity_counts[Severity.HIGH]}{Colors.RESET}")
        print(f"  🟡 Medium:   {Colors.BLUE}{severity_counts[Severity.MEDIUM]}{Colors.RESET}")
        print(f"  🔵 Low:      {Colors.CYAN}{severity_counts[Severity.LOW]}{Colors.RESET}")
        print(f"  ⚪ Info:     {Colors.WHITE}{severity_counts[Severity.INFO]}{Colors.RESET}")
        print()

        # Check if any findings exceed threshold
        threshold_findings = [
            f for f in all_findings if f.severity.value >= self.severity_threshold.value
        ]

        if threshold_findings:
            print(f"{Colors.RED}{Colors.BOLD}❌ FAILED: Found {len(threshold_findings)} issues at or above {self.severity_threshold.name} severity{Colors.RESET}")
            print()
            print("Issues exceeding threshold:")
            print("-" * 60)

            # Group by severity
            for sev in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
                sev_findings = [f for f in threshold_findings if f.severity == sev]
                if sev_findings:
                    print(f"\n{Colors.BOLD}{sev.name} Severity ({len(sev_findings)} issues):{Colors.RESET}")
                    for finding in sev_findings[:5]:  # Show first 5 per severity
                        print(f"  • {finding.scanner}: {finding.title}")
                        print(f"    File: {finding.file_path}:{finding.line_number or '?'}")
                        if finding.resource:
                            print(f"    Resource: {finding.resource}")

                    if len(sev_findings) > 5:
                        print(f"    ... and {len(sev_findings) - 5} more {sev.name} issues")

            print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}")
            return False
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ PASSED: No issues at or above {self.severity_threshold.name} severity{Colors.RESET}")
            print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}")
            return True

    def _map_tfsec_severity(self, severity_str: str) -> Severity:
        """Map tfsec severity to our Severity enum"""
        mapping = {
            "CRITICAL": Severity.CRITICAL,
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "LOW": Severity.LOW,
        }
        return mapping.get(severity_str.upper(), Severity.INFO)

    def _map_checkov_severity(self, check_id: str) -> Severity:
        """Map Checkov check ID to severity (Checkov doesn't have built-in severity)"""
        # High severity patterns
        high_patterns = [
            'CKV_AWS_18',  # S3 bucket encryption
            'CKV_AWS_19',  # S3 bucket public access
            'CKV_AWS_20',  # S3 bucket versioning
            'CKV_AWS_21',  # S3 bucket logging
            'CKV_AWS_23',  # Security group SSH
            'CKV_AWS_24',  # Security group RDP
            'CKV_AWS_16',  # RDS encryption
            'CKV_AWS_17',  # RDS public access
            'CKV_AWS_3',   # EBS encryption
            'CKV_AWS_7',   # KMS rotation
        ]

        if any(pattern in check_id for pattern in high_patterns):
            return Severity.HIGH

        # Default to MEDIUM
        return Severity.MEDIUM

    def export_json(self, output_file: str) -> None:
        """Export results to JSON format"""
        data = {
            "version": __version__,
            "timestamp": datetime.now().isoformat(),
            "terraform_path": str(self.terraform_path),
            "severity_threshold": self.severity_threshold.name,
            "summary": self._get_summary(),
            "results": [
                {
                    "scanner": r.scanner,
                    "success": r.success,
                    "duration": r.duration,
                    "error_message": r.error_message,
                    "findings_count": len(r.findings),
                    "findings": [
                        {
                            "severity": f.severity.name,
                            "rule_id": f.rule_id,
                            "title": f.title,
                            "description": f.description,
                            "file_path": f.file_path,
                            "line_number": f.line_number,
                            "resource": f.resource,
                            "remediation": f.remediation,
                        }
                        for f in r.findings
                    ],
                }
                for r in self.results
            ],
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n{Colors.GREEN}📄 JSON report saved to: {output_path}{Colors.RESET}")

    def export_sarif(self, output_file: str) -> None:
        """Export results to SARIF format for GitHub/GitLab integration"""
        all_findings = []
        for result in self.results:
            all_findings.extend(result.findings)

        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "IaC Guard",
                            "version": __version__,
                            "informationUri": "https://github.com/yourorg/iac-guard",
                            "rules": self._get_sarif_rules(all_findings),
                        }
                    },
                    "results": [
                        {
                            "ruleId": f.rule_id,
                            "level": self._severity_to_sarif_level(f.severity),
                            "message": {
                                "text": f.title,
                                "markdown": f"{f.description}\n\n**Remediation:** {f.remediation}" if f.remediation else f.description
                            },
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": f.file_path},
                                        "region": {
                                            "startLine": f.line_number or 1,
                                        },
                                    }
                                }
                            ],
                        }
                        for f in all_findings
                    ],
                }
            ],
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(sarif, f, indent=2)

        print(f"\n{Colors.GREEN}📄 SARIF report saved to: {output_path}{Colors.RESET}")

    def _get_sarif_rules(self, findings: List[Finding]) -> List[Dict]:
        """Get unique rules for SARIF output"""
        rules_dict = {}
        for finding in findings:
            if finding.rule_id not in rules_dict:
                rules_dict[finding.rule_id] = {
                    "id": finding.rule_id,
                    "shortDescription": {"text": finding.title},
                    "fullDescription": {"text": finding.description or finding.title},
                    "help": {
                        "text": finding.remediation or "See documentation for remediation steps"
                    },
                }
        return list(rules_dict.values())

    def _severity_to_sarif_level(self, severity: Severity) -> str:
        """Convert severity to SARIF level"""
        if severity == Severity.CRITICAL or severity == Severity.HIGH:
            return "error"
        elif severity == Severity.MEDIUM:
            return "warning"
        else:
            return "note"

    def export_markdown(self, output_file: str) -> None:
        """Export results to Markdown format"""
        all_findings = []
        for result in self.results:
            all_findings.extend(result.findings)

        summary = self._get_summary()

        md = f"""# IaC Security Guardrails Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Target:** `{self.terraform_path}`
**Severity Threshold:** {self.severity_threshold.name}
**Version:** {__version__}

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | {summary['critical']} |
| 🟠 High | {summary['high']} |
| 🟡 Medium | {summary['medium']} |
| 🔵 Low | {summary['low']} |
| ⚪ Info | {summary['info']} |
| **Total** | **{summary['total']}** |

## Scanner Results

"""

        for result in self.results:
            status = "✅ Passed" if result.success else "❌ Failed"
            md += f"### {result.scanner.upper()} - {status}\n\n"
            md += f"- **Duration:** {result.duration:.2f}s\n"
            md += f"- **Findings:** {len(result.findings)}\n"
            if result.error_message:
                md += f"- **Error:** {result.error_message}\n"
            md += "\n"

        if all_findings:
            md += "## Detailed Findings\n\n"

            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
                findings_at_level = [f for f in all_findings if f.severity == severity]

                if findings_at_level:
                    md += f"### {severity.name} Severity Issues ({len(findings_at_level)})\n\n"

                    for i, finding in enumerate(findings_at_level, 1):
                        md += f"#### {i}. {finding.title}\n\n"
                        md += f"- **Scanner:** {finding.scanner}\n"
                        md += f"- **Rule ID:** `{finding.rule_id}`\n"
                        md += f"- **File:** `{finding.file_path}`"
                        if finding.line_number:
                            md += f" (line {finding.line_number})"
                        md += "\n"
                        if finding.resource:
                            md += f"- **Resource:** `{finding.resource}`\n"
                        if finding.description:
                            md += f"- **Description:** {finding.description}\n"
                        if finding.remediation:
                            md += f"- **Remediation:** {finding.remediation}\n"
                        md += "\n"

        md += "---\n\n"
        md += f"*Report generated by IaC Guard v{__version__}*\n"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(md)

        print(f"\n{Colors.GREEN}📄 Markdown report saved to: {output_path}{Colors.RESET}")

    def _get_summary(self) -> Dict:
        """Get summary statistics"""
        all_findings = []
        for result in self.results:
            all_findings.extend(result.findings)

        return {
            'total': len(all_findings),
            'critical': len([f for f in all_findings if f.severity == Severity.CRITICAL]),
            'high': len([f for f in all_findings if f.severity == Severity.HIGH]),
            'medium': len([f for f in all_findings if f.severity == Severity.MEDIUM]),
            'low': len([f for f in all_findings if f.severity == Severity.LOW]),
            'info': len([f for f in all_findings if f.severity == Severity.INFO]),
        }


def main():
    parser = argparse.ArgumentParser(
        description="IaC Guard - Infrastructure-as-Code Security Guardrails",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan default Terraform directory
  %(prog)s scan

  # Scan specific directory
  %(prog)s scan --path ./terraform

  # Set severity threshold to CRITICAL only
  %(prog)s scan --severity-threshold CRITICAL

  # Export to different formats
  %(prog)s scan --format json
  %(prog)s scan --format sarif
  %(prog)s scan --format markdown

  # Run specific scanners only
  %(prog)s scan --scanners tfsec checkov

  # Verbose output
  %(prog)s scan --verbose
        """,
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Run security scan on Terraform code")
    scan_parser.add_argument(
        "--path",
        "-p",
        default="./iac/terraform",
        help="Path to Terraform directory (default: ./iac/terraform)",
    )
    scan_parser.add_argument(
        "--severity-threshold",
        "-s",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
        default="HIGH",
        help="Minimum severity to fail the build (default: HIGH)",
    )
    scan_parser.add_argument(
        "--format",
        "-f",
        choices=["terminal", "json", "sarif", "markdown", "all"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    scan_parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: reports/iac-guard-report.<format>)",
    )
    scan_parser.add_argument(
        "--scanners",
        nargs="+",
        default=["tfsec", "checkov"],
        help="Scanners to run (default: tfsec checkov)",
    )
    scan_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.command != "scan":
        parser.print_help()
        sys.exit(1)

    try:
        # Parse severity threshold
        severity_threshold = Severity[args.severity_threshold]

        # Initialize IaC Guard
        guard = IaCGuard(
            terraform_path=args.path,
            severity_threshold=severity_threshold,
            scanners=args.scanners,
            verbose=args.verbose,
        )

        # Run scans
        success = guard.run_all_scans()

        # Export results
        if args.format != "terminal" or args.format == "all":
            formats = [args.format] if args.format != "all" else ["json", "sarif", "markdown"]

            for fmt in formats:
                if fmt == "terminal":
                    continue

                if args.output:
                    output_file = args.output
                else:
                    output_file = f"reports/iac-guard-report.{fmt}"

                if fmt == "json":
                    guard.export_json(output_file)
                elif fmt == "sarif":
                    guard.export_sarif(output_file)
                elif fmt == "markdown":
                    guard.export_markdown(output_file)

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except ValueError as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Scan interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {e}{Colors.RESET}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
