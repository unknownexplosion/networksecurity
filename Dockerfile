FROM python:3.10-slim-buster
WORKDIR /app
COPY . /app

RUN apt-get update -y && apt-get install -y \
    curl \
    unzip \
    && pip install awscli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt
CMD ["python3", "app.py"]