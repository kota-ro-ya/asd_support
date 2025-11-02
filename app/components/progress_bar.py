"""
Progress bar component.
"""

import streamlit as st


def display_progress(current_scene: int, total_scenes: int, event_name: str):
    """
    イベントの進捗バーを表示する
    
    Args:
        current_scene: 現在のシーン番号
        total_scenes: シーンの総数
        event_name: イベント名
    """
    
    st.markdown(f"### 📍 {event_name}の進行状況")
    
    # 進捗率を計算
    if total_scenes > 0:
        progress = (current_scene / total_scenes)
    else:
        progress = 0.0
    
    # プログレスバー表示
    st.progress(progress)
    
    # テキスト表示
    st.markdown(
        f'<div style="text-align: center; color: #666; margin-top: 0.5rem;">'
        f'シーン {current_scene} / {total_scenes}'
        f'</div>',
        unsafe_allow_html=True
    )


def display_event_progress_card(event_progress):
    """
    イベント進捗カードを表示する
    
    Args:
        event_progress: EventProgressオブジェクト
    """
    
    # 完了マーク
    completion_icon = "✅" if event_progress.completed else "⏳"
    
    # カラー設定
    bg_color = "#E8F5E9" if event_progress.completed else "#FFF"
    
    st.markdown(
        f'<div style="padding: 1rem; border-radius: 0.5rem; '
        f'background-color: {bg_color}; border: 1px solid #DDD; margin-bottom: 1rem;">'
        f'<h4>{completion_icon} {event_progress.event_name}</h4>'
        f'<p>✨ 適切な行動: {event_progress.good_actions_count}回</p>'
        f'<p>👍 許容される行動: {event_progress.acceptable_actions_count}回</p>'
        f'<p>💭 不適切な行動: {event_progress.inappropriate_actions_count}回</p>'
        f'<p>⭐ スタンプ: {event_progress.stamps_earned}個</p>'
        f'<p>🎮 プレイ回数: {event_progress.play_count}回</p>'
        f'</div>',
        unsafe_allow_html=True
    )


def display_overall_progress(user):
    """
    全体の進捗状況を表示する
    
    Args:
        user: Userオブジェクト
    """
    
    st.markdown("### 📊 全体の進捗")
    
    total_events = len(user.events)
    completed_events = sum(1 for event in user.events if event.completed)
    total_good_actions = sum(event.good_actions_count for event in user.events)
    total_stamps = sum(event.stamps_earned for event in user.events)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("完了イベント", f"{completed_events}/{total_events}")
    
    with col2:
        st.metric("適切な行動", f"{total_good_actions}回")
    
    with col3:
        st.metric("獲得スタンプ", f"{total_stamps}個")
    
    with col4:
        if total_events > 0:
            completion_rate = (completed_events / total_events) * 100
            st.metric("達成率", f"{completion_rate:.0f}%")
        else:
            st.metric("達成率", "0%")

