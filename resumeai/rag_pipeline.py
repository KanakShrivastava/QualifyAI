import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from groq import Groq
from resumeai.prompts import (
    ANALYSIS_SYSTEM_PROMPT, ANALYSIS_USER_PROMPT, CHAT_SYSTEM_PROMPT
)

class ResumeRAG:
    """
    Lightweight RAG pipeline:
    chunk documents -> embed chunks -> index with FAISS -> retrieve relevant chunks
    -> provide grounded context to the Groq chat model.
    """
    def __init__(self, resume_text: str, jd_text: str, api_key: str,
                 model_name: str = "llama-3.3-70b-versatile"):
        self.resume_text = resume_text
        self.jd_text = jd_text
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.chunks = self._build_chunks()
        if not self.chunks:
            raise ValueError("No readable text was found in the uploaded documents.")
        vectors = self.embedder.encode(
            [item["text"] for item in self.chunks],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        ).astype("float32")
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    @staticmethod
    def _chunk_text(text: str, source: str, chunk_size: int = 850, overlap: int = 140):
        words = re.findall(r"\S+", text)
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            if chunk.strip():
                chunks.append({"source": source, "text": chunk})
            if end == len(words):
                break
            start = end - overlap
        return chunks

    def _build_chunks(self):
        return (
            self._chunk_text(self.resume_text, "Resume")
            + self._chunk_text(self.jd_text, "Job Description")
        )

    def retrieve(self, query: str, k: int = 8) -> str:
        query_vector = self.embedder.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True
        ).astype("float32")
        k = min(k, len(self.chunks))
        scores, indices = self.index.search(query_vector, k)
        selected = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            item = self.chunks[int(idx)]
            selected.append(
                f"[{item['source']} | relevance {float(score):.3f}]\n{item['text']}"
            )
        return "\n\n---\n\n".join(selected)

    def _complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0.2,
            max_tokens=3500,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content or "The model returned an empty response."

    def analyze(self) -> str:
        query = (
            "Compare the complete resume with the complete job description. "
            "Find required skills, responsibilities, experience, projects, education, "
            "keywords, strengths, gaps, and actionable resume improvements."
        )
        context = self.retrieve(query, k=12)
        user_prompt = (
            f"{ANALYSIS_USER_PROMPT}\n\n"
            f"RETRIEVED DOCUMENT CONTEXT:\n{context}\n\n"
            "Remember: do not infer facts that are not present in this context."
        )
        return self._complete(ANALYSIS_SYSTEM_PROMPT, user_prompt)

    def ask(self, question: str) -> str:
        context = self.retrieve(question, k=8)
        user_prompt = (
            f"Retrieved context:\n{context}\n\n"
            f"User question: {question}\n\n"
            "Answer using the retrieved context. If the context does not contain "
            "the answer, clearly say that you cannot verify it from the uploaded files."
        )
        return self._complete(CHAT_SYSTEM_PROMPT, user_prompt)
