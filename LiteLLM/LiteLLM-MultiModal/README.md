# **LiteLLM Multi-Model Management Lab (Local)**

## ** Create Project Folder**

```bash
mkdir -p ~/litellm-multimodel && cd ~/litellm-multimodel
```

## ** Create `Dockerfile` for LiteLLM**

```bash
cat > Dockerfile << 'EOF'
# Python 3.11 slim base
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Copy config
COPY config.yaml /app/config.yaml

# Install LiteLLM proxy dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "litellm[proxy]"

# Expose LiteLLM port
EXPOSE 4000

# Start LiteLLM proxy
CMD ["litellm", "--config", "/app/config.yaml", "--port", "4000"]
EOF
```

## ** Create `config.yaml` with multiple models**

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

# Local-only guardrails (optional, rate-limit example)
guardrails: []
EOF
```

>  This config defines **three models** available via LiteLLM. No API keys needed; all local.


## ** Create `docker-compose.yaml`**

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
    build: .
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

## ** Build LiteLLM Image**

```bash
docker compose build
```

## ** Start Ollama + LiteLLM**

```bash
docker compose up -d
```

* Ollama runs on port **11434**
* LiteLLM runs on port **4000**

## ** Pull Models into Ollama**

```bash
docker exec -it ollama ollama pull llama2
docker exec -it ollama ollama pull mistral
docker exec -it ollama ollama pull falcon
```

>  Wait for each pull to finish.

## ** Test Multi-Model API**

### **Query `llama2`**

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2",
    "messages": [{"role": "user", "content": "Hello from LLaMA2"}]
  }'
```

### **Query `mistral`**

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "messages": [{"role": "user", "content": "Hello from Mistral"}]
  }'
```

### **Query `falcon`**

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "falcon",
    "messages": [{"role": "user", "content": "Hello from Falcon"}]
  }'
```

## ** Check Multi-Model Behavior**

1. Send **different prompts** to each model.
2. Observe **latency** and **response style differences**.
3. Optionally, measure **tokens used** for each call.


## ** Optional: Test Multiple Requests**

```bash
for i in {1..5}; do
  curl -s http://localhost:4000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
      "model": "llama2",
      "messages": [{"role": "user", "content": "Test message '$i'"}]
    }' & 
done
wait
```
>  Checks concurrency handling by LiteLLM
