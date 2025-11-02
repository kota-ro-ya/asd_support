"""
Session management service for Streamlit.
"""

import streamlit as st
from typing import Optional, Any
import logging

from app.models.user import User
from app.models.event import Event
from app.config.constants import SESSION_KEYS, PAGE_NAMES, AI_MODE_LIST, PARENT_MODES_LIST
from app.utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)


class SessionService:
    """Streamlitのセッション状態を管理するクラス"""
    
    @staticmethod
    def initialize_session() -> None:
        """セッション状態を初期化する"""
        try:
            # ユーザー情報
            if SESSION_KEYS["USER_ID"] not in st.session_state:
                st.session_state[SESSION_KEYS["USER_ID"]] = None
            
            if SESSION_KEYS["NICKNAME"] not in st.session_state:
                st.session_state[SESSION_KEYS["NICKNAME"]] = None
            
            # ページ状態
            if SESSION_KEYS["CURRENT_PAGE"] not in st.session_state:
                st.session_state[SESSION_KEYS["CURRENT_PAGE"]] = PAGE_NAMES["MODE_SELECTION"]
            
            # イベント情報
            if SESSION_KEYS["CURRENT_EVENT"] not in st.session_state:
                st.session_state[SESSION_KEYS["CURRENT_EVENT"]] = None
            
            if SESSION_KEYS["CURRENT_SCENE"] not in st.session_state:
                st.session_state[SESSION_KEYS["CURRENT_SCENE"]] = 0
            
            if SESSION_KEYS["EVENT_DATA"] not in st.session_state:
                st.session_state[SESSION_KEYS["EVENT_DATA"]] = None
            
            if SESSION_KEYS["PROGRESS_DATA"] not in st.session_state:
                st.session_state[SESSION_KEYS["PROGRESS_DATA"]] = None
            
            # AI関連
            if SESSION_KEYS["AI_MODE"] not in st.session_state:
                st.session_state[SESSION_KEYS["AI_MODE"]] = AI_MODE_LIST[0]
            
            if SESSION_KEYS["SELECTED_QUESTION"] not in st.session_state:
                st.session_state[SESSION_KEYS["SELECTED_QUESTION"]] = None
            
            if SESSION_KEYS["PARENT_MODE"] not in st.session_state:
                st.session_state[SESSION_KEYS["PARENT_MODE"]] = PARENT_MODES_LIST[0]
            
            logger.info("Session initialized")
            
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            ErrorHandler.handle_error(e, "セッションの初期化に失敗しました")
    
    @staticmethod
    def set_user(user: User) -> None:
        """
        ユーザー情報をセッションに保存
        
        Args:
            user: Userオブジェクト
        """
        st.session_state[SESSION_KEYS["USER_ID"]] = user.user_id
        st.session_state[SESSION_KEYS["NICKNAME"]] = user.nickname
        st.session_state[SESSION_KEYS["PROGRESS_DATA"]] = user
        logger.info(f"User set in session: {user.user_id}")
    
    @staticmethod
    def get_user() -> Optional[User]:
        """
        セッションからユーザー情報を取得
        
        Returns:
            Userオブジェクト。未設定の場合はNone
        """
        return st.session_state.get(SESSION_KEYS["PROGRESS_DATA"])
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """
        セッションからユーザーIDを取得
        
        Returns:
            ユーザーID。未設定の場合はNone
        """
        return st.session_state.get(SESSION_KEYS["USER_ID"])
    
    @staticmethod
    def get_nickname() -> Optional[str]:
        """
        セッションからニックネームを取得
        
        Returns:
            ニックネーム。未設定の場合はNone
        """
        return st.session_state.get(SESSION_KEYS["NICKNAME"])
    
    @staticmethod
    def is_logged_in() -> bool:
        """
        ユーザーがログインしているかチェック
        
        Returns:
            ログインしている場合True
        """
        return st.session_state.get(SESSION_KEYS["USER_ID"]) is not None
    
    @staticmethod
    def set_page(page_name: str) -> None:
        """
        現在のページを設定
        
        Args:
            page_name: ページ名
        """
        st.session_state[SESSION_KEYS["CURRENT_PAGE"]] = page_name
        logger.info(f"Page changed to: {page_name}")
    
    @staticmethod
    def get_page() -> str:
        """
        現在のページを取得
        
        Returns:
            ページ名
        """
        return st.session_state.get(
            SESSION_KEYS["CURRENT_PAGE"], 
            PAGE_NAMES["MODE_SELECTION"]
        )
    
    @staticmethod
    def set_event(event: Event) -> None:
        """
        現在のイベントを設定
        
        Args:
            event: Eventオブジェクト
        """
        st.session_state[SESSION_KEYS["CURRENT_EVENT"]] = event.event_name
        st.session_state[SESSION_KEYS["EVENT_DATA"]] = event
        st.session_state[SESSION_KEYS["CURRENT_SCENE"]] = 0
        logger.info(f"Event set: {event.event_name}")
    
    @staticmethod
    def get_event() -> Optional[Event]:
        """
        現在のイベントを取得
        
        Returns:
            Eventオブジェクト。未設定の場合はNone
        """
        return st.session_state.get(SESSION_KEYS["EVENT_DATA"])
    
    @staticmethod
    def get_event_name() -> Optional[str]:
        """
        現在のイベント名を取得
        
        Returns:
            イベント名。未設定の場合はNone
        """
        return st.session_state.get(SESSION_KEYS["CURRENT_EVENT"])
    
    @staticmethod
    def set_scene(scene_number: int) -> None:
        """
        現在のシーン番号を設定
        
        Args:
            scene_number: シーン番号
        """
        st.session_state[SESSION_KEYS["CURRENT_SCENE"]] = scene_number
        logger.info(f"Scene set to: {scene_number}")
    
    @staticmethod
    def get_scene() -> int:
        """
        現在のシーン番号を取得
        
        Returns:
            シーン番号
        """
        return st.session_state.get(SESSION_KEYS["CURRENT_SCENE"], 0)
    
    @staticmethod
    def next_scene() -> int:
        """
        次のシーンに進む
        
        Returns:
            新しいシーン番号
        """
        current = SessionService.get_scene()
        new_scene = current + 1
        SessionService.set_scene(new_scene)
        return new_scene
    
    @staticmethod
    def set_ai_mode(ai_mode: str) -> None:
        """
        AI人格モードを設定
        
        Args:
            ai_mode: AI人格モード
        """
        st.session_state[SESSION_KEYS["AI_MODE"]] = ai_mode
        logger.info(f"AI mode set to: {ai_mode}")
    
    @staticmethod
    def get_ai_mode() -> str:
        """
        AI人格モードを取得
        
        Returns:
            AI人格モード
        """
        return st.session_state.get(SESSION_KEYS["AI_MODE"], AI_MODE_LIST[0])
    
    @staticmethod
    def set_selected_question(question: str) -> None:
        """
        選択された質問を設定
        
        Args:
            question: 質問文
        """
        st.session_state[SESSION_KEYS["SELECTED_QUESTION"]] = question
    
    @staticmethod
    def get_selected_question() -> Optional[str]:
        """
        選択された質問を取得
        
        Returns:
            質問文。未選択の場合はNone
        """
        return st.session_state.get(SESSION_KEYS["SELECTED_QUESTION"])
    
    @staticmethod
    def clear_session() -> None:
        """セッションをクリアする"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        logger.info("Session cleared")
    
    @staticmethod
    def set_value(key: str, value: Any) -> None:
        """
        任意のキーと値をセッションに保存
        
        Args:
            key: キー
            value: 値
        """
        st.session_state[key] = value
    
    @staticmethod
    def get_value(key: str, default: Any = None) -> Any:
        """
        任意のキーの値をセッションから取得
        
        Args:
            key: キー
            default: デフォルト値
            
        Returns:
            値。存在しない場合はdefault
        """
        return st.session_state.get(key, default)

