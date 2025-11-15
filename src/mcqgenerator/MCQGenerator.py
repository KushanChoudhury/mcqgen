import os
import json
import re
import requests
import traceback
import pathlib
from dotenv import load_dotenv
from src.mcqgenerator.logger import logger

load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.1-8b-instant"
CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


def groq_chat(messages, model=MODEL, temperature=0.2, max_tokens=1024, timeout=60):
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    resp = requests.post(CHAT_URL, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    return data.get("choices", [{}])[0].get("message", {}).get("content")


SYSTEM_GEN = {
    "role": "system",
    "content": (
        "You are an expert MCQ author. Output ONLY valid JSON.\n"
        "Return a JSON object with keys '1','2',... where each value is an object with:\n"
        "- mcq (string)\n"
        "- options: {a,b,c,d}\n"
        "- correct: one of 'a'|'b'|'c'|'d'\n"
        "- explanation: optional one-line explanation\n"
        "Do not output any additional text."
    )
}

GEN_USER_TEMPLATE = (
    "Text:\n{text}\n\n"
    "Create exactly {number} multiple choice questions for '{subject}' students in '{tone}' tone.\n"
    "Use ONLY the JSON shape provided below (RESPONSE_JSON) as the output shape:\n\n"
    "{response_json}\n"
)

SYSTEM_REVIEW = {
    "role": "system",
    "content": (
        "You are an expert English grammarian and pedagogue. Output ONLY valid JSON with two keys:\n"
        "- complexity_analysis: short string (<=50 words)\n"
        "- updated_quiz: quiz JSON in same shape as original\n"
        "Do not output any other text."
    )
}

REVIEW_USER_TEMPLATE = (
    "Subject: {subject}\nGrade: {grade}\nTone: {tone}\n\n"
    "Here is the quiz JSON to evaluate:\n{quiz}\n\n"
    "Provide complexity_analysis and updated_quiz."
)

def _parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{(?:.|\n)*\}", text)
        if m:
            return json.loads(m.group(0))
        raise ValueError("Could not parse JSON from model output")

def generate_quiz(text, number, subject, tone, response_json_string):
    if not response_json_string:
        raise ValueError("response_json_string is required (your response.json contents).")

    user_msg = GEN_USER_TEMPLATE.format(text=text, number=number, subject=subject, tone=tone, response_json=response_json_string)
    messages = [SYSTEM_GEN, {"role": "user", "content": user_msg}]
    logger.info("Calling GROQ to generate quiz...")
    out = groq_chat(messages, temperature=0.25, max_tokens=1500)
    quiz = _parse_json(out)
    logger.info("Generated quiz with %d keys", len(quiz))
    return quiz

def review_quiz(quiz_json, subject, grade, tone):
    quiz_str = json.dumps(quiz_json, ensure_ascii=False, indent=2)
    user_msg = REVIEW_USER_TEMPLATE.format(subject=subject, grade=grade, tone=tone, quiz=quiz_str)
    messages = [SYSTEM_REVIEW, {"role": "user", "content": user_msg}]
    logger.info("Calling GROQ to review quiz...")
    out = groq_chat(messages, temperature=0.0, max_tokens=800)
    review = _parse_json(out)
    logger.info("Review received keys: %s", list(review.keys()))
    return review

def run_pipeline(text, number, subject, tone, grade, response_json_string):
    quiz = generate_quiz(text, number, subject, tone, response_json_string)
    review = review_quiz(quiz, subject, grade, tone)
    final_quiz = review.get("updated_quiz") or quiz
    return {"quiz": quiz, "review": review, "final_quiz": final_quiz}

def format_quiz_human(quiz_json):
    """
    Pretty-print quiz in a readable form.
    """
    lines = []

    # sort keys numerically if they are integers
    try:
        keys = sorted(quiz_json.keys(), key=lambda x: int(x))
    except:
        keys = quiz_json.keys()

    for k in keys:
        item = quiz_json[k]
        mcq = item.get("mcq", "")
        options = item.get("options", {})
        correct = item.get("correct", "")
        explanation = item.get("explanation", "")

        lines.append(f"{k}. {mcq}")

        for key in ["a", "b", "c", "d"]:
            if key in options:
                lines.append(f"   {key}) {options[key]}")

        lines.append(f"   Correct: {correct}")

        if explanation:
            lines.append(f"   Explanation: {explanation}")

        lines.append("")

    return "\n".join(lines)