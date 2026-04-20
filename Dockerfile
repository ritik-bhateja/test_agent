FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim
WORKDIR /app

# All environment variables in one layer
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=ap-south-1 \
    AWS_DEFAULT_REGION=ap-south-1



COPY Backend/requirements.txt requirements.txt
# Install from requirements file
RUN uv pip install -r requirements.txt

# Install system deps + Python deps in one layer (better caching & smaller image)
RUN apt-get update && \
    # Fix CVE (libc6 + dpkg)
    apt-get install -y --only-upgrade libc6 dpkg || apt-get install -y libc6 dpkg && \
    # Minimal required packages
    apt-get install -y --no-install-recommends ca-certificates && \
    \
    # Python setup
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir aws-opentelemetry-distro boto3 && \
    \
    # Cleanup (VERY important for image size)
    apt-get purge -y --auto-remove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip /tmp/*


# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

EXPOSE 9000
EXPOSE 8000
EXPOSE 8080

# Copy entire project (respecting .dockerignore)
COPY . .

# Use the full module path

CMD ["opentelemetry-instrument", "python", "-m", "Backend.main"]
