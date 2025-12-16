# Use Python 3.11 as base image
FROM python:3.11-slim

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy entire Django project
COPY . /app/

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/mediafiles

# Create a non-root user for security
RUN useradd -m -u 1000 django && chown -R django:django /app

# Switch to non-root user
USER django

# Expose port 8000
EXPOSE 8000

# Copy and set permissions for entrypoint script
COPY --chown=django:django entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]