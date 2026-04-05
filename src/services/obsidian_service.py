"""
Obsidian service — loads the fund knowledge vault from local markdown files.

The vault lives at data/obsidian/ and is a structured wiki of fund entities
(companies, people, funds), concepts, and sources. Files use YAML frontmatter
followed by markdown body.

Loading order: overview → concepts → companies → people → funds → sources → index
(log.md is skipped — it's an audit trail, not knowledge)
"""

import os
import re
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

_VAULT_DIR = Path(__file__).parent.parent.parent / "data" / "obsidian"

# Files to skip — not useful as LP chat context
_SKIP_FILES = {"log.md"}

# Load order: specific files first, then directories
_LOAD_ORDER = [
    "overview.md",
    "concepts",
    "entities/companies",
    "entities/people",
    "entities/funds",
    "sources",
    "index.md",
]


def _strip_wikilinks(text: str) -> str:
    """Replace [[page|label]] → label, [[page]] → page."""
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    return text


def _load_file(path: Path) -> str:
    """Read a markdown file and return its content, cleaned up for LLM context."""
    try:
        content = path.read_text(encoding="utf-8").strip()
        content = _strip_wikilinks(content)
        return content
    except Exception as e:
        logger.warning("Failed to read vault file", path=str(path), error=str(e))
        return ""


class ObsidianService:
    def __init__(self):
        self._cached_context: Optional[str] = None

    def get_document_context(self) -> Optional[str]:
        """
        Load all vault markdown files and return them as a single context string.
        Result is cached for the server session.
        """
        if self._cached_context is not None:
            return self._cached_context

        if not _VAULT_DIR.exists():
            logger.warning("Obsidian vault directory not found", path=str(_VAULT_DIR))
            return None

        sections: list[str] = []

        def add_file(path: Path):
            if path.name in _SKIP_FILES:
                return
            content = _load_file(path)
            if content:
                # Use relative path as a section header for the LLM
                rel = path.relative_to(_VAULT_DIR)
                sections.append(f"=== {rel} ===\n{content}")

        for item in _LOAD_ORDER:
            target = _VAULT_DIR / item
            if target.is_file():
                add_file(target)
            elif target.is_dir():
                for md_file in sorted(target.glob("*.md")):
                    add_file(md_file)

        if not sections:
            logger.warning("No vault files found", vault_dir=str(_VAULT_DIR))
            return None

        self._cached_context = "\n\n".join(sections)
        logger.info("Obsidian vault loaded", files=len(sections), chars=len(self._cached_context))
        return self._cached_context


obsidian_service = ObsidianService()
