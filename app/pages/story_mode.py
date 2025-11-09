"""
Story mode page - main learning interface.
"""

import streamlit as st

from app.services.session_service import SessionService
from app.services.progress_service import ProgressService
from app.services.ai_service import AIService
from app.services.scenario_generator import ScenarioGenerator
from app.utils.error_handler import ErrorHandler
from app.config.settings import Settings
from app.config.constants import PAGE_NAMES
from app.components.feedback_display import display_feedback_stream
from app.components.progress_bar import display_progress
from app.components.stamp_display import display_mini_stamps
from app.components.loading_animation import show_loading_with_animation
from app.components.debug_panel import display_debug_panel
from app.utils.debug_info import get_debug_collector
import threading


def render_story_mode():
    """ストーリーモード画面を描画"""
    
    # デバッグセッション開始（初回のみ）
    debug_collector = get_debug_collector()
    session_key = "debug_session_started_story_mode"
    
    if session_key not in st.session_state:
        session_id = f"story_mode_{st.session_state.get('user_id', 'unknown')}_{id(st.session_state)}"
        debug_collector.start_session(
            session_id=session_id,
            page="story_mode",
            user_id=st.session_state.get("user_id"),
            mode="story_mode"
        )
        st.session_state[session_key] = True
    
    # セッションから情報を取得
    event = SessionService.get_event()
    user = SessionService.get_user()
    current_scene_number = SessionService.get_scene()
    
    if not event or not user:
        ErrorHandler.show_warning("イベント情報が見つかりません")
        SessionService.set_page(PAGE_NAMES["EVENT_SELECTION"])
        st.rerun()
        return
    
    # デバッグ情報を記録
    debug_collector.add_reference(
        data_type="event",
        source=event.event_name,
        description=f"Scene {current_scene_number}"
    )
    
    # デバッグパネルを表示（サイドバー）
    display_debug_panel(position="sidebar")
    
    # 現在のイベント進捗を取得
    event_progress = user.get_event_progress(event.event_name)
    
    # AI生成モードの設定（デフォルトはオフ）
    use_ai_variation = st.session_state.get("use_ai_variation", False)
    
    # 毎回新しいシナリオを生成するか（キャッシュを無視）
    force_new = st.session_state.get("force_new_scenario", True)  # デフォルトで毎回新規生成
    
    # シーンを取得（AI生成バリエーション or 固定テンプレート）
    scene = get_scene_with_variation(
        event=event,
        scene_number=current_scene_number,
        use_ai_variation=use_ai_variation,
        force_new=force_new
    )
    
    if scene is None:
        # 全シーン完了 → ふりかえりページへ
        SessionService.set_page(PAGE_NAMES["REVIEW"])
        st.rerun()
        return
    
    # セッション状態のキー
    feedback_key = f"feedback_{event.event_name}_{current_scene_number}"
    choice_made_key = f"choice_made_{event.event_name}_{current_scene_number}"
    
    # フィードバック表示状態を初期化
    if feedback_key not in st.session_state:
        st.session_state[feedback_key] = None
    if choice_made_key not in st.session_state:
        st.session_state[choice_made_key] = False
    
    # ヘッダー
    st.title(f"🎮 {event.event_name}")
    
    # デバッグ情報（開発時のみ表示）
    if Settings.DEBUG_MODE:
        with st.expander("🐛 デバッグ情報", expanded=False):
            st.write(f"現在のシーン番号: {current_scene_number}")
            st.write(f"選択済みフラグ: {st.session_state.get(choice_made_key, False)}")
            st.write(f"フィードバック有無: {st.session_state.get(feedback_key) is not None}")
            st.write(f"AIバリエーション: {use_ai_variation}")
            st.write(f"毎回新規生成: {force_new}")
    
    # 進捗バーを表示
    display_progress(current_scene_number + 1, event.total_scenes(), event.event_name)
    
    st.markdown("---")
    
    # 現在の獲得スタンプを表示
    if event_progress:
        display_mini_stamps(event_progress.good_actions_count)
    
    st.markdown("---")
    
    # シーンの説明
    st.markdown(f"### 📖 場面 {current_scene_number + 1}")
    st.markdown(
        f'<div style="font-size: 1.3rem; padding: 1.5rem; '
        f'background-color: #F0F8FF; border-radius: 0.5rem; '
        f'border-left: 4px solid #4682B4; margin-bottom: 1.5rem;">'
        f'{scene.text}'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # TODO: 画像がある場合は表示
    # if scene.image:
    #     st.image(scene.image, use_column_width=True)
    
    st.markdown("---")
    
    # 選択済みかどうかで表示を切り替え
    if not st.session_state[choice_made_key]:
        # 選択肢を表示
        st.subheader("🤔 どうする？")
        
        # セッションに選択結果を保存するキー
        choice_key = f"choice_{event.event_name}_{current_scene_number}"
        
        # 選択肢ボタンを表示
        for idx, choice in enumerate(scene.choices):
            if st.button(
                choice.text,
                key=f"{choice_key}_{idx}",
                use_container_width=True,
                type="primary"
            ):
                # 選択を処理
                handle_choice_selection(
                    user=user,
                    event=event,
                    scene=scene,
                    choice=choice,
                    scene_number=current_scene_number,
                    feedback_key=feedback_key,
                    choice_made_key=choice_made_key
                )
                st.rerun()
    
    else:
        # フィードバックを表示
        if st.session_state[feedback_key]:
            st.markdown("---")
            st.markdown("### 💬 AIからのフィードバック")
            
            feedback_data = st.session_state[feedback_key]
            
            # フィードバック表示（保存されたデータを使用）
            from app.components.feedback_display import display_feedback
            display_feedback(
                feedback_data["text"],
                feedback_data["evaluation"],
                show_animation=False
            )
            
            st.markdown("---")
            
            # 次のシーンへ進むボタン
            if st.button("次へ ➡️", type="primary", use_container_width=True, key="next_scene_btn"):
                # 現在のシーンのキャッシュをクリア（次回は新しいシーンを生成）
                current_cache_key = f"ai_scene_{event.event_name}_{current_scene_number}_session"
                if current_cache_key in st.session_state:
                    del st.session_state[current_cache_key]
                
                # フィードバック状態をクリア
                st.session_state[feedback_key] = None
                st.session_state[choice_made_key] = False
                
                # 次のシーンへ
                SessionService.next_scene()
                st.rerun()
    
    st.markdown("---")
    
    # 戻るボタン
    if st.button("🏠 イベント選択に戻る", key="back_to_selection_btn"):
        # フィードバック状態をクリア
        st.session_state[feedback_key] = None
        st.session_state[choice_made_key] = False
        
        # AI生成シーンのキャッシュもクリア（次回は新しいシーンを生成）
        for key in list(st.session_state.keys()):
            if key.startswith(f"ai_scene_{event.event_name}_") or key.startswith("debug_session_started_"):
                del st.session_state[key]
        
        # デバッグセッションを終了
        debug_collector = get_debug_collector()
        debug_collector.end_session()
        
        SessionService.set_page(PAGE_NAMES["EVENT_SELECTION"])
        st.rerun()


def handle_choice_selection(user, event, scene, choice, scene_number, feedback_key, choice_made_key):
    """
    選択肢が選ばれたときの処理
    
    Args:
        user: Userオブジェクト
        event: Eventオブジェクト
        scene: Sceneオブジェクト
        choice: Choiceオブジェクト
        scene_number: 現在のシーン番号
        feedback_key: フィードバック保存用のセッションキー
        choice_made_key: 選択済みフラグのセッションキー
    """
    
    try:
        # 楽しい待ち時間アニメーションを表示
        animation_placeholder = st.empty()
        result_container = {"feedback_text": None, "error": None}
        
        def generate_feedback_async():
            """バックグラウンドでフィードバックを生成"""
            try:
                # AIサービスを初期化
                ai_service = AIService()
                
                # ai_feedback_hintを安全に取得
                hint = getattr(choice, 'ai_feedback_hint', '')
                
                # AIフィードバックを生成
                feedback_text = ai_service.generate_feedback(
                    scene_text=scene.text,
                    selected_choice=choice.text,
                    evaluation=choice.evaluation,
                    hint=hint
                )
                
                # フィードバックが空の場合のフォールバック
                if not feedback_text or feedback_text.strip() == "":
                    feedback_text = "よく考えましたね！"
                
                result_container["feedback_text"] = feedback_text
            except Exception as e:
                result_container["error"] = e
        
        # アニメーションとAI生成を並行実行
        feedback_thread = threading.Thread(target=generate_feedback_async)
        feedback_thread.start()
        
        # アニメーションを表示（子供が楽しめる）
        if Settings.ENABLE_FUN_LOADING:
            with animation_placeholder.container():
                show_loading_with_animation(animation_type=Settings.LOADING_ANIMATION_TYPE)
        else:
            # シンプルなスピナーのみ
            with animation_placeholder:
                st.spinner("🤔 AIがかんがえています...")
        
        # AI生成の完了を待つ
        feedback_thread.join()
        
        # アニメーションをクリア
        animation_placeholder.empty()
        
        # エラーチェック
        if result_container["error"]:
            raise result_container["error"]
        
        # フィードバックをセッション状態に保存
        st.session_state[feedback_key] = {
            "text": result_container["feedback_text"],
            "evaluation": choice.evaluation
        }
        
        # 選択済みフラグを立てる
        st.session_state[choice_made_key] = True
        
        # 進捗サービスを初期化
        progress_service = ProgressService()
        
        # 進捗を更新
        progress_service.update_scene_progress(
            user=user,
            event_name=event.event_name,
            scene_number=scene_number,
            selected_choice=choice.text,
            evaluation=choice.evaluation
        )
        
        # セッションのユーザー情報を更新
        updated_user = progress_service.load_user_progress(user.user_id)
        if updated_user:
            SessionService.set_user(updated_user)
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        
        # エラー詳細をログに記録
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"選択処理エラー: {error_detail}")
        
        # ユーザーにエラーを表示
        st.error(f"⚠️ エラーが発生しました: {str(e)}")
        st.error("デバッグ情報:")
        st.code(error_detail)
        
        # エラー時もフラグを立てて進行できるようにする
        st.session_state[choice_made_key] = True
        st.session_state[feedback_key] = {
            "text": "申し訳ございません。フィードバックの生成に失敗しました。",
            "evaluation": choice.evaluation
        }


def get_scene_with_variation(event, scene_number: int, use_ai_variation: bool = False, force_new: bool = False):
    """
    シーンを取得（AI生成バリエーション or 固定テンプレート）
    
    Args:
        event: Eventオブジェクト
        scene_number: シーン番号
        use_ai_variation: AI生成バリエーションを使用するか
        force_new: キャッシュを無視して毎回新規生成するか
        
    Returns:
        Scene object or AI-generated scene data
    """
    # 固定テンプレートのシーンを取得
    base_scene = event.get_scene(scene_number)
    
    if base_scene is None:
        return None
    
    # AI生成モードがオフの場合、または既に生成済みの場合は固定テンプレートを返す
    if not use_ai_variation:
        return base_scene
    
    # AI生成バリエーションを試みる
    try:
        scenario_gen = ScenarioGenerator()
        
        # キャッシュキーをチェック（シーンごとに異なるキー）
        # force_newがTrueの場合でも、同じセッション内では同じシーンを返す
        session_cache_key = f"ai_scene_{event.event_name}_{scene_number}_session"
        
        # 同じセッション内では同じシーンを返す（リロード対策）
        if session_cache_key in st.session_state:
            return create_scene_from_dict(st.session_state[session_cache_key])
        
        # AI生成（force_newの値を渡す）
        scene_dict = scenario_gen.get_scene_with_variation(
            event_name=event.event_name,
            scene_number=scene_number,
            use_ai_generation=True,
            force_new=force_new  # 毎回新規生成するかどうか
        )
        
        if scene_dict:
            # セッションにキャッシュ（このセッション中は同じシーンを使う）
            st.session_state[session_cache_key] = scene_dict
            return create_scene_from_dict(scene_dict)
        
        # AI生成失敗時は固定テンプレートにフォールバック
        return base_scene
        
    except Exception as e:
        ErrorHandler.handle_error(e, "シーンのバリエーション生成に失敗しました")
        return base_scene


def create_scene_from_dict(scene_dict: dict):
    """
    辞書形式のシーンデータからSceneオブジェクトのようなオブジェクトを生成
    
    Args:
        scene_dict: シーンデータの辞書
        
    Returns:
        Scene-like object
    """
    from app.models.event import Choice
    
    class SceneVariation:
        """AI生成されたシーンバリエーション"""
        def __init__(self, text, image, choices):
            self.text = text
            self.image = image
            self.choices = [
                Choice(
                    text=c.get("text", ""),
                    evaluation=c.get("evaluation", "acceptable"),
                    ai_feedback_hint=c.get("hint", "")
                )
                for c in choices
            ]
    
    return SceneVariation(
        text=scene_dict.get("situation_text", scene_dict.get("text", "")),
        image=scene_dict.get("image", ""),
        choices=scene_dict.get("choices", [])
    )

