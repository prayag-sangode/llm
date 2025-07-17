import sys
import requests
from datetime import datetime, timedelta

model_ids = [
    "mistralai/Mistral-Small-3.1-24B-Instruct-2503",
    "meta-llama/Llama-3.3-70B-Instruct",
    "Qwen/Qwen3-30B-A3B",
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Teuken/Teuken-7B-Instruct",
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B-Swiss",
    "Qwen/Qwen2.5-Coder-7B-Instruct-Swiss",
    "mistralai/Mistral-Nemo-Instruct-2407-Swiss",
    "Qwen/Qwen2-VL-7B-Instruct-Swiss",
    "jina-ai/Jina-Embeddings-V2-Base-de",
    "jina-ai/Jina-Embeddings-V2-Base-code",
    "BAAI/bge-m3",
    "Alibaba-NLP/bce-reranker-base_v1"
]

if len(sys.argv) != 2:
    print("Usage: python3 check_selected_model_updates.py <N_days>")
    sys.exit(1)

try:
    n_days = int(sys.argv[1])
except ValueError:
    print("Invalid number of days")
    sys.exit(1)

cutoff_date = datetime.utcnow() - timedelta(days=n_days)

print(f"Models updated in the last {n_days} days:\n")

for model_id in model_ids:
    url = f"https://huggingface.co/api/models/{model_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            last_modified = datetime.strptime(data.get("lastModified"), "%Y-%m-%dT%H:%M:%S.%fZ")
            if last_modified > cutoff_date:
                print(f"- {model_id} (Last updated: {last_modified.strftime('%Y-%m-%d %H:%M:%S')} UTC)")
        else:
            print(f"- Failed to fetch {model_id}: Status {response.status_code}")
    except Exception as e:
        print(f"- Error checking {model_id}: {e}")
(llmbench-env) prayag@vllm-auto-benchmarking:~/misc$ cat check_selected_model_updates.py
import sys
import requests
from datetime import datetime, timedelta

model_ids = [
    "mistralai/Mistral-Small-3.1-24B-Instruct-2503",
    "meta-llama/Llama-3.3-70B-Instruct",
    "Qwen/Qwen3-30B-A3B",
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Teuken/Teuken-7B-Instruct",
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B-Swiss",
    "Qwen/Qwen2.5-Coder-7B-Instruct-Swiss",
    "mistralai/Mistral-Nemo-Instruct-2407-Swiss",
    "Qwen/Qwen2-VL-7B-Instruct-Swiss",
    "jina-ai/Jina-Embeddings-V2-Base-de",
    "jina-ai/Jina-Embeddings-V2-Base-code",
    "BAAI/bge-m3",
    "Alibaba-NLP/bce-reranker-base_v1"
]

if len(sys.argv) != 2:
    print("Usage: python3 check_selected_model_updates.py <N_days>")
    sys.exit(1)

try:
    n_days = int(sys.argv[1])
except ValueError:
    print("Invalid number of days")
    sys.exit(1)

cutoff_date = datetime.utcnow() - timedelta(days=n_days)

print(f"Models updated in the last {n_days} days:\n")

for model_id in model_ids:
    url = f"https://huggingface.co/api/models/{model_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            last_modified = datetime.strptime(data.get("lastModified"), "%Y-%m-%dT%H:%M:%S.%fZ")
            if last_modified > cutoff_date:
                print(f"- {model_id} (Last updated: {last_modified.strftime('%Y-%m-%d %H:%M:%S')} UTC)")
        else:
            print(f"- Failed to fetch {model_id}: Status {response.status_code}")
    except Exception as e:
        print(f"- Error checking {model_id}: {e}")
