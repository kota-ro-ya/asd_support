"""
AI service for OpenAI API interactions.
"""

from openai import OpenAI
from typing import Optional, Generator
import logging
import time

from app.config.settings import Settings
from app.config.prompts import AI_PERSONAS, get_feedback_system_prompt, GUIDE_SYSTEM_PROMPT
from app.utils.error_handler import ErrorHandler
from app.utils.debug_info import get_debug_collector

logger = logging.getLogger(__name__)


class AIService:
    """OpenAI APIとのやり取りを管理するクラス"""
    
    def __init__(self):
        """AIServiceの初期化"""
        try:
            self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
            self.model = Settings.OPENAI_MODEL
            self.debug_collector = get_debug_collector()
            logger.info("AIService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AIService: {e}")
            raise
    
    def generate_feedback(self, scene_text: str, selected_choice: str, 
                         evaluation: str, hint: str = "") -> Optional[str]:
        """
        子どもの行動選択に対するAIフィードバックを生成
        
        Args:
            scene_text: シーンの説明
            selected_choice: 選択された行動
            evaluation: 評価（appropriate/acceptable/inappropriate）
            hint: AI判定のヒント
            
        Returns:
            AIが生成したフィードバック文字列。失敗時はNone
        """
        try:
            system_prompt = get_feedback_system_prompt(
                scene_text=scene_text,
                selected_choice=selected_choice,
                evaluation=evaluation,
                hint=hint
            )
            
            # API呼び出しの計測開始
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"選択した行動: {selected_choice}"}
                ],
                max_tokens=Settings.MAX_TOKENS,
                temperature=Settings.TEMPERATURE
            )
            
            # デバッグ情報を記録
            response_time = time.time() - start_time
            self.debug_collector.add_api_call(
                model=self.model,
                agent_type="feedback_generator",
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                response_time=response_time,
                temperature=Settings.TEMPERATURE,
                max_tokens=Settings.MAX_TOKENS,
                stream=False
            )
            
            feedback = response.choices[0].message.content
            
            # 生成されたフィードバックの品質を評価（品質チェックエージェント）
            if Settings.DEBUG_MODE or Settings.DEBUG_LOG_ALWAYS:
                try:
                    from app.services.agent_coordinator import AgentCoordinator
                    coordinator = AgentCoordinator()
                    
                    quality_result = coordinator.validate_content_quality(
                        content_type="feedback",
                        content={
                            "feedback": feedback,
                            "evaluation": evaluation,
                            "choice": selected_choice
                        },
                        criteria={
                            "clarity": "フィードバックが明確で理解しやすいか",
                            "appropriateness": "評価に適した内容か",
                            "educational_value": "教育的価値があるか"
                        }
                    )
                    
                    # 品質スコアを記録（0-100）
                    self.debug_collector.add_evaluation(
                        evaluation_type="feedback_quality",
                        score=quality_result.get("score", 0),
                        criteria="品質管理エージェントによる評価",
                        details={
                            "is_valid": quality_result.get("is_valid", True),
                            "issues": quality_result.get("issues", []),
                            "suggestions": quality_result.get("suggestions", []),
                            "user_evaluation": evaluation
                        }
                    )
                except Exception as e:
                    logger.warning(f"Quality check failed: {e}")
            logger.info(f"Generated feedback for choice: {selected_choice}")
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            ErrorHandler.handle_api_error(e)
            return None
    
    def generate_feedback_stream(self, scene_text: str, selected_choice: str, 
                                 evaluation: str, hint: str = "") -> Generator[str, None, None]:
        """
        子どもの行動選択に対するAIフィードバックをストリーミング生成
        
        Args:
            scene_text: シーンの説明
            selected_choice: 選択された行動
            evaluation: 評価
            hint: AI判定のヒント
            
        Yields:
            AIが生成したフィードバックの断片
        """
        try:
            system_prompt = get_feedback_system_prompt(
                scene_text=scene_text,
                selected_choice=selected_choice,
                evaluation=evaluation,
                hint=hint
            )
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"選択した行動: {selected_choice}"}
                ],
                max_tokens=Settings.MAX_TOKENS,
                temperature=Settings.TEMPERATURE,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.info(f"Generated streaming feedback for choice: {selected_choice}")
            
        except Exception as e:
            logger.error(f"Error generating streaming feedback: {e}")
            ErrorHandler.handle_api_error(e)
            yield ""
    
    def answer_parent_question(self, question: str, ai_mode: str) -> Optional[str]:
        """
        保護者からの質問に対してAIが回答を生成
        
        Args:
            question: 保護者からの質問
            ai_mode: AI人格モード
            
        Returns:
            AIが生成した回答文字列。失敗時はNone
        """
        try:
            if ai_mode not in AI_PERSONAS:
                logger.error(f"Invalid AI mode: {ai_mode}")
                return None
            
            system_prompt = AI_PERSONAS[ai_mode]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=Settings.MAX_TOKENS * 2,  # 保護者向けは少し長めに
                temperature=Settings.TEMPERATURE
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer for question in mode: {ai_mode}")
            return answer
            
        except Exception as e:
            logger.error(f"Error answering parent question: {e}")
            ErrorHandler.handle_api_error(e)
            return None
    
    def answer_parent_question_stream(self, question: str, 
                                     ai_mode: str) -> Generator[str, None, None]:
        """
        保護者からの質問に対してAIが回答をストリーミング生成
        
        Args:
            question: 保護者からの質問
            ai_mode: AI人格モード
            
        Yields:
            AIが生成した回答の断片
        """
        try:
            if ai_mode not in AI_PERSONAS:
                logger.error(f"Invalid AI mode: {ai_mode}")
                yield ""
                return
            
            system_prompt = AI_PERSONAS[ai_mode]
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=Settings.MAX_TOKENS * 2,
                temperature=Settings.TEMPERATURE,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.info(f"Generated streaming answer for question in mode: {ai_mode}")
            
        except Exception as e:
            logger.error(f"Error answering parent question (stream): {e}")
            ErrorHandler.handle_api_error(e)
            yield ""

    def get_situation_guide(self, event_name: str, scene_description: str,
                            child_action: str, parent_action: str, ai_mode: str) -> Optional[str]:
        """
        保護者向けシチュエーション別ガイドを生成

        Args:
            event_name: イベント名
            scene_description: シーンの説明
            child_action: 子どもがとった行動
            parent_action: 保護者が選択した行動
            ai_mode: AI人格モード

        Returns:
            AIが生成したガイド文字列。失敗時はNone
        """
        try:
            if ai_mode not in AI_PERSONAS:
                logger.error(f"Invalid AI mode: {ai_mode}")
                return None

            # 親の行動オプションから評価とヒントを取得（constants.pyから直接使用）
            from app.config.constants import PARENT_ACTION_OPTIONS
            selected_parent_action_detail = next(
                (opt for opt in PARENT_ACTION_OPTIONS if opt["text"] == parent_action),
                None
            )

            if selected_parent_action_detail is None:
                logger.error(f"Invalid parent action selected: {parent_action}")
                return None

            # AI人格のプロンプトとシチュエーションガイドのプロンプトを組み合わせる
            persona_prompt = AI_PERSONAS[ai_mode]
            guide_prompt_content = GUIDE_SYSTEM_PROMPT(
                event_name=event_name,
                scene_description=scene_description,
                child_action=child_action,
                parent_action_text=selected_parent_action_detail["text"],
                evaluation=selected_parent_action_detail["evaluation"],
                ai_hint=selected_parent_action_detail["ai_hint"]
            )

            # ユーザーメッセージを調整
            user_message = f"""
イベント: {event_name}
シーン: {scene_description}
子どもの行動: {child_action}
保護者の行動: {parent_action}
この状況での私（保護者）の行動について、{ai_mode}の視点から具体的なガイドとアドバイスをお願いします。
            """

            messages = [
                {"role": "system", "content": persona_prompt},
                {"role": "user", "content": guide_prompt_content},
                {"role": "user", "content": user_message}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=Settings.MAX_TOKENS * 3, # 長めの回答を想定
                temperature=Settings.TEMPERATURE
            )

            guide_answer = response.choices[0].message.content
            logger.info(f"Generated situation guide for event: {event_name}, child_action: {child_action}")
            return guide_answer

        except Exception as e:
            logger.error(f"Error generating situation guide: {e}")
            ErrorHandler.handle_api_error(e)
            return None

    def get_situation_guide_stream(self, event_name: str, scene_description: str,
                                   child_action: str, parent_action: str, ai_mode: str) -> Generator[str, None, None]:
        """
        保護者向けシチュエーション別ガイドをストリーミング生成
        """
        try:
            if ai_mode not in AI_PERSONAS:
                logger.error(f"Invalid AI mode: {ai_mode}")
                yield ""
                return

            from app.config.constants import PARENT_ACTION_OPTIONS
            selected_parent_action_detail = next(
                (opt for opt in PARENT_ACTION_OPTIONS if opt["text"] == parent_action),
                None
            )

            if selected_parent_action_detail is None:
                logger.error(f"Invalid parent action selected: {parent_action}")
                yield ""
                return

            persona_prompt = AI_PERSONAS[ai_mode]
            guide_prompt_content = GUIDE_SYSTEM_PROMPT(
                event_name=event_name,
                scene_description=scene_description,
                child_action=child_action,
                parent_action_text=selected_parent_action_detail["text"],
                evaluation=selected_parent_action_detail["evaluation"],
                ai_hint=selected_parent_action_detail["ai_hint"]
            )

            user_message = f"""
イベント: {event_name}
シーン: {scene_description}
子どもの行動: {child_action}
保護者の行動: {parent_action}
この状況での私（保護者）の行動について、{ai_mode}の視点から具体的なガイドとアドバイスをお願いします。
            """

            messages = [
                {"role": "system", "content": persona_prompt},
                {"role": "user", "content": guide_prompt_content},
                {"role": "user", "content": user_message}
            ]

            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=Settings.MAX_TOKENS * 3,
                temperature=Settings.TEMPERATURE,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            logger.info(f"Generated streaming situation guide for event: {event_name}, child_action: {child_action}")

        except Exception as e:
            logger.error(f"Error generating streaming situation guide: {e}")
            ErrorHandler.handle_api_error(e)
            yield ""
    
    def get_parent_advice(self, question: str, context: str, ai_mode: str) -> Optional[str]:
        """
        保護者向けのアドバイスを生成（シチュエーション別ガイド用）
        
        Args:
            question: 保護者からの質問
            context: 状況のコンテキスト
            ai_mode: AI人格モード
            
        Returns:
            AIが生成したアドバイス文字列。失敗時はNone
        """
        try:
            if ai_mode not in AI_PERSONAS:
                logger.error(f"Invalid AI mode: {ai_mode}")
                return None
            
            system_prompt = AI_PERSONAS[ai_mode]
            
            # コンテキストと質問を組み合わせる
            full_message = f"{context}\n\n質問: {question}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_message}
                ],
                max_tokens=Settings.MAX_TOKENS * 2,
                temperature=Settings.TEMPERATURE
            )
            
            advice = response.choices[0].message.content
            logger.info(f"Generated parent advice in mode: {ai_mode}")
            return advice
            
        except Exception as e:
            logger.error(f"Error generating parent advice: {e}")
            ErrorHandler.handle_api_error(e)
            return None
    
    def generate_parent_action_feedback(
        self, 
        event: str, 
        child_action: str, 
        parent_action: str, 
        evaluation: str,
        ai_mode: str = "🩺 ロジカルドクター",
        detail_level: str = "brief"
    ) -> Optional[str]:
        """
        保護者の対応選択に対するAIフィードバックを生成（簡易版・詳細版）
        
        Args:
            event: イベント名（例：「床屋」）
            child_action: 子どもの行動（例：「バリカンの音を聞いてパニックになる」）
            parent_action: 保護者が選択した対応（例：「事前に予告し、イヤーマフの使用を提案する」）
            evaluation: 評価（appropriate/acceptable/inappropriate）
            ai_mode: AI人格モード
            detail_level: "brief"（簡易）または "detailed"（詳細）
            
        Returns:
            AIが生成したフィードバック文字列。失敗時はNone
        """
        try:
            if ai_mode not in AI_PERSONAS:
                logger.error(f"Invalid AI mode: {ai_mode}")
                return None
            
            from app.config.prompts import get_parent_action_feedback_prompt
            
            system_prompt = get_parent_action_feedback_prompt(
                event=event,
                child_action=child_action,
                parent_action=parent_action,
                evaluation=evaluation,
                ai_mode=ai_mode,
                detail_level=detail_level
            )
            
            user_message = f"""
イベント: {event}
子どもの行動: {child_action}
保護者の対応: {parent_action}
評価: {evaluation}

この保護者の対応について、{detail_level}のフィードバックをお願いします。
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=Settings.MAX_TOKENS if detail_level == "brief" else Settings.MAX_TOKENS * 3,
                temperature=Settings.TEMPERATURE
            )
            
            feedback = response.choices[0].message.content
            logger.info(f"Generated parent action feedback ({detail_level}) for event: {event}")
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating parent action feedback: {e}")
            ErrorHandler.handle_api_error(e)
            return None
    
    def generate_parent_action_feedback_stream(
        self, 
        event: str, 
        child_action: str, 
        parent_action: str, 
        evaluation: str,
        ai_mode: str = "🩺 ロジカルドクター",
        detail_level: str = "brief",
        rag_context: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        保護者の対応選択に対するAIフィードバックをストリーミング生成（RAG対応準備済み）
        
        Args:
            event: イベント名
            child_action: 子どもの行動
            parent_action: 保護者が選択した対応
            evaluation: 評価
            ai_mode: AI人格モード
            detail_level: "brief"（簡易）または "detailed"（詳細）
            rag_context: RAGから取得したコンテキスト（将来的に使用）
            
        Yields:
            AIが生成したフィードバックの断片
        """
        try:
            if ai_mode not in AI_PERSONAS:
                logger.error(f"Invalid AI mode: {ai_mode}")
                yield ""
                return
            
            from app.config.prompts import get_parent_action_feedback_prompt
            
            system_prompt = get_parent_action_feedback_prompt(
                event=event,
                child_action=child_action,
                parent_action=parent_action,
                evaluation=evaluation,
                ai_mode=ai_mode,
                detail_level=detail_level,
                rag_context=rag_context
            )
            
            user_message = f"""
イベント: {event}
子どもの行動: {child_action}
保護者の対応: {parent_action}
評価: {evaluation}

この保護者の対応について、{detail_level}のフィードバックをお願いします。
            """
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=Settings.MAX_TOKENS if detail_level == "brief" else Settings.MAX_TOKENS * 3,
                temperature=Settings.TEMPERATURE,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.info(f"Generated streaming parent action feedback ({detail_level}) for event: {event}")
            
        except Exception as e:
            logger.error(f"Error generating streaming parent action feedback: {e}")
            ErrorHandler.handle_api_error(e)
            yield ""

