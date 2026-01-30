"""Memory storage and management."""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from .tokens import TokenCounter, CompressionStrategy
from .config import Config


class MemoryStore:
    """Manages memory storage and retrieval."""

    MEMORY_FILE = "memories.json"
    HOT_FILE = "hot.md"

    def __init__(self, path: Path, data: Dict[str, Any]):
        self.path = path
        self._data = data

    @classmethod
    def initialize(cls, path: Path) -> "MemoryStore":
        """Initialize a new memory store at path."""
        path.mkdir(parents=True, exist_ok=True)

        # Create default structure
        data = {
            "version": 1,
            "created": time.time(),
            "memories": [],
            "categories": {},
        }

        store = cls(path, data)
        store.save()

        # Create default config
        config_path = path / "config.yml"
        if not config_path.exists():
            Config(Config._deep_merge({}, {})).save(config_path)

        # Create hot file
        store._write_hot_file()

        # Create index file
        store._write_index()

        return store

    @classmethod
    def load(cls, is_global: bool = False, project_path: Optional[Path] = None) -> "MemoryStore":
        """Load existing memory store."""
        if is_global:
            path = Config.global_path()
        else:
            path = (project_path or Path.cwd()) / ".vibemem"

        memory_file = path / cls.MEMORY_FILE

        if not memory_file.exists():
            # Auto-initialize if not exists
            return cls.initialize(path)

        with open(memory_file) as f:
            data = json.load(f)

        return cls(path, data)

    def save(self):
        """Save memory store to disk."""
        self.path.mkdir(parents=True, exist_ok=True)

        with open(self.path / self.MEMORY_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

        self._write_hot_file()
        self._write_index()

    def add(self, category: str, content: str, priority: str = "normal") -> Dict[str, Any]:
        """Add a memory item."""
        # Parse category:subcategory format
        if ":" in category:
            category, subcategory = category.split(":", 1)
        else:
            subcategory = None

        item = {
            "id": self._generate_id(content),
            "category": category,
            "subcategory": subcategory,
            "content": content,
            "priority": priority,
            "tokens": TokenCounter.count(content),
            "timestamp": time.time(),
            "compressed": False,
        }

        self._data["memories"].append(item)

        # Track category
        if category not in self._data["categories"]:
            self._data["categories"][category] = {
                "count": 0,
                "tokens": 0,
            }
        self._data["categories"][category]["count"] += 1
        self._data["categories"][category]["tokens"] += item["tokens"]

        return item

    def remove(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Remove a memory item by ID or content match."""
        for i, item in enumerate(self._data["memories"]):
            if item["id"] == item_id or item_id in item["content"]:
                removed = self._data["memories"].pop(i)

                # Update category counts
                cat = removed["category"]
                if cat in self._data["categories"]:
                    self._data["categories"][cat]["count"] -= 1
                    self._data["categories"][cat]["tokens"] -= removed["tokens"]

                return removed
        return None

    def list(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all memory items, optionally filtered by category."""
        memories = self._data["memories"]
        if category:
            memories = [m for m in memories if m["category"] == category]
        return sorted(memories, key=lambda x: (-x["timestamp"]))

    def get_relevant(self, query: str, max_items: int = 20) -> List[Dict[str, Any]]:
        """Get memories relevant to a query."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored = []
        for item in self._data["memories"]:
            score = 0
            content_lower = item["content"].lower()
            category_lower = item["category"].lower()

            # Category match
            if category_lower in query_lower or query_lower in category_lower:
                score += 10

            # Word overlap
            content_words = set(content_lower.split())
            overlap = len(query_words & content_words)
            score += overlap * 2

            # Substring match
            if query_lower in content_lower:
                score += 5

            # Priority boost
            if item["priority"] == "critical":
                score += 5
            elif item["priority"] == "low":
                score -= 2

            # Recency boost (items from last 24h)
            age_hours = (time.time() - item["timestamp"]) / 3600
            if age_hours < 24:
                score += 3
            elif age_hours < 168:  # 1 week
                score += 1

            if score > 0:
                scored.append((score, item))

        # Sort by score descending
        scored.sort(key=lambda x: -x[0])
        return [item for _, item in scored[:max_items]]

    def get_hot(self, max_tokens: int = 8000) -> List[Dict[str, Any]]:
        """Get hot memories (always loaded) within token budget."""
        config = Config.load(self.path.parent)

        return CompressionStrategy.smart_compress(
            self._data["memories"],
            max_tokens,
            preserve_categories=config.compression.get("preserve_categories", [])
        )

    def total_tokens(self) -> int:
        """Get total token count of all memories."""
        return sum(item["tokens"] for item in self._data["memories"])

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens for text."""
        return TokenCounter.count(text)

    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content."""
        hash_input = f"{content}{time.time()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:12]

    def _write_hot_file(self):
        """Write hot memory file (always-loaded context)."""
        hot_items = self.get_hot()

        lines = ["# vibemem - Project Memory", ""]

        # Group by category
        by_category = {}
        for item in hot_items:
            cat = item["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)

        # Write grouped
        for category in sorted(by_category.keys()):
            items = by_category[category]
            lines.append(f"## {category.title()}")
            for item in items:
                prefix = "**[!]** " if item["priority"] == "critical" else "- "
                lines.append(f"{prefix}{item['content']}")
            lines.append("")

        hot_content = "\n".join(lines)
        with open(self.path / self.HOT_FILE, "w") as f:
            f.write(hot_content)

    def _write_index(self):
        """Write index file with pointers to detailed memories."""
        lines = ["# vibemem Index", ""]

        for category, stats in self._data["categories"].items():
            if stats["count"] > 0:
                lines.append(f"- **{category}**: {stats['count']} items ({stats['tokens']} tokens)")

        lines.append("")
        lines.append("Use `vibemem show -c <category>` to view details.")

        with open(self.path / "index.md", "w") as f:
            f.write("\n".join(lines))

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all memories in a category."""
        return [m for m in self._data["memories"] if m["category"] == category]

    def to_markdown(self, items: Optional[List[Dict]] = None, include_metadata: bool = False) -> str:
        """Convert memories to markdown format."""
        items = items or self._data["memories"]

        lines = []
        by_category = {}

        for item in items:
            cat = item["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)

        for category in sorted(by_category.keys()):
            lines.append(f"## {category.title()}")
            for item in by_category[category]:
                content = item["content"]
                if include_metadata:
                    lines.append(f"- [{item['priority']}] {content}")
                else:
                    lines.append(f"- {content}")
            lines.append("")

        return "\n".join(lines)
