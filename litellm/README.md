# Self-Hosted LLM Lab Using LiteLLM and Ollama

---

## Create project folder

```bash
mkdir -p ~/litellm-lab && cd ~/litellm-lab
```

## Create `Dockerfile` for LiteLLM

```bash
cat > Dockerfile << 'EOF'
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
EOF
```

---

## Create `config.yaml`

Example for Ollama backend:

```bash
cat > config.yaml << 'EOF'
model_list:
  - model_name: "llama2"
    litellm_params:
      model: "ollama/llama2"
      api_base: "http://ollama:11434"
  - model_name: "mistral"
    litellm_params:
      model: "ollama/mistral"
      api_base: "http://ollama:11434"
  - model_name: "falcon"
    litellm_params:
      model: "ollama/falcon"
      api_base: "http://ollama:11434"
EOF
```

---

##  Build custom Docker image

```bash
docker build -t litellm-amd64:latest .
```

* This ensures **AMD64 compatibility** because base image is Python AMD64.

---

## Update `docker-compose.yaml`

```bash
cat > docker-compose.yaml << 'EOF'
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"
    command: ["serve"]

  litellm:
    image: litellm-amd64:latest
    container_name: litellm
    restart: unless-stopped
    depends_on:
      - ollama
    ports:
      - "4000:4000"
    volumes:
      - ./config.yaml:/app/config.yaml

volumes:
  ollama_models:
EOF
```

---

## Start everything

```bash
docker compose up -d
```

* Ollama runs on port **11434**
* LiteLLM runs on port **4000**

---

## Pull models into Ollama

```bash
docker exec -it ollama ollama pull llama2
docker exec -it ollama ollama pull mistral
docker exec -it ollama ollama pull falcon
```

---

## Test LiteLLM

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [{"role": "user", "content": "Hello from custom LiteLLM image"}]
  }'
```

## Output for reference


Do you want me to do that?
