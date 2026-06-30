# ==========================================
# Stage 1: Build & Dependency Resolution
# ==========================================
FROM python:3.13-slim-bookworm AS builder

# Install uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:0.11.21 /uv /uvx /bin/

WORKDIR /app

# Install system build dependencies for FAISS and other compiled wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration and lockfiles for caching
COPY pyproject.toml uv.lock ./

# Mount cache for faster rebuilds and sync dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy agent application code
COPY app/ app/
COPY mcp_server/ mcp_server/
COPY main.py main.py

# ==========================================
# Stage 2: Runtime Environment
# ==========================================
FROM python:3.13-slim-bookworm AS runner

WORKDIR /app

# Copy the synced virtualenv and python sources from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app
COPY --from=builder /app/mcp_server /app/mcp_server
COPY --from=builder /app/main.py /app/main.py

# Install OpenMP (required for faiss-cpu operations)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set Path to point to the virtual environment binary directory
ENV PATH="/app/.venv/bin:$PATH"
ENV OUTPUT_DIR="/app/output"

# Run as non-root system user for container security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN mkdir -p /app/output && chown -R appuser:appgroup /app

USER appuser

# Document persistence and execution commands
VOLUME [ "/app/output" ]
ENTRYPOINT [ "python", "main.py" ]
