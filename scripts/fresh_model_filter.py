# fresh_model_filter.py
import sys
from datetime import datetime, timezone, timedelta
from huggingface_hub import list_models, model_info

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
CUTOFF = datetime.now(timezone.utc) - timedelta(days=DAYS)

def check_fresh_models(author, prefix=None):
    print(f"🔍 Checking {author}/{prefix or '*'}...")
    fresh = []
    for model in list_models(author=author):
        if prefix and not model.modelId.startswith(f"{author}/{prefix}"):
            continue
        try:
            info = model_info(model.modelId)
            modified = info.lastModified
            if modified and modified > CUTOFF:
                fresh.append((model.modelId, modified))
        except Exception:
            continue

    if fresh:
        for model_id, timestamp in fresh:
            print(f"✅ {model_id} | Last Modified: {timestamp}")
    else:
        print(f"❌ No fresh model variants found in the last {DAYS} days.\n")

# Example usage
check_fresh_models("mistralai", "Mistral-7B-Instruct")
check_fresh_models("meta-llama", "Llama-3-")
check_fresh_models("microsoft", "Phi-")
