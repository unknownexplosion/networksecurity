# Use a supported Debian base
FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps: curl/unzip for AWS CLI; ca-certs for TLS; build tools only if needed
# If your requirements need wheels compiled (numpy/pandas/cryptography), leave build-essential & gcc.
# Otherwise you can remove them to keep the image smaller.
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
      unzip \
      ca-certificates \
      build-essential \
      gcc \
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
  /tmp/aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update; \
  aws --version; \
  rm -rf /tmp/aws /tmp/awscliv2.zip

# Upgrade pip (often fixes build failures for modern wheels)
RUN python -m pip install --upgrade pip

# Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install -r requirements.txt

# App code last so code changes don’t bust earlier caches
COPY . /app

# (Optional) non-root user
# RUN useradd -m -u 10001 app && chown -R app:app /app
# USER app

EXPOSE 8080
CMD ["python", "app.py"]
