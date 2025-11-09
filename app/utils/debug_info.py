"""
デバッグ情報収集とロギングのユーティリティ
パフォーマンス計測、API使用状況、リファレンスデータなどを記録
"""

import time
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager

from app.config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class APICallInfo:
    """API呼び出し情報"""
    timestamp: str
    model: str
    agent_type: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    response_time: float = 0.0
    temperature: float = 0.7
    max_tokens: int = 0
    stream: bool = False


@dataclass
class ReferenceDataInfo:
    """リファレンスされたデータ情報"""
    data_type: str  # "event", "scenario", "cache", "rag", etc.
    source: str  # ファイル名やデータソース
    data_id: Optional[str] = None
    description: Optional[str] = None
    relevance_score: Optional[float] = None


@dataclass
class EvaluationInfo:
    """評価情報"""
    evaluation_type: str  # "user_response", "content_quality", etc.
    score: float
    criteria: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class CacheInfo:
    """キャッシュ情報"""
    cache_type: str  # "scenario", "response", etc.
    action: str  # "hit", "miss", "write"
    key: Optional[str] = None


@dataclass
class ErrorInfo:
    """エラー情報"""
    timestamp: str
    error_type: str
    message: str
    traceback: Optional[str] = None


@dataclass
class DebugSession:
    """デバッグセッション情報"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    total_duration: float = 0.0
    
    # 収集されたデータ
    api_calls: List[APICallInfo] = field(default_factory=list)
    references: List[ReferenceDataInfo] = field(default_factory=list)
    evaluations: List[EvaluationInfo] = field(default_factory=list)
    cache_operations: List[CacheInfo] = field(default_factory=list)
    errors: List[ErrorInfo] = field(default_factory=list)
    
    # 統計情報
    total_api_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    cache_hit_rate: float = 0.0
    
    # メタデータ
    page: Optional[str] = None
    user_id: Optional[str] = None
    event_name: Optional[str] = None
    mode: Optional[str] = None
    
    def calculate_statistics(self):
        """統計情報を計算"""
        self.total_api_calls = len(self.api_calls)
        self.total_tokens = sum(call.total_tokens for call in self.api_calls)
        
        # 簡易的なコスト計算（gpt-4o-miniの料金）
        # Input: $0.150 / 1M tokens, Output: $0.600 / 1M tokens
        input_cost = sum(call.prompt_tokens for call in self.api_calls) * 0.150 / 1_000_000
        output_cost = sum(call.completion_tokens for call in self.api_calls) * 0.600 / 1_000_000
        self.total_cost = input_cost + output_cost
        
        # キャッシュヒット率
        cache_hits = len([c for c in self.cache_operations if c.action == "hit"])
        cache_total = len([c for c in self.cache_operations if c.action in ["hit", "miss"]])
        self.cache_hit_rate = (cache_hits / cache_total * 100) if cache_total > 0 else 0.0


class DebugInfoCollector:
    """デバッグ情報収集クラス"""
    
    def __init__(self):
        """初期化"""
        self.current_session: Optional[DebugSession] = None
        self.session_start_time: Optional[float] = None
        
        # ログディレクトリの作成
        self.log_dir = Settings.BASE_DIR / "logs" / "debug"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("DebugInfoCollector initialized")
    
    def start_session(
        self,
        session_id: str,
        page: Optional[str] = None,
        user_id: Optional[str] = None,
        event_name: Optional[str] = None,
        mode: Optional[str] = None
    ):
        """デバッグセッションを開始"""
        self.session_start_time = time.time()
        self.current_session = DebugSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            page=page,
            user_id=user_id,
            event_name=event_name,
            mode=mode
        )
        
        if Settings.DEBUG_MODE:
            logger.info(f"Debug session started: {session_id}")
    
    def end_session(self):
        """デバッグセッションを終了"""
        if not self.current_session or not self.session_start_time:
            return None
        
        self.current_session.end_time = datetime.now().isoformat()
        self.current_session.total_duration = time.time() - self.session_start_time
        self.current_session.calculate_statistics()
        
        # ログファイルに保存
        if Settings.DEBUG_MODE or Settings.DEBUG_LOG_ALWAYS:
            self._save_to_log()
        
        session_data = self.current_session
        self.current_session = None
        self.session_start_time = None
        
        logger.info(f"Debug session ended: {session_data.session_id}")
        return session_data
    
    def add_api_call(
        self,
        model: str,
        agent_type: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        response_time: float = 0.0,
        temperature: float = 0.7,
        max_tokens: int = 0,
        stream: bool = False
    ):
        """API呼び出し情報を記録"""
        if not self.current_session:
            return
        
        api_info = APICallInfo(
            timestamp=datetime.now().isoformat(),
            model=model,
            agent_type=agent_type,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            response_time=response_time,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        self.current_session.api_calls.append(api_info)
        
        if Settings.DEBUG_MODE:
            logger.debug(
                f"API Call: {agent_type or 'generic'} - "
                f"{prompt_tokens + completion_tokens} tokens - "
                f"{response_time:.2f}s"
            )
    
    def add_reference(
        self,
        data_type: str,
        source: str,
        data_id: Optional[str] = None,
        description: Optional[str] = None,
        relevance_score: Optional[float] = None
    ):
        """リファレンスデータ情報を記録"""
        if not self.current_session:
            return
        
        ref_info = ReferenceDataInfo(
            data_type=data_type,
            source=source,
            data_id=data_id,
            description=description,
            relevance_score=relevance_score
        )
        
        self.current_session.references.append(ref_info)
        
        if Settings.DEBUG_MODE:
            logger.debug(f"Reference: {data_type} from {source}")
    
    def add_evaluation(
        self,
        evaluation_type: str,
        score: float,
        criteria: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """評価情報を記録"""
        if not self.current_session:
            return
        
        eval_info = EvaluationInfo(
            evaluation_type=evaluation_type,
            score=score,
            criteria=criteria,
            details=details
        )
        
        self.current_session.evaluations.append(eval_info)
        
        if Settings.DEBUG_MODE:
            logger.debug(f"Evaluation: {evaluation_type} - Score: {score}")
    
    def add_cache_operation(
        self,
        cache_type: str,
        action: str,
        key: Optional[str] = None
    ):
        """キャッシュ操作情報を記録"""
        if not self.current_session:
            return
        
        cache_info = CacheInfo(
            cache_type=cache_type,
            action=action,
            key=key
        )
        
        self.current_session.cache_operations.append(cache_info)
        
        if Settings.DEBUG_MODE:
            logger.debug(f"Cache {action}: {cache_type}")
    
    def add_error(
        self,
        error_type: str,
        message: str,
        traceback: Optional[str] = None
    ):
        """エラー情報を記録"""
        if not self.current_session:
            return
        
        error_info = ErrorInfo(
            timestamp=datetime.now().isoformat(),
            error_type=error_type,
            message=message,
            traceback=traceback
        )
        
        self.current_session.errors.append(error_info)
        
        logger.error(f"Error recorded: {error_type} - {message}")
    
    @contextmanager
    def measure_time(self, operation_name: str):
        """処理時間を計測するコンテキストマネージャー"""
        start = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start
            if Settings.DEBUG_MODE:
                logger.debug(f"{operation_name}: {elapsed:.3f}s")
    
    def get_current_session_summary(self) -> Optional[Dict[str, Any]]:
        """現在のセッションのサマリーを取得"""
        if not self.current_session:
            return None
        
        # 一時的に統計を計算
        temp_session = self.current_session
        temp_session.calculate_statistics()
        
        return {
            "session_id": temp_session.session_id,
            "duration": time.time() - self.session_start_time if self.session_start_time else 0,
            "api_calls": temp_session.total_api_calls,
            "total_tokens": temp_session.total_tokens,
            "estimated_cost": f"${temp_session.total_cost:.4f}",
            "cache_hit_rate": f"{temp_session.cache_hit_rate:.1f}%",
            "errors": len(temp_session.errors),
            "references": len(temp_session.references),
            "evaluations": len(temp_session.evaluations)
        }
    
    def _save_to_log(self):
        """ログファイルに保存"""
        if not self.current_session:
            return
        
        try:
            # ファイル名: debug_YYYYMMDD.jsonl (1日ごと)
            date_str = datetime.now().strftime("%Y%m%d")
            log_file = self.log_dir / f"debug_{date_str}.jsonl"
            
            # セッションデータをJSON形式で保存
            session_dict = asdict(self.current_session)
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(session_dict, ensure_ascii=False) + "\n")
            
            logger.info(f"Debug session saved to {log_file}")
            
        except Exception as e:
            logger.error(f"Failed to save debug session: {e}")
    
    def get_session_data(self) -> Optional[DebugSession]:
        """現在のセッションデータを取得"""
        return self.current_session


# グローバルインスタンス
_debug_collector = DebugInfoCollector()


def get_debug_collector() -> DebugInfoCollector:
    """デバッグコレクターのシングルトンインスタンスを取得"""
    return _debug_collector

