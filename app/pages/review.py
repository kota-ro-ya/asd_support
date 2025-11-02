"""
Review page - display results and stamps.
"""

import streamlit as st

from app.services.session_service import SessionService
from app.services.progress_service import ProgressService
from app.utils.error_handler import ErrorHandler
from app.config.constants import PAGE_NAMES, STAMP_THRESHOLDS
from app.components.stamp_display import display_stamps


def render_review():
    """ふりかえり画面を描画"""
    
    # セッションから情報を取得
    event = SessionService.get_event()
    user = SessionService.get_user()
    
    if not event or not user:
        ErrorHandler.show_warning("イベント情報が見つかりません")
        SessionService.set_page(PAGE_NAMES["EVENT_SELECTION"])
        st.rerun()
        return
    
    # イベントの進捗を取得
    event_progress = user.get_event_progress(event.event_name)
    
    if not event_progress:
        ErrorHandler.show_warning("進捗情報が見つかりません")
        SessionService.set_page(PAGE_NAMES["EVENT_SELECTION"])
        st.rerun()
        return
    
    # ヘッダー
    st.title("🎉 おつかれさま！")
    st.markdown(f"### {event.event_name}のふりかえり")
    
    st.markdown("---")
    
    # 結果を表示
    st.subheader("📊 今回の結果")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "✨ 適切な行動",
            f"{event_progress.good_actions_count}回",
            delta=None
        )
    
    with col2:
        st.metric(
            "👍 許容される行動",
            f"{event_progress.acceptable_actions_count}回",
            delta=None
        )
    
    with col3:
        st.metric(
            "💭 不適切な行動",
            f"{event_progress.inappropriate_actions_count}回",
            delta=None
        )
    
    st.markdown("---")
    
    # スタンプの計算と付与
    good_count = event_progress.good_actions_count
    stamps_to_award = 0
    
    if good_count >= STAMP_THRESHOLDS["gold"]:
        stamps_to_award = 3
    elif good_count >= STAMP_THRESHOLDS["silver"]:
        stamps_to_award = 2
    elif good_count >= STAMP_THRESHOLDS["bronze"]:
        stamps_to_award = 1
    
    # スタンプを付与（まだ完了していない場合）
    if not event_progress.completed:
        progress_service = ProgressService()
        progress_service.complete_event(
            user=user,
            event_name=event.event_name,
            stamps_earned=stamps_to_award
        )
        
        # ユーザー情報を再読み込み
        updated_user = progress_service.load_user_progress(user.user_id)
        if updated_user:
            SessionService.set_user(updated_user)
            event_progress = updated_user.get_event_progress(event.event_name)
    
    # スタンプを表示
    display_stamps(good_count)
    
    st.markdown("---")
    
    # メッセージ
    if good_count >= STAMP_THRESHOLDS["gold"]:
        message = "完璧です！とても素晴らしい判断ができました！✨"
        st.balloons()
    elif good_count >= STAMP_THRESHOLDS["silver"]:
        message = "とても良くできました！この調子で頑張りましょう！👏"
    elif good_count >= STAMP_THRESHOLDS["bronze"]:
        message = "よく頑張りました！少しずつ上達していますよ！💪"
    else:
        message = "挑戦してくれてありがとう！次はもっと良くなりますよ！😊"
    
    st.success(message)
    
    st.markdown("---")
    
    # 詳細な振り返り
    with st.expander("📝 詳しい振り返りを見る", expanded=False):
        st.markdown("### シーンごとの行動")
        
        for i, scene_record in enumerate(event_progress.scene_history[-event.total_scenes():]):
            evaluation_icon = "✨" if scene_record["evaluation"] == "appropriate" else "👍" if scene_record["evaluation"] == "acceptable" else "💭"
            
            st.markdown(
                f"**シーン {scene_record['scene_number'] + 1}:** "
                f"{evaluation_icon} {scene_record['selected_choice']}"
            )
    
    st.markdown("---")
    
    # ボタン
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 もう一度挑戦", use_container_width=True, type="secondary"):
            # イベントをリセットして再開
            progress_service = ProgressService()
            progress_service.reset_event_progress(user, event.event_name)
            
            # ユーザー情報を再読み込み
            updated_user = progress_service.load_user_progress(user.user_id)
            if updated_user:
                SessionService.set_user(updated_user)
            
            SessionService.set_scene(0)
            SessionService.set_page(PAGE_NAMES["STORY_MODE"])
            st.rerun()
    
    with col2:
        if st.button("🎯 イベント選択", use_container_width=True, type="primary"):
            SessionService.set_page(PAGE_NAMES["EVENT_SELECTION"])
            st.rerun()
    
    with col3:
        if st.button("🏠 モード選択", use_container_width=True, type="primary"):
            SessionService.set_page(PAGE_NAMES["MODE_SELECTION"])
            st.rerun()

