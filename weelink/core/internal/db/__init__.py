from .engine import MongoDB
from .model import BotDocument, MessageDocument
from .repo import BotRepository, MessageRepository


mongodb = MongoDB()

__all__ = [
    "mongodb",
    "BotDocument",
    "MessageDocument",
    "BotRepository",
    "MessageRepository"
]