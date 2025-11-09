"""
Parent guide page - Situation-based guidance for parents.
"""

import streamlit as st
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.services.session_service import SessionService
from app.services.ai_service import AIService
# from app.services.rag_service import RAGService  # 専門エージェントシステムに置き換え
from app.services.scenario_generator import ScenarioGenerator
from app.services.specialized_agent_service import SpecializedAgentService
from app.config.settings import Settings
from app.config.constants import PAGE_NAMES
from app.utils.file_handler import FileHandler
from app.utils.error_handler import ErrorHandler
from app.components.debug_panel import display_debug_panel
from app.utils.debug_info import get_debug_collector

logger = logging.getLogger(__name__)


def display_sequential_responses(service, question, context, tone):
    """各専門家が順番にストリーミング表示"""
    full_answer = ""
    current_agent = None
    current_response = ""
    placeholder = None
    
    for chunk_data in service.generate_sequential_expert_responses_stream(question, context, tone):
        if chunk_data["chunk"] == "__START__":
            # 新しい専門家の開始
            current_agent = chunk_data
            current_response = ""
            
            # ヘッダー表示
            st.markdown(f"### {chunk_data['agent_icon']} {chunk_data['agent_name']}の見解")
            placeholder = st.empty()
            
        elif chunk_data["chunk"] == "__END__":
            # 現在の専門家の回答終了
            full_answer += f"\n\n### {current_agent['agent_icon']} {current_agent['agent_name']}の見解\n{current_response}\n"
            current_agent = None
            current_response = ""
            placeholder = None
            
        else:
            # ストリーミング表示
            current_response += chunk_data["chunk"]
            if placeholder:
                placeholder.markdown(current_response)
    
    return full_answer


def handle_question_submission(
    question: str,
    action_idx: int,
    event: str,
    child_action: str,
    action_text: str,
    evaluation: str,
    chat_history_key: str,
    question_counter_key: str,
    custom_response_mode: str,
    custom_selected_expert: str,
    tone_mode_key: str,
    is_free_question: bool = False
):
    """質問を処理して回答を生成する共通関数
    
    Args:
        is_free_question: Trueの場合、シチュエーションのコンテキストを含めない（自由質問モード）
    """
    # セッション状態の初期化
    if chat_history_key not in st.session_state:
        st.session_state[chat_history_key] = []
    if question_counter_key not in st.session_state:
        st.session_state[question_counter_key] = 0
    
    # 自由質問の場合はシチュエーションのコンテキストを含めない
    if is_free_question:
        context = """
これはASD支援に関する一般的な質問です。シチュエーションに限定されない、保護者の方への包括的なアドバイスをお願いします。

過去の会話履歴:
"""
    else:
        context = f"""
シチュエーション: {event}でお子さんが「{child_action}」しています。
保護者の対応: 「{action_text}」
評価: {evaluation}

過去の会話履歴:
"""
    
    # 過去の会話履歴をコンテキストに追加
    for chat in st.session_state.get(chat_history_key, []):
        context += f"\nQ: {chat['question']}\nA: {chat['answer'][:200]}...\n"
    
    try:
        specialized_service = SpecializedAgentService()
        
        # 口調は詳細解説と同じものを使用
        tone = "friendly" if "フレンドリー" in st.session_state.get(tone_mode_key, "フレンドリー") else "standard"
        
        # 回答を格納する変数
        full_answer = ""
        expert_name = ""
        
        if "1人の専門家" in custom_response_mode:
            # 選択された専門家による回答
            if custom_selected_expert:
                agent_id = specialized_service.get_agent_id_from_display_name(custom_selected_expert)
                if agent_id:
                    agent_info = specialized_service.get_agent_info(agent_id)
                    expert_name = f"{agent_info['icon']} {agent_info['name']}"
                    
                    st.markdown(f"### {expert_name}からの回答")
                    
                    stream_generator = specialized_service.generate_single_expert_response_stream(
                        agent_id=agent_id,
                        question=question,
                        context=context,
                        tone=tone
                    )
                    full_answer = st.write_stream(stream_generator)
                else:
                    st.error("専門家の選択に失敗しました")
                    return
            else:
                st.warning("専門家を選択してください")
                return
            
        elif "4人の専門家" in custom_response_mode:
            # 順番モード：4人が順番にストリーミング表示
            expert_name = "👥 4人の専門家チーム"
            full_answer = display_sequential_responses(
                specialized_service,
                question,
                context,
                tone
            )
            
        else:  # 統合回答
            # 統合モード：15-20秒待ってから統合回答
            expert_name = "🔄 統合回答（4人の専門家）"
            stream_generator = specialized_service.generate_comprehensive_response_stream(
                question=question,
                context=context,
                tone=tone
            )
            full_answer = st.write_stream(stream_generator)
        
        # 回答が空でないことを確認
        if not full_answer or not full_answer.strip():
            st.warning("回答が生成されませんでした。もう一度お試しください。")
            return
        
        # 会話履歴に追加
        st.session_state[chat_history_key].append({
            "question": question,
            "answer": full_answer,
            "expert": expert_name
        })
        
        # 質問カウンターをインクリメント
        st.session_state[question_counter_key] += 1
        
        # 候補質問をクリア（新しい質問を生成するため）
        suggested_questions_key = f"suggested_questions_{action_idx}"
        if suggested_questions_key in st.session_state:
            del st.session_state[suggested_questions_key]
        
        # 質問フィールドをクリアするためにrerun
        st.rerun()
        
    except Exception as e:
        ErrorHandler.handle_error(e, "専門家への質問中にエラーが発生しました")
        st.error(f"申し訳ございません。専門家への質問中にエラーが発生しました: {str(e)}")
        logger.error(f"Error in handle_question_submission: {e}", exc_info=True)


def render_parent_guide():
    """保護者向けガイド画面を描画"""
    
    # デバッグセッション開始（初回のみ）
    debug_collector = get_debug_collector()
    session_key = "debug_session_started_parent_guide"
    
    if session_key not in st.session_state:
        session_id = f"parent_guide_{st.session_state.get('user_id', 'unknown')}_{id(st.session_state)}"
        debug_collector.start_session(
            session_id=session_id,
            page="parent_guide",
            user_id=st.session_state.get("user_id"),
            mode="parent_guide"
        )
        st.session_state[session_key] = True
    
    # ユーザー情報を取得
    user = SessionService.get_user()
    nickname = SessionService.get_nickname()
    
    if not user or not nickname:
        st.warning("⚠️ ユーザー情報が見つかりません。")
        if st.button("モード選択に戻る"):
            SessionService.set_page(PAGE_NAMES["MODE_SELECTION"])
            st.rerun()
        return
    
    # デバッグパネルを表示（サイドバー）
    display_debug_panel(position="sidebar")
    
    # ヘッダー
    st.title("👨‍👩‍👧 保護者向けシチュエーション別ガイド")
    
    # モード選択に戻るボタン
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🏠 モード選択に戻る", use_container_width=True):
            # 保護者向けガイド関連のセッション情報をクリア
            keys_to_clear = [key for key in st.session_state.keys() 
                           if any(prefix in key for prefix in [
                               "chat_history_", 
                               "brief_expert_", 
                               "pre_selected_expert_",
                               "brief_feedback_",
                               "detailed_feedback_",
                               "show_detailed_",
                               "custom_response_mode_",
                               "custom_selected_expert_",
                               "question_counter_",
                               "response_mode_",
                               "tone_mode_",
                               "suggested_questions_",
                               "selected_suggested_question_",
                               "pending_suggested_question_",
                               "selected_action_idx",
                               "selected_situation",
                               "debug_session_started_"  # デバッグセッションもクリア
                           ])]
            for key in keys_to_clear:
                del st.session_state[key]
            
            # デバッグセッションを終了
            debug_collector = get_debug_collector()
            debug_collector.end_session()
            
            SessionService.set_page(PAGE_NAMES["MODE_SELECTION"])
            st.rerun()
    
    st.markdown("---")
    
    # 説明
    st.markdown(
        """
        <div style="padding: 1.5rem; background-color: #FFF3E0; border-radius: 0.5rem; border-left: 4px solid #FF9800;">
            <h4 style="margin-top: 0; color: #E65100;">このガイドについて</h4>
            <p style="margin-bottom: 0;">
                お子さんが様々な場面で困った行動をとった時、保護者としてどう対応すればよいかを学ぶことができます。<br>
                実際のシチュエーションを選んで、適切な対応方法をAIと一緒に考えましょう。
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # AI生成モードの切り替え
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📋 シチュエーションを選択してください")
    with col2:
        use_ai_generation = st.checkbox(
            "🤖 AI生成",
            value=st.session_state.get("use_ai_generation", False),
            help="オンにすると、AIが新しいシチュエーションを生成します"
        )
        st.session_state["use_ai_generation"] = use_ai_generation
    
    # ガイドデータを読み込む
    guide_data = load_guide_data()
    
    if not guide_data:
        st.error("⚠️ ガイドデータの読み込みに失敗しました。")
        return
    
    # シチュエーション選択
    situation_guides = guide_data.get("situation_guides", [])
    
    if not situation_guides:
        st.warning("現在、利用可能なシチュエーションがありません。")
        return
    
    # シチュエーションをグループ化（イベント別）
    situations_by_event = group_situations_by_event(situation_guides)
    
    # 選択されたシチュエーションを取得
    selected_situation = st.session_state.get("selected_situation")
    
    if selected_situation is None:
        # シチュエーション選択画面
        render_situation_selection(situations_by_event, use_ai_generation)
    else:
        # 選択されたシチュエーションの詳細を表示
        if isinstance(selected_situation, dict):
            # AI生成されたシチュエーション
            render_situation_detail(selected_situation)
        else:
            # 既存のシチュエーション（インデックス）
            render_situation_detail(situation_guides[selected_situation])


def load_guide_data() -> Optional[Dict]:
    """ガイドデータを読み込む"""
    guide_path = Settings.DATA_DIR / "parent_guide_data.json"
    return FileHandler.read_json(guide_path)


def group_situations_by_event(situations: List[Dict]) -> Dict[str, List[Dict]]:
    """シチュエーションをイベント別にグループ化"""
    grouped = {}
    
    for idx, situation in enumerate(situations):
        event = situation.get("event", "その他")
        if event not in grouped:
            grouped[event] = []
        
        # インデックスを追加
        situation_with_idx = situation.copy()
        situation_with_idx["index"] = idx
        grouped[event].append(situation_with_idx)
    
    return grouped


def render_situation_selection(situations_by_event: Dict[str, List[Dict]], use_ai_generation: bool = False):
    """シチュエーション選択画面を描画"""
    
    for event_name, situations in situations_by_event.items():
        st.markdown(f"### 🎯 {event_name}")
        
        # AI生成モードの場合、「新しいシチュエーションを生成」ボタンを追加
        if use_ai_generation:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button(
                    "✨ 新規生成",
                    key=f"generate_new_{event_name}",
                    use_container_width=True,
                    type="primary"
                ):
                    # AI生成
                    with st.spinner("AIが新しいシチュエーションを生成中..."):
                        scenario_gen = ScenarioGenerator()
                        new_situation = scenario_gen.generate_random_parent_situation(event_name)
                        
                        if new_situation:
                            st.session_state["selected_situation"] = new_situation
                            st.success("✅ 新しいシチュエーションを生成しました！")
                            st.rerun()
                        else:
                            ErrorHandler.show_warning("シチュエーションの生成に失敗しました。既存のものから選択してください。")
        
        # 既存のシチュエーション一覧
        for situation in situations:
            child_action = situation.get("child_action", "")
            scene_number = situation.get("scene_number", 0)
            idx = situation.get("index", 0)
            
            # カード表示
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(
                    f"""
                    <div style="padding: 1rem; background-color: #F5F5F5; 
                    border-radius: 0.5rem; border-left: 3px solid #2196F3;">
                        <strong>シーン {scene_number + 1}:</strong> 子どもが「{child_action}」した場合
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                if st.button("選択", key=f"select_situation_{idx}", use_container_width=True):
                    st.session_state["selected_situation"] = idx
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)


def render_situation_detail(situation: Dict):
    """選択されたシチュエーションの詳細を表示"""
    
    event = situation.get("event", "")
    scene_number = situation.get("scene_number", 0)
    child_action = situation.get("child_action", "")
    parent_actions = situation.get("parent_actions", [])
    
    # 戻るボタン
    if st.button("← シチュエーション一覧に戻る"):
        # 現在のシチュエーションに関連するセッション情報をクリア
        keys_to_clear = [key for key in st.session_state.keys() 
                       if any(prefix in key for prefix in [
                           "chat_history_", 
                           "brief_expert_", 
                           "pre_selected_expert_",
                           "brief_feedback_",
                           "detailed_feedback_",
                           "show_detailed_",
                           "custom_response_mode_",
                           "custom_selected_expert_",
                           "question_counter_",
                           "response_mode_",
                           "tone_mode_",
                           "suggested_questions_",
                           "selected_suggested_question_",
                           "pending_suggested_question_",
                           "selected_action_idx"
                       ])]
        for key in keys_to_clear:
            del st.session_state[key]
        
        st.session_state["selected_situation"] = None
        st.rerun()
    
    st.markdown("---")
    
    # シチュエーション情報
    st.markdown(f"### 📍 {event} - シーン {scene_number + 1}")
    
    st.markdown(
        f"""
        <div style="padding: 1.5rem; background-color: #E3F2FD; border-radius: 0.5rem; margin-bottom: 1.5rem;">
            <h4 style="margin-top: 0; color: #1565C0;">状況</h4>
            <p style="font-size: 1.1rem; margin-bottom: 0;">
                お子さんが <strong>「{child_action}」</strong> しています。
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 保護者の対応選択肢
    st.subheader("💭 あなたならどう対応しますか？")
    st.markdown("各選択肢をクリックすると、AIからのアドバイスが表示されます。")
    
    # 選択された対応を取得
    selected_action_idx = st.session_state.get("selected_action_idx")
    
    for idx, action in enumerate(parent_actions):
        action_text = action.get("text", "")
        evaluation = action.get("evaluation", "")
        
        # 評価に応じた色とアイコン
        if evaluation == "appropriate":
            color = "#4CAF50"
            icon = "✅"
            label = "適切"
        elif evaluation == "acceptable":
            color = "#FF9800"
            icon = "⚠️"
            label = "許容"
        else:  # inappropriate
            color = "#F44336"
            icon = "❌"
            label = "不適切"
        
        # 選択済みかどうか
        is_selected = selected_action_idx == idx
        bg_color = "#FFFDE7" if is_selected else "#FFFFFF"
        
        st.markdown(
            f"""
            <div style="padding: 1rem; background-color: {bg_color}; 
            border-radius: 0.5rem; border: 2px solid {color}; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-size: 1.1rem;">{action_text}</span>
                    <span style="color: {color}; font-weight: bold;">{icon} {label}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 選択されていない場合、専門家選択と詳しく知るボタンを表示
        if not is_selected:
            st.markdown("**どの専門家からアドバイスを受けますか？**")
            
            # デフォルト値の設定
            default_expert = st.session_state.get(f"pre_selected_expert_{idx}", "🧠 臨床心理士")
            
            pre_selected_expert = st.radio(
                "専門家を選択",
                [
                    "🧠 臨床心理士",
                    "⚕️ 小児科医",
                    "🏫 特別支援教育専門家",
                    "💙 家族支援専門家"
                ],
                key=f"pre_selected_expert_{idx}",
                help="🧠 臨床心理士：ABA、TEACCH、SSTなどの専門知識\n⚕️ 小児科医：医学的見地、発達評価\n🏫 特別支援教育：学校での支援、合理的配慮\n💙 家族支援：保護者のメンタルケア、きょうだい支援",
                index=[
                    "🧠 臨床心理士",
                    "⚕️ 小児科医",
                    "🏫 特別支援教育専門家",
                    "💙 家族支援専門家"
                ].index(default_expert),
                horizontal=True,
                label_visibility="collapsed"
            )
            
            if st.button(
                f"💡 この対応について詳しく知る",
                key=f"action_detail_{idx}",
                use_container_width=True
            ):
                # ボタンクリック時点でのラジオボタンの値をsession_stateから取得
                selected_expert = st.session_state.get(f"pre_selected_expert_{idx}", "🧠 臨床心理士")
                # 選択した専門家をbrief_expertに保存
                st.session_state[f"brief_expert_{idx}"] = selected_expert
                st.session_state["selected_action_idx"] = idx
                # 詳細表示フラグをリセット
                st.session_state[f"show_detailed_{idx}"] = False
                st.rerun()
        
        # 選択されている場合、AIのフィードバックを表示
        if is_selected:
            display_ai_feedback(action_text, evaluation, event, child_action, idx)
        
        st.markdown("<br>", unsafe_allow_html=True)


def display_ai_feedback(
    action_text: str,
    evaluation: str,
    event: str,
    child_action: str,
    action_idx: int
):
    """AIのフィードバックを表示（簡易版・詳細版）"""
    
    # 関数全体で使用するキーを最初に定義
    chat_history_key = f"chat_history_{action_idx}"
    question_counter_key = f"question_counter_{action_idx}"
    
    # 評価に応じた色
    if evaluation == "appropriate":
        bg_color = "#E8F5E9"
        border_color = "#4CAF50"
        title = "👍 素晴らしい対応です！"
    elif evaluation == "acceptable":
        bg_color = "#FFF3E0"
        border_color = "#FF9800"
        title = "⚠️ 悪くはありませんが..."
    else:
        bg_color = "#FFEBEE"
        border_color = "#F44336"
        title = "❌ より良い対応を考えてみましょう"
    
    # 簡易フィードバック用の専門家選択
    st.markdown("### 💡 AIフィードバック")
    st.markdown("まず、簡易的なフィードバックをお伝えします。")
    
    brief_expert_key = f"brief_expert_{action_idx}"
    # デフォルト値は設定されているか、pre_expert から引き継がれているはず
    # 既に設定されている場合はそれを使用、なければデフォルト
    if brief_expert_key not in st.session_state:
        # pre_expert からの引き継ぎを試みる
        pre_expert_key = f"pre_expert_{action_idx}"
        if pre_expert_key in st.session_state:
            st.session_state[brief_expert_key] = st.session_state[pre_expert_key]
        else:
            st.session_state[brief_expert_key] = "🧠 臨床心理士"
    
    st.markdown("**💬 別の専門家の意見も聞きたい場合は変更できます**")
    brief_selected_expert = st.radio(
        "専門家を選択",
        [
            "🧠 臨床心理士",
            "⚕️ 小児科医",
            "🏫 特別支援教育専門家",
            "💙 家族支援専門家"
        ],
        key=f"brief_selected_expert_{action_idx}",
        help="🧠 臨床心理士：ABA、TEACCH、SSTなどの専門知識\n⚕️ 小児科医：医学的見地、発達評価\n🏫 特別支援教育：学校での支援、合理的配慮\n💙 家族支援：保護者のメンタルケア、きょうだい支援",
        index=[
            "🧠 臨床心理士",
            "⚕️ 小児科医",
            "🏫 特別支援教育専門家",
            "💙 家族支援専門家"
        ].index(st.session_state[brief_expert_key]),
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state[brief_expert_key] = brief_selected_expert
    
    # 簡易フィードバックの生成とキャッシュ（ストリーミング対応）
    brief_feedback_key = f"brief_feedback_{event}_{child_action}_{action_text}_{brief_selected_expert}"
    
    if brief_feedback_key not in st.session_state:
        # ヘッダーを先に表示
        st.markdown(
            f"""
            <div style="padding: 1.5rem; background-color: {bg_color}; 
            border-radius: 0.5rem; border-left: 4px solid {border_color}; margin: 1rem 0;">
                <h4 style="margin-top: 0; color: {border_color};">{title}</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        try:
            specialized_service = SpecializedAgentService()
            
            # 選択された専門家のIDを取得
            agent_id = specialized_service.get_agent_id_from_display_name(brief_selected_expert)
            if not agent_id:
                st.error("専門家の選択に失敗しました")
                return
            
            agent_info = specialized_service.get_agent_info(agent_id)
            
            # 専門家名を表示
            st.markdown(f"**{agent_info['icon']} {agent_info['name']}からのフィードバック:**")
            
            # コンテキストと質問の構築
            context = f"""
シチュエーション: {event}でお子さんが「{child_action}」しています。
保護者の対応: 「{action_text}」
評価: {evaluation}
"""
            
            if evaluation == "appropriate":
                question = """
この対応について、簡潔にフィードバックをください。
- なぜこの対応が良いのか
- 今後も心がけるべきポイント
"""
            elif evaluation == "acceptable":
                question = """
この対応について、簡潔にフィードバックをください。
- この対応の良い点
- さらに改善できる点
"""
            else:  # inappropriate
                question = """
この対応について、簡潔にフィードバックをください。
- なぜこの対応が適切でないのか
- どのように対応すればよいのか
"""
            
            # ストリーミング表示（選択された専門家による回答）
            stream_generator = specialized_service.generate_single_expert_response_stream(
                agent_id=agent_id,
                question=question,
                context=context,
                tone="friendly"
            )
            
            full_answer = st.write_stream(stream_generator)
            st.session_state[brief_feedback_key] = full_answer
            
        except Exception as e:
            ErrorHandler.handle_error(e, "AIフィードバックの生成中にエラーが発生しました")
            st.session_state[brief_feedback_key] = "申し訳ございません。フィードバックの生成に失敗しました。"
    else:
        # キャッシュされたフィードバックを表示
        specialized_service = SpecializedAgentService()
        agent_id = specialized_service.get_agent_id_from_display_name(brief_selected_expert)
        
        if agent_id:
            agent_info = specialized_service.get_agent_info(agent_id)
            
            # ヘッダー表示
            st.markdown(
                f"""
                <div style="padding: 1.5rem; background-color: {bg_color}; 
                border-radius: 0.5rem; border-left: 4px solid {border_color}; margin: 1rem 0;">
                    <h4 style="margin-top: 0; color: {border_color};">{title}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # 専門家名を表示
            st.markdown(f"**{agent_info['icon']} {agent_info['name']}からのフィードバック:**")
            
            # キャッシュされたフィードバックを表示
            brief_feedback = st.session_state.get(brief_feedback_key, "")
            st.markdown(brief_feedback)
    
    # 「より詳細に知りたい方へ」セクション
    st.markdown("---")
    st.subheader("📚 より詳細に知りたい方へ")
    
    st.markdown(
        """
        <div style="padding: 1rem; background-color: #F3E5F5; border-radius: 0.5rem; margin-bottom: 1rem;">
            <p style="margin: 0;">
            <strong>🎓 専門家チームが回答します：</strong><br>
            🧠 臨床心理士 / ⚕️ 小児科医 / 🏫 特別支援教育 / 💙 家族支援
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 回答モードの選択
    response_mode_key = f"response_mode_{action_idx}"
    if response_mode_key not in st.session_state:
        st.session_state[response_mode_key] = "💬 1人の専門家を選ぶ（早い・おすすめ）"
    
    response_mode = st.radio(
        "回答モード",
        ["💬 1人の専門家を選ぶ（早い・おすすめ）", "👥 4人の専門家（順番に回答）", "🔄 統合回答（総合的）"],
        key=f"parent_response_mode_{action_idx}",
        help="1人の専門家：3-5秒で回答開始、専門家を選べます\n4人の専門家：すぐに開始、順番に表示\n統合回答：15-20秒後に統合した回答",
        index=["💬 1人の専門家を選ぶ（早い・おすすめ）", "👥 4人の専門家（順番に回答）", "🔄 統合回答（総合的）"].index(st.session_state[response_mode_key])
    )
    st.session_state[response_mode_key] = response_mode
    
    # 1人の専門家モードの場合、専門家を選択
    selected_expert = None
    if "1人の専門家" in response_mode:
        st.markdown("**どの専門家に質問しますか？**")
        selected_expert = st.radio(
            "専門家選択",
            [
                "🧠 臨床心理士",
                "⚕️ 小児科医",
                "🏫 特別支援教育専門家",
                "💙 家族支援専門家"
            ],
            key=f"parent_selected_expert_{action_idx}",
            help="🧠 臨床心理士：ABA、TEACCH、SSTなどの専門知識\n⚕️ 小児科医：医学的見地、発達評価\n🏫 特別支援教育：学校での支援、合理的配慮\n💙 家族支援：保護者のメンタルケア、きょうだい支援",
            horizontal=True,
            label_visibility="collapsed"
        )
    
    # 口調の選択
    tone_mode_key = f"tone_mode_{action_idx}"
    if tone_mode_key not in st.session_state:
        st.session_state[tone_mode_key] = "😊 フレンドリー（おすすめ）"
    
    tone_mode = st.radio(
        "口調",
        ["😊 フレンドリー（おすすめ）", "📖 標準"],
        key=f"parent_tone_mode_{action_idx}",
        help="フレンドリー：親しみやすく柔らかい表現\n標準：専門的で形式的な表現",
        index=["😊 フレンドリー（おすすめ）", "📖 標準"].index(st.session_state[tone_mode_key])
    )
    st.session_state[tone_mode_key] = tone_mode
    
    # キャッシュキーに専門家情報を含める
    expert_for_key = selected_expert if selected_expert else "none"
    detailed_feedback_key = f"detailed_feedback_{event}_{child_action}_{action_text}_{response_mode}_{expert_for_key}_{tone_mode}"
    
    if detailed_feedback_key not in st.session_state:
        # まだ詳細解説を生成していない場合、ボタンを表示
        if st.button("📚 詳しく聞く", key=f"show_detailed_btn_{action_idx}", type="primary"):
            # ボタンがクリックされたら、その場で生成開始
            try:
                specialized_service = SpecializedAgentService()
                
                context = f"""
シチュエーション: {event}でお子さんが「{child_action}」しています。
保護者の対応: 「{action_text}」
評価: {evaluation}
"""
                
                question = f"""
この対応について、より詳しく解説してください。
- なぜこの対応が{evaluation}なのか
- 具体的にどうすればよいのか
- 注意すべき点は何か
"""
                
                tone = "friendly" if "フレンドリー" in tone_mode else "standard"
                
                # ヘッダー表示
                st.markdown(
                    """
                    <div style="padding: 1.5rem; background-color: #F3E5F5; 
                    border-radius: 0.5rem; border-left: 4px solid #9C27B0; margin-top: 1rem;">
                        <h4 style="margin-top: 0; color: #6A1B9A;">
                        💬 専門家からの詳細な解説
                        </h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if "1人の専門家" in response_mode:
                    # 選択された専門家による回答
                    if selected_expert:
                        agent_id = specialized_service.get_agent_id_from_display_name(selected_expert)
                        if agent_id:
                            agent_info = specialized_service.get_agent_info(agent_id)
                            st.markdown(f"### {agent_info['icon']} {agent_info['name']}からの回答")
                            
                            stream_generator = specialized_service.generate_single_expert_response_stream(
                                agent_id=agent_id,
                                question=question,
                                context=context,
                                tone=tone
                            )
                            full_answer = st.write_stream(stream_generator)
                            st.session_state[detailed_feedback_key] = full_answer
                        else:
                            st.error("専門家の選択に失敗しました")
                    else:
                        st.warning("専門家を選択してください")
                    
                elif "4人の専門家" in response_mode:
                    # 順番モード：4人が順番にストリーミング表示
                    full_answer = display_sequential_responses(
                        specialized_service,
                        question,
                        context,
                        tone
                    )
                    st.session_state[detailed_feedback_key] = full_answer
                    
                else:  # 統合回答
                    # 統合モード：15-20秒待ってから統合回答
                    stream_generator = specialized_service.generate_comprehensive_response_stream(
                        question=question,
                        context=context,
                        tone=tone
                    )
                    full_answer = st.write_stream(stream_generator)
                    st.session_state[detailed_feedback_key] = full_answer
                
            except Exception as e:
                ErrorHandler.handle_error(e, "詳細な解説の生成中にエラーが発生しました")
                st.error("申し訳ございません。詳細な解説の生成に失敗しました。")
    else:
        # キャッシュされた詳細フィードバックを表示
        st.markdown(
            """
            <div style="padding: 1.5rem; background-color: #F3E5F5; 
            border-radius: 0.5rem; border-left: 4px solid #9C27B0; margin-top: 1rem;">
                <h4 style="margin-top: 0; color: #6A1B9A;">💬 詳細な解説</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 1人の専門家モードの場合、専門家名を表示
        if "1人の専門家" in response_mode and selected_expert:
            specialized_service = SpecializedAgentService()
            agent_id = specialized_service.get_agent_id_from_display_name(selected_expert)
            if agent_id:
                agent_info = specialized_service.get_agent_info(agent_id)
                st.markdown(f"### {agent_info['icon']} {agent_info['name']}からの回答")
        
        # キャッシュされたフィードバックを表示
        detailed_feedback = st.session_state.get(detailed_feedback_key, "")
        st.markdown(detailed_feedback)
    
    # 専門家エージェントに詳しく質問できる機能（チャット形式）
    st.markdown("---")
    st.subheader("👥 自由に質問する")
    
    st.markdown(
        """
        <div style="padding: 1rem; background-color: #F3E5F5; border-radius: 0.5rem; margin-bottom: 1rem;">
            <p style="margin: 0;">
            <strong>💡 この対応について、もっと詳しく質問できます</strong><br>
            専門家チームがあなたの質問に回答します。何度でも質問できます。
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 会話履歴を保持するためのセッションステート（chat_history_keyは既に上で定義済み）
    if chat_history_key not in st.session_state:
        st.session_state[chat_history_key] = []
    
    # 回答モードの選択（カスタム質問用）
    custom_response_mode_key = f"custom_response_mode_{action_idx}"
    if custom_response_mode_key not in st.session_state:
        st.session_state[custom_response_mode_key] = "💬 1人の専門家を選ぶ（早い・おすすめ）"
    
    custom_response_mode = st.radio(
        "回答モード（カスタム質問）",
        ["💬 1人の専門家を選ぶ（早い・おすすめ）", "👥 4人の専門家（順番に回答）", "🔄 統合回答（総合的）"],
        key=f"custom_answer_mode_{action_idx}",
        help="1人の専門家：3-5秒で回答開始、専門家を選べます\n4人の専門家：すぐに開始、順番に表示\n統合回答：15-20秒後に統合した回答",
        index=["💬 1人の専門家を選ぶ（早い・おすすめ）", "👥 4人の専門家（順番に回答）", "🔄 統合回答（総合的）"].index(st.session_state[custom_response_mode_key])
    )
    st.session_state[custom_response_mode_key] = custom_response_mode
    
    # カスタム質問用の専門家選択
    custom_selected_expert = None
    if "1人の専門家" in custom_response_mode:
        st.markdown("**どの専門家に質問しますか？**")
        custom_selected_expert = st.radio(
            "専門家選択（カスタム質問）",
            [
                "🧠 臨床心理士",
                "⚕️ 小児科医",
                "🏫 特別支援教育専門家",
                "💙 家族支援専門家"
            ],
            key=f"custom_selected_expert_{action_idx}",
            help="🧠 臨床心理士：ABA、TEACCH、SSTなどの専門知識\n⚕️ 小児科医：医学的見地、発達評価\n🏫 特別支援教育：学校での支援、合理的配慮\n💙 家族支援：保護者のメンタルケア、きょうだい支援",
            horizontal=True,
            label_visibility="collapsed"
        )
    
    # 過去の会話履歴を表示
    if st.session_state[chat_history_key]:
        st.markdown("### 💬 会話履歴")
        for i, chat in enumerate(st.session_state[chat_history_key]):
            # 質問を表示
            st.markdown(
                f"""
                <div style="padding: 1rem; background-color: #E3F2FD; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                    <strong>🙋 質問 {i+1}:</strong> {chat['question']}
                </div>
                """,
                unsafe_allow_html=True
            )
            # 回答を表示
            st.markdown(
                f"""
                <div style="padding: 1rem; background-color: #E8F5E9; border-radius: 0.5rem; margin-bottom: 1rem;">
                    <strong>{chat['expert']} からの回答:</strong><br>
                    {chat['answer']}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # 会話履歴をクリアするボタン
        if st.button("🗑️ 会話履歴をクリア", key=f"clear_chat_{action_idx}"):
            st.session_state[chat_history_key] = []
            st.rerun()
        
        st.markdown("---")
    
    # 関連質問の候補を表示
    st.markdown("### 💡 こんな質問はいかがですか？")
    st.markdown("クリックすると、その質問の回答が表示されます")
    
    # 関連質問をAIで生成（1回だけ生成してキャッシュ）
    suggested_questions_key = f"suggested_questions_{action_idx}"
    if suggested_questions_key not in st.session_state:
        try:
            # シンプルなプロンプトで関連質問を生成
            from openai import OpenAI
            client = OpenAI(api_key=Settings.OPENAI_API_KEY)
            
            prompt = f"""以下の状況について、保護者が知りたいと思うような具体的な質問を3つ提案してください。

状況:
- イベント: {event}
- 子どもの行動: {child_action}
- 保護者の対応: {action_text}

要件:
- 各質問は30文字以内で簡潔に
- この具体的な状況に関連する実用的な質問
- 一般的すぎる質問は避ける
- JSON形式で返す: {{"questions": ["質問1", "質問2", "質問3"]}}
"""
            
            response = client.chat.completions.create(
                model=Settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "あなたはASD支援の専門家です。保護者が知りたいと思う具体的な質問を提案してください。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            st.session_state[suggested_questions_key] = result.get("questions", [])
        except Exception as e:
            logger.error(f"Error generating suggested questions: {e}")
            # フォールバック用のデフォルト質問
            st.session_state[suggested_questions_key] = [
                f"{event}でよくある困りごとは何ですか？",
                f"{child_action}する理由を教えてください",
                "家庭でできる工夫を教えてください"
            ]
    
    # 関連質問をボタンとして表示
    suggested_questions = st.session_state.get(suggested_questions_key, [])
    
    # 処理待ちの候補質問があるかチェック
    pending_question_key = f"pending_suggested_question_{action_idx}"
    pending_question_data = st.session_state.get(pending_question_key)
    
    if pending_question_data:
        # 保存されたデータから質問と設定を取り出す
        pending_question = pending_question_data.get("question")
        saved_mode = pending_question_data.get("mode")
        saved_expert = pending_question_data.get("expert")
        saved_tone_key = pending_question_data.get("tone_key")
        saved_event = pending_question_data.get("event")
        saved_child_action = pending_question_data.get("child_action")
        saved_action_text = pending_question_data.get("action_text")
        saved_evaluation = pending_question_data.get("evaluation")
        
        # 質問カウンターの初期化を確認
        if question_counter_key not in st.session_state:
            st.session_state[question_counter_key] = 0
        
        # フラグをクリア（処理前にクリアして無限ループを防ぐ）
        del st.session_state[pending_question_key]
        
        # 質問を処理（保存された値を使用）
        try:
            handle_question_submission(
                pending_question,
                action_idx,
                saved_event,
                saved_child_action,
                saved_action_text,
                saved_evaluation,
                chat_history_key,
                question_counter_key,
                saved_mode,
                saved_expert,
                saved_tone_key
            )
        except Exception as e:
            ErrorHandler.handle_error(e, "候補質問の処理中にエラーが発生しました")
            st.error(f"申し訳ございません。質問の処理中にエラーが発生しました。")
            logger.error(f"Error processing suggested question: {e}", exc_info=True)
    else:
        # 候補質問ボタンを表示
        for i, suggested_q in enumerate(suggested_questions):
            if st.button(f"❓ {suggested_q}", key=f"suggested_q_{action_idx}_{i}", use_container_width=True):
                try:
                    # 専門家が選択されていない場合のデフォルト値を設定
                    effective_custom_selected_expert = custom_selected_expert
                    if not effective_custom_selected_expert and "1人の専門家" in custom_response_mode:
                        effective_custom_selected_expert = "🧠 臨床心理士"
                    
                    # 口調の実際の値を取得
                    tone_value = st.session_state.get(tone_mode_key, "😊 フレンドリー（おすすめ）")
                    
                    # デバッグ情報をログに出力
                    logger.info(f"候補質問クリック: {suggested_q}")
                    logger.info(f"event={event}, child_action={child_action}")
                    logger.info(f"custom_response_mode={custom_response_mode}")
                    logger.info(f"effective_custom_selected_expert={effective_custom_selected_expert}")
                    
                    # 次のrerunで処理するために質問と現在の設定を保存
                    st.session_state[pending_question_key] = {
                        "question": suggested_q,
                        "mode": custom_response_mode,
                        "expert": effective_custom_selected_expert,
                        "tone_key": tone_mode_key,
                        "event": event,
                        "child_action": child_action,
                        "action_text": action_text,
                        "evaluation": evaluation
                    }
                    logger.info(f"候補質問データを保存しました: {pending_question_key}")
                    st.rerun()
                except Exception as e:
                    logger.error(f"候補質問ボタンクリック時のエラー: {e}", exc_info=True)
                    st.error(f"エラーが発生しました: {str(e)}")
                    raise
    
    st.markdown("---")
    st.markdown("**または、自由に質問を入力：**")
    
    # 新しい質問入力
    # 質問カウンターの初期化（既に上で定義済み）
    if question_counter_key not in st.session_state:
        st.session_state[question_counter_key] = 0
    
    question = st.text_area(
        "新しい質問を入力してください",
        value="",  # 常に空の状態から開始
        placeholder="ASD支援に関する質問をご自由に入力してください",
        key=f"expert_question_{action_idx}_{st.session_state[question_counter_key]}",
        height=100
    )
    
    if st.button("💬 専門家に質問する", key=f"ask_experts_btn_{action_idx}", type="primary"):
        if question and question.strip():
            handle_question_submission(
                question,
                action_idx,
                event,
                child_action,
                action_text,
                evaluation,
                chat_history_key,
                question_counter_key,
                custom_response_mode,
                custom_selected_expert,
                tone_mode_key,
                is_free_question=True  # 自由質問モード
            )
        else:
            ErrorHandler.show_warning("質問を入力してください")

