# Multi-stage build for replicate-batch-process
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY pyproject.toml .
COPY setup.py .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt && \
    pip install --no-cache-dir --user build

# Copy source code
COPY . .

# Build the package
RUN python -m build --wheel

# Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    REPLICATE_API_TOKEN=""

# Create non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY --from=builder /app/dist/*.whl /tmp/

# Install the package
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm -rf /tmp/*.whl

# Copy essential files
COPY --chown=appuser:appuser config.py .
COPY --chown=appuser:appuser main.py .
COPY --chown=appuser:appuser example_usage.py .
COPY --chown=appuser:appuser replicate_batch_process/ ./replicate_batch_process/

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Create output directory
RUN mkdir -p /app/output

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import replicate_batch_process; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "replicate_batch_process.main"]