# list_models_by_author.py
from huggingface_hub import list_models, model_info
from huggingface_hub.utils import HfHubHTTPError

authors = [
    "mistralai",
    "meta-llama",
    "Qwen",
    "Teuken",
    "deepseek-ai",
    "jina-ai",
    "BAAI",
    "Alibaba-NLP"
]

for author in authors:
    print(f"Fetching models for author: {author}")
    models = list_models(author=author)
    for model in models:
        model_id = model.modelId
        try:
            info = model_info(model_id)
            last_modified = info.lastModified or "Unknown"
        except HfHubHTTPError:
            last_modified = "Unavailable"
        print(f"{model_id} | Last Modified: {last_modified}")
    print()
