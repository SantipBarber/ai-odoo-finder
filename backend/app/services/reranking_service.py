"""
Reranking Service using Qwen3-Reranker-4B.

This service reranks search results using a cross-encoder model
to improve precision@3 by better understanding query-document relevance.
"""

import logging
from typing import List, Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logger = logging.getLogger(__name__)

# Default instruction for Odoo module search
DEFAULT_INSTRUCTION = """Given a user search query for Odoo modules, retrieve relevant modules that match the query requirements."""

# Max length for model input
MAX_LENGTH = 8192

# Chat template prefix and suffix (as per Qwen3-Reranker documentation)
PREFIX = '<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
SUFFIX = '<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'


class RerankingService:
    """
    Reranks search results using Qwen3-Reranker-4B cross-encoder.

    The model scores query-document pairs and returns relevance scores
    that can be used to reorder search results for better precision.
    """

    _instance = None
    _model = None
    _tokenizer = None
    _prefix_tokens = None
    _suffix_tokens = None
    _yes_token_id = None
    _no_token_id = None

    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_name: str = "Qwen/Qwen3-Reranker-4B"):
        """
        Initialize the reranking service.

        Args:
            model_name: HuggingFace model identifier
        """
        if RerankingService._model is None:
            self.model_name = model_name
            self._load_model()

    def _load_model(self):
        """Load the model and tokenizer."""
        logger.info(f"Loading reranking model: {self.model_name}")

        try:
            RerankingService._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side='left'
            )

            # Pre-compute prefix and suffix tokens
            RerankingService._prefix_tokens = RerankingService._tokenizer.encode(
                PREFIX, add_special_tokens=False
            )
            RerankingService._suffix_tokens = RerankingService._tokenizer.encode(
                SUFFIX, add_special_tokens=False
            )

            # Get token IDs for yes/no
            RerankingService._yes_token_id = RerankingService._tokenizer.convert_tokens_to_ids("yes")
            RerankingService._no_token_id = RerankingService._tokenizer.convert_tokens_to_ids("no")

            logger.info(f"Token IDs - yes: {RerankingService._yes_token_id}, no: {RerankingService._no_token_id}")

            # Determine device
            if torch.cuda.is_available():
                device = "cuda"
                dtype = torch.float16
            elif torch.backends.mps.is_available():
                device = "mps"
                dtype = torch.float16
            else:
                device = "cpu"
                dtype = torch.float32

            logger.info(f"Using device: {device}")

            RerankingService._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=dtype,
                device_map=device,
                trust_remote_code=True
            ).eval()

            logger.info("Reranking model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load reranking model: {e}")
            raise

    def _format_input(self, query: str, document: str, instruction: str = None) -> str:
        """
        Format input for the reranker model.

        Args:
            query: User search query
            document: Document text to evaluate
            instruction: Optional custom instruction

        Returns:
            Formatted input string (without prefix/suffix - those are added during tokenization)
        """
        inst = instruction or DEFAULT_INSTRUCTION
        return f"<Instruct>: {inst}\n<Query>: {query}\n<Document>: {document}"

    def _tokenize_with_template(self, input_text: str) -> Dict:
        """
        Tokenize input with proper prefix and suffix tokens.

        Args:
            input_text: Formatted input string

        Returns:
            Tokenized inputs ready for model
        """
        tokenizer = RerankingService._tokenizer
        prefix_tokens = RerankingService._prefix_tokens
        suffix_tokens = RerankingService._suffix_tokens

        # Calculate max length for content
        max_content_length = MAX_LENGTH - len(prefix_tokens) - len(suffix_tokens)

        # Tokenize the content
        content_tokens = tokenizer.encode(
            input_text,
            add_special_tokens=False,
            truncation=True,
            max_length=max_content_length
        )

        # Combine: prefix + content + suffix
        full_tokens = prefix_tokens + content_tokens + suffix_tokens

        # Create attention mask
        attention_mask = [1] * len(full_tokens)

        return {
            'input_ids': torch.tensor([full_tokens]),
            'attention_mask': torch.tensor([attention_mask])
        }

    def _compute_score(self, input_text: str) -> float:
        """
        Compute relevance score for a query-document pair.

        Args:
            input_text: Formatted input string

        Returns:
            Relevance score between 0 and 1
        """
        # Tokenize with proper template
        inputs = self._tokenize_with_template(input_text)

        # Move to same device as model
        device = next(RerankingService._model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = RerankingService._model(**inputs)
            logits = outputs.logits[:, -1, :]

            # Extract logits for yes/no tokens
            yes_logit = logits[:, RerankingService._yes_token_id]
            no_logit = logits[:, RerankingService._no_token_id]

            # Convert to probability
            probs = torch.softmax(torch.stack([no_logit, yes_logit], dim=-1), dim=-1)
            score = probs[:, 1].item()  # Probability of "yes"

        return score

    def rerank(
        self,
        query: str,
        candidates: List[Dict],
        top_k: int = 10,
        instruction: str = None
    ) -> List[Dict]:
        """
        Rerank candidate documents by relevance to query.

        Args:
            query: User search query
            candidates: List of candidate documents with keys:
                       - technical_name, name, summary, ai_description, keywords
            top_k: Number of results to return
            instruction: Optional custom instruction

        Returns:
            Reranked list of candidates with added 'rerank_score' field
        """
        if not candidates:
            return []

        logger.info(f"Reranking {len(candidates)} candidates for query: '{query[:50]}...'")

        scored_candidates = []

        for candidate in candidates:
            # Build document text from available fields
            doc_parts = []

            if candidate.get('name'):
                doc_parts.append(f"Name: {candidate['name']}")

            if candidate.get('summary'):
                doc_parts.append(f"Summary: {candidate['summary']}")

            if candidate.get('ai_description'):
                doc_parts.append(f"Description: {candidate['ai_description']}")

            if candidate.get('keywords'):
                keywords = candidate['keywords']
                if isinstance(keywords, list):
                    keywords = ', '.join(keywords)
                doc_parts.append(f"Keywords: {keywords}")

            document = '\n'.join(doc_parts)

            # Compute relevance score
            input_text = self._format_input(query, document, instruction)
            score = self._compute_score(input_text)

            # Add score to candidate
            candidate_with_score = candidate.copy()
            candidate_with_score['rerank_score'] = score
            scored_candidates.append(candidate_with_score)

        # Sort by rerank score (descending)
        scored_candidates.sort(key=lambda x: x['rerank_score'], reverse=True)

        # Log top results
        if scored_candidates:
            top_3 = scored_candidates[:3]
            logger.info(f"Top 3 after reranking: {[c['technical_name'] for c in top_3]}")
            logger.info(f"Top 3 scores: {[round(c['rerank_score'], 4) for c in top_3]}")

        return scored_candidates[:top_k]

    def is_available(self) -> bool:
        """Check if the model is loaded and available."""
        return RerankingService._model is not None


# Singleton getter
_reranking_service: Optional[RerankingService] = None


def get_reranking_service() -> RerankingService:
    """Get or create the reranking service singleton."""
    global _reranking_service
    if _reranking_service is None:
        _reranking_service = RerankingService()
    return _reranking_service