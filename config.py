import os
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
VK_API_VERSION = "5.199"

DB_URL = "sqlite:///vk_posts.db"

# Hugging Face Inference API
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = "zai-org/GLM-5"  # Free, non-gated model
