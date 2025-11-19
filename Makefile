.PHONY: help install scan scan-insecure test format clean setup

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
RESET := \033[0m

help: ## Show this help message
	@echo "$(CYAN)IaC Security Guardrails - Available Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

install: ## Install all dependencies
	@echo "$(CYAN)Installing Python dependencies...$(RESET)"
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Python dependencies installed$(RESET)"
	@echo ""
	@echo "$(YELLOW)Note: You still need to install security scanners:$(RESET)"
	@echo "  - tfsec: curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash"
	@echo "  - checkov: pip install checkov"
	@echo "  - conftest: brew install conftest (or download from GitHub)"

setup: install ## Full setup including pre-commit hooks
	@echo "$(CYAN)Setting up pre-commit hooks...$(RESET)"
	pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed$(RESET)"

scan: ## Run security scan on main Terraform code
	@echo "$(CYAN)Running IaC security scan...$(RESET)"
	python3 iac_guard.py scan --path ./iac/terraform

scan-insecure: ## Run security scan on insecure examples (should fail)
	@echo "$(CYAN)Running IaC security scan on insecure examples...$(RESET)"
	@echo "$(YELLOW)Note: This scan should fail with HIGH severity issues$(RESET)"
	python3 iac_guard.py scan --path ./iac/terraform/examples || true

scan-verbose: ## Run security scan with verbose output
	@echo "$(CYAN)Running IaC security scan (verbose)...$(RESET)"
	python3 iac_guard.py scan --path ./iac/terraform --verbose

scan-all: ## Generate all report formats
	@echo "$(CYAN)Running IaC security scan with all output formats...$(RESET)"
	python3 iac_guard.py scan --path ./iac/terraform --format all

format: ## Format Terraform code
	@echo "$(CYAN)Formatting Terraform code...$(RESET)"
	terraform fmt -recursive ./iac/terraform/
	@echo "$(GREEN)✓ Terraform code formatted$(RESET)"

format-python: ## Format Python code
	@echo "$(CYAN)Formatting Python code...$(RESET)"
	black iac_guard.py
	@echo "$(GREEN)✓ Python code formatted$(RESET)"

validate: ## Validate Terraform configuration
	@echo "$(CYAN)Validating Terraform configuration...$(RESET)"
	cd ./iac/terraform && terraform init -backend=false && terraform validate

lint: ## Run linters on code
	@echo "$(CYAN)Running Python linters...$(RESET)"
	flake8 iac_guard.py --max-line-length=100 --extend-ignore=E203,W503 || true
	pylint iac_guard.py --max-line-length=100 || true

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(CYAN)Running pre-commit hooks...$(RESET)"
	pre-commit run --all-files

test: ## Run tests (if available)
	@echo "$(CYAN)Running tests...$(RESET)"
	@if [ -d "tests" ]; then \
		pytest tests/ -v; \
	else \
		echo "$(YELLOW)No tests directory found$(RESET)"; \
	fi

clean: ## Clean generated files and caches
	@echo "$(CYAN)Cleaning generated files...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .tox .coverage htmlcov/ dist/ build/
	rm -f iac_guard_old.py
	@echo "$(GREEN)✓ Cleaned$(RESET)"

clean-reports: ## Clean report files
	@echo "$(CYAN)Cleaning report files...$(RESET)"
	rm -rf reports/*.json reports/*.sarif reports/*.md
	@echo "$(GREEN)✓ Reports cleaned$(RESET)"

check-deps: ## Check if required tools are installed
	@echo "$(CYAN)Checking dependencies...$(RESET)"
	@echo -n "Python 3: "
	@python3 --version 2>/dev/null && echo "$(GREEN)✓$(RESET)" || echo "$(RED)✗ Not found$(RESET)"
	@echo -n "Terraform: "
	@terraform --version 2>/dev/null | head -1 && echo "$(GREEN)✓$(RESET)" || echo "$(RED)✗ Not found$(RESET)"
	@echo -n "tfsec: "
	@tfsec --version 2>/dev/null && echo "$(GREEN)✓$(RESET)" || echo "$(RED)✗ Not found$(RESET)"
	@echo -n "Checkov: "
	@checkov --version 2>/dev/null && echo "$(GREEN)✓$(RESET)" || echo "$(RED)✗ Not found$(RESET)"
	@echo -n "Conftest: "
	@conftest --version 2>/dev/null && echo "$(GREEN)✓$(RESET)" || echo "$(RED)✗ Not found$(RESET)"
	@echo -n "pre-commit: "
	@pre-commit --version 2>/dev/null && echo "$(GREEN)✓$(RESET)" || echo "$(RED)✗ Not found$(RESET)"

demo: ## Run a demonstration of the security pipeline
	@echo "$(CYAN)╔════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(CYAN)║  IaC Security Guardrails - Demo                        ║$(RESET)"
	@echo "$(CYAN)╚════════════════════════════════════════════════════════╝$(RESET)"
	@echo ""
	@echo "$(GREEN)Step 1: Scanning SECURE Terraform code...$(RESET)"
	@echo "$(YELLOW)Expected: PASS ✅$(RESET)"
	@echo ""
	@python3 iac_guard.py scan --path ./iac/terraform || true
	@echo ""
	@echo "$(CYAN)Press Enter to continue to Step 2...$(RESET)"
	@read dummy
	@echo ""
	@echo "$(RED)Step 2: Scanning INSECURE Terraform code...$(RESET)"
	@echo "$(YELLOW)Expected: FAIL ❌ (with HIGH severity issues)$(RESET)"
	@echo ""
	@python3 iac_guard.py scan --path ./iac/terraform/examples || true
	@echo ""
	@echo "$(GREEN)╔════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(GREEN)║  Demo Complete!                                        ║$(RESET)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════╝$(RESET)"

version: ## Show version information
	@python3 iac_guard.py --version

docs: ## Generate documentation (if available)
	@echo "$(CYAN)Documentation available in:$(RESET)"
	@echo "  - README.md (Main documentation)"
	@echo "  - QUICKSTART.md (Quick start guide)"
	@echo "  - SECURITY_POLICIES.md (Policy reference)"
	@echo "  - CONTRIBUTING.md (Contribution guide)"
