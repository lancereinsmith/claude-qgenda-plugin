FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev group)
RUN uv sync --no-dev --frozen

# Copy application code
COPY qgenda_core.py server.py ./

# MCP server port (configurable via MCP_PORT env var)
ENV MCP_PORT=8000
EXPOSE ${MCP_PORT}

# Run the MCP server with SSE transport
CMD uv run python server.py --transport sse --port "${MCP_PORT}"
