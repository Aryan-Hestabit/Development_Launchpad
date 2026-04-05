# Day 5 - Medical LLM Assistant Deployment

This folder contains the Day 5 deployment demo for a medical assistant application built with Streamlit and a local LLM backend.

## Overview

`deploy/app.py` launches a Streamlit app that allows users to:

- Ask a single medical question in **Generate** mode
- Have a multi-turn conversation in **Chat** mode
- Adjust temperature, top-p, and top-k settings
- Clear the chat history at any time

The app is designed to use a local `llama_cpp` model backend and focuses on safe, evidence-based medical responses.

## Prerequisites

- Python 3.10 or newer
- A local quantized LLaMA-compatible model file (e.g. `model_q8_0.gguf`)
- `streamlit`
- `llama-cpp-python`

## Recommended installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install streamlit llama-cpp-python
```

## Running the app

From this folder:

```bash
cd /home/aryan/HestaBit_Training/Github_latest/Development_Launchpad/Week-8/Day-5/deploy
streamlit run app.py
```

Then open the URL shown by Streamlit in your browser.

## Notes

- `deploy/app.py` imports `config.py` and `model_loader.py`, so those files must be available in the same folder or on the Python path.
- The model loader should point to a valid model file using a `MODEL_PATH` constant.
- The app includes a safety-focused prompt and is not a substitute for qualified medical advice.

## App features

- **Generate mode**: returns a focused answer for a single medical question.
- **Chat mode**: supports multi-turn dialogue with conversation history.
- **Safety controls**: uses stop sequences and response cleaning to reduce extraneous output.

## Troubleshooting

- If Streamlit fails to start, confirm your virtual environment is active and dependencies are installed.
- If the model cannot load, verify the path in `config.py` and ensure the GGUF file exists.
- If imports fail for `model_loader` or `config`, place those files next to `app.py` or update the Python module path.
