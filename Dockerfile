FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create a script to wait for MySQL
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
host="$1"\n\
shift\n\
cmd="$@"\n\
\n\
until nc -z "$host" 3306; do\n\
  >&2 echo "MySQL is unavailable - sleeping"\n\
  sleep 1\n\
done\n\
\n\
>&2 echo "MySQL is up - executing command"\n\
exec $cmd' > /usr/local/bin/wait-for-mysql.sh

RUN chmod +x /usr/local/bin/wait-for-mysql.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
