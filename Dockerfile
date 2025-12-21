# Final runtime image: minimal image containing only runtime deps and the venv copied from builder
FROM python:3.14-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive

# Install SSH client and certificates (needed to connect to switches)
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the pre-built virtualenv from the builder image (builder image must be built and tagged as `zyxel-builder`)
COPY --from=zyxel-builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

# Expose nothing by default; entrypoint is the CLI
ENTRYPOINT ["zyxel-cli"]
