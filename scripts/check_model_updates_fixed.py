import sys
import datetime
import time
from huggingface_hub import HfApi

def is_recent(date_str, days):
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        return (now - dt).days <= days
    except Exception:
        return False

def main(days):
    authors = ["mistralai", "meta-llama", "microsoft", "google", "tiiuae", "openchat", "Phind"]
    api = HfApi()

    for author in authors:
        print(f"\n Fetching models for author: {author}")
        try:
            models = api.list_models(author=author)
        except Exception as e:
            print(f" Failed to fetch models for {author}: {e}")
            continue

        recent_models = []
        for model in models:
            last_modified = model.lastModified or model.created_at
            if not last_modified:
                continue
            dt = datetime.datetime.fromisoformat(str(last_modified))
            age = (datetime.datetime.now(datetime.timezone.utc) - dt).days
            if age <= days:
                recent_models.append((model.modelId, dt.strftime("%Y-%m-%d %H:%M:%S")))

            time.sleep(0.25)  # avoid rate limits

        if recent_models:
            for model_id, mod_time in sorted(recent_models, key=lambda x: x[1], reverse=True):
                print(f" {model_id} | Last Modified: {mod_time}")
        else:
            print(" No recent models found.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_recent_models.py <days>")
        sys.exit(1)

    try:
        days_arg = int(sys.argv[1])
    except ValueError:
        print("Invalid number of days.")
        sys.exit(1)

    main(days_arg)
(llmbench-env) prayag@vllm-auto-benchmarking:~/misc$ ls
check_model_updates_fixed.py  check_selected_model_updates.py  debug_list_all_models.py  requirements.txt          venv
check_recent_models.py        check_selected_models1.py        fresh_model_filter.py     selected_models_check.py
(llmbench-env) prayag@vllm-auto-benchmarking:~/misc$ cat check_model_updates_fixed.py
import sys
import requests
from datetime import datetime, timedelta

# Curated and corrected model list from Hugging Face
model_ids = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "meta-llama/Meta-Llama-3-70B-Instruct",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "Qwen/Qwen1.5-32B",
    "Qwen/Qwen1.5-72B-Chat",
    "Qwen/Qwen2-72B-Instruct",
    "Qwen/Qwen2.5-72B-Instruct",
    "Qwen/Qwen2.5-32B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "deepseek-ai/deepseek-coder-33b-instruct",
    "deepseek-ai/deepseek-llm-67b-chat",
    "Teuken/Teuken-7B-Instruct-v0.1",
    "jina-ai/jina-embeddings-v2-base-en",
    "jina-ai/jina-embeddings-v2-base-code",
    "BAAI/bge-m3",
    "Alibaba-NLP/bce-reranker-base_v1"
]

# CLI argument for number of days
if len(sys.argv) != 2:
    print("Usage: python3 check_model_updates_fixed.py <N_days>")
    sys.exit(1)

try:
    n_days = int(sys.argv[1])
except ValueError:
    print("Invalid number of days")
    sys.exit(1)

cutoff_date = datetime.utcnow() - timedelta(days=n_days)

print(f"✅ Models updated in the last {n_days} days:\n")

# Check each model's last modified date
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
            print(f"- ❌ Failed to fetch {model_id}: Status {response.status_code}")
    except Exception as e:
        print(f"- ❌ Error checking {model_id}: {e}")
