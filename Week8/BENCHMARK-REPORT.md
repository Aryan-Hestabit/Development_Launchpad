# BENCHMARK REPORT — DAY 4

## Inference Benchmarking of TinyLlama Medical Assistant

## 1. Overview

This report presents the benchmarking results for different inference configurations of the **TinyLlama-1.1B medical assistant model** developed in previous stages.

The objective of this stage was to evaluate the **runtime performance of the model under different deployment settings** and understand the trade-offs between:

* inference speed
* latency
* GPU memory usage
* output quality

The following models were evaluated:

1. Base TinyLlama model
2. Fine-tuned model (LoRA merged into base model)
3. Quantized INT4 model
4. GGUF model running using **llama.cpp**

---

# 2. Experimental Setup

## Hardware

| Component | Specification   |
| --------- | --------------- |
| GPU       | NVIDIA Tesla T4 |
| VRAM      | 16 GB           |
| Platform  | Google Colab    |

---

## Software Stack

| Tool                  | Purpose                         |
| --------------------- | ------------------------------- |
| Transformers          | Model loading and GPU inference |
| PyTorch               | Deep learning framework         |
| sentence-transformers | Semantic similarity evaluation  |
| llama.cpp             | CPU inference for GGUF models   |

---

# 3. Evaluation Metrics

The following metrics were used for benchmarking.

| Metric            | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| Tokens/sec        | Number of tokens generated per second                       |
| Latency           | Time required to generate the response                      |
| VRAM Usage        | GPU memory used during inference                            |
| Cosine Similarity | Semantic similarity between generated and reference answers |

Cosine similarity was used instead of accuracy because **LLMs generate free-form text where multiple outputs may be correct**.

---

# 4. Benchmark Results

## GPU Inference (Transformers)

| Model           | Tokens/sec | Latency (s) | VRAM (GB) | Cosine Similarity |
| --------------- | ---------- | ----------- | --------- | ----------------- |
| Base Model      | 17.82      | 0.183       | 2.30      | 0.795             |
| Fine-Tuned FP16 | 27.98      | 0.036       | 2.30      | 0.795             |
| INT4 Quantized  | 22.88      | 3.57        | 0.91      | -0.013            |

---

## GGUF Inference (llama.cpp)

| Model     | Prompt Speed    | Generation Speed |
| --------- | --------------- | ---------------- |
| GGUF q8_0 | 18.5 tokens/sec | 7.7 tokens/sec   |

GGUF inference was executed using **llama.cpp**, which allows running quantized models efficiently without requiring GPU support.

---

# 5. Observations

## Fine-Tuned Model Performance

The fine-tuned model achieved the **highest token generation speed (~28 tokens/sec)** while maintaining the same cosine similarity score as the base model.

This indicates that **LoRA fine-tuning did not negatively affect inference performance**.

---

## Quantized INT4 Model

The INT4 model significantly reduced GPU memory usage:

| Model | VRAM    |
| ----- | ------- |
| FP16  | 2.30 GB |
| INT4  | 0.91 GB |

This corresponds to roughly a **60% reduction in GPU memory usage**.

However, the INT4 model showed a drop in cosine similarity, suggesting **quality degradation caused by aggressive quantization**.

---

## GGUF Model Performance

The GGUF model executed using **llama.cpp** achieved:

* prompt processing speed: **18.5 tokens/sec**
* generation speed: **7.7 tokens/sec**

Although slower than GPU inference, GGUF allows the model to run **on CPU-only environments**, making it useful for lightweight local deployments.

---

# 6. Trade-off Analysis

| Format          | Speed  | Memory Usage | Quality  |
| --------------- | ------ | ------------ | -------- |
| FP16            | Medium | High         | High     |
| Fine-Tuned FP16 | Fast   | High         | High     |
| INT4            | Medium | Low          | Lower    |
| GGUF            | Slower | CPU-friendly | Moderate |

Key insight:

Lower precision models reduce memory requirements but may introduce quality degradation.

---

# 7. Key Findings

* Fine-tuning did not negatively impact inference speed
* INT4 quantization reduced GPU memory usage by **more than 60%**
* GGUF models enable **CPU-only inference using llama.cpp**
* Quantization allows deployment on hardware with limited resources

---