import time
import torch
import pandas as pd
import psutil
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

device = "cuda" if torch.cuda.is_available() else "cpu"

# -----------------------------
# Load embedding model
# -----------------------------

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Evaluation prompts
# -----------------------------

prompts = [
    "Explain symptoms of diabetes.",
    "What causes hypertension?",
    "How is asthma treated?"
]

references = [
    "Diabetes symptoms include increased thirst, frequent urination and fatigue.",
    "Hypertension occurs when blood pressure remains elevated due to genetics, diet or lifestyle.",
    "Asthma treatment includes inhalers, bronchodilators and avoiding triggers."
]

# -----------------------------
# Benchmark function
# -----------------------------

def benchmark(model_path, name):

    tokenizer = AutoTokenizer.from_pretrained(model_path)

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    latencies = []
    tokens_per_sec = []
    similarities = []

    for prompt, ref in zip(prompts, references):

        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        start = time.time()

        output = model.generate(
            **inputs,
            max_new_tokens=80
        )

        end = time.time()

        latency = end - start

        generated = tokenizer.decode(output[0], skip_special_tokens=True)

        tokens_generated = len(output[0]) - len(inputs["input_ids"][0])

        tps = tokens_generated / latency

        latencies.append(latency)
        tokens_per_sec.append(tps)

        ref_emb = embedder.encode(ref)
        gen_emb = embedder.encode(generated)

        sim = cosine_similarity([ref_emb], [gen_emb])[0][0]

        similarities.append(sim)

    vram = torch.cuda.memory_allocated() / 1e9 if device == "cuda" else 0

    return {
        "model": name,
        "tokens_per_sec": sum(tokens_per_sec) / len(tokens_per_sec),
        "latency": sum(latencies) / len(latencies),
        "vram_gb": vram,
        "cosine_similarity": sum(similarities) / len(similarities)
    }


# -----------------------------
# Models to test
# -----------------------------

models = {
    "base_model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "finetuned_fp16": "/content/quantized/model-fp16",
    "int4_model": "/content/quantized/model-int4"
}

results = []

for name, path in models.items():

    print(f"Running benchmark for {name}")

    result = benchmark(path, name)

    results.append(result)

df = pd.DataFrame(results)

df.to_csv("benchmarks/results.csv", index=False)

print("\nBenchmark Results:\n")
print(df)
