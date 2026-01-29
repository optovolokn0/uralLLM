import os
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
VK_API_VERSION = "5.199"

DB_URL = "sqlite:///vk_posts.db"

# Ollama configuration
OLLAMA_MODEL = "mistral"
