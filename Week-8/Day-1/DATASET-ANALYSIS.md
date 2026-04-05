# DATASET ANALYSIS — LLM FINE-TUNING (DAY 1)

## Overview

This document summarizes the preparation and analysis of the instruction tuning dataset used for fine-tuning **TinyLlama 1.1B** as a **medical assistant chatbot**.

The dataset was constructed by combining multiple medical datasets and converting them into a unified **instruction tuning format** suitable for supervised fine-tuning (SFT).

Target format:

```
{"instruction": "...", "input": "...", "output": "..."}
```

The final dataset contains **three task categories**:

1. Medical Question Answering
2. Biomedical Reasoning
3. Medical Information Extraction

These tasks help the model learn both **factual answering and reasoning abilities** within the healthcare domain.

---

# Dataset Sources

The dataset was built using the following HuggingFace datasets.

| Task Type  | Dataset                  | HF ID                            | Samples |
| ---------- | ------------------------ | -------------------------------- | ------- |
| QA         | MedQuAD (Medical Meadow) | medalpaca/medical_meadow_medqa   | 500     |
| Reasoning  | PubMedQA                 | qiaojin/PubMedQA                 | 500     |
| Extraction | WikiDoc                  | medalpaca/medical_meadow_wikidoc | 500     |

Total initial samples:

```
1500
```

---

# Dataset Conversion

The source datasets use different schemas.
All datasets were converted into a unified instruction tuning structure.

### Example Conversion

Original dataset fields:

```
question
context
long_answer
```

Converted to:

```
instruction → task description
input → question + truncated context
output → final answer
```

Example training sample:

```
{
"instruction": "Answer the medical question.",
"input": "What causes hypertension?",
"output": "Hypertension occurs due to increased blood pressure caused by genetic and lifestyle factors."
}
```

Instruction templates were randomized to increase **instruction diversity**.

---

# Data Cleaning Pipeline

A preprocessing script (`utils/data_cleaner.py`) was implemented to ensure dataset quality.

The following cleaning steps were applied:

### 1. Text Normalization

* Removed newline characters
* Removed extra whitespace
* Standardized text formatting

### 2. Duplicate Removal

Duplicate samples were removed based on:

```
instruction + input
```

This prevents the model from overfitting repeated samples.

### 3. Empty Sample Filtering

Samples were removed if:

* instruction was empty
* output was empty
* output length was extremely short

### 4. Context Truncation

PubMedQA contexts can be very large.

To maintain training stability:

```
Only first 3 context passages were used
```

This reduces extremely long inputs.

### 5. Token Length Filtering

TinyLlama has a **2048 token context window**.

To ensure stable training, samples exceeding the threshold were removed.

```
Maximum token length: 1024
```

Token lengths were calculated using the **TinyLlama tokenizer**.

---

# Dataset Statistics

After cleaning and filtering:

| Metric             | Value |
| ------------------ | ----- |
| Total samples      | ~1477 |
| Training samples   | ~1329 |
| Validation samples | ~148  |
| QA samples         | 500   |
| Reasoning samples  | 500   |
| Extraction samples | 500   |

Dataset split:

```
Train: 90%
Validation: 10%
```

---

# Token Length Analysis

Token length was computed using:

```
TinyLlama/TinyLlama-1.1B-Chat-v1.0 tokenizer
```

Each sample token count included:

```
instruction + input + output
```

### Token Statistics

| Metric         | Approx Value |
| -------------- | ------------ |
| Minimum tokens | ~40          |
| Average tokens | ~300         |
| Maximum tokens | <1024        |

This ensures samples fit comfortably within the model's context window.

---

# Distribution Visualization

Token distribution was analyzed using histogram plots.

![Token Distribution](Screenshots/my_plot.png)

Observed pattern:

* Most samples fall between **150 – 450 tokens**
* Very few samples approach the upper threshold
* No extreme outliers remain after filtering

This distribution is ideal for efficient fine-tuning.

---

# Instruction Diversity

To improve generalization, multiple instruction templates were used.

Examples:

```
Answer the medical question.
Provide a clear medical explanation.
Respond as a medical assistant.
Analyze the research context and provide the answer.
Extract the key medical information from the text.
```

Instruction diversity helps the model learn **robust instruction-following behavior**.

---

# Dataset Quality Assessment

The dataset is suitable for fine-tuning because it satisfies the following properties:

* Balanced task distribution
* Clean and normalized text
* No duplicate samples
* Controlled token lengths
* Diverse instruction phrasing
* Domain-specific medical knowledge

These characteristics are important for **efficient LoRA fine-tuning**.

---

# Final Dataset Structure

```
project/
│
├── data/
│   ├── train.jsonl
│   └── val.jsonl
│
├── utils/
│   └── data_cleaner.py
│
├── notebooks/
│   └── dataset_analysis.ipynb
│
└── DATASET-ANALYSIS.md
```