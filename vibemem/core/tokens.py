"""Token counting utilities."""

from typing import Optional
import tiktoken


class TokenCounter:
    """Count tokens for various models."""

    _encoders = {}

    @classmethod
    def get_encoder(cls, model: str = "cl100k_base"):
        """Get or create a tiktoken encoder."""
        if model not in cls._encoders:
            try:
                cls._encoders[model] = tiktoken.get_encoding(model)
            except Exception:
                # Fallback to cl100k_base (GPT-4/Claude approximate)
                cls._encoders[model] = tiktoken.get_encoding("cl100k_base")
        return cls._encoders[model]

    @classmethod
    def count(cls, text: str, model: str = "cl100k_base") -> int:
        """Count tokens in text."""
        if not text:
            return 0
        encoder = cls.get_encoder(model)
        return len(encoder.encode(text))

    @classmethod
    def truncate_to_tokens(cls, text: str, max_tokens: int, model: str = "cl100k_base") -> str:
        """Truncate text to fit within token limit."""
        encoder = cls.get_encoder(model)
        tokens = encoder.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return encoder.decode(tokens[:max_tokens])

    @classmethod
    def estimate_from_chars(cls, text: str) -> int:
        """Quick estimate without full encoding (avg 4 chars per token)."""
        return len(text) // 4


class CompressionStrategy:
    """Strategies for compressing memory to fit token budgets."""

    @staticmethod
    def smart_compress(
        items: list,
        target_tokens: int,
        preserve_categories: list = None
    ) -> list:
        """
        Intelligently compress items to fit target token count.

        Strategy:
        1. Keep all 'critical' priority items
        2. Keep all items in preserve_categories
        3. Summarize long items
        4. Drop low priority items if needed
        """
        preserve_categories = preserve_categories or ["critical", "error", "arch"]

        # Separate protected and compressible items
        protected = []
        compressible = []

        for item in items:
            if item['priority'] == 'critical' or item['category'] in preserve_categories:
                protected.append(item)
            else:
                compressible.append(item)

        # Calculate tokens
        protected_tokens = sum(item['tokens'] for item in protected)

        if protected_tokens >= target_tokens:
            # Even protected items exceed budget - need to summarize them
            return CompressionStrategy._summarize_items(protected, target_tokens)

        remaining_budget = target_tokens - protected_tokens

        # Sort compressible by priority and recency
        priority_order = {'normal': 0, 'low': 1}
        compressible.sort(key=lambda x: (priority_order.get(x['priority'], 2), -x.get('timestamp', 0)))

        # Add compressible items until budget exhausted
        result = protected.copy()
        current_tokens = protected_tokens

        for item in compressible:
            if current_tokens + item['tokens'] <= target_tokens:
                result.append(item)
                current_tokens += item['tokens']
            elif remaining_budget > 100:
                # Try to fit a summarized version
                summarized = CompressionStrategy._summarize_single(item, remaining_budget // 2)
                if summarized:
                    result.append(summarized)
                    current_tokens += summarized['tokens']
                    remaining_budget = target_tokens - current_tokens

        return result

    @staticmethod
    def _summarize_items(items: list, target_tokens: int) -> list:
        """Summarize items to fit budget."""
        result = []
        budget_per_item = max(50, target_tokens // len(items))

        for item in items:
            if item['tokens'] <= budget_per_item:
                result.append(item)
            else:
                summarized = CompressionStrategy._summarize_single(item, budget_per_item)
                if summarized:
                    result.append(summarized)

        return result

    @staticmethod
    def _summarize_single(item: dict, max_tokens: int) -> Optional[dict]:
        """Summarize a single item to fit token budget."""
        content = item['content']

        # Simple truncation with ellipsis for now
        # TODO: Use LLM for smart summarization
        truncated = TokenCounter.truncate_to_tokens(content, max_tokens - 10)
        if truncated != content:
            truncated = truncated.rstrip() + "..."

        new_item = item.copy()
        new_item['content'] = truncated
        new_item['tokens'] = TokenCounter.count(truncated)
        new_item['compressed'] = True

        return new_item

    @staticmethod
    def to_pointers(items: list) -> list:
        """Convert items to pointer format (category + reference only)."""
        pointers = []
        for item in items:
            pointer = {
                'category': item['category'],
                'content': f"[See .vibemem/{item['category']}.md for details]",
                'tokens': 15,  # Approximate
                'pointer': True,
                'original_id': item.get('id'),
            }
            pointers.append(pointer)
        return pointers
