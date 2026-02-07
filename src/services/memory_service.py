"""
Conversation memory management service.

Stores and retrieves conversation history for contextual responses.
Uses MCP Memory server (or fallback to in-memory storage).
"""

from collections import deque
from typing import Dict, List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationMessage:
    """Represents a single message in the conversation."""

    def __init__(self, role: str, content: str):
        self.role = role  # "user" or "assistant"
        self.content = content


class MemoryService:
    """Manages conversation history for users."""

    MAX_MESSAGES = 5  # Store last 5 messages (user + assistant pairs)

    def __init__(self):
        """Initialize memory service."""
        # In-memory storage: user_id -> deque of messages
        self._memory: Dict[int, deque] = {}
        logger.info("Memory service initialized")

    async def store_message(self, user_id: int, role: str, content: str):
        """
        Store a message in conversation history.

        Args:
            user_id: Telegram user ID
            role: Message role ("user" or "assistant")
            content: Message content
        """
        if user_id not in self._memory:
            self._memory[user_id] = deque(maxlen=self.MAX_MESSAGES * 2)  # *2 for user+assistant pairs

        message = ConversationMessage(role, content)
        self._memory[user_id].append(message)

        logger.debug(
            "Stored message",
            user_id=user_id,
            role=role,
            message_count=len(self._memory[user_id]),
        )

    async def get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """
        Retrieve conversation history for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        if user_id not in self._memory:
            return []

        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in self._memory[user_id]
        ]

        logger.debug(
            "Retrieved conversation history",
            user_id=user_id,
            message_count=len(messages),
        )

        return messages

    async def clear_history(self, user_id: int):
        """
        Clear conversation history for a user.

        Args:
            user_id: Telegram user ID
        """
        if user_id in self._memory:
            del self._memory[user_id]
            logger.info("Cleared conversation history", user_id=user_id)

    async def get_recent_context(self, user_id: int, max_messages: int = 4) -> str:
        """
        Get recent conversation context as a formatted string.

        Args:
            user_id: Telegram user ID
            max_messages: Maximum number of recent messages to include

        Returns:
            Formatted conversation context
        """
        history = await self.get_conversation_history(user_id)

        if not history:
            return ""

        # Take last N messages
        recent = history[-max_messages:]

        # Format as context string
        context_parts = []
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")

        return "\n".join(context_parts)


# Global memory service instance
memory_service = MemoryService()
