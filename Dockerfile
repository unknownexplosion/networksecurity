FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install system dependencies and Python packages
RUN apt-get update -y && \
    apt-get install -y curl unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir awscli && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Create necessary directories and template
RUN mkdir -p final_model prediction_output networksecurity/templates && \
    echo '<html><head><title>Network Security Results</title><style>body{font-family:Arial,sans-serif;margin:40px;}.table{border-collapse:collapse;width:100%;}.table th,.table td{border:1px solid #ddd;padding:8px;text-align:left;}.table th{background-color:#f2f2f2;}</style></head><body><h1>Network Security Prediction Results</h1>{{ table|safe }}</body></html>' > networksecurity/templates/table.html

# Expose the correct port
EXPOSE 8000

# Run the application
CMD ["python3", "app.py"]