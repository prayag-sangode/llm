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
