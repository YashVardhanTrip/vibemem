"""Extract memories from conversation logs and session files."""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Patterns that indicate memory-worthy content
CORRECTION_PATTERNS = [
    r"no[,.]?\s+(it'?s|the|that|this)\s+(?:actually\s+)?(.+)",
    r"not\s+(\d+)[,.]?\s+(?:it'?s|use)\s+(\d+)",
    r"wrong[,.]?\s+(.+)",
    r"actually[,.]?\s+(.+)",
    r"(?:the\s+)?correct\s+(?:one\s+is|answer\s+is|way\s+is)\s+(.+)",
    r"should\s+be\s+(.+?)\s+not\s+(.+)",
    r"use\s+(.+?)\s+instead\s+of\s+(.+)",
    r"don'?t\s+(?:use|do)\s+(.+)",
    r"never\s+(.+)",
    r"always\s+(.+)",
]

SPECIFICATION_PATTERNS = [
    r"(?:the\s+)?api\s+(?:is\s+)?(?:on|at)\s+(?:port\s+)?(\d+)",
    r"(?:the\s+)?(?:server|service|app)\s+runs\s+(?:on|at)\s+(.+)",
    r"(?:we\s+)?use\s+(.+?)\s+for\s+(.+)",
    r"(?:the\s+)?architecture\s+is\s+(.+)",
    r"(?:the\s+)?database\s+is\s+(.+)",
    r"credentials?\s+(?:are|is)\s+(.+)",
    r"(?:the\s+)?format\s+(?:is|should\s+be)\s+(.+)",
]

CATEGORY_KEYWORDS = {
    "arch": ["architecture", "structure", "design", "pattern", "flow", "system"],
    "api": ["api", "endpoint", "port", "url", "route", "request", "response"],
    "gotcha": ["gotcha", "watch out", "careful", "note", "warning", "caveat", "bug"],
    "error": ["error", "mistake", "wrong", "incorrect", "don't", "never", "avoid"],
    "cred": ["credential", "password", "api key", "token", "secret", "auth"],
    "style": ["style", "format", "convention", "naming", "prefer", "always use"],
    "platform": ["hackerone", "bugcrowd", "github", "gitlab", "jira"],
}


def extract_memories(
    file_path: Path,
    model: str = "claude-haiku",
    use_llm: bool = True
) -> List[Dict[str, Any]]:
    """
    Extract memories from a conversation log or session file.

    Args:
        file_path: Path to the file to analyze
        model: LLM model to use for extraction (if use_llm=True)
        use_llm: Whether to use LLM for smart extraction

    Returns:
        List of extracted memory items
    """
    content = file_path.read_text()

    # Try to parse as JSON (Claude Code session format)
    try:
        data = json.loads(content)
        if isinstance(data, list):
            content = _extract_from_messages(data)
        elif isinstance(data, dict) and "messages" in data:
            content = _extract_from_messages(data["messages"])
    except json.JSONDecodeError:
        pass  # Treat as plain text

    memories = []

    # Pattern-based extraction (always run, fast)
    memories.extend(_extract_with_patterns(content))

    # LLM-based extraction (optional, more accurate)
    if use_llm:
        try:
            llm_memories = _extract_with_llm(content, model)
            memories.extend(llm_memories)
        except Exception as e:
            # Fall back to pattern-only if LLM fails
            pass

    # Deduplicate
    seen = set()
    unique = []
    for mem in memories:
        key = mem["content"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(mem)

    return unique


def _extract_from_messages(messages: List[Dict]) -> str:
    """Extract text content from message list."""
    lines = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if isinstance(content, list):
            # Handle content blocks
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    content = block.get("text", "")
                    break

        if content:
            lines.append(f"[{role}]: {content}")

    return "\n".join(lines)


def _extract_with_patterns(content: str) -> List[Dict[str, Any]]:
    """Extract memories using regex patterns."""
    memories = []

    # Look for corrections
    for pattern in CORRECTION_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            text = match.group(0).strip()
            if len(text) > 10:  # Skip very short matches
                memories.append({
                    "category": _categorize(text),
                    "content": _clean_text(text),
                    "priority": "normal",
                    "source": "pattern",
                })

    # Look for specifications
    for pattern in SPECIFICATION_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            text = match.group(0).strip()
            if len(text) > 10:
                memories.append({
                    "category": _categorize(text),
                    "content": _clean_text(text),
                    "priority": "normal",
                    "source": "pattern",
                })

    return memories


def _extract_with_llm(content: str, model: str) -> List[Dict[str, Any]]:
    """Extract memories using LLM."""
    import os

    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return []

    # Truncate content if too long
    if len(content) > 50000:
        content = content[:25000] + "\n...[truncated]...\n" + content[-25000:]

    prompt = f"""Analyze this conversation and extract important information that should be remembered for future sessions.

Look for:
1. Corrections (user correcting AI's mistakes)
2. Specifications (ports, URLs, architecture details)
3. Gotchas (things to watch out for)
4. Preferences (coding style, conventions)
5. Credentials or configuration details (note: don't include actual secrets)

For each item, provide:
- category: one of [arch, api, gotcha, error, cred, style, platform]
- content: concise statement of what to remember
- priority: critical/normal/low

Return as JSON array. Only include genuinely useful memories, not obvious things.

Conversation:
{content}

Respond with ONLY a JSON array, no other text:"""

    try:
        import httpx

        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "anthropic/claude-3-haiku",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
            },
            timeout=60,
        )

        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"]

            # Parse JSON from response
            # Handle potential markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            memories = json.loads(text.strip())
            for mem in memories:
                mem["source"] = "llm"
            return memories

    except Exception as e:
        pass

    return []


def _categorize(text: str) -> str:
    """Categorize text based on keywords."""
    text_lower = text.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category

    return "gotcha"  # Default category


def _clean_text(text: str) -> str:
    """Clean extracted text."""
    # Remove role prefixes
    text = re.sub(r"^\[(human|assistant|user|ai)\]:\s*", "", text, flags=re.IGNORECASE)

    # Normalize whitespace
    text = " ".join(text.split())

    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]

    return text
