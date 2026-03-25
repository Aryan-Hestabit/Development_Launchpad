# FINAL REPORT — WEEK 8

## LLM Fine-Tuning, Quantisation & Optimised Inference

---

# 1. Overview

This project demonstrates a complete **end-to-end LLM engineering pipeline**, covering:

* Dataset creation for instruction tuning
* Parameter-efficient fine-tuning using **QLoRA**
* Model quantisation (INT8, INT4, GGUF)
* Inference benchmarking
* Deployment as a **local LLM API and UI**

The objective was to build a **medical assistant chatbot** that can run efficiently on **limited hardware (Colab / CPU)**.

---

# 2. Model Selection

| Model          | Reason                                  |
| -------------- | --------------------------------------- |
| TinyLlama 1.1B | Lightweight, fast, suitable for Colab   |
| Architecture   | Transformer-based causal language model |
| Use Case       | Medical assistant chatbot               |

---

# 3. Dataset Preparation (Day 1)

## 3.1 Dataset Sources

| Type       | Dataset                |
| ---------- | ---------------------- |
| QA         | MedQuAD (medalpaca)    |
| Reasoning  | PubMedQA               |
| Extraction | Medical Meadow Wikidoc |

---

## 3.2 Dataset Design

Final format:

```json
{
  "instruction": "...",
  "input": "...",
  "output": "..."
}
```

---

## 3.3 Dataset Characteristics

* Total samples: **~1500**
* Balanced across:

  * QA
  * reasoning
  * extraction
* Cleaned and deduplicated
* Token length analysis performed
* Outliers removed

---

## 3.4 Key Insight

```text
Dataset quality has a greater impact than model size.
```

---

# 4. Fine-Tuning (Day 2)

## 4.1 Approach

Used **QLoRA (Quantized LoRA)**:

```text
4-bit base model (frozen)
+ LoRA adapters (trainable)
```

---

## 4.2 Training Configuration

| Parameter     | Value |
| ------------- | ----- |
| Rank (r)      | 16    |
| Learning rate | 2e-4  |
| Batch size    | 4     |
| Epochs        | 3     |
| Precision     | 4-bit |
| GPU           | T4    |

---

## 4.3 LoRA Configuration

* Target modules: `q_proj`, `v_proj`
* Trainable parameters: **~0.4%**

---

## 4.4 Training Results

| Metric          | Value |
| --------------- | ----- |
| Train Loss      | ~1.25 |
| Validation Loss | ~1.48 |

---

## 4.5 Observations

* Efficient fine-tuning achieved with minimal parameters
* Slight validation loss increase indicates mild overfitting

---

## 4.6 Key Insight

```text
LoRA enables efficient adaptation by modifying only attention layers instead of the full model.
```

---

# 5. Quantisation (Day 3)

## 5.1 Objective

Reduce model size while maintaining acceptable performance.

---

## 5.2 Formats Generated

| Format      | Size   |
| ----------- | ------ |
| FP16        | 2.1 GB |
| INT8        | 1.2 GB |
| INT4        | 771 MB |
| GGUF (q8_0) | 1.1 GB |

---

## 5.3 Pipeline

```text
FP16 Model
    ↓
INT8 / INT4 Quantisation
    ↓
GGUF Conversion
    ↓
llama.cpp inference
```

---

## 5.4 Observations

* INT4 achieved significant memory reduction
* GGUF enabled CPU-based inference
* Trade-off observed between size and accuracy

---

## 5.5 Key Insight

```text
Quantisation enables deployment on limited hardware but introduces approximation errors.
```

---

# 6. Inference Benchmarking (Day 4)

## 6.1 Setup

* GPU: Tesla T4
* Evaluation: tokens/sec, latency, VRAM, cosine similarity

---

## 6.2 Results

| Model      | Tokens/sec | Latency | VRAM    | Similarity |
| ---------- | ---------- | ------- | ------- | ---------- |
| Base       | 17.82      | 0.18s   | 2.30 GB | 0.79       |
| Fine-tuned | 27.98      | 0.036s  | 2.30 GB | 0.79       |
| INT4       | 22.88      | 3.57s   | 0.91 GB | -0.01      |

---

## 6.3 GGUF (llama.cpp)

* Prompt: 18.5 tokens/sec
* Generation: 7.7 tokens/sec

---

## 6.4 Observations

* Fine-tuned model improved speed without quality loss
* INT4 reduced memory but degraded output quality
* GGUF enabled CPU deployment

---

## 6.5 Key Insight

```text
Efficient inference requires balancing speed, memory, and output quality.
```

---

# 7. Deployment (Day 5)

## 7.1 Architecture

```text
Streamlit UI
    ↓
llama.cpp (via llama-cpp-python)
    ↓
GGUF model
```

---

## 7.2 Features Implemented

* Generate mode (stateless inference)
* Chat mode (stateful conversation)
* System prompt support
* Temperature, top-p, top-k controls
* Chat history management
* Token limit trimming
* Streaming responses
* Multi-user session support

---

## 7.3 Model Loading Strategy

* `st.cache_resource` for model caching
* `st.session_state` for chat history

---

## 7.4 Key Insight

```text
Separating model caching and session state is essential for scalable LLM applications.
```

---

# 8. Inference Optimisation Techniques

## Implemented

* KV caching (via llama.cpp / transformers)
* Quantized inference
* Prompt trimming

---

## Conceptually Covered

* vLLM (Paged KV cache)
* Speculative decoding
* Prompt compression

---

# 9. System Architecture

```text
Dataset → QLoRA Training → Quantisation → Benchmarking → Deployment
```

---

# 10. Challenges Faced

* CUDA / BF16 compatibility issues
* Model loading and path resolution errors
* INT4 quality degradation
* GGUF conversion issues
* Streamlit import and environment setup

---

# 11. Improvements & Future Work

## Model Improvements

* Increase LoRA rank (r = 32)
* Expand target modules (`k_proj`, `o_proj`)
* Improve prompt formatting

---

## Inference Improvements

* Integrate **vLLM** for higher throughput
* Add **token-level streaming optimization**
* Implement **speculative decoding**

---

## System Improvements

* Add **multi-session backend (user IDs)**
* Integrate **RAG (Retrieval-Augmented Generation)**
* Add **conversation summarization for long chats**

---

# 12. Key Learnings

* Transformer architecture and attention mechanisms
* Instruction tuning vs pretraining
* Parameter-efficient fine-tuning (LoRA / QLoRA)
* Quantisation techniques and trade-offs
* Inference optimisation strategies
* Deployment of LLMs as local services

---

# 13. Final Outcome

This project successfully demonstrates:

```text
✔ Fine-tuning an LLM on custom data
✔ Reducing model size via quantisation
✔ Running models on CPU using GGUF
✔ Benchmarking inference performance
✔ Deploying a production-style chatbot interface
```

---

# 14. Conclusion

The project highlights that **large language models can be efficiently trained, optimized, and deployed even on limited hardware using modern techniques like QLoRA and quantisation**.

It bridges the gap between:

```text
Research → Engineering → Deployment
```

and demonstrates a **complete LLM lifecycle pipeline**.

---

# 🚀 End of Week 8

This marks the completion of:

```text
LLM Fine-Tuning
Quantisation
Optimised Inference
Deployment
```

A full-stack LLM engineering workflow.
