"""
Main application entry point for ASD Support App.
"""

import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# ロギング設定を最初に初期化
from app.utils.logger_config import setup_logging
setup_logging()

from app.services.session_service import SessionService
from app.config.settings import Settings
from app.config.constants import PAGE_NAMES
from app.utils.error_handler import ErrorHandler
from app.components.sidebar import render_sidebar
from app.pages.mode_selection import render_mode_selection
from app.pages.event_selection import render_event_selection
from app.pages.story_mode import render_story_mode
from app.pages.review import render_review
from app.pages.parent_guide import render_parent_guide


def main():
    """メインアプリケーション"""
    
    # ページ設定
    st.set_page_config(
        page_title=Settings.APP_TITLE,
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # カスタムCSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            border-radius: 0.5rem;
            font-weight: 500;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 設定の検証
    try:
        Settings.validate()
    except Exception as e:
        st.error("⚠️ 設定の検証に失敗しました")
        st.error(f"エラー: {str(e)}")
        st.info("`.env`ファイルを確認し、必要な環境変数が設定されているか確認してください。")
        st.stop()
    
    # セッション初期化
    SessionService.initialize_session()
    
    # サイドバーを描画（保護者向けAI質問モード）
    render_sidebar()
    
    # 現在のページを取得
    current_page = SessionService.get_page()
    
    # ページごとの描画
    try:
        if current_page == PAGE_NAMES["MODE_SELECTION"]:
            render_mode_selection()
        
        elif current_page == PAGE_NAMES["EVENT_SELECTION"]:
            render_event_selection()
        
        elif current_page == PAGE_NAMES["STORY_MODE"]:
            render_story_mode()
        
        elif current_page == PAGE_NAMES["REVIEW"]:
            render_review()
        
        elif current_page == PAGE_NAMES["PARENT_GUIDE"]:
            render_parent_guide()
        
        else:
            # デフォルトはモード選択画面
            SessionService.set_page(PAGE_NAMES["MODE_SELECTION"])
            st.rerun()
    
    except Exception as e:
        ErrorHandler.handle_error(e, "ページの描画中にエラーが発生しました")
        st.error("アプリケーションでエラーが発生しました。")
        
        if st.button("🔄 リセットして再起動"):
            SessionService.clear_session()
            st.rerun()
    
    # フッター
    st.markdown("---")
    st.caption(f"🌟 {Settings.APP_TITLE} v{Settings.APP_VERSION} | ASD支援のための学習アプリ")


if __name__ == "__main__":
    main()

