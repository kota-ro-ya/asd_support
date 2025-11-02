"""
Error handling and logging utilities.
"""

import logging
import streamlit as st
from typing import Optional, Callable, Any
import traceback

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ErrorHandler:
    """エラーハンドリングとユーザーへの通知を管理するクラス"""
    
    @staticmethod
    def handle_error(error: Exception, user_message: str = "エラーが発生しました", 
                    show_details: bool = False) -> None:
        """
        エラーを処理し、ユーザーに通知する
        
        Args:
            error: 発生した例外
            user_message: ユーザーに表示するメッセージ
            show_details: 詳細を表示するかどうか
        """
        # ログに記録
        logger.error(f"{user_message}: {str(error)}")
        logger.error(traceback.format_exc())
        
        # ユーザーに通知
        st.error(f"❌ {user_message}")
        
        if show_details:
            with st.expander("詳細を表示"):
                st.code(str(error))
    
    @staticmethod
    def handle_api_error(error: Exception) -> None:
        """
        API関連のエラーを処理する
        
        Args:
            error: 発生した例外
        """
        logger.error(f"API error: {str(error)}")
        logger.error(traceback.format_exc())
        
        st.error("🔌 通信エラーが発生しました")
        st.info("時間をおいて再度お試しください。")
    
    @staticmethod
    def handle_file_error(error: Exception, file_path: str) -> None:
        """
        ファイル操作のエラーを処理する
        
        Args:
            error: 発生した例外
            file_path: 対象ファイルのパス
        """
        logger.error(f"File error for {file_path}: {str(error)}")
        logger.error(traceback.format_exc())
        
        st.error("📁 ファイルの読み込みに失敗しました")
        st.info("ファイルが存在するか確認してください。")
    
    @staticmethod
    def handle_validation_error(message: str) -> None:
        """
        バリデーションエラーを処理する
        
        Args:
            message: エラーメッセージ
        """
        logger.warning(f"Validation error: {message}")
        st.warning(f"⚠️ {message}")
    
    @staticmethod
    def safe_execute(func: Callable, *args, 
                    error_message: str = "処理中にエラーが発生しました",
                    default_return: Any = None, **kwargs) -> Any:
        """
        関数を安全に実行し、エラーが発生した場合は適切に処理する
        
        Args:
            func: 実行する関数
            *args: 関数の位置引数
            error_message: エラー時に表示するメッセージ
            default_return: エラー時に返すデフォルト値
            **kwargs: 関数のキーワード引数
            
        Returns:
            関数の実行結果、またはエラー時はdefault_return
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle_error(e, error_message)
            return default_return
    
    @staticmethod
    def log_info(message: str) -> None:
        """
        情報ログを記録
        
        Args:
            message: ログメッセージ
        """
        logger.info(message)
    
    @staticmethod
    def log_warning(message: str) -> None:
        """
        警告ログを記録
        
        Args:
            message: ログメッセージ
        """
        logger.warning(message)
    
    @staticmethod
    def log_error(message: str) -> None:
        """
        エラーログを記録
        
        Args:
            message: ログメッセージ
        """
        logger.error(message)
    
    @staticmethod
    def show_success(message: str) -> None:
        """
        成功メッセージを表示
        
        Args:
            message: 表示するメッセージ
        """
        st.success(f"✅ {message}")
        logger.info(message)
    
    @staticmethod
    def show_info(message: str) -> None:
        """
        情報メッセージを表示
        
        Args:
            message: 表示するメッセージ
        """
        st.info(f"ℹ️ {message}")
        logger.info(message)
    
    @staticmethod
    def show_warning(message: str) -> None:
        """
        警告メッセージを表示
        
        Args:
            message: 表示するメッセージ
        """
        st.warning(f"⚠️ {message}")
        logger.warning(message)

