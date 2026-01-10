# Use Python 3.12
FROM python:3.12

# Arguments for host UID/GID
ARG UID=1000
ARG GID=1000

# Create group and user with same UID/GID as the host
RUN groupadd -g $GID appuser && \
    useradd -m -u $UID -g appuser appuser

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Django code into the container
COPY . /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Gives permission to run script
RUN chmod +x /app/entrypoint.sh

# Switch to the non-root user
USER appuser

# Expose Django default port
EXPOSE 8000

# Default command: run Django development server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["./entrypoint.sh"]
