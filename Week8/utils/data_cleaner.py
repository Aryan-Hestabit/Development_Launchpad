"""
data_cleaner.py
---------------
Healthcare Instruction Tuning Dataset Cleaner
Loads raw HuggingFace datasets, maps them to the unified JSONL format,
removes outliers, and saves train/val splits.

Format:
    {"instruction": "...", "input": "...", "output": "..."}
"""

import json
import re
import os
from collections import Counter


# ── Token length estimator (no tokenizer needed at this stage) ──────────────
def estimate_tokens(text: str) -> int:
    """Rough token count: ~1 token per 4 characters (GPT-style heuristic)."""
    return max(1, len(text) // 4)


# ── Text normalisation ───────────────────────────────────────────────────────
def normalise(text: str) -> str:
    """Strip HTML tags, collapse whitespace, fix common encoding artifacts."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    return text


# ── Per-sample validation ────────────────────────────────────────────────────
def is_valid(sample: dict,
             min_output_tokens: int = 10,
             max_output_tokens: int = 512,
             max_instruction_tokens: int = 256,
             skip_text_check: bool = False) -> tuple:
    """
    Returns (True, "") if sample passes all checks,
    otherwise (False, reason_string).

    Parameters
    ----------
    skip_text_check : bool
        If True, skips the alphabetic character count check.
        Use for QA datasets where outputs may be short but valid.
    """
    instruction = sample.get("instruction", "")
    output      = sample.get("output", "")

    if not instruction or not output:
        return False, "empty_field"

    out_tokens  = estimate_tokens(output)
    inst_tokens = estimate_tokens(instruction)

    if out_tokens < min_output_tokens:
        return False, "output_too_short"
    if out_tokens > max_output_tokens:
        return False, "output_too_long"
    if inst_tokens > max_instruction_tokens:
        return False, "instruction_too_long"

    if not skip_text_check:
        if len(re.sub(r"[^a-zA-Z]", "", output)) < 20:
            return False, "output_not_text"

    return True, ""


# ── Deduplication ────────────────────────────────────────────────────────────
def deduplicate(samples: list) -> list:
    """Remove exact-duplicate (instruction, output) pairs."""
    seen = set()
    unique = []
    for s in samples:
        key = (s["instruction"].lower(), s["output"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


# ── Main cleaning pipeline ───────────────────────────────────────────────────
def clean_dataset(raw_samples: list,
                  min_output_tokens: int = 10,
                  max_output_tokens: int = 512,
                  max_instruction_tokens: int = 256,
                  skip_text_check: bool = False) -> tuple:
    """
    Cleans raw samples.

    Parameters
    ----------
    raw_samples            : list of dicts with keys instruction / input / output
    min_output_tokens      : lower bound for output length (default 10)
    max_output_tokens      : upper bound for output length (default 512)
    max_instruction_tokens : upper bound for instruction length (default 256)
    skip_text_check        : skip alphabetic content check (True for QA datasets)

    Returns
    -------
    (cleaned_samples, stats_dict)
    """
    stats = Counter()
    cleaned = []

    for sample in raw_samples:
        sample = {
            "instruction": normalise(sample.get("instruction", "")),
            "input":       normalise(sample.get("input", "")),
            "output":      normalise(sample.get("output", "")),
        }

        valid, reason = is_valid(
            sample,
            min_output_tokens,
            max_output_tokens,
            max_instruction_tokens,
            skip_text_check
        )

        if valid:
            cleaned.append(sample)
            stats["passed"] += 1
        else:
            stats[f"removed_{reason}"] += 1

    before_dedup = len(cleaned)
    cleaned = deduplicate(cleaned)
    stats["removed_duplicate"] = before_dedup - len(cleaned)

    return cleaned, dict(stats)


# ── Train / Val split ────────────────────────────────────────────────────────
def split_dataset(samples: list,
                  val_ratio: float = 0.1,
                  seed: int = 42) -> tuple:
    """Deterministic shuffle then split."""
    import random
    random.seed(seed)
    shuffled = samples[:]
    random.shuffle(shuffled)
    split_idx = int(len(shuffled) * (1 - val_ratio))
    return shuffled[:split_idx], shuffled[split_idx:]


# ── JSONL I/O ────────────────────────────────────────────────────────────────
def save_jsonl(samples: list, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"  Saved {len(samples):,} samples → {path}")


def load_jsonl(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ── Token-length statistics helper ──────────────────────────────────────────
def token_length_stats(samples: list) -> dict:
    """Return mean / min / max / p95 token lengths for output field."""
    import statistics
    lengths = [estimate_tokens(s["output"]) for s in samples]
    lengths.sort()
    n = len(lengths)
    return {
        "count":  n,
        "mean":   round(statistics.mean(lengths), 1),
        "min":    lengths[0],
        "max":    lengths[-1],
        "p50":    lengths[n // 2],
        "p95":    lengths[int(n * 0.95)],
    }