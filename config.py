import os
import unicodedata
from typing import List
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

# Exactly the 7 regional dialects the model was trained on
VALID_REGIONS: List[str] = [
    "Pabna",
    "Noakhali",
    "Jashore",
    "Rangpur",
    "Mymensingh",
    "Barishal",
    "Chittagong",
]

# Exact decoding settings required by the fine-tuned model (Section 6 of requirements)
MAX_SOURCE_LEN: int = 40
MAX_TARGET_LEN: int = 32
NUM_BEAMS: int = 4
LENGTH_PENALTY: float = 1.0
EARLY_STOPPING: bool = True

DEFAULT_HF_REPO_ID: str = os.getenv("HF_REPO_ID", "your-username/banglat5-dialect-to-standard")
DEFAULT_HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")

def normalize_bengali_text(text: str) -> str:
    """Apply Unicode NFC normalization and clean invisible characters."""
    if not text:
        return ""
    # NFC normalization for Bengali glyph consistency
    normalized = unicodedata.normalize("NFC", text)
    # Remove zero-width characters (ZWNJ, ZWJ, etc. that can corrupt tokenization)
    cleaned = "".join(ch for ch in normalized if ch not in ["\u200B", "\u200C", "\u200D", "\uFEFF"])
    return " ".join(cleaned.strip().split())

def format_model_input(region: str, sentence: str) -> str:
    """
    CRITICAL: The model was fine-tuned expecting input text in this exact format:
    translate {region} to Bangla: {dialect_sentence}
    """
    cleaned_sentence = normalize_bengali_text(sentence)
    return f"translate {region} to Bangla: {cleaned_sentence}"
