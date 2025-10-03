FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for MySQL and UV
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Copy UV configuration files
COPY pyproject.toml uv.lock ./

# Install Python dependencies using UV
RUN uv sync --frozen

# Copy application code
COPY . .

# Copy and setup entrypoint and health check scripts
COPY docker-entrypoint.sh /usr/local/bin/
COPY health_check.py /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/health_check.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app \
    && mkdir -p /app/logs \
    && chown -R app:app /app/logs

# Create migrations directory and copy migration files
RUN mkdir -p /app/database/migrations
COPY ../database/migrations/ /app/database/migrations/
RUN chown -R app:app /app/database

USER app

# Health check with migration verification
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python /usr/local/bin/health_check.py || exit 1

EXPOSE 8000

# Set entrypoint and default command
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]