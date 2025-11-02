"""
Cache Manager for AI-generated content.
AI生成コンテンツの永続的なキャッシュ管理
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.config.settings import Settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    AI生成コンテンツのキャッシュを管理するクラス
    """
    
    def __init__(self):
        """CacheManagerの初期化"""
        self.cache_dir = Settings.DATA_DIR / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.scenario_cache_file = self.cache_dir / "scenario_cache.json"
        self.situation_cache_file = self.cache_dir / "situation_cache.json"
        
        # メモリキャッシュ
        self._memory_cache = {}
        
        logger.info("CacheManager initialized")
    
    def get_cached_scenario(
        self,
        event_name: str,
        scene_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        キャッシュされたシナリオを取得
        
        Args:
            event_name: イベント名
            scene_number: シーン番号
            
        Returns:
            キャッシュされたシナリオ（なければNone）
        """
        if not Settings.ENABLE_SCENARIO_CACHE:
            return None
        
        cache_key = f"{event_name}_{scene_number}"
        
        # メモリキャッシュをチェック
        if cache_key in self._memory_cache:
            cached_data = self._memory_cache[cache_key]
            if self._is_cache_valid(cached_data):
                logger.info(f"Memory cache hit for {cache_key}")
                return cached_data.get("content")
        
        # ファイルキャッシュをチェック
        cache_data = self._load_cache_file(self.scenario_cache_file)
        
        if cache_key in cache_data:
            cached_data = cache_data[cache_key]
            if self._is_cache_valid(cached_data):
                # メモリキャッシュにも保存
                self._memory_cache[cache_key] = cached_data
                logger.info(f"File cache hit for {cache_key}")
                return cached_data.get("content")
            else:
                # 期限切れのキャッシュを削除
                logger.info(f"Cache expired for {cache_key}")
                del cache_data[cache_key]
                self._save_cache_file(self.scenario_cache_file, cache_data)
        
        return None
    
    def save_scenario_cache(
        self,
        event_name: str,
        scene_number: int,
        content: Dict[str, Any]
    ):
        """
        シナリオをキャッシュに保存
        
        Args:
            event_name: イベント名
            scene_number: シーン番号
            content: キャッシュするコンテンツ
        """
        if not Settings.ENABLE_SCENARIO_CACHE:
            return
        
        cache_key = f"{event_name}_{scene_number}"
        
        cached_data = {
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "expiry": (datetime.now() + timedelta(hours=Settings.CACHE_EXPIRY_HOURS)).isoformat()
        }
        
        # メモリキャッシュに保存
        self._memory_cache[cache_key] = cached_data
        
        # ファイルキャッシュに保存
        cache_data = self._load_cache_file(self.scenario_cache_file)
        cache_data[cache_key] = cached_data
        
        # キャッシュサイズ制限のチェック
        if len(cache_data) > Settings.MAX_CACHE_SIZE:
            cache_data = self._evict_old_entries(cache_data)
        
        self._save_cache_file(self.scenario_cache_file, cache_data)
        logger.info(f"Saved scenario cache for {cache_key}")
    
    def get_cached_situation(
        self,
        event_name: str,
        situation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        キャッシュされた保護者向けシチュエーションを取得
        
        Args:
            event_name: イベント名
            situation_id: シチュエーションID
            
        Returns:
            キャッシュされたシチュエーション（なければNone）
        """
        if not Settings.ENABLE_SCENARIO_CACHE:
            return None
        
        cache_key = f"{event_name}_{situation_id}"
        
        # メモリキャッシュをチェック
        if cache_key in self._memory_cache:
            cached_data = self._memory_cache[cache_key]
            if self._is_cache_valid(cached_data):
                logger.info(f"Memory cache hit for situation {cache_key}")
                return cached_data.get("content")
        
        # ファイルキャッシュをチェック
        cache_data = self._load_cache_file(self.situation_cache_file)
        
        if cache_key in cache_data:
            cached_data = cache_data[cache_key]
            if self._is_cache_valid(cached_data):
                self._memory_cache[cache_key] = cached_data
                logger.info(f"File cache hit for situation {cache_key}")
                return cached_data.get("content")
            else:
                del cache_data[cache_key]
                self._save_cache_file(self.situation_cache_file, cache_data)
        
        return None
    
    def save_situation_cache(
        self,
        event_name: str,
        situation_id: str,
        content: Dict[str, Any]
    ):
        """
        保護者向けシチュエーションをキャッシュに保存
        
        Args:
            event_name: イベント名
            situation_id: シチュエーションID
            content: キャッシュするコンテンツ
        """
        if not Settings.ENABLE_SCENARIO_CACHE:
            return
        
        cache_key = f"{event_name}_{situation_id}"
        
        cached_data = {
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "expiry": (datetime.now() + timedelta(hours=Settings.CACHE_EXPIRY_HOURS)).isoformat()
        }
        
        self._memory_cache[cache_key] = cached_data
        
        cache_data = self._load_cache_file(self.situation_cache_file)
        cache_data[cache_key] = cached_data
        
        if len(cache_data) > Settings.MAX_CACHE_SIZE:
            cache_data = self._evict_old_entries(cache_data)
        
        self._save_cache_file(self.situation_cache_file, cache_data)
        logger.info(f"Saved situation cache for {cache_key}")
    
    def clear_all_cache(self):
        """全てのキャッシュをクリア"""
        self._memory_cache.clear()
        
        if self.scenario_cache_file.exists():
            self.scenario_cache_file.unlink()
        
        if self.situation_cache_file.exists():
            self.situation_cache_file.unlink()
        
        logger.info("All cache cleared")
    
    def clear_expired_cache(self):
        """期限切れのキャッシュをクリア"""
        # メモリキャッシュから期限切れを削除
        expired_keys = [
            key for key, data in self._memory_cache.items()
            if not self._is_cache_valid(data)
        ]
        for key in expired_keys:
            del self._memory_cache[key]
        
        # ファイルキャッシュから期限切れを削除
        for cache_file in [self.scenario_cache_file, self.situation_cache_file]:
            if cache_file.exists():
                cache_data = self._load_cache_file(cache_file)
                original_size = len(cache_data)
                
                cache_data = {
                    key: data for key, data in cache_data.items()
                    if self._is_cache_valid(data)
                }
                
                if len(cache_data) < original_size:
                    self._save_cache_file(cache_file, cache_data)
                    logger.info(f"Removed {original_size - len(cache_data)} expired entries from {cache_file.name}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュの統計情報を取得"""
        scenario_cache = self._load_cache_file(self.scenario_cache_file)
        situation_cache = self._load_cache_file(self.situation_cache_file)
        
        return {
            "memory_cache_size": len(self._memory_cache),
            "scenario_cache_size": len(scenario_cache),
            "situation_cache_size": len(situation_cache),
            "cache_enabled": Settings.ENABLE_SCENARIO_CACHE,
            "cache_expiry_hours": Settings.CACHE_EXPIRY_HOURS,
            "max_cache_size": Settings.MAX_CACHE_SIZE
        }
    
    def _load_cache_file(self, cache_file: Path) -> Dict[str, Any]:
        """キャッシュファイルを読み込む"""
        if not cache_file.exists():
            return {}
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache file {cache_file}: {e}")
            return {}
    
    def _save_cache_file(self, cache_file: Path, cache_data: Dict[str, Any]):
        """キャッシュファイルに保存"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache file {cache_file}: {e}")
    
    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """キャッシュが有効期限内かチェック"""
        try:
            expiry_str = cached_data.get("expiry")
            if not expiry_str:
                return False
            
            expiry = datetime.fromisoformat(expiry_str)
            return datetime.now() < expiry
        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            return False
    
    def _evict_old_entries(self, cache_data: Dict[str, Any]) -> Dict[str, Any]:
        """古いエントリを削除してキャッシュサイズを制限内に収める"""
        # タイムスタンプでソート
        sorted_entries = sorted(
            cache_data.items(),
            key=lambda x: x[1].get("timestamp", ""),
            reverse=True
        )
        
        # 最新のエントリのみを保持
        return dict(sorted_entries[:Settings.MAX_CACHE_SIZE])

