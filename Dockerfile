FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy tank libraries
COPY ../tank-lib /tmp/tank-lib
COPY ../tank-api /tmp/tank-api

# Install Python dependencies
RUN pip install --no-cache-dir /tmp/tank-lib /tmp/tank-api

# Copy application code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/ping')"

# Run application
CMD ["gunicorn", "wsgi:app", "-w", "4", "-b", "0.0.0.0:8000"]

