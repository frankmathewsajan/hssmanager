# Use a slim Python image
FROM python:3.12-slim

# Install uv directly from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Install dependencies without installing the project itself
RUN uv sync --frozen --no-install-project

# Copy the rest of the code
COPY . .

# Expose Django's port
EXPOSE 8000

# Run the server (Binding to 0.0.0.0 is critical for Docker)
CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]