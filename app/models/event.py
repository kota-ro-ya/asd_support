"""
Event, Scene, and Choice data models.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Choice:
    """選択肢"""
    text: str
    evaluation: str  # appropriate/acceptable/inappropriate
    ai_feedback_hint: str = ""
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "text": self.text,
            "evaluation": self.evaluation,
            "ai_feedback_hint": self.ai_feedback_hint
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Choice':
        """辞書から生成"""
        return cls(
            text=data["text"],
            evaluation=data["evaluation"],
            ai_feedback_hint=data.get("ai_feedback_hint", "")
        )


@dataclass
class Scene:
    """シーン情報"""
    scene_number: int
    text: str
    choices: List[Choice]
    image: Optional[str] = None
    sound: Optional[str] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "scene_number": self.scene_number,
            "text": self.text,
            "image": self.image,
            "sound": self.sound,
            "choices": [choice.to_dict() for choice in self.choices]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Scene':
        """辞書から生成"""
        choices = [Choice.from_dict(c) for c in data.get("choices", [])]
        
        return cls(
            scene_number=data["scene_number"],
            text=data["text"],
            choices=choices,
            image=data.get("image"),
            sound=data.get("sound")
        )


@dataclass
class Event:
    """イベント情報"""
    event_name: str
    description: str
    scenes: List[Scene] = field(default_factory=list)
    thumbnail: Optional[str] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "event_name": self.event_name,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "scenes": [scene.to_dict() for scene in self.scenes]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """辞書から生成"""
        scenes = [Scene.from_dict(s) for s in data.get("scenes", [])]
        
        return cls(
            event_name=data["event_name"],
            description=data["description"],
            scenes=scenes,
            thumbnail=data.get("thumbnail")
        )
    
    def get_scene(self, scene_number: int) -> Optional[Scene]:
        """特定のシーンを取得"""
        for scene in self.scenes:
            if scene.scene_number == scene_number:
                return scene
        return None
    
    def total_scenes(self) -> int:
        """シーンの総数を取得"""
        return len(self.scenes)

