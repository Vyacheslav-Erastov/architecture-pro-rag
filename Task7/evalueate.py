import json
import os
from datetime import datetime
from openai import OpenAI

from pipeline.rag import RAGEngine

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

JUDGE_MODEL = "arcee-ai/trinity-large-preview:free"


JUDGE_PROMPT = """
You are an impartial evaluator of a RAG system.

You will be given:
- a user question
- an expected answer
- the actual answer produced by the system

Your task:
1. Decide whether the answer is correct.
2. Decide whether the system behaved correctly (answered or refused when appropriate).
3. Detect hallucinations or unsupported claims.

Return only "true" if Actual answer similary with Expected answer else return "false"
"""


def judge_answer(question, expected, should_answer, actual_answer):
    messages = [
        {"role": "system", "content": JUDGE_PROMPT},
        {
            "role": "user",
            "content": f"""
Question:
{question}

Expected answer:
{expected}

Actual answer:
{actual_answer}
""",
        },
    ]

    response = client.chat.completions.create(
        model=JUDGE_MODEL, messages=messages, temperature=0
    )

    if not response.choices:
        return None

    content = response.choices[0].message.content.strip()

    if "true" in content:
        return True
    elif "false" in content:
        return False
    else:
        return None


def main():
    rag = RAGEngine()
    with open("golden_questions.json", "r", encoding="utf-8") as f:
        golden = json.load(f)

    for qid, q in golden.items():
        question = q["question"]
        expected = q["expected_answer"]
        should_answer = q["should_answer"]
        actual_answer, chunks_exist, sources = rag.answer(query=q["question"])

        evaluation = judge_answer(question, expected, should_answer, actual_answer)

        log_entry = {
            "id": qid,
            "timestamp": str(datetime.now()),
            "question": question,
            "actual_answer": actual_answer,
            "expected_answer": expected,
            "should_answer": should_answer,
            "chunks_exist": chunks_exist,
            "sources": sources,
            "success_answer": evaluation,
        }

        with open("logs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
