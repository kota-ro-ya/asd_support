"""
Sidebar component for parent AI question mode.
専門エージェントシステムによる高精度な回答を提供
ストリーミング表示で待ち時間を快適に
"""

import streamlit as st
import random
from pathlib import Path

from app.services.specialized_agent_service import SpecializedAgentService
from app.services.session_service import SessionService
from app.services.progress_service import ProgressService
from app.utils.file_handler import FileHandler
from app.utils.error_handler import ErrorHandler
from app.config.settings import Settings


def render_sidebar():
    """保護者向けAI質問モードのサイドバーを描画（専門エージェントシステム）"""
    
    with st.sidebar:
        st.header("👥 保護者向けAI相談")
        
        st.markdown(
            """
            <div style="padding: 0.8rem; background-color: #F3E5F5; border-radius: 0.5rem; margin-bottom: 1rem;">
                <p style="margin: 0; font-size: 0.85rem;">
                <strong>🎓 専門家チームが回答</strong><br>
                🧠 臨床心理士 / ⚕️ 小児科医<br>
                🏫 特別支援教育 / 💙 家族支援
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.divider()
        
        # よくある質問モード（専門エージェントシステム使用）
        render_faq_mode()
        
        st.divider()
        
        # ユーザー情報表示
        nickname = SessionService.get_nickname()
        if nickname:
            st.caption(f"👤 ユーザー: {nickname}")


def render_faq_mode():
    """
    よくある質問モードのUIを描画（専門エージェントシステム使用・ストリーミング対応）
    """
    # FAQ質問リストの読み込み
    faq_path = Settings.DATA_DIR / "parent_guide_data.json"
    faq_data = FileHandler.read_json(faq_path)
    
    if faq_data and "faq_questions" in faq_data:
        questions = faq_data["faq_questions"]
        
        # セッションに表示質問リストが保存されていない場合、初期化
        if "displayed_faq_questions" not in st.session_state:
            # ランダムに5つの質問を選択
            if len(questions) > 5:
                st.session_state.displayed_faq_questions = random.sample(questions, 5)
            else:
                st.session_state.displayed_faq_questions = questions
        
        displayed_questions = st.session_state.displayed_faq_questions
        
        st.subheader("💡 よくある質問")
        
        # 質問リストをリフレッシュするボタン
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("気になる質問を選んでください：")
        with col2:
            if st.button("🔄", help="質問リストを更新", key="refresh_faq_btn"):
                # 新しい質問リストをランダムに選択
                if len(questions) > 5:
                    st.session_state.displayed_faq_questions = random.sample(questions, 5)
                else:
                    st.session_state.displayed_faq_questions = questions
                st.rerun()
        
        # 質問の選択
        selected_question = st.radio(
            "質問リスト",
            displayed_questions,
            key="faq_question_selector",
            label_visibility="collapsed"
        )
        
        # 回答モードの選択
        response_mode = st.radio(
            "回答モード",
            ["💬 1人の専門家を選ぶ（早い・おすすめ）", "👥 4人の専門家（順番に回答）", "🔄 統合回答（総合的）"],
            key="sidebar_response_mode",
            help="1人の専門家：3-5秒で回答開始、専門家を選べます\n4人の専門家：すぐに開始、順番に表示\n統合回答：15-20秒後に統合した回答"
        )
        
        # 1人の専門家モードの場合、専門家を選択
        selected_expert = None
        if "1人の専門家" in response_mode:
            st.markdown("**専門家を選択してください：**")
            selected_expert = st.radio(
                "専門家選択",
                [
                    "🧠 臨床心理士",
                    "⚕️ 小児科医",
                    "🏫 特別支援教育専門家",
                    "💙 家族支援専門家"
                ],
                key="sidebar_selected_expert",
                help="🧠 臨床心理士：ABA、TEACCH、SSTなどの専門知識\n⚕️ 小児科医：医学的見地、発達評価\n🏫 特別支援教育：学校での支援、合理的配慮\n💙 家族支援：保護者のメンタルケア、きょうだい支援",
                label_visibility="collapsed"
            )
        
        # 口調の選択
        tone_mode = st.radio(
            "口調",
            ["😊 フレンドリー（おすすめ）", "📖 標準"],
            key="sidebar_tone_mode",
            help="フレンドリー：親しみやすく柔らかい表現\n標準：専門的で形式的な表現"
        )
        
        # 質問ボタン
        if st.button("💬 専門家に質問する", use_container_width=True, type="primary", key="ask_faq_btn"):
            if selected_question:
                tone = "friendly" if "フレンドリー" in tone_mode else "standard"
                
                try:
                    specialized_service = SpecializedAgentService()
                    
                    st.markdown("---")
                    
                    if "1人の専門家" in response_mode:
                        # 選択された専門家による回答
                        if selected_expert:
                            agent_id = specialized_service.get_agent_id_from_display_name(selected_expert)
                            if agent_id:
                                agent_info = specialized_service.get_agent_info(agent_id)
                                st.markdown(f"**{agent_info['icon']} {agent_info['name']}からの回答:**")
                                
                                stream_generator = specialized_service.generate_single_expert_response_stream(
                                    agent_id=agent_id,
                                    question=selected_question,
                                    context="",
                                    tone=tone
                                )
                                full_answer = st.write_stream(stream_generator)
                                
                                # 会話履歴に保存
                                save_conversation(selected_question, full_answer, f"{agent_info['name']}")
                            else:
                                st.error("専門家の選択に失敗しました")
                        else:
                            st.warning("専門家を選択してください")
                        
                    elif "4人の専門家" in response_mode:
                        # 順番モード：4人が順番にストリーミング表示
                        full_answer = display_sequential_responses(
                            specialized_service,
                            selected_question,
                            "",
                            tone
                        )
                        
                        # 会話履歴に保存
                        save_conversation(selected_question, full_answer, "専門家4人（順番）")
                        
                    else:  # 統合回答
                        # 統合モード：15-20秒待ってから統合回答
                        stream_generator = specialized_service.generate_comprehensive_response_stream(
                            question=selected_question,
                            context="",
                            tone=tone
                        )
                        full_answer = st.write_stream(stream_generator)
                        
                        # 会話履歴に保存
                        save_conversation(selected_question, full_answer, "専門家チーム（統合）")
                    
                except Exception as e:
                    ErrorHandler.handle_error(e, "専門家チームの回答生成に失敗しました")
            else:
                st.warning("質問を選択してください")
        
        st.divider()
        
        # カスタム質問
        st.subheader("✍️ 自由に質問")
        custom_question = st.text_area(
            "自分で質問を入力できます",
            placeholder="例: 子どもが朝起きられないときはどうすれば良いですか？",
            height=100,
            key="faq_custom_question"
        )
        
        if st.button("📝 この質問を専門家に聞く", use_container_width=True, key="ask_custom_faq_btn"):
            if custom_question.strip():
                tone = "friendly" if "フレンドリー" in tone_mode else "standard"
                
                try:
                    specialized_service = SpecializedAgentService()
                    
                    st.markdown("---")
                    
                    if "1人の専門家" in response_mode:
                        # 選択された専門家による回答
                        if selected_expert:
                            agent_id = specialized_service.get_agent_id_from_display_name(selected_expert)
                            if agent_id:
                                agent_info = specialized_service.get_agent_info(agent_id)
                                st.markdown(f"**{agent_info['icon']} {agent_info['name']}からの回答:**")
                                
                                stream_generator = specialized_service.generate_single_expert_response_stream(
                                    agent_id=agent_id,
                                    question=custom_question,
                                    context="",
                                    tone=tone
                                )
                                full_answer = st.write_stream(stream_generator)
                                
                                # 会話履歴に保存
                                save_conversation(custom_question, full_answer, f"{agent_info['name']}")
                            else:
                                st.error("専門家の選択に失敗しました")
                        else:
                            st.warning("専門家を選択してください")
                        
                    elif "4人の専門家" in response_mode:
                        # 順番モード：4人が順番にストリーミング表示
                        full_answer = display_sequential_responses(
                            specialized_service,
                            custom_question,
                            "",
                            tone
                        )
                        
                        # 会話履歴に保存
                        save_conversation(custom_question, full_answer, "専門家4人（順番）")
                        
                    else:  # 統合回答
                        # 統合モード：15-20秒待ってから統合回答
                        stream_generator = specialized_service.generate_comprehensive_response_stream(
                            question=custom_question,
                            context="",
                            tone=tone
                        )
                        full_answer = st.write_stream(stream_generator)
                        
                        # 会話履歴に保存
                        save_conversation(custom_question, full_answer, "専門家チーム（統合）")
                    
                except Exception as e:
                    ErrorHandler.handle_error(e, "専門家チームの回答生成に失敗しました")
            else:
                st.warning("質問を入力してください")
    
    else:
        st.error("質問リストの読み込みに失敗しました")


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


def save_conversation(question, answer, ai_mode):
    """会話履歴を保存"""
    user = SessionService.get_user()
    if user:
        progress_service = ProgressService()
        progress_service.add_conversation(
            user=user,
            ai_mode=ai_mode,
            question=question,
            answer=answer,
            topic_tags=["よくある質問"]
        )
