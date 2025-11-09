"""
ロギング設定の強化
デバッグモード、アプリケーションログ、エラーログを適切に管理
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

from app.config.settings import Settings


def setup_logging():
    """
    アプリケーション全体のロギングを設定
    
    - DEBUG_MODE=True: コンソールとファイルに詳細ログ
    - DEBUG_MODE=False: ファイルのみに警告以上のログ
    """
    
    # ログディレクトリの作成
    log_dir = Settings.BASE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # ルートロガーの取得
    root_logger = logging.getLogger()
    
    # 既存のハンドラをクリア（重複を避けるため）
    root_logger.handlers.clear()
    
    # ログレベルの設定
    if Settings.DEBUG_MODE:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
    
    # フォーマッタの作成
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラ（DEBUG_MODEの時のみ）
    if Settings.DEBUG_MODE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(console_handler)
    
    # アプリケーションログファイルハンドラ（日次ローテーション）
    app_log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    app_file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_file_handler.setLevel(logging.INFO if not Settings.DEBUG_MODE else logging.DEBUG)
    app_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(app_file_handler)
    
    # エラーログファイルハンドラ（エラーと重大なログのみ）
    error_log_file = log_dir / f"error_{datetime.now().strftime('%Y%m%d')}.log"
    error_file_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_file_handler)
    
    # パフォーマンスログファイルハンドラ（デバッグモード時のみ）
    if Settings.DEBUG_MODE:
        perf_log_file = log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
        perf_file_handler = RotatingFileHandler(
            perf_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        perf_file_handler.setLevel(logging.DEBUG)
        perf_file_handler.setFormatter(simple_formatter)
        
        # パフォーマンス用のロガーを作成
        perf_logger = logging.getLogger('performance')
        perf_logger.addHandler(perf_file_handler)
        perf_logger.propagate = False  # ルートロガーに伝播しない
    
    # サードパーティライブラリのログレベルを調整
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # 初期化メッセージ
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("ASD Support Application - Logging System Initialized")
    logger.info(f"Debug Mode: {Settings.DEBUG_MODE}")
    logger.info(f"Log Directory: {log_dir}")
    logger.info("=" * 80)


def get_performance_logger():
    """パフォーマンス計測用のロガーを取得"""
    return logging.getLogger('performance')


class PerformanceLogger:
    """パフォーマンス計測とロギングのヘルパークラス"""
    
    def __init__(self, operation_name: str):
        """
        初期化
        
        Args:
            operation_name: 計測する処理の名前
        """
        self.operation_name = operation_name
        self.logger = get_performance_logger()
        self.start_time = None
    
    def __enter__(self):
        """コンテキストマネージャーの開始"""
        import time
        self.start_time = time.time()
        if Settings.DEBUG_MODE:
            self.logger.debug(f"[START] {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーの終了"""
        import time
        elapsed = time.time() - self.start_time
        
        if exc_type is not None:
            self.logger.error(f"[ERROR] {self.operation_name} - {elapsed:.3f}s - {exc_val}")
        else:
            if Settings.DEBUG_MODE:
                self.logger.debug(f"[END] {self.operation_name} - {elapsed:.3f}s")
        
        return False  # 例外を再送出


# 便利な関数
def log_api_call(model: str, operation: str, tokens: int, response_time: float):
    """API呼び出しをログに記録"""
    logger = get_performance_logger()
    logger.info(
        f"API_CALL | Model: {model} | Operation: {operation} | "
        f"Tokens: {tokens} | Time: {response_time:.3f}s"
    )


def log_user_action(user_id: str, action: str, details: str = ""):
    """ユーザーアクションをログに記録"""
    logger = logging.getLogger('user_action')
    logger.info(f"USER_ACTION | UserID: {user_id} | Action: {action} | Details: {details}")


def log_error_with_context(error: Exception, context: dict):
    """エラーをコンテキスト情報と共にログに記録"""
    logger = logging.getLogger(__name__)
    logger.error(
        f"Error occurred: {type(error).__name__}: {str(error)}\n"
        f"Context: {context}",
        exc_info=True
    )

