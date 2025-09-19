# Multi-stage build for optimized production image
# Stage 1: Builder
FROM python:3.9-slim-bullseye as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    build-essential \
    pkg-config \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.9-slim-bullseye

# Metadata
LABEL maintainer="AI Vision Systems <support@aivisionsystems.com>"
LABEL version="1.0.0"
LABEL description="Rodent AI Vision Box - Real-time rodent detection system"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash rodentai && \
    mkdir -p /app /app/data /app/logs /app/models && \
    chown -R rodentai:rodentai /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/rodentai/.local

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=rodentai:rodentai . /app/

# Set Python path
ENV PATH=/home/rodentai/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Switch to non-root user
USER rodentai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Volumes for persistent data
VOLUME ["/app/data", "/app/logs", "/app/config"]

# Default environment variables
ENV LOG_LEVEL=INFO
ENV DETECTION_CONFIDENCE=0.25
ENV ALERT_COOLDOWN=600

# Entry point
ENTRYPOINT ["python", "-u", "src/main.py"]