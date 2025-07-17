import sys
import requests
from datetime import datetime, timedelta, timezone

# Number of days passed as argument
days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

# Selected models to track (match substrings)
selected_keywords = [
    "mistralai", "microsoft", "meta", "deepseek", "google", "cohere", "anthropic",
    "databricks", "together", "openchat", "nous", "intel", "qwen", "snowflake",
]

url = "https://huggingface.co/api/models?full=True&limit=10000"
print(f"Fetching latest models from Hugging Face… (cutoff: {cutoff_date.date()})")

try:
    response = requests.get(url)
    response.raise_for_status()
    models = response.json()
except Exception as e:
    print(f"Failed to fetch model list: {e}")
    sys.exit(1)

print(f"\n🔍 Showing models modified in the last {days} days:\n")

for model in models:
    model_id = model.get("modelId", "")
    last_modified = model.get("lastModified")

    if not last_modified:
        continue

    try:
        modified_date = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            modified_date = datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    # Check if model_id contains any selected keyword and was modified recently
    if any(kw.lower() in model_id.lower() for kw in selected_keywords):
        status = "🟢 UPDATED" if modified_date > cutoff_date else "⚪️ OLD"
        print(f"{status} — {model_id} — {modified_date.date()}")
