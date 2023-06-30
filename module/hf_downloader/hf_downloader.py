from huggingface_hub import hf_hub_url, cached_download
import os

from ..config import IMAGE_CONFIG

class HFDownloader:
    def __init__(self, repo_id=IMAGE_CONFIG['HF_REPO_ID'], base_dir=IMAGE_CONFIG['HF_MODEL_DIR']):
        self.repo_id = repo_id
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)

    def download_model(self, model_file_name):
        print(f"Model {model_file_name} not found locally. Downloading from Hugging Face Hub...")
        model_url = hf_hub_url(repo_id=self.repo_id, filename=model_file_name)
        cached_download(url=model_url, cache_dir=self.base_dir, force_filename=model_file_name)

        # Remove the lock file if it exists
        lock_file = os.path.join(self.base_dir, f'{model_file_name}.lock')
        if os.path.exists(lock_file):
            os.remove(lock_file)
