import logging
import os

from huggingface_hub import hf_hub_download

from ..config import IMAGE_CONFIG

logger = logging.getLogger(__name__)


class HFDownloader:
    def __init__(
        self,
        repo_id: str = IMAGE_CONFIG.HF_REPO_ID,
        base_dir: str = IMAGE_CONFIG.HF_MODEL_DIR,
    ):
        self.repo_id = repo_id
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def download_model(self, model_file_name: str) -> str:
        logger.info("Model %s not found locally. Downloading from Hugging Face Hub...", model_file_name)
        path = hf_hub_download(
            repo_id=self.repo_id,
            filename=model_file_name,
            local_dir=self.base_dir,
        )
        return path
