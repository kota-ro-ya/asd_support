"""
Scenario Generator Service for dynamic content generation.
AI駆動のシナリオ生成とテンプレート管理
"""

import logging
import json
import random
from typing import Dict, Optional, List, Any
from pathlib import Path

from app.services.agent_coordinator import AgentCoordinator
from app.services.cache_manager import CacheManager
from app.config.settings import Settings
from app.utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


class ScenarioGenerator:
    """
    シナリオの動的生成とバリエーション管理を行うクラス
    """
    
    def __init__(self):
        """ScenarioGeneratorの初期化"""
        self.agent_coordinator = AgentCoordinator()
        self.cache_manager = CacheManager()
        logger.info("ScenarioGenerator initialized")
    
    def get_scene_with_variation(
        self,
        event_name: str,
        scene_number: int,
        use_ai_generation: bool = True,
        force_new: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        シーンのバリエーションを取得（AI生成 or 固定テンプレート）
        
        Args:
            event_name: イベント名
            scene_number: シーン番号
            use_ai_generation: AIでバリエーションを生成するか
            force_new: キャッシュを無視して新規生成するか
            
        Returns:
            シーン情報（状況説明と選択肢）
        """
        try:
            # キャッシュチェック（force_newでない場合）
            if not force_new:
                cached_scenario = self.cache_manager.get_cached_scenario(event_name, scene_number)
                if cached_scenario:
                    logger.info(f"Using cached scenario for {event_name}_{scene_number}")
                    return cached_scenario
            
            # 基本テンプレートを読み込み
            base_template = self._load_base_template(event_name, scene_number)
            
            if not base_template:
                logger.error(f"Base template not found for {event_name}, scene {scene_number}")
                return None
            
            # AI生成を使用する場合
            if use_ai_generation:
                generated_scene = self._generate_with_ai(
                    event_name,
                    scene_number,
                    base_template
                )
                
                if generated_scene:
                    # 品質チェック
                    quality_result = self.agent_coordinator.validate_content_quality(
                        content_type="scenario",
                        content=generated_scene,
                        criteria={
                            "min_score": 80,
                            "educational_appropriateness": True,
                            "language_level": "elementary_school",
                            "asd_considerations": True
                        }
                    )
                    
                    # 品質基準を満たす場合はキャッシュして返す
                    if quality_result.get("is_valid", False) and quality_result.get("score", 0) >= Settings.AI_QUALITY_THRESHOLD:
                        self.cache_manager.save_scenario_cache(event_name, scene_number, generated_scene)
                        logger.info(f"Generated and cached high-quality scenario for {event_name}_{scene_number}")
                        return generated_scene
                    else:
                        logger.warning(
                            f"Generated scenario quality insufficient (score: {quality_result.get('score', 0)}). "
                            f"Falling back to base template."
                        )
            
            # AI生成失敗 or 使用しない場合は基本テンプレートを返す
            logger.info(f"Using base template for {event_name}_{scene_number}")
            return base_template
            
        except Exception as e:
            logger.error(f"Error getting scene with variation: {e}")
            # エラー時はフォールバック
            return self._load_base_template(event_name, scene_number)
    
    def _load_base_template(
        self,
        event_name: str,
        scene_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        基本テンプレートを読み込む
        
        Args:
            event_name: イベント名
            scene_number: シーン番号
            
        Returns:
            基本シーン情報
        """
        try:
            # イベントファイル名のマッピング
            event_file_map = {
                "トイレ": "toilet.json",
                "床屋": "barber.json",
                "病院": "hospital.json",
                "公園": "park.json",
                "朝のルーティン": "morning_routine.json"
            }
            
            filename = event_file_map.get(event_name)
            if not filename:
                logger.error(f"Unknown event name: {event_name}")
                return None
            
            event_path = Settings.DATA_DIR / "events" / filename
            event_data = FileHandler.read_json(event_path)
            
            if not event_data:
                return None
            
            scenes = event_data.get("scenes", [])
            
            # シーン番号に対応するシーンを検索
            for scene in scenes:
                if scene.get("scene_number") == scene_number:
                    return {
                        "text": scene.get("text", ""),
                        "image": scene.get("image", ""),
                        "choices": scene.get("choices", [])
                    }
            
            logger.warning(f"Scene {scene_number} not found in {event_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading base template: {e}")
            return None
    
    def _generate_with_ai(
        self,
        event_name: str,
        scene_number: int,
        base_template: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        AIを使用してシーンのバリエーションを生成
        
        Args:
            event_name: イベント名
            scene_number: シーン番号
            base_template: 基本テンプレート
            
        Returns:
            AI生成されたシーン情報
        """
        try:
            # 学習目標を推定（選択肢から）
            learning_goal = self._infer_learning_goal(base_template)
            
            # エージェントコーディネーターを使用して生成
            generated = self.agent_coordinator.generate_scenario_variation(
                event_name=event_name,
                scene_number=scene_number,
                base_situation=base_template.get("text", ""),
                learning_goal=learning_goal
            )
            
            if generated:
                # 画像は元のテンプレートから継承
                generated["image"] = base_template.get("image", "")
                return generated
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating with AI: {e}")
            return None
    
    def _infer_learning_goal(self, template: Dict[str, Any]) -> str:
        """
        テンプレートから学習目標を推定
        
        Args:
            template: シーンテンプレート
            
        Returns:
            推定された学習目標
        """
        choices = template.get("choices", [])
        
        if not choices:
            return "適切な社会的行動を学ぶ"
        
        # 適切な選択肢のヒントから学習目標を推定
        for choice in choices:
            if choice.get("evaluation") == "appropriate":
                hint = choice.get("ai_feedback_hint", "")
                if hint:
                    return f"「{hint}」という行動を学ぶ"
        
        return "適切な社会的行動を学ぶ"
    
    def generate_random_parent_situation(
        self,
        event_name: str,
        max_attempts: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        保護者向けのランダムなシチュエーションを生成
        
        Args:
            event_name: イベント名
            max_attempts: 生成試行の最大回数
            
        Returns:
            生成されたシチュエーション情報
        """
        try:
            # イベントから子どもの行動例を取得
            child_behaviors = self._get_child_behaviors_from_event(event_name)
            
            if not child_behaviors:
                logger.warning(f"No child behaviors found for {event_name}")
                return None
            
            # 最大試行回数まで生成を試みる
            for attempt in range(max_attempts):
                logger.info(f"Generating parent situation (attempt {attempt + 1}/{max_attempts})")
                
                generated = self.agent_coordinator.generate_parent_situation(
                    event_name=event_name,
                    child_behaviors=child_behaviors
                )
                
                if not generated:
                    continue
                
                # 品質チェック
                quality_result = self.agent_coordinator.validate_content_quality(
                    content_type="parent_situation",
                    content=generated,
                    criteria={
                        "min_score": 75,
                        "educational_appropriateness": True,
                        "practical_advice": True,
                        "parent_friendly": True
                    }
                )
                
                # 品質基準を満たす場合は返す
                if quality_result.get("is_valid", False) and quality_result.get("score", 0) >= 75:
                    logger.info(f"Generated high-quality parent situation (score: {quality_result.get('score', 0)})")
                    return generated
                else:
                    logger.warning(
                        f"Generated situation quality insufficient "
                        f"(score: {quality_result.get('score', 0)}). Retrying..."
                    )
            
            # 全試行失敗時は既存データからランダムに選択
            logger.warning("All generation attempts failed. Falling back to existing data.")
            return self._get_fallback_parent_situation(event_name)
            
        except Exception as e:
            logger.error(f"Error generating random parent situation: {e}")
            return self._get_fallback_parent_situation(event_name)
    
    def _get_child_behaviors_from_event(self, event_name: str) -> List[str]:
        """
        イベントから子どもの行動例を抽出
        
        Args:
            event_name: イベント名
            
        Returns:
            子どもの行動リスト
        """
        try:
            # イベントファイル名のマッピング
            event_file_map = {
                "トイレ": "toilet.json",
                "床屋": "barber.json",
                "病院": "hospital.json",
                "公園": "park.json",
                "朝のルーティン": "morning_routine.json"
            }
            
            filename = event_file_map.get(event_name)
            if not filename:
                return []
            
            event_path = Settings.DATA_DIR / "events" / filename
            event_data = FileHandler.read_json(event_path)
            
            if not event_data:
                return []
            
            # 全シーンから選択肢のテキストを収集
            behaviors = []
            scenes = event_data.get("scenes", [])
            
            for scene in scenes:
                choices = scene.get("choices", [])
                for choice in choices:
                    behaviors.append(choice.get("text", ""))
            
            return behaviors
            
        except Exception as e:
            logger.error(f"Error getting child behaviors: {e}")
            return []
    
    def _get_fallback_parent_situation(self, event_name: str) -> Optional[Dict[str, Any]]:
        """
        フォールバック用：既存の保護者向けガイドからランダムに選択
        
        Args:
            event_name: イベント名
            
        Returns:
            既存のシチュエーション情報
        """
        try:
            guide_path = Settings.DATA_DIR / "parent_guide_data.json"
            guide_data = FileHandler.read_json(guide_path)
            
            if not guide_data:
                return None
            
            situations = guide_data.get("situation_guides", [])
            
            # 指定されたイベントに該当するシチュエーションをフィルタリング
            event_situations = [
                s for s in situations
                if s.get("event") == event_name
            ]
            
            if not event_situations:
                return None
            
            # ランダムに1つ選択
            selected = random.choice(event_situations)
            logger.info(f"Selected fallback situation from existing data for {event_name}")
            return selected
            
        except Exception as e:
            logger.error(f"Error getting fallback situation: {e}")
            return None
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self.cache_manager.clear_all_cache()
        logger.info("Scenario cache cleared")
    
    def clear_expired_cache(self):
        """期限切れのキャッシュをクリア"""
        self.cache_manager.clear_expired_cache()
        logger.info("Expired cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュの統計情報を取得"""
        return self.cache_manager.get_cache_stats()

