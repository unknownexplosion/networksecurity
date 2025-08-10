# Use a supported Debian base
FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (curl/unzip for AWS CLI installer; ca-certs for HTTPS)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
      unzip \
      ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# --- Install AWS CLI v2 (multi-arch: amd64 & arm64) ---
RUN set -eux; \
  arch="$(dpkg --print-architecture)"; \
  case "$arch" in \
    amd64)  aws_arch="x86_64" ;; \
    arm64)  aws_arch="aarch64" ;; \
    *) echo "Unsupported arch: $arch"; exit 1 ;; \
  esac; \
  curl -sSL "https://awscli.amazonaws.com/awscli-exe-linux-${aws_arch}.zip" -o /tmp/awscliv2.zip; \
  unzip -q /tmp/awscliv2.zip -d /tmp; \
  /tmp/aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli; \
  rm -rf /tmp/aws /tmp/awscliv2.zip

# Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code last so code changes don’t bust earlier caches
COPY . /app

# (Optional) non-root user
# RUN useradd -m app && chown -R app:app /app
# USER app

CMD ["python", "app.py"]
