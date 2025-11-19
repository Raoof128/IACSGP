# Multi-stage Dockerfile for IaC Security Guardrails
# Optimized for size and security

# Stage 1: Builder
FROM python:3.14-slim AS builder

LABEL maintainer="IaC Security Team <security@yourorg.com>"
LABEL description="Infrastructure-as-Code Security Guardrails - Security scanning pipeline for Terraform"
LABEL org.opencontainers.image.source="https://github.com/yourorg/iac-security-guardrails"

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Install tfsec
ARG TFSEC_VERSION=1.28.1
RUN wget -q "https://github.com/aquasecurity/tfsec/releases/download/v${TFSEC_VERSION}/tfsec-linux-amd64" -O /usr/local/bin/tfsec \
    && chmod +x /usr/local/bin/tfsec

# Install Checkov
RUN pip install --no-cache-dir --user checkov

# Install Conftest
ARG CONFTEST_VERSION=0.45.0
RUN wget -q "https://github.com/open-policy-agent/conftest/releases/download/v${CONFTEST_VERSION}/conftest_${CONFTEST_VERSION}_Linux_x86_64.tar.gz" \
    && tar xzf conftest_${CONFTEST_VERSION}_Linux_x86_64.tar.gz \
    && mv conftest /usr/local/bin/ \
    && chmod +x /usr/local/bin/conftest \
    && rm conftest_${CONFTEST_VERSION}_Linux_x86_64.tar.gz

# Install Terraform
ARG TERRAFORM_VERSION=1.6.0
RUN wget -q "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" \
    && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && chmod +x /usr/local/bin/terraform \
    && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Stage 2: Runtime
FROM python:3.14-slim

LABEL maintainer="IaC Security Team <security@yourorg.com>"
LABEL version="1.0.0"

# Create non-root user
RUN groupadd -r iacguard && useradd -r -g iacguard iacguard

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/iacguard/.local

# Copy binaries from builder
COPY --from=builder /usr/local/bin/tfsec /usr/local/bin/tfsec
COPY --from=builder /usr/local/bin/conftest /usr/local/bin/conftest
COPY --from=builder /usr/local/bin/terraform /usr/local/bin/terraform

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY --chown=iacguard:iacguard . .

# Create reports directory
RUN mkdir -p /app/reports && chown -R iacguard:iacguard /app/reports

# Set PATH
ENV PATH=/home/iacguard/.local/bin:$PATH

# Switch to non-root user
USER iacguard

# Verify installations
RUN python3 --version && \
    terraform version && \
    tfsec --version && \
    checkov --version && \
    conftest --version

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 iac_guard.py --version || exit 1

# Set entrypoint
ENTRYPOINT ["python3", "iac_guard.py"]

# Default command
CMD ["scan", "--help"]

# Metadata
LABEL org.opencontainers.image.title="IaC Security Guardrails"
LABEL org.opencontainers.image.description="Automated security scanning pipeline for Terraform"
LABEL org.opencontainers.image.url="https://github.com/yourorg/iac-security-guardrails"
LABEL org.opencontainers.image.documentation="https://github.com/yourorg/iac-security-guardrails#readme"
LABEL org.opencontainers.image.licenses="MIT"
