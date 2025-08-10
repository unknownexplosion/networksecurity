FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update -y && \
    apt-get install -y curl unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir awscli && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p final_model prediction_output networksecurity/templates && \
    echo '<html><head><title>Network Security Results</title></head><body><h1>Prediction Results</h1>{{ table|safe }}</body></html>' > networksecurity/templates/table.html

EXPOSE 8000

CMD ["python3", "app.py"]