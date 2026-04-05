import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "quantized", "model_q8_0.gguf")


CONTEXT_WINDOW = 2048
MAX_NEW_TOKENS = 768

TEMPERATURE = 0.7
TOP_P = 0.9
TOP_K = 40

CHAT_HISTORY_LIMIT = 1500