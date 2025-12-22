# Builder stage: creates a self-contained virtualenv with the app and dependencies
FROM python:3.14-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libssl-dev \
    libffi-dev \
    curl \
    ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Copy project metadata and source
COPY pyproject.toml uv.lock ./
COPY src ./src

# Use `uv` to create a project venv and install the package, then copy to /opt/venv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    export PATH="/root/.local/bin:$PATH" && \
    uv venv && \
    uv pip install . && \
    cp -a .venv /opt/venv

# Final runtime image: minimal image containing only runtime deps and the venv copied from builder
FROM python:3.14-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive

# Install SSH client and certificates (needed to connect to switches)
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the pre-built virtualenv from the builder stage
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}"

ARG VERSION=latest
LABEL version=$VERSION

WORKDIR /app

# Expose nothing by default; entrypoint is the CLI
ENTRYPOINT ["zyxel-cli"]
