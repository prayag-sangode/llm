#!/bin/bash

# List of HuggingFace model IDs to benchmark
MODELS=(
  #"facebook/opt-1.3b"
  #"NousResearch/Hermes-3-Llama-3.1-8B"
  #"openGPT-X/Teuken-7B-instruct-research-v0.4"
  "mistralai/Mistral-7B-Instruct-v0.2"
  "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
  "Qwen/Qwen3-30B-A3B-FP8"
  "Qwen/Qwen2.5-Coder-32B-Instruct"
  #"mistralai/Mistral-Small-24B-Instruct-2501"
  #"mistralai/Mixtral-8x7B-Instruct-v0.1"
  #"deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
  #"meta-llama/Llama-3.3-70B-Instruct"
  #"Qwen/Qwen2.5-VL-72B-Instruct"
)

# Benchmark settings
NUM_PROMPTS=10
DATASET_URL="https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json"
DATASET_FILE="ShareGPT_V3_unfiltered_cleaned_split.json"
HOST_CACHE="$HOME/.cache/huggingface"
VLLM_VERSION="v0.9.2"
DATE=$(date +'%d%m%Y%H%M%S')

# Pull vLLM Docker image
docker pull vllm/vllm-openai:$VLLM_VERSION

# Clone vLLM repo if not present
if [ ! -d "vllm" ]; then
  git clone https://github.com/vllm-project/vllm.git
fi

# Download dataset if not exists
if [ ! -f "$DATASET_FILE" ]; then
  wget -O "$DATASET_FILE" "$DATASET_URL"
fi

# Stop any running container on VM
if [ -n "$(docker ps -q)" ]; then
  docker stop $(docker ps -q)
else
  echo "No running containers to stop."
fi

# Ensure mlflow is installed
pip install -q mlflow pandas

# Base port
PORT_BASE=8000
i=0

for MODEL in "${MODELS[@]}"; do
  PORT=$((PORT_BASE + i))
  CONTAINER_NAME="vllm-$(echo $MODEL | tr '/' '-' | tr ':' '-')"

  echo "Launching model $MODEL on port $PORT..."

  #docker run -d --rm --runtime=nvidia --gpus all \
  #  -v "$HOST_CACHE:/root/.cache/huggingface" \
  #  -v "$(pwd):/app" \
  #  -p "$PORT:8000" \
  #  --ipc=host \
  #  --name "$CONTAINER_NAME" \
  #  vllm/vllm-openai:$VLLM_VERSION \
  #  --model "$MODEL"

  docker run -d --rm --runtime=nvidia --gpus all \
     -v "$HOST_CACHE:/root/.cache/huggingface" \
     -v "$(pwd):/app" \
     -p "$PORT:8000" \
     --ipc=host \
     --name "$CONTAINER_NAME" \
     vllm/vllm-openai:$VLLM_VERSION \
     --model "$MODEL" \
     --trust-remote-code

  echo "Waiting for model to be ready..."
  until curl -s "http://localhost:$PORT/v1/models" >/dev/null; do
    sleep 5
  done

  echo "Model is ready. Starting benchmark..."

  docker exec -i "$CONTAINER_NAME" bash -c "
    pip install -q datasets pandas &&
    python3 /vllm-workspace/benchmarks/benchmark_serving.py \
      --backend vllm \
      --model \"$MODEL\" \
      --trust-remote-code \
      --endpoint /v1/completions \
      --dataset-name sharegpt \
      --dataset-path /app/$DATASET_FILE \
      --num-prompts $NUM_PROMPTS > /app/benchmark_${CONTAINER_NAME}.log
  "

  LOG_FILE="benchmark_${CONTAINER_NAME}.log"
  echo "Benchmark complete. Extracting metrics from: $LOG_FILE"

  # Extract throughput and latency
  LATENCY=$(grep "Median TTFT" "$LOG_FILE" | awk '{print $NF}')
  THROUGHPUT=$(grep "Total Token throughput" "$LOG_FILE" | awk '{print $NF}')
  REQUEST_THROUGHPUT=$(grep "Request throughput" "$LOG_FILE" | awk '{print $NF}')
  OUTPUT_TOKEN_THROUGHPUT=$(grep "Output token throughput" "$LOG_FILE" | awk '{print $NF}')
  MEAN_TTFT=$(grep "Mean TTFT" "$LOG_FILE" | awk '{print $NF}')
  P99_TTFT=$(grep "P99 TTFT" "$LOG_FILE" | awk '{print $NF}')
  MEAN_TPOT=$(grep "Mean TPOT" "$LOG_FILE" | awk '{print $NF}')
  P99_TPOT=$(grep "P99 TPOT" "$LOG_FILE" | awk '{print $NF}')
  MEAN_ITL=$(grep "Mean ITL" "$LOG_FILE" | awk '{print $NF}')
  P99_ITL=$(grep "P99 ITL" "$LOG_FILE" | awk '{print $NF}')

  echo "======== Parsed Metrics ========"
  echo "Model                     : $MODEL"
  echo "vLLM Version              : $VLLM_VERSION"
  echo "Port                      : $PORT"
  echo "Latency (Median TTFT, ms): ${LATENCY:-Not Found}"
  echo "Throughput (Total Token) : ${THROUGHPUT:-Not Found}"
  echo "Request Throughput        : ${REQUEST_THROUGHPUT:-Not Found}"
  echo "Output Token Throughput   : ${OUTPUT_TOKEN_THROUGHPUT:-Not Found}"
  echo "Mean TTFT (ms)            : ${MEAN_TTFT:-Not Found}"
  echo "P99 TTFT (ms)             : ${P99_TTFT:-Not Found}"
  echo "Mean TPOT (ms)            : ${MEAN_TPOT:-Not Found}"
  echo "P99 TPOT (ms)             : ${P99_TPOT:-Not Found}"
  echo "Mean ITL (ms)             : ${MEAN_ITL:-Not Found}"
  echo "P99 ITL (ms)              : ${P99_ITL:-Not Found}"
  echo "================================"


  # Log to MLflow
python3 <<EOF
import mlflow

mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("vLLM Benchmarks-${VLLM_VERSION}-${DATE}")

latency = float("${LATENCY:-1}")
throughput = float("${THROUGHPUT:-1}")
latency_p99 = float("${P99_TTFT:-1}")
tpot_p50 = float("${MEAN_TPOT:-1}")
tpot_p99 = float("${P99_TPOT:-1}")
itl_p50 = float("${MEAN_ITL:-1}")
itl_p99 = float("${P99_ITL:-1}")
req_throughput = float("${REQUEST_THROUGHPUT:-1}")
output_throughput = float("${OUTPUT_TOKEN_THROUGHPUT:-1}")
total_generated_tokens = throughput * ${NUM_PROMPTS}

with mlflow.start_run(run_name="${MODEL}"):
    mlflow.log_param("model", "${MODEL}")
    mlflow.log_param("vllm_version", "${VLLM_VERSION}")
    mlflow.log_param("port", "${PORT}")
    mlflow.log_param("num_prompts", ${NUM_PROMPTS})

    mlflow.log_metric("latency_p50", latency)
    mlflow.log_metric("throughput", throughput)
    mlflow.log_metric("latency_p99", latency_p99)
    mlflow.log_metric("tpot_p50", tpot_p50)
    mlflow.log_metric("tpot_p99", tpot_p99)
    mlflow.log_metric("itl_p50", itl_p50)
    mlflow.log_metric("itl_p99", itl_p99)
    mlflow.log_metric("req_throughput", req_throughput)
    mlflow.log_metric("output_token_throughput", output_throughput)
    mlflow.log_metric("total_generated_tokens", total_generated_tokens)

    mlflow.log_artifact("${LOG_FILE}")
EOF

  docker stop "$CONTAINER_NAME"
  ((i++))
done

echo "All benchmarks and MLflow logging completed."

# Check via mlflow
mlflow ui --host 0.0.0.0 --port 5000
