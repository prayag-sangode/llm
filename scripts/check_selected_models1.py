import requests
from datetime import datetime, timedelta
import pytz

def fetch_model_info(model_id):
    url = f"https://huggingface.co/api/models/{model_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('lastModified', 'Unknown')
        else:
            return None
    except Exception as e:
        return None

def main(days):
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

    print(f"Checking if models are modified in last {days} days...\n")
    cutoff_date = datetime.now(pytz.utc) - timedelta(days=days)

    for model_id in model_ids:
        last_modified_str = fetch_model_info(model_id)
        if last_modified_str:
            last_modified = datetime.fromisoformat(last_modified_str)
            if last_modified > cutoff_date:
                print(f"{model_id} | Last Modified: {last_modified}  Newer than {days} days")
            else:
                print(f"{model_id} | Last Modified: {last_modified}  Older than {days} days")
        else:
            print(f"{model_id} | ❓ Unable to fetch info")
