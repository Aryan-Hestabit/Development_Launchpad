# TRAINING REPORT — DAY 2

## Parameter-Efficient Fine-Tuning using QLoRA

## 1. Overview

This report summarizes the **fine-tuning process of TinyLlama 1.1B** using **QLoRA (Quantized Low Rank Adaptation)** on a **medical instruction dataset** created in Day 1.

The objective was to adapt the base model to behave as a **medical assistant chatbot** capable of answering medical questions, performing biomedical reasoning, and extracting medical information from text.

Fine-tuning was performed using **parameter-efficient techniques**, ensuring that only a small percentage of the model parameters were trained while the base model remained frozen.

---

# 2. Model Information

| Attribute          | Value                                         |
| ------------------ | --------------------------------------------- |
| Base Model         | TinyLlama-1.1B-Chat                           |
| Architecture       | Transformer Decoder                           |
| Total Parameters   | ~1.1 Billion                                  |
| Fine-Tuning Method | QLoRA                                         |
| Task Type          | Instruction Tuning (Causal Language Modeling) |

The base model was loaded in **4-bit quantized format** using **BitsAndBytes** to reduce memory consumption and enable training on a **single Tesla T4 GPU**.

---

# 3. Hardware Configuration

| Component | Specification                                     |
| --------- | ------------------------------------------------- |
| Platform  | Google Colab                                      |
| GPU       | NVIDIA Tesla T4                                   |
| VRAM      | 16 GB                                             |
| Framework | PyTorch                                           |
| Libraries | transformers, peft, trl, bitsandbytes, accelerate |

Training was executed using **QLoRA with 4-bit quantization**, allowing the model to be fine-tuned efficiently within limited GPU memory.

---

# 4. Dataset

The dataset used for fine-tuning was created during **Day 1** by combining three medical datasets and converting them into a unified **instruction-tuning format**.

### Dataset Sources

| Task                   | Dataset  | Samples |
| ---------------------- | -------- | ------- |
| Medical QA             | MedQuAD  | 500     |
| Biomedical Reasoning   | PubMedQA | 500     |
| Information Extraction | WikiDoc  | 500     |

Total samples before filtering:

```
1500
```

Dataset split:

| Split      | Samples |
| ---------- | ------- |
| Training   | ~1300   |
| Validation | ~150    |

All samples follow the instruction format:

```
{"instruction": "...", "input": "...", "output": "..."}
```

---

# 5. QLoRA Configuration

Parameter-Efficient Fine-Tuning was implemented using **LoRA adapters** attached to attention layers.

### LoRA Hyperparameters

| Parameter      | Value                          |
| -------------- | ------------------------------ |
| Rank (r)       | 16                             |
| Alpha          | 32                             |
| Dropout        | 0.05                           |
| Target Modules | q_proj, k_proj, v_proj, o_proj |

These adapters allow the model to learn task-specific behavior while keeping the base model weights frozen.

---

# 6. Quantization Configuration

QLoRA was implemented using **4-bit quantization** with the following configuration:

| Setting             | Value   |
| ------------------- | ------- |
| Quantization        | 4-bit   |
| Quantization Type   | NF4     |
| Compute dtype       | FP16    |
| Double Quantization | Enabled |

This configuration significantly reduces memory usage while maintaining model performance.

---

# 7. Training Configuration

| Parameter              | Value                       |
| ---------------------- | --------------------------- |
| Batch Size             | 4                           |
| Learning Rate          | 2e-4                        |
| Epochs                 | 3                           |
| Optimizer              | AdamW                       |
| Gradient Checkpointing | Enabled                     |
| Mixed Precision        | Disabled (T4 compatibility) |

Training was performed using the **TRL SFTTrainer**, which is optimized for instruction tuning tasks.

---

# 8. Trainable Parameters

The LoRA adapters introduced only a small number of trainable parameters.

| Metric               | Value |
| -------------------- | ----- |
| Total Parameters     | ~1.1B |
| Trainable Parameters | ~5.7M |
| Trainable Percentage | ~0.4% |

This demonstrates the efficiency of **Parameter-Efficient Fine-Tuning (PEFT)**.

---

# 9. Training Results

Training progress over steps:

| Step | Training Loss | Validation Loss |
| ---- | ------------- | --------------- |
| 200  | 1.2977        | 1.4698          |
| 400  | 1.2473        | 1.4844          |
| 600  | 1.3085        | 1.4852          |
| 800  | 1.1633        | 1.5009          |

Final metrics:

| Metric              | Value         |
| ------------------- | ------------- |
| Final Training Loss | ~1.25         |
| Training Runtime    | ~1508 seconds |
| Samples / second    | ~2.64         |
| Steps / second      | ~0.66         |

The training loss decreased consistently, indicating that the model successfully learned patterns from the instruction dataset.

Validation loss remained relatively stable, suggesting only **minor overfitting**, which is expected for a small dataset (~1500 samples).

---

# 10. Model Output

After training, the LoRA adapter weights were saved.

Output directory:

```
/adapters/
```

Generated files:

```
adapter_model.bin
adapter_config.json
```

Adapter size:

```
~30–40 MB
```

This is significantly smaller than the full model size (~2.2 GB), demonstrating the efficiency of LoRA-based fine-tuning.

---

# 11. Observations

Several key observations were made during training:

* The model converged quickly within **3 epochs**
* Training loss stabilized around **1.2–1.3**
* Validation loss remained within a close range (~1.47–1.50)
* LoRA adapters effectively adapted the model with minimal trainable parameters

The results indicate that the model successfully learned to generate **structured medical responses** from the instruction dataset.

---

# 12. Limitations

Some limitations were observed during training:

* The dataset size (~1500 samples) is relatively small for fine-tuning a large language model
* Slight validation loss increase indicates mild overfitting
* Accuracy metrics are not applicable because the model is trained for **text generation rather than classification**

Future improvements could include:

* Increasing dataset size
* Introducing more instruction diversity
* Applying additional LoRA targets (MLP layers)

---

#