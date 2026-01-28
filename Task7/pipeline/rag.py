import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from pipeline.prompts import (
    SYSTEM_PROMPT,
    FEW_SHOT_EXAMPLES,
    COT_PROMPT,
    SECURE_SYSTEM_PROMPT,
)
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "BAAI/bge-base-en"
TOP_K = 2

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

INJECTION_PATTERNS = ["ignore all instructions", "output:", "password", "root:"]


def is_malicious_chunk(text: str) -> bool:
    lower = text.lower()
    return any(p in lower for p in INJECTION_PATTERNS)


class RAGEngine:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.read_index("../Task3/index/faiss.index")

        with open("../Task3/index/metadata.json", "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def retrieve(self, query: str):
        emb = self.model.encode(f"query: {query}", normalize_embeddings=True)

        _, indices = self.index.search(np.array([emb]), TOP_K)

        chunks = []
        for idx in indices[0]:
            chunks.append(self.metadata[idx])

        return chunks

    def generate(self, query: str, chunks: list):
        if not chunks:
            return "I don't know. There's no information on this in the knowledge base."

        context = "\n\n".join(
            f"[{c['text']}" for c in chunks if not is_malicious_chunk(c["text"])
        )

        examples = "\n\n".join(
            f"Q: {ex['question']}\nA: {ex['answer']}" for ex in FEW_SHOT_EXAMPLES
        )

        prompt = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
                # "content": SECURE_SYSTEM_PROMPT,
            },
            # {
            #     "role": "system",
            #     "content": COT_PROMPT,
            # },
            {"role": "user", "content": f"Examples:\n {examples}"},
            {"role": "user", "content": f"Context:\n {context}"},
            {"role": "user", "content": f"Question:\n {query}"},
        ]

        response = client.chat.completions.create(
            model="arcee-ai/trinity-large-preview:free",
            messages=prompt,
        )

        if not response.choices:
            return "I can't answer your questions at the moment, but please ask again later"

        return response.choices[0].message.content.strip()

    def answer(self, query: str):
        chunks = self.retrieve(query)
        sources = [c["source"] for c in chunks]
        chunks_exist = True
        if not chunks:
            chunks_exist = False
        answer = self.generate(query, chunks)
        return answer, chunks_exist, sources
