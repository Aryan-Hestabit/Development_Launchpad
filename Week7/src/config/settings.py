from pathlib import Path


# Project Root
BASE_DIR = Path(__file__).resolve().parents[2]

# Data Paths
DATA_DIR = BASE_DIR / "src" / "data"
RAW_DATA_PATH = DATA_DIR / "raw"
CHUNK_OUTPUT_PATH = DATA_DIR / "chunks"

# Vectorstore
VECTORSTORE_PATH = BASE_DIR / "src" / "vectorstore"

# Logs
LOGS_PATH = BASE_DIR / "src" / "logs"

# Chunking
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

# Retrieval
TOP_K = 5