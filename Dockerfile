FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 1. Create user
RUN groupadd -g 1000 django && useradd -m -u 1000 -g django django

WORKDIR /app

RUN chown django:django /app

ENV HOME=/home/django
ENV UV_CACHE_DIR=/home/django/.cache/uv
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./
RUN chown django:django pyproject.toml uv.lock

USER django
RUN --mount=type=cache,target=/home/django/.cache/uv,uid=1000,gid=1000 \
    uv sync --frozen --no-install-project

USER root
COPY . .
RUN chown -R django:django /app

USER django

EXPOSE 8000
CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]