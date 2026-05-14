FROM python:3.11-slim

# Prevent Python buffering
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose container port
EXPOSE 8000

# Health Check
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# Run application using Gunicorn
CMD ["gunicorn", "--workers", "4", "--threads", "2", "--bind", "0.0.0.0:8000", "app:app"]
