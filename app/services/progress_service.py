"""
User progress management service.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime
import logging
import uuid

from app.models.user import User, EventProgress, DailyActivity
from app.models.conversation import Conversation
from app.utils.file_handler import FileHandler
from app.utils.validator import Validator
from app.utils.date_utils import DateUtils
from app.utils.error_handler import ErrorHandler
from app.config.settings import Settings
from app.config.constants import EVENT_NAMES

logger = logging.getLogger(__name__)


class ProgressService:
    """ユーザー進捗データの管理を行うクラス"""
    
    def __init__(self):
        """ProgressServiceの初期化"""
        self.progress_dir = Settings.USER_PROGRESS_DIR
        FileHandler.ensure_directory(self.progress_dir)
        logger.info("ProgressService initialized successfully")
    
    def load_user_progress(self, user_id: str) -> Optional[User]:
        """
        ユーザーの進捗データを読み込む
        
        Args:
            user_id: ユーザーID
            
        Returns:
            Userオブジェクト。存在しない場合はNone
        """
        try:
            if not Validator.is_valid_user_id(user_id):
                logger.error(f"Invalid user_id: {user_id}")
                return None
            
            file_path = self.progress_dir / f"{user_id}.json"
            data = FileHandler.read_json(file_path)
            
            if data is None:
                logger.info(f"No progress file found for user: {user_id}")
                return None
            
            if not Validator.validate_progress_data(data):
                logger.error(f"Invalid progress data for user: {user_id}")
                return None
            
            user = User.from_dict(data)
            logger.info(f"Loaded progress for user: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error loading user progress: {e}")
            ErrorHandler.handle_error(e, "進捗データの読み込みに失敗しました")
            return None
    
    def save_user_progress(self, user: User) -> bool:
        """
        ユーザーの進捗データを保存する
        
        Args:
            user: Userオブジェクト
            
        Returns:
            成功時True、失敗時False
        """
        try:
            if not Validator.is_valid_user_id(user.user_id):
                logger.error(f"Invalid user_id: {user.user_id}")
                return False
            
            # 最終アクセス時刻を更新
            user.update_last_access()
            
            file_path = self.progress_dir / f"{user.user_id}.json"
            data = user.to_dict()
            
            success = FileHandler.write_json(file_path, data)
            
            if success:
                logger.info(f"Saved progress for user: {user.user_id}")
            else:
                logger.error(f"Failed to save progress for user: {user.user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving user progress: {e}")
            ErrorHandler.handle_error(e, "進捗データの保存に失敗しました")
            return False
    
    def create_new_user(self, nickname: str) -> Optional[User]:
        """
        新しいユーザーを作成する
        
        Args:
            nickname: ニックネーム
            
        Returns:
            作成されたUserオブジェクト。失敗時はNone
        """
        try:
            if not Validator.is_valid_nickname(nickname):
                ErrorHandler.handle_validation_error("ニックネームが無効です")
                return None
            
            # 8文字の16進数IDを生成
            user_id = uuid.uuid4().hex[:8]
            current_time = DateUtils.get_current_datetime_iso()
            
            # 全イベントの初期進捗を作成
            events = []
            for event_name in EVENT_NAMES:
                event_progress = EventProgress(event_name=event_name)
                events.append(event_progress)
            
            user = User(
                user_id=user_id,
                nickname=nickname,
                created_at=current_time,
                last_access=current_time,
                events=events,
                ai_conversations=[],
                daily_activity=[]
            )
            
            # 保存
            if self.save_user_progress(user):
                logger.info(f"Created new user: {user_id}, nickname: {nickname}")
                return user
            else:
                return None
            
        except Exception as e:
            logger.error(f"Error creating new user: {e}")
            ErrorHandler.handle_error(e, "新しいユーザーの作成に失敗しました")
            return None
    
    def update_scene_progress(self, user: User, event_name: str, 
                            scene_number: int, selected_choice: str,
                            evaluation: str) -> bool:
        """
        シーンの進捗を更新する
        
        Args:
            user: Userオブジェクト
            event_name: イベント名
            scene_number: シーン番号
            selected_choice: 選択した行動
            evaluation: 評価
            
        Returns:
            成功時True、失敗時False
        """
        try:
            event_progress = user.get_event_progress(event_name)
            if event_progress is None:
                logger.error(f"Event not found: {event_name}")
                return False
            
            # 評価に応じてカウントを更新
            if evaluation == "appropriate":
                event_progress.good_actions_count += 1
            elif evaluation == "acceptable":
                event_progress.acceptable_actions_count += 1
            elif evaluation == "inappropriate":
                event_progress.inappropriate_actions_count += 1
            
            # シーン履歴に追加
            scene_record = {
                "scene_number": scene_number,
                "selected_choice": selected_choice,
                "evaluation": evaluation,
                "timestamp": DateUtils.get_current_datetime_iso()
            }
            event_progress.scene_history.append(scene_record)
            
            # 現在のシーンを更新
            event_progress.current_scene = scene_number + 1
            
            # プレイ回数とタイムスタンプの更新
            if event_progress.first_played_at is None:
                event_progress.first_played_at = DateUtils.get_current_datetime_iso()
            event_progress.last_played_at = DateUtils.get_current_datetime_iso()
            
            # 日次活動の更新
            self._update_daily_activity(user, event_name)
            
            # 保存
            return self.save_user_progress(user)
            
        except Exception as e:
            logger.error(f"Error updating scene progress: {e}")
            ErrorHandler.handle_error(e, "進捗の更新に失敗しました")
            return False
    
    def complete_event(self, user: User, event_name: str, stamps_earned: int) -> bool:
        """
        イベントを完了としてマークする
        
        Args:
            user: Userオブジェクト
            event_name: イベント名
            stamps_earned: 獲得したスタンプ数
            
        Returns:
            成功時True、失敗時False
        """
        try:
            event_progress = user.get_event_progress(event_name)
            if event_progress is None:
                logger.error(f"Event not found: {event_name}")
                return False
            
            event_progress.completed = True
            event_progress.stamps_earned += stamps_earned
            event_progress.play_count += 1
            
            # 日次活動にスタンプを追加
            today = DateUtils.get_current_date_str()
            daily = self._get_or_create_daily_activity(user, today)
            daily.stamps_earned += stamps_earned
            
            # 保存
            return self.save_user_progress(user)
            
        except Exception as e:
            logger.error(f"Error completing event: {e}")
            ErrorHandler.handle_error(e, "イベント完了の記録に失敗しました")
            return False
    
    def add_conversation(self, user: User, ai_mode: str, question: str, 
                        answer: str, topic_tags: list = None) -> bool:
        """
        AI会話履歴を追加する
        
        Args:
            user: Userオブジェクト
            ai_mode: AI人格モード
            question: 質問内容
            answer: 回答内容
            topic_tags: トピックタグのリスト
            
        Returns:
            成功時True、失敗時False
        """
        try:
            conversation = Conversation.create_new(
                ai_mode=ai_mode,
                question=question,
                answer=answer,
                topic_tags=topic_tags or []
            )
            
            user.ai_conversations.append(conversation.to_dict())
            
            # 保存
            return self.save_user_progress(user)
            
        except Exception as e:
            logger.error(f"Error adding conversation: {e}")
            ErrorHandler.handle_error(e, "会話履歴の保存に失敗しました")
            return False
    
    def _update_daily_activity(self, user: User, event_name: str) -> None:
        """
        日次活動を更新する（内部メソッド）
        
        Args:
            user: Userオブジェクト
            event_name: イベント名
        """
        today = DateUtils.get_current_date_str()
        daily = self._get_or_create_daily_activity(user, today)
        
        if event_name not in daily.events_played:
            daily.events_played.append(event_name)
        
        daily.total_scenes_completed += 1
    
    def _get_or_create_daily_activity(self, user: User, date: str) -> DailyActivity:
        """
        指定日の日次活動を取得または作成する（内部メソッド）
        
        Args:
            user: Userオブジェクト
            date: 日付（YYYY-MM-DD形式）
            
        Returns:
            DailyActivityオブジェクト
        """
        for activity in user.daily_activity:
            if activity.date == date:
                return activity
        
        # 新しい日次活動を作成
        new_activity = DailyActivity(date=date)
        user.daily_activity.append(new_activity)
        return new_activity
    
    def reset_event_progress(self, user: User, event_name: str) -> bool:
        """
        特定のイベントの進捗をリセットする
        
        Args:
            user: Userオブジェクト
            event_name: イベント名
            
        Returns:
            成功時True、失敗時False
        """
        try:
            event_progress = user.get_event_progress(event_name)
            if event_progress is None:
                logger.error(f"Event not found: {event_name}")
                return False
            
            event_progress.current_scene = 0
            event_progress.completed = False
            
            # 保存
            return self.save_user_progress(user)
            
        except Exception as e:
            logger.error(f"Error resetting event progress: {e}")
            ErrorHandler.handle_error(e, "進捗のリセットに失敗しました")
            return False

