FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=ap-south-1 \
    AWS_DEFAULT_REGION=ap-south-1

COPY Backend/requirements.txt requirements.txt

# System + main deps
RUN apt-get update && \
    apt-get install -y --only-upgrade libc6 dpkg || apt-get install -y libc6 dpkg && \
    apt-get install -y --no-install-recommends ca-certificates && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir aws-opentelemetry-distro && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip /tmp/*

# ✅ Separate layer (as you wanted)
RUN pip install --no-cache-dir boto3

# User
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

COPY . .

EXPOSE 9000 8000 8080

CMD ["opentelemetry-instrument", "python", "-m", "Backend.main"]
