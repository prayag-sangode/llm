# Use official Python AMD64 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy config file
COPY config.yaml /app/config.yaml

# Install LiteLLM + proxy dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "litellm[proxy]"

# Expose LiteLLM port
EXPOSE 4000

# Run LiteLLM with config
CMD ["litellm", "--config", "/app/config.yaml", "--port", "4000"]
