FROM python:3.10-slim-buster

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/

# Update package lists and install system dependencies
RUN apt-get update -y && \
    apt-get install -y awscli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Expose port if your app uses one (adjust as needed)
EXPOSE 8080

# Run the application
CMD ["python3", "app.py"]