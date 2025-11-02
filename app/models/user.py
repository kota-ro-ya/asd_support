"""
User data model.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class EventProgress:
    """イベントの進捗情報"""
    event_name: str
    current_scene: int = 0
    good_actions_count: int = 0
    acceptable_actions_count: int = 0
    inappropriate_actions_count: int = 0
    stamps_earned: int = 0
    completed: bool = False
    first_played_at: Optional[str] = None
    last_played_at: Optional[str] = None
    play_count: int = 0
    scene_history: List[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "event_name": self.event_name,
            "current_scene": self.current_scene,
            "good_actions_count": self.good_actions_count,
            "acceptable_actions_count": self.acceptable_actions_count,
            "inappropriate_actions_count": self.inappropriate_actions_count,
            "stamps_earned": self.stamps_earned,
            "completed": self.completed,
            "first_played_at": self.first_played_at,
            "last_played_at": self.last_played_at,
            "play_count": self.play_count,
            "scene_history": self.scene_history
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EventProgress':
        """辞書から生成"""
        return cls(**data)


@dataclass
class DailyActivity:
    """日次活動記録"""
    date: str  # YYYY-MM-DD形式
    events_played: List[str] = field(default_factory=list)
    total_scenes_completed: int = 0
    stamps_earned: int = 0
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "date": self.date,
            "events_played": self.events_played,
            "total_scenes_completed": self.total_scenes_completed,
            "stamps_earned": self.stamps_earned
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DailyActivity':
        """辞書から生成"""
        return cls(**data)


@dataclass
class User:
    """ユーザー情報"""
    user_id: str
    nickname: str
    created_at: str
    last_access: str
    events: List[EventProgress] = field(default_factory=list)
    ai_conversations: List[dict] = field(default_factory=list)
    daily_activity: List[DailyActivity] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "created_at": self.created_at,
            "last_access": self.last_access,
            "events": [event.to_dict() for event in self.events],
            "ai_conversations": self.ai_conversations,
            "daily_activity": [activity.to_dict() for activity in self.daily_activity]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """辞書から生成"""
        events = [EventProgress.from_dict(e) for e in data.get("events", [])]
        daily_activity = [DailyActivity.from_dict(d) for d in data.get("daily_activity", [])]
        
        return cls(
            user_id=data["user_id"],
            nickname=data["nickname"],
            created_at=data["created_at"],
            last_access=data["last_access"],
            events=events,
            ai_conversations=data.get("ai_conversations", []),
            daily_activity=daily_activity
        )
    
    def get_event_progress(self, event_name: str) -> Optional[EventProgress]:
        """特定のイベントの進捗を取得"""
        for event in self.events:
            if event.event_name == event_name:
                return event
        return None
    
    def update_last_access(self):
        """最終アクセス時刻を更新"""
        self.last_access = datetime.now().isoformat()

