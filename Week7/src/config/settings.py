from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Project Root
BASE_DIR = Path(__file__).resolve().parents[2]

# Data Paths
DATA_DIR          = BASE_DIR / "src" / "data"
RAW_DATA_PATH     = DATA_DIR / "raw"
CHUNK_OUTPUT_PATH = DATA_DIR / "chunks"
IMAGES_DIR        = DATA_DIR / "images"

# Vectorstore
VECTORSTORE_PATH  = BASE_DIR / "src" / "vectorstore"
IMAGE_INDEX_FILE  = VECTORSTORE_PATH / "image_index.json"
IMAGE_FAISS_INDEX = VECTORSTORE_PATH / "image.index"

# Logs
LOGS_PATH = BASE_DIR / "src" / "logs"

# Chunking
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 150

# Retrieval
TOP_K = 5

# Image pipeline
IMG_EXTS       = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
CLIP_MODEL     = "openai/clip-vit-base-patch32"
BLIP_MODEL     = "Salesforce/blip-image-captioning-base"

# Embedding fusion weights
IMAGE_WEIGHT = 0.5
TEXT_WEIGHT  = 0.5

# Gemini
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL   = "gemini-2.5-flash"
GEMINI_MODEL_SQL = "gemini-2.5-flash"
DB_DIR = BASE_DIR / "src" / "data" / "db"

# Redis
REDIS_HOST           = "localhost"
REDIS_PORT           = 6379
REDIS_DB             = 0
MEMORY_MAX_MESSAGES  = 10   

# Evaluation
HALLUCINATION_THRESHOLD = 0.4   # confidence below this → hallucination flagged
CHAT_LOGS_PATH          = BASE_DIR / "CHAT-LOGS.json"
