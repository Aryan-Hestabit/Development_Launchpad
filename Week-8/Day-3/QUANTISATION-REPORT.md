# QUANTISATION REPORT — DAY 3

## LLM Quantisation (FP16 → INT8 → INT4 → GGUF)

## 1. Overview

This report summarizes the **model quantisation process** performed after fine-tuning **TinyLlama-1.1B** using **QLoRA**.

The objective of quantisation is to **reduce model size and memory usage while maintaining acceptable inference quality**. Quantised models are significantly more efficient for deployment, enabling inference on **limited GPU resources or even CPUs**.

During this stage, the fine-tuned model was converted into multiple formats and evaluated in terms of **model size**. Performance benchmarking (speed and latency) will be conducted in **Day 4**.

---

# 2. What is Quantisation?

Quantisation is the process of converting model weights from **high-precision numerical formats** (such as FP16 or FP32) to **lower precision formats** like INT8 or INT4.

This reduces:

* Memory usage
* Model size
* Inference latency
* Hardware requirements

However, lower precision may introduce **small accuracy degradation**.

General conversion pipeline:

```
FP16 → INT8 → INT4 → GGUF
```

---

# 3. Types of Quantisation Used

The following quantisation formats were generated during the experiment.

| Format      | Description                                        |
| ----------- | -------------------------------------------------- |
| FP16        | Full precision half-float weights (baseline model) |
| INT8        | 8-bit quantisation using BitsAndBytes              |
| INT4        | 4-bit quantisation using NF4 scheme                |
| GGUF (q8_0) | CPU-optimized format used by llama.cpp             |

---

# 4. Quantisation Pipeline

The fine-tuned LoRA model was first **merged with the base TinyLlama model** to produce a standalone model.

Pipeline used:

```
Base Model (TinyLlama 1.1B)
        +
LoRA Adapters
        ↓
Merged Fine-Tuned Model
        ↓
FP16 Model
        ↓
INT8 Quantisation
        ↓
INT4 Quantisation
        ↓
GGUF Conversion (q8_0)
```

The GGUF format was generated using **llama.cpp**, which is optimized for CPU-based inference.

---

# 5. Model Size Comparison

After quantisation, the sizes of each model variant were measured.

| Format             | Model Size |
| ------------------ | ---------- |
| FP16 (HuggingFace) | 2.1 GB     |
| FP16 (GGUF)        | 2.1 GB     |
| INT8               | 1.2 GB     |
| INT4               | 771 MB     |
| GGUF q8_0          | 1.1 GB     |

---

# 6. Observations

### Size Reduction

Quantisation significantly reduced model size:

| Conversion       | Size Reduction |
| ---------------- | -------------- |
| FP16 → INT8      | ~43% smaller   |
| FP16 → INT4      | ~63% smaller   |
| FP16 → GGUF q8_0 | ~48% smaller   |

The **INT4 model achieved the highest compression**, reducing the model size from **2.1 GB to 771 MB**.

---

### Memory Efficiency

Lower-precision models require less VRAM during inference.

| Format | Memory Usage      |
| ------ | ----------------- |
| FP16   | Highest           |
| INT8   | Moderate          |
| INT4   | Lowest            |
| GGUF   | Optimized for CPU |

This makes INT4 and GGUF models suitable for **edge devices or local deployment environments**.

---

### Deployment Implications

Different quantisation formats serve different deployment scenarios.

| Format | Best Use Case                      |
| ------ | ---------------------------------- |
| FP16   | Training and evaluation            |
| INT8   | GPU inference                      |
| INT4   | Low-memory GPU inference           |
| GGUF   | CPU-based inference with llama.cpp |

GGUF is particularly useful because it enables **running LLMs locally without requiring GPUs**.

---

# 7. Accuracy vs Compression Trade-off

Quantisation introduces a **trade-off between model size and performance**.

General trend:

```
Higher Precision → Better Quality
Lower Precision → Smaller Model
```

Expected behavior:

| Format    | Expected Quality   |
| --------- | ------------------ |
| FP16      | Highest            |
| INT8      | Very good          |
| INT4      | Slight degradation |
| GGUF q8_0 | Similar to INT8    |

In most practical scenarios, **INT8 and q8_0 provide an excellent balance between quality and efficiency**.

---

# 8. Key Advantages of Quantisation

The quantisation process provides several benefits:

* Reduced model size
* Faster inference
* Lower VRAM requirements
* Improved deployment flexibility
* Ability to run models on CPUs

These advantages are essential for deploying LLMs in **production environments with limited hardware resources**.

---

# 9. Conclusion

The TinyLlama fine-tuned model was successfully quantised into multiple formats. The results demonstrate significant improvements in **storage efficiency and deployment flexibility**.

Key outcomes:

* FP16 baseline model size: **2.1 GB**
* INT8 model size reduced to **1.2 GB**
* INT4 model size reduced to **771 MB**
* GGUF q8_0 model created for CPU inference (**1.1 GB**)

Quantisation allows the fine-tuned model to be deployed across a wide range of environments, from **GPU servers to local CPU machines**.

