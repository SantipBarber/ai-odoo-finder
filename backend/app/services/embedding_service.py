import requests
from typing import List

from ..config import get_settings

settings = get_settings()


class EmbeddingService:
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.embedding_model
        self.base_url = "https://openrouter.ai/api/v1"

    def get_embedding(self, text: str) -> List[float]:
        """
        Generar embedding para un texto usando Qwen3-Embedding.

        Args:
            text: Texto a vectorizar

        Returns:
            Lista de floats (384 dimensiones)
        """
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío")

        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "input": text
            }
        )

        response.raise_for_status()
        data = response.json()

        embedding = data['data'][0]['embedding']

        # Verificar dimensiones
        if len(embedding) != settings.embedding_dimensions:
            raise ValueError(f"Embedding tiene {len(embedding)} dimensiones, esperadas {settings.embedding_dimensions}")

        return embedding

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generar embeddings para múltiples textos.

        Args:
            texts: Lista de textos

        Returns:
            Lista de embeddings
        """
        embeddings = []
        for text in texts:
            try:
                emb = self.get_embedding(text)
                embeddings.append(emb)
            except Exception as e:
                print(f"❌ Error generando embedding: {e}")
                # Embedding nulo (todos ceros)
                embeddings.append([0.0] * settings.embedding_dimensions)

        return embeddings


# Singleton
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
