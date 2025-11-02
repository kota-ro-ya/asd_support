"""
Stamp display component.
"""

import streamlit as st
from app.config.constants import STAMP_THRESHOLDS


def display_stamps(good_actions_count: int):
    """
    獲得したスタンプを表示する
    
    Args:
        good_actions_count: 適切な行動の回数
    """
    
    st.markdown("### 🎁 獲得したスタンプ")
    
    # スタンプの判定
    stamps = []
    if good_actions_count >= STAMP_THRESHOLDS["gold"]:
        stamps = ["🥇", "🥈", "🥉"]
        message = "ゴールドスタンプ獲得！完璧だね！✨"
    elif good_actions_count >= STAMP_THRESHOLDS["silver"]:
        stamps = ["🥈", "🥉"]
        message = "シルバースタンプ獲得！とても良くできたね！"
    elif good_actions_count >= STAMP_THRESHOLDS["bronze"]:
        stamps = ["🥉"]
        message = "ブロンズスタンプ獲得！よく頑張ったね！"
    else:
        stamps = []
        message = "次回はスタンプを目指して頑張ろう！"
    
    # スタンプ表示
    if stamps:
        cols = st.columns(len(stamps))
        for i, stamp in enumerate(stamps):
            with cols[i]:
                st.markdown(
                    f'<div style="font-size: 4rem; text-align: center;">{stamp}</div>',
                    unsafe_allow_html=True
                )
    
    st.success(message)


def display_stamps_summary(user_events: list):
    """
    全イベントのスタンプ獲得状況を表示する
    
    Args:
        user_events: EventProgressのリスト
    """
    
    st.markdown("### 🏆 スタンプコレクション")
    
    total_stamps = 0
    
    for event in user_events:
        if event.stamps_earned > 0:
            st.markdown(f"**{event.event_name}**: {'⭐' * event.stamps_earned}")
            total_stamps += event.stamps_earned
    
    if total_stamps == 0:
        st.info("まだスタンプを獲得していません。イベントに挑戦してみよう！")
    else:
        st.success(f"合計 {total_stamps} 個のスタンプを獲得しました！")


def display_mini_stamps(good_actions_count: int):
    """
    小さいスタンプ表示（進行中の表示用）
    
    Args:
        good_actions_count: 適切な行動の回数
    """
    
    stamp_display = "⭐" * good_actions_count
    
    if stamp_display:
        st.markdown(
            f'<div style="font-size: 1.5rem; padding: 0.5rem; '
            f'background-color: #FFF8DC; border-radius: 0.5rem; text-align: center;">'
            f'{stamp_display} ({good_actions_count}個)'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="font-size: 1rem; padding: 0.5rem; '
            f'background-color: #F0F0F0; border-radius: 0.5rem; text-align: center; color: #888;">'
            f'まだスタンプがありません'
            f'</div>',
            unsafe_allow_html=True
        )

