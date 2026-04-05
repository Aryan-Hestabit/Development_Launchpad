import streamlit as st
import time
import re

from model_loader import load_model
from config import *

# Cached Model Loading
@st.cache_resource(show_spinner="Loading LLM...")
def get_llm():
    return load_model()

llm = get_llm()

# Session State Init
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  
if "temperature" not in st.session_state:
    st.session_state.temperature = TEMPERATURE
if "top_p" not in st.session_state:
    st.session_state.top_p = TOP_P
if "top_k" not in st.session_state:
    st.session_state.top_k = TOP_K

# Sidebar
st.sidebar.title("Settings")
mode = st.sidebar.selectbox("Mode", ["Generate", "Chat"])

temperature = st.sidebar.slider("Temperature", 0.1, 1.5, st.session_state.temperature)
top_p       = st.sidebar.slider("Top-p", 0.1, 1.0, st.session_state.top_p)
top_k       = st.sidebar.slider("Top-k", 1, 100, st.session_state.top_k)

# Persist slider values across reruns
st.session_state.temperature = temperature
st.session_state.top_p = top_p
st.session_state.top_k = top_k

if st.sidebar.button("Clear Chat"):
    st.session_state.chat_history = []

# Title
st.title("🧠 Medical LLM Assistant")

# Stop Sequences
STOP_SEQUENCES = [
    "User:", "<|user|>", "<|system|>",
    "\nUser", "\nHuman:", "\nQ:", "\n###",
    "Medical Assistant:", "Assistant:"
]

# Prompt Builders
def build_generate_prompt(user_input: str) -> str:
    system = (
        "You are a highly knowledgeable and cautious medical assistant. "
        "Answer the following medical question accurately and concisely using evidence-based information. "
        "Structure your answer clearly. "
        "If the question requires a diagnosis or prescription, advise the user to consult a licensed doctor. "
        "Do NOT simulate any further conversation, follow-up questions, or dialogue after your answer. "
        "Answer ONLY the question below and then stop."
    )
    prompt = (
        f"<|system|>\n{system}</s>\n"
        f"<|user|>\n{user_input.strip()}</s>\n"
        f"<|assistant|>\n"
    )
    return prompt


def build_chat_prompt(history: list) -> str:
    system = (
        "You are a knowledgeable, empathetic, and safety-conscious medical assistant. "
        "Your goals:\n"
        "- Provide clear, concise, evidence-based medical information.\n"
        "- Ask clarifying questions when the user's query is vague.\n"
        "- Always advise users to consult a qualified healthcare professional "
        "for diagnosis, prescriptions, or emergencies.\n"
        "- Never fabricate drug names, dosages, or clinical data.\n"
        "- If a question involves an emergency, prioritize safety instructions first.\n"
        "- Answer ONLY the current question. "
        "Do NOT simulate further conversation, follow-up questions, or user messages after your reply."
    )

    prompt = f"<|system|>\n{system}</s>\n"

    for turn in history:
        if turn["role"] == "user":
            prompt += f"<|user|>\n{turn['content']}</s>\n"
        elif turn["role"] == "assistant":
            prompt += f"<|assistant|>\n{turn['content']}</s>\n"

    # Leave the assistant tag open for the model to complete
    prompt += "<|assistant|>\n"

    return prompt

# -----------------------
# Response Cleaner
# -----------------------

def clean_response(text: str) -> str:
    stop_patterns = [
        r"\nUser[:\s]",
        r"\n<\|user\|>",
        r"\n<\|system\|>",
        r"\nMedical Assistant[:\s]",
        r"\nAssistant[:\s]",
    ]

    for pattern in stop_patterns:
        match = re.search(pattern, text)
        if match:
            text = text[:match.start()]

    return text.strip()

# -----------------------
# Streaming Function
# -----------------------

def stream_response(prompt: str, container) -> str:
    try:
        stream = llm(
            prompt,
            max_tokens=MAX_NEW_TOKENS,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stream=True,
            stop=STOP_SEQUENCES
        )
    except Exception as e:
        container.error(f"Model error: {e}")
        return ""

    response = ""
    placeholder = container.empty()

    for chunk in stream:
        token = chunk["choices"][0].get("text", "")
        response += token
        placeholder.markdown(response + "▌")  # typing cursor effect

    # Final render without cursor
    cleaned = clean_response(response)
    placeholder.markdown(cleaned)

    return cleaned

# -----------------------
# Generate Mode
# -----------------------

if mode == "Generate":

    st.markdown("Ask a single medical question and get a direct, focused answer.")

    prompt_input = st.text_area(
        "Enter your medical question",
        placeholder="e.g. What are the symptoms of malaria?"
    )

    if st.button("Generate") and prompt_input.strip():

        formatted_prompt = build_generate_prompt(prompt_input)

        st.markdown("### Response")
        container = st.container()
        stream_response(formatted_prompt, container)

    elif st.button and not prompt_input.strip():
        st.warning("Please enter a question before generating.")

# -----------------------
# Chat Mode
# -----------------------

else:

    st.markdown("Have a multi-turn conversation with the medical assistant.")

    # Render full history FIRST before handling new input
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Ask something...")

    if user_input and user_input.strip():
        user_input = user_input.strip()

        # Append user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        # Trim history by character count to stay within context limit
        while len(str(st.session_state.chat_history)) > CHAT_HISTORY_LIMIT:
            st.session_state.chat_history.pop(0)

        # Build prompt from full history
        prompt = build_chat_prompt(st.session_state.chat_history)

        # Render new user message
        st.chat_message("user").write(user_input)

        # Stream assistant response inside chat bubble
        with st.chat_message("assistant"):
            response = stream_response(prompt, st)

        # Save assistant response to history
        if response:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })