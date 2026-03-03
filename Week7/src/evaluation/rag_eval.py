import json
import re
import sys
from datetime import datetime
from pathlib import Path

from google import genai
from langchain_core.prompts import PromptTemplate

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.settings import (
    GEMINI_API_KEY, GEMINI_MODEL,
    HALLUCINATION_THRESHOLD, CHAT_LOGS_PATH,
)

client = genai.Client(api_key=GEMINI_API_KEY)

REFINEMENT_PROMPT = PromptTemplate(
    input_variables=["question", "context", "answer"],
    template=(
        "You are a critical evaluator. Review the answer below and decide if it is accurate "
        "and well-supported by the context.\n\n"
        "Question: {question}\n\n"
        "Context:\n{context}\n\n"
        "Answer:\n{answer}\n\n"
        "If the answer is accurate and complete, respond with:\n"
        "KEEP: <original answer>\n\n"
        "If the answer needs improvement, respond with:\n"
        "REWRITE: <improved answer>\n\n"
        "Only output one of the two formats above."
    )
)


def confidence_score(answer: str, context: str) -> float:
    if not context or not answer:
        return 0.0
    stopwords = {"the","a","an","is","in","it","of","to","and","or","for",
                 "on","at","by","be","are","was","were","with","this","that"}
    answer_words  = set(re.findall(r"\b\w+\b", answer.lower())) - stopwords
    context_words = set(re.findall(r"\b\w+\b", context.lower())) - stopwords
    if not answer_words:
        return 0.0
    return round(len(answer_words & context_words) / len(answer_words), 3)


def hallucination_detected(score: float) -> bool:
    return score < HALLUCINATION_THRESHOLD


def refinement_loop(question: str, context: str, answer: str) -> tuple[str, bool]:
    prompt   = REFINEMENT_PROMPT.format(question=question, context=context, answer=answer)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt).text.strip()
    if response.startswith("REWRITE:"):
        return response[len("REWRITE:"):].strip(), True
    if response.startswith("KEEP:"):
        return response[len("KEEP:"):].strip(), False
    return answer, False


def log_trace(endpoint, question, context, answer, refined_answer, was_rewritten, confidence, hallucination):
    entry = {
        "timestamp":      datetime.utcnow().isoformat(),
        "endpoint":       endpoint,
        "question":       question,
        "context":        context[:500],
        "answer":         answer,
        "refined_answer": refined_answer,
        "was_rewritten":  was_rewritten,
        "confidence":     confidence,
        "hallucination":  hallucination,
    }
    logs = []
    if CHAT_LOGS_PATH.exists():
        try:
            logs = json.loads(CHAT_LOGS_PATH.read_text())
        except json.JSONDecodeError:
            logs = []
    logs.append(entry)
    CHAT_LOGS_PATH.write_text(json.dumps(logs, indent=2))