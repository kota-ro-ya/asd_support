"""
Conversation data model for AI interactions.
"""

from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class Conversation:
    """AI会話履歴"""
    timestamp: str
    ai_mode: str
    question: str
    answer: str
    topic_tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "timestamp": self.timestamp,
            "ai_mode": self.ai_mode,
            "question": self.question,
            "answer": self.answer,
            "topic_tags": self.topic_tags
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Conversation':
        """辞書から生成"""
        return cls(
            timestamp=data["timestamp"],
            ai_mode=data["ai_mode"],
            question=data["question"],
            answer=data["answer"],
            topic_tags=data.get("topic_tags", [])
        )
    
    @classmethod
    def create_new(cls, ai_mode: str, question: str, answer: str, 
                   topic_tags: List[str] = None) -> 'Conversation':
        """新しい会話を作成"""
        return cls(
            timestamp=datetime.now().isoformat(),
            ai_mode=ai_mode,
            question=question,
            answer=answer,
            topic_tags=topic_tags or []
        )

