"""
Main mode selection page - Choose between child events and parent guide.
"""

import streamlit as st
from app.services.session_service import SessionService
from app.config.constants import PAGE_NAMES


def render_mode_selection():
    """メインモード選択画面を描画"""
    
    # ユーザー情報を取得
    user = SessionService.get_user()
    nickname = SessionService.get_nickname()
    
    if not user or not nickname:
        # ユーザーが未登録の場合、登録画面を表示
        from app.pages.event_selection import render_user_registration
        render_user_registration()
        return
    
    # ヘッダー
    st.title(f"🌟 {nickname}さん、ようこそ！")
    st.markdown("---")
    
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style="color: #1976D2;">どちらのモードを利用しますか？</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 2カラムレイアウトでモード選択
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        render_child_mode_card()
    
    with col2:
        render_parent_mode_card()
    
    st.markdown("---")
    st.caption("💡 いつでもこの画面に戻って、別のモードを選ぶことができます。")


def render_child_mode_card():
    """子供向けモードのカードを描画"""
    
    st.markdown(
        """
        <div style="padding: 2rem; border-radius: 1rem; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; text-align: center; min-height: 300px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🎮</div>
            <h2 style="color: white; margin-bottom: 1rem;">子供向けモード</h2>
            <p style="font-size: 1.1rem; margin-bottom: 1.5rem;">
                日常生活のいろいろな場面で<br>
                どうすればいいかを学ぼう！
            </p>
            <ul style="text-align: left; margin: 0 auto; max-width: 280px; font-size: 1rem;">
                <li>トイレ、床屋、病院など</li>
                <li>楽しいストーリーで学習</li>
                <li>スタンプを集めよう！</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button(
        "🎮 子供向けモードを始める",
        key="child_mode_btn",
        type="primary",
        use_container_width=True
    ):
        SessionService.set_page(PAGE_NAMES["EVENT_SELECTION"])
        st.rerun()


def render_parent_mode_card():
    """保護者向けモードのカードを描画"""
    
    st.markdown(
        """
        <div style="padding: 2rem; border-radius: 1rem; 
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white; text-align: center; min-height: 300px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">👨‍👩‍👧</div>
            <h2 style="color: white; margin-bottom: 1rem;">保護者向けガイド</h2>
            <p style="font-size: 1.1rem; margin-bottom: 1.5rem;">
                お子さんへの対応方法を<br>
                シチュエーション別に学ぶ
            </p>
            <ul style="text-align: left; margin: 0 auto; max-width: 280px; font-size: 1rem;">
                <li>実際の場面での対応例</li>
                <li>AI による解説とアドバイス</li>
                <li>適切な関わり方のヒント</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button(
        "👨‍👩‍👧 保護者向けガイドを見る",
        key="parent_mode_btn",
        type="primary",
        use_container_width=True
    ):
        SessionService.set_page(PAGE_NAMES["PARENT_GUIDE"])
        st.rerun()

