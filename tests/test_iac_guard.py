"""
Unit tests for IaC Guard CLI tool
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import iac_guard


class TestSeverity(unittest.TestCase):
    """Test Severity enum"""

    def test_severity_values(self):
        """Test severity level values are correct"""
        self.assertEqual(iac_guard.Severity.CRITICAL.value, 4)
        self.assertEqual(iac_guard.Severity.HIGH.value, 3)
        self.assertEqual(iac_guard.Severity.MEDIUM.value, 2)
        self.assertEqual(iac_guard.Severity.LOW.value, 1)
        self.assertEqual(iac_guard.Severity.INFO.value, 0)

    def test_severity_string(self):
        """Test severity string representation"""
        self.assertEqual(str(iac_guard.Severity.HIGH), "HIGH")
        self.assertEqual(str(iac_guard.Severity.CRITICAL), "CRITICAL")


class TestFinding(unittest.TestCase):
    """Test Finding dataclass"""

    def test_finding_creation(self):
        """Test creating a Finding"""
        finding = iac_guard.Finding(
            scanner="tfsec",
            severity=iac_guard.Severity.HIGH,
            rule_id="AWS001",
            title="Test finding",
            description="Test description",
            file_path="test.tf",
            line_number=42,
        )

        self.assertEqual(finding.scanner, "tfsec")
        self.assertEqual(finding.severity, iac_guard.Severity.HIGH)
        self.assertEqual(finding.rule_id, "AWS001")
        self.assertEqual(finding.line_number, 42)

    def test_finding_string(self):
        """Test Finding string representation"""
        finding = iac_guard.Finding(
            scanner="checkov",
            severity=iac_guard.Severity.CRITICAL,
            rule_id="CKV_001",
            title="Critical issue",
            description="Critical description",
            file_path="main.tf",
        )

        self.assertIn("CRITICAL", str(finding))
        self.assertIn("checkov", str(finding))
        self.assertIn("Critical issue", str(finding))


class TestScanResult(unittest.TestCase):
    """Test ScanResult dataclass"""

    def test_scan_result_creation(self):
        """Test creating a ScanResult"""
        result = iac_guard.ScanResult(
            scanner="tfsec",
            success=True,
            duration=1.23,
        )

        self.assertEqual(result.scanner, "tfsec")
        self.assertTrue(result.success)
        self.assertEqual(result.duration, 1.23)
        self.assertEqual(len(result.findings), 0)

    def test_get_findings_by_severity(self):
        """Test filtering findings by severity"""
        findings = [
            iac_guard.Finding(
                scanner="test",
                severity=iac_guard.Severity.CRITICAL,
                rule_id="001",
                title="Critical",
                description="desc",
                file_path="test.tf",
            ),
            iac_guard.Finding(
                scanner="test",
                severity=iac_guard.Severity.HIGH,
                rule_id="002",
                title="High",
                description="desc",
                file_path="test.tf",
            ),
            iac_guard.Finding(
                scanner="test",
                severity=iac_guard.Severity.LOW,
                rule_id="003",
                title="Low",
                description="desc",
                file_path="test.tf",
            ),
        ]

        result = iac_guard.ScanResult(
            scanner="test",
            success=True,
            findings=findings,
        )

        # Filter by HIGH (should get CRITICAL and HIGH)
        high_findings = result.get_findings_by_severity(iac_guard.Severity.HIGH)
        self.assertEqual(len(high_findings), 2)

        # Filter by CRITICAL (should get only CRITICAL)
        critical_findings = result.get_findings_by_severity(iac_guard.Severity.CRITICAL)
        self.assertEqual(len(critical_findings), 1)


class TestIaCGuard(unittest.TestCase):
    """Test IaCGuard main class"""

    def setUp(self):
        """Set up test fixtures"""
        # Use the actual terraform directory if it exists
        self.test_path = Path(__file__).parent.parent / "iac" / "terraform"
        if not self.test_path.exists():
            # Create a temporary test directory
            self.test_path = Path(__file__).parent / "test_terraform"
            self.test_path.mkdir(exist_ok=True)
            # Create a dummy .tf file
            (self.test_path / "test.tf").write_text("# Test terraform file\n")

    def test_guard_initialization(self):
        """Test IaCGuard initialization"""
        guard = iac_guard.IaCGuard(
            terraform_path=str(self.test_path),
            severity_threshold=iac_guard.Severity.HIGH,
        )

        self.assertEqual(guard.severity_threshold, iac_guard.Severity.HIGH)
        self.assertTrue(guard.terraform_path.exists())
        self.assertTrue(guard.reports_dir.exists())

    def test_guard_initialization_invalid_path(self):
        """Test IaCGuard initialization with invalid path"""
        with self.assertRaises(ValueError):
            iac_guard.IaCGuard(
                terraform_path="/nonexistent/path",
                severity_threshold=iac_guard.Severity.HIGH,
            )

    def test_check_dependencies(self):
        """Test dependency checking"""
        guard = iac_guard.IaCGuard(
            terraform_path=str(self.test_path),
        )

        deps = guard.check_dependencies()

        self.assertIsInstance(deps, dict)
        self.assertIn('terraform', deps)
        self.assertIn('tfsec', deps)
        self.assertIn('checkov', deps)

    def test_map_tfsec_severity(self):
        """Test tfsec severity mapping"""
        guard = iac_guard.IaCGuard(
            terraform_path=str(self.test_path),
        )

        self.assertEqual(
            guard._map_tfsec_severity("CRITICAL"),
            iac_guard.Severity.CRITICAL
        )
        self.assertEqual(
            guard._map_tfsec_severity("HIGH"),
            iac_guard.Severity.HIGH
        )
        self.assertEqual(
            guard._map_tfsec_severity("MEDIUM"),
            iac_guard.Severity.MEDIUM
        )
        self.assertEqual(
            guard._map_tfsec_severity("LOW"),
            iac_guard.Severity.LOW
        )
        self.assertEqual(
            guard._map_tfsec_severity("UNKNOWN"),
            iac_guard.Severity.INFO
        )

    def test_map_checkov_severity(self):
        """Test Checkov severity mapping"""
        guard = iac_guard.IaCGuard(
            terraform_path=str(self.test_path),
        )

        # High severity checks
        self.assertEqual(
            guard._map_checkov_severity("CKV_AWS_18"),
            iac_guard.Severity.HIGH
        )

        # Default to MEDIUM
        self.assertEqual(
            guard._map_checkov_severity("CKV_UNKNOWN"),
            iac_guard.Severity.MEDIUM
        )

    def test_get_summary(self):
        """Test summary generation"""
        guard = iac_guard.IaCGuard(
            terraform_path=str(self.test_path),
        )

        # Add some test results
        guard.results = [
            iac_guard.ScanResult(
                scanner="test",
                success=True,
                findings=[
                    iac_guard.Finding(
                        scanner="test",
                        severity=iac_guard.Severity.CRITICAL,
                        rule_id="001",
                        title="Critical",
                        description="desc",
                        file_path="test.tf",
                    ),
                    iac_guard.Finding(
                        scanner="test",
                        severity=iac_guard.Severity.HIGH,
                        rule_id="002",
                        title="High",
                        description="desc",
                        file_path="test.tf",
                    ),
                ],
            )
        ]

        summary = guard._get_summary()

        self.assertEqual(summary['total'], 2)
        self.assertEqual(summary['critical'], 1)
        self.assertEqual(summary['high'], 1)
        self.assertEqual(summary['medium'], 0)


class TestReportExport(unittest.TestCase):
    """Test report export functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_path = Path(__file__).parent.parent / "iac" / "terraform"
        if not self.test_path.exists():
            self.test_path = Path(__file__).parent / "test_terraform"
            self.test_path.mkdir(exist_ok=True)
            (self.test_path / "test.tf").write_text("# Test\n")

        self.guard = iac_guard.IaCGuard(
            terraform_path=str(self.test_path),
        )

        # Add test findings
        self.guard.results = [
            iac_guard.ScanResult(
                scanner="test",
                success=True,
                duration=1.0,
                findings=[
                    iac_guard.Finding(
                        scanner="test",
                        severity=iac_guard.Severity.HIGH,
                        rule_id="TEST001",
                        title="Test Finding",
                        description="Test description",
                        file_path="test.tf",
                        line_number=10,
                        remediation="Fix it",
                    ),
                ],
            )
        ]

    def test_export_json(self):
        """Test JSON export"""
        output_file = self.guard.reports_dir / "test_report.json"

        self.guard.export_json(str(output_file))

        self.assertTrue(output_file.exists())

        with open(output_file, 'r') as f:
            data = json.load(f)

        self.assertIn('version', data)
        self.assertIn('timestamp', data)
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)

        # Cleanup
        output_file.unlink()

    def test_export_markdown(self):
        """Test Markdown export"""
        output_file = self.guard.reports_dir / "test_report.md"

        self.guard.export_markdown(str(output_file))

        self.assertTrue(output_file.exists())

        content = output_file.read_text()
        self.assertIn("# IaC Security Guardrails Report", content)
        self.assertIn("Test Finding", content)

        # Cleanup
        output_file.unlink()

    def test_severity_to_sarif_level(self):
        """Test SARIF severity mapping"""
        self.assertEqual(
            self.guard._severity_to_sarif_level(iac_guard.Severity.CRITICAL),
            "error"
        )
        self.assertEqual(
            self.guard._severity_to_sarif_level(iac_guard.Severity.HIGH),
            "error"
        )
        self.assertEqual(
            self.guard._severity_to_sarif_level(iac_guard.Severity.MEDIUM),
            "warning"
        )
        self.assertEqual(
            self.guard._severity_to_sarif_level(iac_guard.Severity.LOW),
            "note"
        )


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
