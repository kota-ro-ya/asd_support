"""
Data validation utilities.
"""

import re
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class Validator:
    """データ検証を行うクラス"""
    
    @staticmethod
    def is_valid_user_id(user_id: str) -> bool:
        """
        ユーザーIDの妥当性を検証
        
        Args:
            user_id: ユーザーID
            
        Returns:
            妥当な場合True
        """
        if not user_id or not isinstance(user_id, str):
            return False
        
        # 8文字の16進数文字列かチェック
        pattern = r'^[a-f0-9]{8}$'
        return bool(re.match(pattern, user_id))
    
    @staticmethod
    def is_valid_nickname(nickname: str) -> bool:
        """
        ニックネームの妥当性を検証
        
        Args:
            nickname: ニックネーム
            
        Returns:
            妥当な場合True
        """
        if not nickname or not isinstance(nickname, str):
            return False
        
        # 1〜20文字の範囲
        if len(nickname) < 1 or len(nickname) > 20:
            return False
        
        # 空白のみの場合は無効
        if nickname.strip() == "":
            return False
        
        return True
    
    @staticmethod
    def is_valid_evaluation(evaluation: str) -> bool:
        """
        評価タイプの妥当性を検証
        
        Args:
            evaluation: 評価タイプ
            
        Returns:
            妥当な場合True
        """
        valid_evaluations = ['appropriate', 'acceptable', 'inappropriate']
        return evaluation in valid_evaluations
    
    @staticmethod
    def is_valid_event_name(event_name: str, valid_events: list) -> bool:
        """
        イベント名の妥当性を検証
        
        Args:
            event_name: イベント名
            valid_events: 有効なイベント名のリスト
            
        Returns:
            妥当な場合True
        """
        return event_name in valid_events
    
    @staticmethod
    def is_valid_scene_number(scene_number: int, max_scenes: int) -> bool:
        """
        シーン番号の妥当性を検証
        
        Args:
            scene_number: シーン番号
            max_scenes: シーンの総数
            
        Returns:
            妥当な場合True
        """
        return isinstance(scene_number, int) and 0 <= scene_number < max_scenes
    
    @staticmethod
    def validate_progress_data(data: dict) -> bool:
        """
        進捗データの妥当性を包括的に検証
        
        Args:
            data: 進捗データ
            
        Returns:
            妥当な場合True
        """
        try:
            # 必須フィールドの存在確認
            required_fields = ['user_id', 'nickname', 'created_at', 'last_access']
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # ユーザーID検証
            if not Validator.is_valid_user_id(data['user_id']):
                logger.error(f"Invalid user_id: {data['user_id']}")
                return False
            
            # ニックネーム検証
            if not Validator.is_valid_nickname(data['nickname']):
                logger.error(f"Invalid nickname: {data['nickname']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating progress data: {e}")
            return False
    
    @staticmethod
    def validate_event_data(data: dict) -> bool:
        """
        イベントデータの妥当性を包括的に検証
        
        Args:
            data: イベントデータ
            
        Returns:
            妥当な場合True
        """
        try:
            # 必須フィールドの存在確認
            required_fields = ['event_name', 'description', 'scenes']
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # シーンリストの検証
            if not isinstance(data['scenes'], list) or len(data['scenes']) == 0:
                logger.error("Scenes must be a non-empty list")
                return False
            
            # 各シーンの検証
            for scene in data['scenes']:
                if not Validator._validate_scene(scene):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating event data: {e}")
            return False
    
    @staticmethod
    def _validate_scene(scene: dict) -> bool:
        """
        シーンデータの妥当性を検証（内部用）
        
        Args:
            scene: シーンデータ
            
        Returns:
            妥当な場合True
        """
        required_fields = ['scene_number', 'text', 'choices']
        for field in required_fields:
            if field not in scene:
                logger.error(f"Scene missing required field: {field}")
                return False
        
        # 選択肢の検証
        if not isinstance(scene['choices'], list) or len(scene['choices']) == 0:
            logger.error("Choices must be a non-empty list")
            return False
        
        for choice in scene['choices']:
            if not Validator._validate_choice(choice):
                return False
        
        return True
    
    @staticmethod
    def _validate_choice(choice: dict) -> bool:
        """
        選択肢データの妥当性を検証（内部用）
        
        Args:
            choice: 選択肢データ
            
        Returns:
            妥当な場合True
        """
        required_fields = ['text', 'evaluation']
        for field in required_fields:
            if field not in choice:
                logger.error(f"Choice missing required field: {field}")
                return False
        
        # 評価タイプの検証
        if not Validator.is_valid_evaluation(choice['evaluation']):
            logger.error(f"Invalid evaluation: {choice['evaluation']}")
            return False
        
        return True

