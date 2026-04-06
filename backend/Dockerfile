# ─────────────────────────────────────────────────────────────────
# Backend Dockerfile
# Builds the Django application container
# ─────────────────────────────────────────────────────────────────

# Use official Python 3.11 slim image (smaller than full image)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1    
# Prevents Python from writing .pyc files (cleaner)
ENV PYTHONUNBUFFERED=1          
# Ensures logs appear immediately (important for Docker)

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (Docker layer caching optimization)
# If requirements.txt hasn't changed, Docker skips this step
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Collect static files for production
RUN python manage.py collectstatic --noinput || true

# Expose port 8000 for Django
EXPOSE 8000

# Start Daphne (ASGI server — handles both HTTP and WebSocket)
# Daphne replaces Gunicorn when using Django Channels
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "mental_health_project.asgi:application"]
