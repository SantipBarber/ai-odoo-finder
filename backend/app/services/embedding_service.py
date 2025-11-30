from typing import List

import requests

from ..config import get_settings

settings = get_settings()


class EmbeddingService:
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.embedding_model
        self.base_url = "https://openrouter.ai/api/v1"

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Qwen3-Embedding."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.model, "input": text},
        )

        response.raise_for_status()
        data = response.json()

        embedding = data["data"][0]["embedding"]

        if len(embedding) != settings.embedding_dimensions:
            raise ValueError(
                f"Embedding has {len(embedding)} dimensions, expected {settings.embedding_dimensions}"
            )

        return embedding

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            try:
                emb = self.get_embedding(text)
                embeddings.append(emb)
            except Exception as e:
                print(f"Error generating embedding: {e}")
                embeddings.append([0.0] * settings.embedding_dimensions)

        return embeddings


_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
