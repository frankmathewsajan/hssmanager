FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 2026 Best Practice: Don't run as root
RUN groupadd -r django && useradd -r -g django django

WORKDIR /app

# Enable bytecode compilation for speed
ENV UV_COMPILE_BYTECODE=1
# Ensure uv uses the .venv in the project root
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

COPY pyproject.toml uv.lock ./

# Mount the cache to speed up subsequent builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY . .

# Fix permissions
RUN chown -R django:django /app
USER django

EXPOSE 8000
CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]