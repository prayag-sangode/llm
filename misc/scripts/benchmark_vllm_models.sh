#!/bin/bash

# List of HuggingFace model IDs to benchmark
MODELS=(
  "NousResearch/Hermes-3-Llama-3.1-8B"
  "facebook/opt-1.3b"
  "mistralai/Mistral-7B-Instruct-v0.2"
)

# Benchmark settings
NUM_PROMPTS=10
DATASET_URL="https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json"
DATASET_FILE="ShareGPT_V3_unfiltered_cleaned_split.json"
HOST_CACHE="$HOME/.cache/huggingface"
BENCHMARK_SCRIPT="benchmark_serving.py"

# Pull latest vLLM OpenAI Docker image
docker pull vllm/vllm-openai:latest

# Clone vLLM repo if not already present
if [ ! -d "vllm" ]; then
  git clone https://github.com/vllm-project/vllm.git
fi

# Download dataset if not exists
if [ ! -f "$DATASET_FILE" ]; then
  wget -O "$DATASET_FILE" "$DATASET_URL"
fi

# Start benchmark for each model
PORT_BASE=8000
i=0
for MODEL in "${MODELS[@]}"; do
  PORT=$((PORT_BASE + i))
  CONTAINER_NAME="vllm-$(echo $MODEL | tr '/' '-' | tr ':' '-')"

  echo "Starting container for $MODEL on port $PORT..."

  docker run -d --rm --runtime=nvidia --gpus all \
    -v "$HOST_CACHE:/root/.cache/huggingface" \
    -v "$(pwd):/app" \
    -p "$PORT:8000" \
    --ipc=host \
    --name "$CONTAINER_NAME" \
    vllm/vllm-openai:latest \
    --model "$MODEL"

  echo "Waiting for model to load..."
  until curl -s "http://localhost:$PORT/v1/models" >/dev/null; do
    sleep 5
  done

  echo "Model $MODEL is ready. Benchmarking..."

  docker exec -it "$CONTAINER_NAME" bash -c "
  pip install -q datasets pandas &&
  python3 /vllm-workspace/benchmarks/benchmark_serving.py \
    --backend vllm \
    --model \"$MODEL\" \
    --endpoint /v1/completions \
    --dataset-name sharegpt \
    --dataset-path /app/$DATASET_FILE \
    --num-prompts $NUM_PROMPTS > /app/benchmark_${CONTAINER_NAME}.log
"
  echo "Benchmark for $MODEL complete. Logs: benchmark_${CONTAINER_NAME}.log"

  docker stop "$CONTAINER_NAME"
  ((i++))
done

echo "All benchmarks completed."
