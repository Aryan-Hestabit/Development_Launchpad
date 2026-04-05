import json
import random
import re
from datasets import load_dataset
from transformers import AutoTokenizer
from sklearn.model_selection import train_test_split

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

TOTAL_PER_DATASET = 500
MAX_TOKENS = 1024
VAL_SPLIT = 0.1

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# instruction templates for diversity
REASONING_INSTRUCTIONS = [
    "Answer the biomedical research question using the context.",
    "Analyze the research context and provide the answer.",
    "Determine the correct medical conclusion based on the context."
]

EXTRACTION_INSTRUCTIONS = [
    "Extract the key medical information from the text.",
    "Identify important medical facts in the passage.",
    "Summarize the important medical details."
]

# ---------------------------------------------------
# TOKENIZER
# ---------------------------------------------------

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


# ---------------------------------------------------
# TEXT CLEANING
# ---------------------------------------------------

def clean_text(text):
    if text is None:
        return ""
    text = str(text)
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------
# TOKEN COUNT
# ---------------------------------------------------

def token_length(sample):

    combined = sample["instruction"] + " " + sample["input"] + " " + sample["output"]

    return len(tokenizer(combined).input_ids)


# ---------------------------------------------------
# DUPLICATE REMOVAL
# ---------------------------------------------------

def remove_duplicates(samples):

    seen = set()
    unique = []

    for s in samples:

        key = s["instruction"] + s["input"]

        if key not in seen:
            seen.add(key)
            unique.append(s)

    return unique


# ---------------------------------------------------
# FILTER BAD SAMPLES
# ---------------------------------------------------

def filter_samples(samples):

    filtered = []

    for s in samples:

        if s["instruction"] == "":
            continue

        if s["output"] == "":
            continue

        if len(s["output"]) < 5:
            continue

        if token_length(s) > MAX_TOKENS:
            continue

        filtered.append(s)

    return filtered


# ---------------------------------------------------
# MEDQUAD (QA)
# ---------------------------------------------------

def load_medquad():

    dataset = load_dataset(
        "medalpaca/medical_meadow_medqa",
        split="train"
    )

    samples = []

    for row in dataset.shuffle(seed=42).select(range(TOTAL_PER_DATASET)):

        samples.append({
            "instruction": "Please answer with one of the option in the bracket",
            "input": clean_text(row["instruction"] + " " + row["input"]),
            "output": clean_text(row["output"])
        })

    return samples


# ---------------------------------------------------
# PUBMEDQA (REASONING)
# ---------------------------------------------------

def load_pubmedqa():

    dataset = load_dataset(
        "qiaojin/PubMedQA",
        "pqa_labeled",
        split="train"
    )

    samples = []

    dataset = dataset.shuffle(seed=42)

    for row in dataset:

        contexts = row["context"]["contexts"][:3]

        context_text = " ".join(contexts)

        output = row["final_decision"] + ". " + row["long_answer"]

        samples.append({
            "instruction": random.choice(REASONING_INSTRUCTIONS),
            "input": clean_text(row["question"] + " " + context_text),
            "output": clean_text(output)
        })

        if len(samples) >= TOTAL_PER_DATASET:
            break

    return samples


# ---------------------------------------------------
# WIKIDOC (EXTRACTION)
# ---------------------------------------------------

def load_wikidoc():

    dataset = load_dataset(
        "medalpaca/medical_meadow_wikidoc",
        split="train"
    )

    samples = []

    for row in dataset.shuffle(seed=42).select(range(TOTAL_PER_DATASET)):

        samples.append({
            "instruction": random.choice(EXTRACTION_INSTRUCTIONS),
            "input": clean_text(row["input"]),
            "output": clean_text(row["output"])
        })

    return samples


# ---------------------------------------------------
# BUILD FINAL DATASET
# ---------------------------------------------------

def build_dataset():

    print("Loading datasets...")

    qa = load_medquad()
    reasoning = load_pubmedqa()
    extraction = load_wikidoc()

    dataset = qa + reasoning + extraction

    print("Initial samples:", len(dataset))

    dataset = remove_duplicates(dataset)

    print("After duplicate removal:", len(dataset))

    dataset = filter_samples(dataset)

    print("After filtering:", len(dataset))

    random.shuffle(dataset)

    return dataset


# ---------------------------------------------------
# SAVE JSONL
# ---------------------------------------------------

def save_jsonl(data, path):

    with open(path, "w") as f:

        for row in data:

            json.dump(row, f)

            f.write("\n")


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

if __name__ == "__main__":

    dataset = build_dataset()

    train, val = train_test_split(
        dataset,
        test_size=VAL_SPLIT,
        random_state=42
    )

    save_jsonl(train, "data/train.jsonl")
    save_jsonl(val, "data/val.jsonl")

    print("Dataset saved")

    print("Train samples:", len(train))
    print("Validation samples:", len(val))