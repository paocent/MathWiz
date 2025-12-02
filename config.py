# config.py
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DATA_DIR = os.path.join(BASE_DIR, "data")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
VECTOR_DIR = os.path.join(DATA_DIR, "vector_store")
DB_PATH = os.path.join(DATA_DIR, "math_agent.db")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
EMBED_DIM = int(os.getenv("EMBED_DIM", 128))
TOP_K = int(os.getenv("TOP_K", 4))
SOLVER_CONF_THRESH = float(os.getenv("SOLVER_CONF_THRESH", 0.75))

# LLM provider keys (optional)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE = os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_BASE = os.getenv("MISTRAL_BASE", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
