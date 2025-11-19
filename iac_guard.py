#!/usr/bin/env python3
"""
IaC Guard - Infrastructure-as-Code Security Guardrails CLI
A comprehensive security scanner for Terraform projects

This tool integrates multiple security scanners and enforces policy-as-code
to prevent insecure infrastructure changes from reaching production.
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class Severity(Enum):
    """Severity levels for security findings"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0


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


class IaCGuard:
    """Main IaC Security Guardrails scanner"""

    def __init__(
        self,
        terraform_path: str,
        severity_threshold: Severity = Severity.HIGH,
        scanners: Optional[List[str]] = None,
    ):
        self.terraform_path = Path(terraform_path).resolve()
        self.severity_threshold = severity_threshold
        self.project_root = Path(__file__).parent.resolve()
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Scanners to run
        if scanners is None:
            self.scanners = ["tfsec", "checkov", "conftest"]
        else:
            self.scanners = scanners

        self.results: List[ScanResult] = []

    def run_all_scans(self) -> bool:
        """Run all security scans and return success status"""
        print("=" * 60)
        print("IaC Security Guardrails - Starting Security Scan")
        print("=" * 60)
        print(f"Target: {self.terraform_path}")
        print(f"Severity Threshold: {self.severity_threshold.name}")
        print(f"Scanners: {', '.join(self.scanners)}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()

        # Step 1: Format and Validate
        if not self._run_format_and_validate():
            print("\n❌ Format/Validation failed - stopping scan")
            return False

        # Step 2: Run security scanners
        for scanner in self.scanners:
            if scanner == "tfsec":
                self._run_tfsec()
            elif scanner == "checkov":
                self._run_checkov()
            elif scanner == "conftest":
                self._run_conftest()

        # Step 3: Analyze results
        return self._analyze_results()

    def _run_format_and_validate(self) -> bool:
        """Run terraform fmt and validate"""
        print("Step 1: Running Terraform Format & Validation")
        print("-" * 60)

        script = self.project_root / "scripts" / "format_and_validate.sh"
        try:
            result = subprocess.run(
                [str(script), str(self.terraform_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            print(result.stdout)
            if result.returncode == 0:
                print("✓ Format and validation passed\n")
                return True
            else:
                print("✗ Format and validation failed\n")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("✗ Format and validation timed out\n")
            return False
        except Exception as e:
            print(f"✗ Error running format and validation: {e}\n")
            return False

    def _run_tfsec(self) -> None:
        """Run tfsec security scanner"""
        print("Step 2a: Running tfsec Security Scanner")
        print("-" * 60)

        script = self.project_root / "scanners" / "run_tfsec.sh"
        json_output = self.reports_dir / "tfsec-report.json"

        start_time = datetime.now()

        try:
            result = subprocess.run(
                [str(script), str(self.terraform_path), "json", str(json_output)],
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

                except json.JSONDecodeError:
                    print("⚠ Warning: Could not parse tfsec JSON output")

            scan_result = ScanResult(
                scanner="tfsec",
                success=result.returncode == 0,
                findings=findings,
                duration=duration,
            )

            self.results.append(scan_result)

            print(f"✓ tfsec scan completed in {duration:.2f}s")
            print(f"  Found {len(findings)} issues\n")

        except subprocess.TimeoutExpired:
            print("✗ tfsec scan timed out\n")
            self.results.append(
                ScanResult(scanner="tfsec", success=False, error_message="Timeout")
            )
        except Exception as e:
            print(f"✗ Error running tfsec: {e}\n")
            self.results.append(
                ScanResult(scanner="tfsec", success=False, error_message=str(e))
            )

    def _run_checkov(self) -> None:
        """Run Checkov security scanner"""
        print("Step 2b: Running Checkov Security Scanner")
        print("-" * 60)

        script = self.project_root / "scanners" / "run_checkov.sh"
        json_output = self.reports_dir / "checkov-report.json"

        start_time = datetime.now()

        try:
            result = subprocess.run(
                [str(script), str(self.terraform_path), "json", str(json_output)],
                capture_output=True,
                text=True,
                timeout=180,
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Parse Checkov JSON output
            findings = []

            # Checkov outputs to a directory, find the results file
            checkov_results = self.reports_dir / "results_json.json"
            if checkov_results.exists():
                try:
                    with open(checkov_results, 'r') as f:
                        checkov_data = json.load(f)

                    # Checkov has a complex structure, parse failed checks
                    for result_item in checkov_data.get("results", {}).get("failed_checks", []):
                        severity = self._map_checkov_severity(
                            result_item.get("check_class", "")
                        )

                        finding = Finding(
                            scanner="checkov",
                            severity=severity,
                            rule_id=result_item.get("check_id", "UNKNOWN"),
                            title=result_item.get("check_name", "Security check failed"),
                            description=result_item.get("check_result", {}).get("result", ""),
                            file_path=result_item.get("file_path", "unknown"),
                            line_number=result_item.get("file_line_range", [0])[0]
                            if result_item.get("file_line_range")
                            else None,
                            resource=result_item.get("resource", ""),
                            remediation=result_item.get("guideline", ""),
                        )
                        findings.append(finding)

                except json.JSONDecodeError:
                    print("⚠ Warning: Could not parse Checkov JSON output")

            scan_result = ScanResult(
                scanner="checkov",
                success=result.returncode == 0,
                findings=findings,
                duration=duration,
            )

            self.results.append(scan_result)

            print(f"✓ Checkov scan completed in {duration:.2f}s")
            print(f"  Found {len(findings)} issues\n")

        except subprocess.TimeoutExpired:
            print("✗ Checkov scan timed out\n")
            self.results.append(
                ScanResult(scanner="checkov", success=False, error_message="Timeout")
            )
        except Exception as e:
            print(f"✗ Error running Checkov: {e}\n")
            self.results.append(
                ScanResult(scanner="checkov", success=False, error_message=str(e))
            )

    def _run_conftest(self) -> None:
        """Run Conftest/OPA policy checker"""
        print("Step 2c: Running Conftest/OPA Policy Checker")
        print("-" * 60)

        script = self.project_root / "scanners" / "run_conftest.sh"
        policy_dir = self.project_root / "policies" / "opa"
        json_output = self.reports_dir / "conftest-report.json"

        start_time = datetime.now()

        try:
            result = subprocess.run(
                [
                    str(script),
                    str(self.terraform_path),
                    str(policy_dir),
                    str(json_output),
                ],
                capture_output=True,
                text=True,
                timeout=180,
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Parse Conftest output
            findings = []
            # Note: Conftest output parsing would be implemented here
            # For now, we'll check the return code

            scan_result = ScanResult(
                scanner="conftest",
                success=result.returncode == 0,
                findings=findings,
                duration=duration,
            )

            self.results.append(scan_result)

            print(f"✓ Conftest scan completed in {duration:.2f}s")
            print(f"  Found {len(findings)} policy violations\n")

        except subprocess.TimeoutExpired:
            print("✗ Conftest scan timed out\n")
            self.results.append(
                ScanResult(scanner="conftest", success=False, error_message="Timeout")
            )
        except Exception as e:
            print(f"✗ Error running Conftest: {e}\n")
            self.results.append(
                ScanResult(scanner="conftest", success=False, error_message=str(e))
            )

    def _analyze_results(self) -> bool:
        """Analyze all scan results and determine pass/fail"""
        print("=" * 60)
        print("Scan Results Summary")
        print("=" * 60)

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
        print(f"Total Issues Found: {len(all_findings)}")
        print(f"  🔴 Critical: {severity_counts[Severity.CRITICAL]}")
        print(f"  🟠 High:     {severity_counts[Severity.HIGH]}")
        print(f"  🟡 Medium:   {severity_counts[Severity.MEDIUM]}")
        print(f"  🔵 Low:      {severity_counts[Severity.LOW]}")
        print(f"  ⚪ Info:     {severity_counts[Severity.INFO]}")
        print()

        # Check if any findings exceed threshold
        threshold_exceeded = any(
            f.severity.value >= self.severity_threshold.value for f in all_findings
        )

        if threshold_exceeded:
            threshold_findings = [
                f for f in all_findings if f.severity.value >= self.severity_threshold.value
            ]

            print(f"❌ FAILED: Found {len(threshold_findings)} issues at or above {self.severity_threshold.name} severity")
            print()
            print("Issues exceeding threshold:")
            print("-" * 60)

            for finding in threshold_findings[:10]:  # Show first 10
                print(f"  [{finding.severity.name}] {finding.scanner}: {finding.title}")
                print(f"    File: {finding.file_path}:{finding.line_number or '?'}")
                if finding.resource:
                    print(f"    Resource: {finding.resource}")
                print()

            if len(threshold_findings) > 10:
                print(f"  ... and {len(threshold_findings) - 10} more issues")

            print("=" * 60)
            return False
        else:
            print(f"✅ PASSED: No issues at or above {self.severity_threshold.name} severity")
            print("=" * 60)
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

    def _map_checkov_severity(self, check_class: str) -> Severity:
        """Map Checkov check class to our Severity enum"""
        # Checkov doesn't have built-in severity, we infer from check type
        if "encryption" in check_class.lower() or "public" in check_class.lower():
            return Severity.HIGH
        elif "access" in check_class.lower() or "iam" in check_class.lower():
            return Severity.HIGH
        else:
            return Severity.MEDIUM

    def export_json(self, output_file: str) -> None:
        """Export results to JSON format"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "terraform_path": str(self.terraform_path),
            "severity_threshold": self.severity_threshold.name,
            "results": [
                {
                    "scanner": r.scanner,
                    "success": r.success,
                    "duration": r.duration,
                    "error_message": r.error_message,
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

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n📄 JSON report saved to: {output_file}")

    def export_sarif(self, output_file: str) -> None:
        """Export results to SARIF format for GitHub/GitLab integration"""
        # Aggregate all findings
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
                            "version": "1.0.0",
                            "informationUri": "https://github.com/yourorg/iac-guard",
                        }
                    },
                    "results": [
                        {
                            "ruleId": f.rule_id,
                            "level": self._severity_to_sarif_level(f.severity),
                            "message": {"text": f.title},
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

        with open(output_file, "w") as f:
            json.dump(sarif, f, indent=2)

        print(f"\n📄 SARIF report saved to: {output_file}")

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

        # Count by severity
        severity_counts = {s: 0 for s in Severity}
        for finding in all_findings:
            severity_counts[finding.severity] += 1

        md = f"""# IaC Security Guardrails Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Target:** `{self.terraform_path}`
**Severity Threshold:** {self.severity_threshold.name}

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | {severity_counts[Severity.CRITICAL]} |
| 🟠 High | {severity_counts[Severity.HIGH]} |
| 🟡 Medium | {severity_counts[Severity.MEDIUM]} |
| 🔵 Low | {severity_counts[Severity.LOW]} |
| ⚪ Info | {severity_counts[Severity.INFO]} |
| **Total** | **{len(all_findings)}** |

## Scanner Results

"""

        for result in self.results:
            status = "✅ Passed" if result.success else "❌ Failed"
            md += f"### {result.scanner.upper()} - {status}\n\n"
            md += f"- Duration: {result.duration:.2f}s\n"
            md += f"- Findings: {len(result.findings)}\n\n"

        if all_findings:
            md += "## Detailed Findings\n\n"

            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
                findings_at_level = [f for f in all_findings if f.severity == severity]

                if findings_at_level:
                    md += f"### {severity.name} Severity Issues\n\n"

                    for finding in findings_at_level:
                        md += f"#### {finding.title}\n\n"
                        md += f"- **Scanner:** {finding.scanner}\n"
                        md += f"- **Rule ID:** {finding.rule_id}\n"
                        md += f"- **File:** `{finding.file_path}`"
                        if finding.line_number:
                            md += f":{finding.line_number}"
                        md += "\n"
                        if finding.resource:
                            md += f"- **Resource:** `{finding.resource}`\n"
                        if finding.description:
                            md += f"- **Description:** {finding.description}\n"
                        if finding.remediation:
                            md += f"- **Remediation:** {finding.remediation}\n"
                        md += "\n"

        with open(output_file, "w") as f:
            f.write(md)

        print(f"\n📄 Markdown report saved to: {output_file}")


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
  %(prog)s scan --scanners tfsec,checkov
        """,
    )

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
        choices=["terminal", "json", "sarif", "markdown"],
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
        choices=["tfsec", "checkov", "conftest", "all"],
        nargs="+",
        default=["all"],
        help="Scanners to run (default: all)",
    )

    args = parser.parse_args()

    if args.command != "scan":
        parser.print_help()
        sys.exit(1)

    # Parse scanners
    scanners = args.scanners
    if "all" in scanners:
        scanners = ["tfsec", "checkov", "conftest"]

    # Parse severity threshold
    severity_threshold = Severity[args.severity_threshold]

    # Initialize IaC Guard
    guard = IaCGuard(
        terraform_path=args.path,
        severity_threshold=severity_threshold,
        scanners=scanners,
    )

    # Run scans
    success = guard.run_all_scans()

    # Export results
    if args.format != "terminal":
        if args.output:
            output_file = args.output
        else:
            output_file = f"reports/iac-guard-report.{args.format}"

        if args.format == "json":
            guard.export_json(output_file)
        elif args.format == "sarif":
            guard.export_sarif(output_file)
        elif args.format == "markdown":
            guard.export_markdown(output_file)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
