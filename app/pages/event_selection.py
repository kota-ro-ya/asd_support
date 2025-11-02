"""
Event selection page.
"""

import streamlit as st
from pathlib import Path

from app.models.event import Event
from app.services.session_service import SessionService
from app.services.progress_service import ProgressService
from app.utils.file_handler import FileHandler
from app.utils.error_handler import ErrorHandler
from app.config.settings import Settings
from app.config.constants import EVENT_NAMES, EVENT_FILE_MAPPING, PAGE_NAMES
from app.components.progress_bar import display_overall_progress


def render_event_selection():
    """イベント選択画面を描画"""
    
    # ユーザー情報を取得
    user = SessionService.get_user()
    nickname = SessionService.get_nickname()
    
    if not user or not nickname:
        # ユーザーが未登録の場合、登録画面を表示
        render_user_registration()
        return
    
    # ヘッダー
    st.title(f"🌟 {nickname}さん、今日はどこへ行こう？")
    
    # モード選択に戻るボタン
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🏠 モード選択に戻る", use_container_width=True):
            SessionService.set_page(PAGE_NAMES["MODE_SELECTION"])
            st.rerun()
    
    st.markdown("---")
    
    # 全体の進捗状況を表示
    with st.expander("📊 これまでの進捗を見る", expanded=False):
        display_overall_progress(user)
    
    st.markdown("---")
    
    # AI生成モードの切り替え（目立つように大きく表示）
    st.markdown("---")
    st.markdown("### 🎯 学びたい場面を選んでね")
    
    # 目立つボックスで囲む
    st.markdown(
        """
        <div style="background-color: #FFF9E6; padding: 1.5rem; border-radius: 0.8rem; 
        border: 3px solid #FFA500; margin-bottom: 1rem;">
            <h3 style="margin-top: 0; color: #FF8C00;">⚙️ AI設定（ここで選んでね！）</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🤖 AIバリエーション")
        use_ai_variation = st.checkbox(
            "AIが毎回違う問題を作ります",
            value=st.session_state.get("use_ai_variation", False),
            key="use_ai_variation_checkbox",
            help="オンにすると、AIが毎回異なるシナリオを生成します"
        )
        st.session_state["use_ai_variation"] = use_ai_variation
    
    with col2:
        if use_ai_variation:
            st.markdown("### 🔄 毎回新しく生成")
            force_new = st.checkbox(
                "いつも新しい問題にする",
                value=st.session_state.get("force_new_scenario", True),
                key="force_new_scenario_checkbox",
                help="オンにすると、キャッシュを使わず毎回新しい内容を生成します"
            )
            st.session_state["force_new_scenario"] = force_new
        else:
            st.markdown("### 🔄 毎回新しく生成")
            st.markdown("_（左側をオンにすると選べます）_")
    
    # AIモードの説明（大きく目立つように）
    if use_ai_variation:
        if st.session_state.get("force_new_scenario", True):
            st.markdown(
                """
                <div style="background-color: #E8F5E9; padding: 1.2rem; border-radius: 0.5rem; 
                border-left: 5px solid #4CAF50; margin: 1rem 0;">
                    <p style="font-size: 1.2rem; margin: 0; color: #2E7D32;">
                        ✅ <strong>設定完了！</strong> 場面1、場面2ともに毎回完全に違う内容が出てきます！
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background-color: #FFF3E0; padding: 1.2rem; border-radius: 0.5rem; 
                border-left: 5px solid #FF9800; margin: 1rem 0;">
                    <p style="font-size: 1.1rem; margin: 0; color: #E65100;">
                        ⚠️ 一度作った問題は24時間同じものが出ます
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            """
            <div style="background-color: #E3F2FD; padding: 1.2rem; border-radius: 0.5rem; 
            border-left: 5px solid #2196F3; margin: 1rem 0;">
                <p style="font-size: 1.1rem; margin: 0; color: #1565C0;">
                    📘 いつもと同じ問題で練習します
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # イベントカードを表示
    cols = st.columns(2)
    
    for idx, event_name in enumerate(EVENT_NAMES):
        with cols[idx % 2]:
            render_event_card(event_name, user)
    
    st.markdown("---")
    
    # フッター
    st.caption("💡 ヒント: 各イベントをクリックして、その場面での行動を学びましょう！")


def render_user_registration():
    """ユーザー登録画面を描画"""
    
    st.title("🎮 ASD支援アプリへようこそ！")
    st.markdown("---")
    
    st.subheader("はじめに、ニックネームを教えてください")
    
    nickname = st.text_input(
        "ニックネーム（1〜20文字）",
        max_chars=20,
        placeholder="例: ぽんたくん",
        key="nickname_input"
    )
    
    if st.button("はじめる！", type="primary", use_container_width=True):
        if nickname and nickname.strip():
            # 新しいユーザーを作成
            progress_service = ProgressService()
            user = progress_service.create_new_user(nickname.strip())
            
            if user:
                SessionService.set_user(user)
                ErrorHandler.show_success(f"ようこそ、{nickname}さん！")
                st.rerun()
            else:
                ErrorHandler.show_warning("ユーザーの作成に失敗しました。もう一度お試しください。")
        else:
            ErrorHandler.show_warning("ニックネームを入力してください")
    
    st.markdown("---")
    st.info("💡 このアプリでは、日常生活のいろいろな場面での行動を学ぶことができます。")


def render_event_card(event_name: str, user):
    """
    イベントカードを描画
    
    Args:
        event_name: イベント名
        user: Userオブジェクト
    """
    
    # イベントの進捗情報を取得
    event_progress = user.get_event_progress(event_name)
    
    # 完了状態を確認
    is_completed = event_progress and event_progress.completed
    completion_icon = "✅" if is_completed else "📍"
    
    # スタンプ数
    stamps = event_progress.stamps_earned if event_progress else 0
    stamp_display = "⭐" * stamps if stamps > 0 else ""
    
    # カードの背景色
    bg_color = "#E8F5E9" if is_completed else "#FFFFFF"
    border_color = "#4CAF50" if is_completed else "#DDD"
    
    # カード表示
    st.markdown(
        f'<div style="padding: 1.5rem; border-radius: 0.5rem; '
        f'background-color: {bg_color}; border: 2px solid {border_color}; '
        f'margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
        f'<h3 style="margin: 0;">{completion_icon} {event_name}</h3>'
        f'<p style="margin: 0.5rem 0; color: #666;">プレイ回数: {event_progress.play_count if event_progress else 0}回</p>'
        f'<p style="margin: 0; font-size: 1.2rem;">{stamp_display}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # イベント開始ボタン
    button_text = "もう一度挑戦" if is_completed else "はじめる"
    
    if st.button(
        button_text,
        key=f"event_btn_{event_name}",
        type="primary" if not is_completed else "secondary",
        use_container_width=True
    ):
        # イベントデータを読み込む
        event_file = EVENT_FILE_MAPPING.get(event_name)
        if event_file:
            event_path = Settings.EVENTS_DIR / event_file
            event_data = FileHandler.read_json(event_path)
            
            if event_data:
                event = Event.from_dict(event_data)
                
                # イベントをリセット（新しくプレイする場合）
                if is_completed:
                    progress_service = ProgressService()
                    progress_service.reset_event_progress(user, event_name)
                
                # セッションに保存
                SessionService.set_event(event)
                SessionService.set_scene(0)
                SessionService.set_page(PAGE_NAMES["STORY_MODE"])
                
                st.rerun()
            else:
                ErrorHandler.show_warning(f"{event_name}のデータ読み込みに失敗しました")
        else:
            ErrorHandler.show_warning(f"{event_name}のファイルが見つかりません")

