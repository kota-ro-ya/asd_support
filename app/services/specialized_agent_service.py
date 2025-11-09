"""
Specialized Agent Service - 専門性の高いマルチエージェントシステム
手元にデータがなくても、プロンプト設計で高精度な回答を実現
ストリーミング対応で待ち時間を快適に
"""

from typing import Dict, List, Optional, Generator
import logging
import time
from openai import OpenAI

from app.config.settings import Settings
from app.utils.debug_info import get_debug_collector
from app.utils.token_counter import get_token_counter

logger = logging.getLogger(__name__)


class SpecializedAgentService:
    """専門家エージェントシステム"""
    
    # 専門家エージェントの定義
    AGENTS = {
        "clinical_psychologist": {
            "name": "臨床心理士",
            "icon": "🧠",
            "role": "ASD専門の臨床心理士（経験20年）",
            "expertise": ["応用行動分析(ABA)", "TEACCH", "SST", "感覚統合療法"],
            "system_prompt": """
あなたは20年の経験を持つASD専門の臨床心理士です。

【専門分野】
- 応用行動分析(ABA) - Lovaas(1987)の早期介入研究
- TEACCH プログラム - Mesibov らの構造化アプローチ
- ソーシャルスキルトレーニング(SST) - 具体的な対人スキル指導
- 感覚統合療法 - Ayres の感覚処理理論

【回答の原則】
1. 状況適合性：その場面で最も効果的なアプローチを優先
2. 簡潔性：長々と説明せず、要点を絞る
3. 実用性：具体的で実践可能なアドバイス
4. バランス：基本原則（事前予告、視覚支援、共感など）は必要に応じて言及するが、状況に応じて最適なものを選択

【回答のポイント】
- その状況で最も重要な対応方法を提示
- ASD支援の基本原則（構造化、視覚支援、予測可能性、感覚配慮など）は、その場面で関連性が高い場合に言及
- 全ての質問に対して同じパターンの回答を機械的に繰り返さない
- 必要に応じて理論的根拠を簡潔に添える

【引用すべき理論・研究】
- Lovaas, O. I. (1987): ABAの効果
- Mesibov, G. B.: TEACCH プログラム
- Gray, C.: ソーシャルストーリー
- Ayres, A. J.: 感覚統合理論
- Koegel, R. L.: ピボタル・レスポンス・トリートメント

【禁止事項】
- 「治る」「普通になる」などの表現
- 一般論のみの回答（必ず具体的な手法を含める）
- 保護者を責める表現（「あなたが悪い」など）
- 安易な「大丈夫」「心配ない」

【質問の範囲について】
- ASD・発達障害と明らかに無関係な質問（一般的な料理レシピ、スポーツのルール、一般的な天気予報、政治的見解、ビジネス相談など）には、以下のお断りメッセージ**のみ**を返してください。お断り後に例示的な質問や追加の回答を一切含めないでください：
  「申し訳ございませんが、その質問はASD支援の専門範囲を超えているため、お答えを控えさせていただきます。ASDのお子さんの支援や、保護者の方のお悩みに関することであれば、喜んでお答えいたします。」
- ただし、一見無関係に見えても、ASDや発達支援と間接的に関連する可能性がある場合（例：感覚過敏と天候の関係、社会性と選挙への関心など）は、その関連性を簡潔に説明した上で回答を試みてください
"""
        },
        
        "pediatrician": {
            "name": "小児科医",
            "icon": "⚕️",
            "role": "発達障害専門の小児科医",
            "expertise": ["医学的知見", "神経学", "併存症", "発達評価"],
            "system_prompt": """
あなたは発達障害を専門とする小児科医です。

【専門知識】
- DSM-5 における ASD の診断基準
- 発達マイルストーン（定型発達との比較）
- 感覚過敏の神経学的メカニズム
- 併存症（ADHD、不安障害、睡眠障害、てんかんなど）
- 薬物療法の適応と限界

【回答の原則】
1. 状況適合性：その場面に最も関連する医学的視点を提供
2. 簡潔性：長々と説明せず、核心を伝える
3. 実用性：保護者が理解しやすく、実践可能な説明
4. 安全性：必要な場合のみ受診を推奨

【回答のポイント】
- その症状・行動の医学的メカニズムを、必要に応じて簡潔に説明
- 感覚過敏、神経発達などの基本的な医学知識は、その場面で特に重要な場合に言及
- 具体的な場面に即した実践的なアドバイス

【引用すべき文献・ガイドライン】
- DSM-5（米国精神医学会, 2013）
- ICD-11（WHO, 2022）
- 日本小児神経学会「ASD診療ガイドライン」
- Cochrane Review（システマティックレビュー）
- 厚生労働省「発達障害者支援法」

【禁止事項】
- 診断行為（「ASDです」と断定）※診断は医師の対面診察が必要
- 具体的な薬の推奨（「◯◯を飲んでください」）※処方は医師のみ
- 民間療法・代替医療の推奨（エビデンスなし）
- 「様子を見ましょう」のみの回答（具体的な観察ポイントを示す）

【質問の範囲について】
- ASD・発達障害と明らかに無関係な質問（一般的な料理レシピ、スポーツのルール、一般的な天気予報、政治的見解、ビジネス相談など）には、以下のお断りメッセージ**のみ**を返してください。お断り後に例示的な質問や追加の回答を一切含めないでください：
  「申し訳ございませんが、その質問はASD支援の専門範囲を超えているため、お答えを控えさせていただきます。ASDのお子さんの支援や、保護者の方のお悩みに関することであれば、喜んでお答えいたします。」
- ただし、一見無関係に見えても、ASDや発達支援と間接的に関連する可能性がある場合は、その医学的関連性を簡潔に説明した上で回答を試みてください
"""
        },
        
        "special_education_teacher": {
            "name": "特別支援教育専門家",
            "icon": "🏫",
            "role": "特別支援教育歴15年のベテラン教師",
            "expertise": ["IEP", "合理的配慮", "インクルーシブ教育", "UD"],
            "system_prompt": """
あなたは特別支援教育歴15年のベテラン教師です。

【専門知識】
- 個別教育計画(IEP)の作成と評価
- 合理的配慮の具体例（障害者差別解消法）
- インクルーシブ教育の実践
- ユニバーサルデザイン（UD）の教室づくり
- 視覚支援ツール（絵カード、スケジュールボードなど）

【回答の原則】
1. 状況適合性：その場面で最も効果的な支援方法を優先
2. 実践的：今日から実行できる提案
3. 簡潔性：長々と説明せず、要点を絞る
4. 現実的：家庭で無理なくできる範囲

【回答のポイント】
- その状況で特に有効な支援方法を提示
- 視覚支援、構造化、合理的配慮などの基本ツールは、その場面で効果的な場合に提案
- 全ての場面に同じ方法論を機械的に適用しない

【引用すべき資料・制度】
- 文部科学省「特別支援教育の推進について」（2007）
- 「合理的配慮」の具体例（文科省, 2012）
- ユニバーサルデザイン（CAST, 2011）
- 「個別の教育支援計画」「個別の指導計画」
- インクルーシブ教育システム構築事業

【禁止事項】
- 学校批判（「先生が悪い」など）
- 理想論のみ（現場の制約を無視した提案）
- 保護者に過度な負担を求める（「毎日学校に行って...」など）
- 「特別支援学級に行けばいい」などの安易な提案

【質問の範囲について】
- ASD・発達障害と明らかに無関係な質問（一般的な料理レシピ、スポーツのルール、一般的な天気予報、政治的見解、ビジネス相談など）には、以下のお断りメッセージ**のみ**を返してください。お断り後に例示的な質問や追加の回答を一切含めないでください：
  「申し訳ございませんが、その質問はASD支援の専門範囲を超えているため、お答えを控えさせていただきます。ASDのお子さんの支援や、保護者の方のお悩みに関することであれば、喜んでお答えいたします。」
- ただし、一見無関係に見えても、ASDや発達支援と間接的に関連する可能性がある場合（例：学校行事、社会的イベントなど）は、その教育的関連性を簡潔に説明した上で回答を試みてください
"""
        },
        
        "family_support_specialist": {
            "name": "家族支援専門家",
            "icon": "💙",
            "role": "家族全体を支援する家族療法の専門家",
            "expertise": ["ペアトレ", "保護者メンタルヘルス", "きょうだい支援", "夫婦連携"],
            "system_prompt": """
あなたは家族全体を支援する家族療法の専門家です。

【専門知識】
- ペアレント・トレーニング（前田・佐藤モデル）
- 保護者のストレス管理とバーンアウト予防
- きょうだい児支援（シブリングサポート）
- 夫婦の役割分担とコミュニケーション
- レジリエンス（回復力）の強化

【回答の原則】
1. 状況適合性：その場面での家族の気持ちに寄り添う
2. 簡潔性：長々と説明せず、心に響く言葉を
3. 実用性：今できる具体的な対処法
4. 共感：保護者の頑張りを認める

【回答のポイント】
- その場面での保護者の気持ちを理解し、共感を示す
- セルフケア、きょうだい支援、レスパイトケアなどは、その状況で特に関連性が高い場合に言及
- 全ての質問に対して同じパターンの回答を機械的に繰り返さない

【引用すべき概念・プログラム】
- ペアレント・トレーニング（行動療法ベース）
- レジリエンス理論（Masten, A. S.）
- マインドフルネス（ストレス軽減法）
- 「Good enough parent」（Winnicott, D. W.）
- きょうだい支援プログラム（Sibshops）

【禁止事項】
- 完璧主義の押し付け（「もっと頑張れば...」）
- 保護者の感情を否定（「それは間違っています」）
- 「頑張れ」の安易な使用（すでに頑張っている）
- きょうだいを「我慢させるべき」という考え

【質問の範囲について】
- ASD・発達障害と明らかに無関係な質問（一般的な料理レシピ、スポーツのルール、一般的な天気予報、政治的見解、ビジネス相談など）には、以下のお断りメッセージ**のみ**を返してください。お断り後に例示的な質問や追加の回答を一切含めないでください：
  「申し訳ございませんが、その質問はASD支援の専門範囲を超えているため、お答えを控えさせていただきます。ASDのお子さんの支援や、保護者の方のお悩みに関することであれば、喜んでお答えいたします。」
- ただし、一見無関係に見えても、ASDや発達支援と間接的に関連する可能性がある場合（例：家族のストレス管理、保護者のメンタルヘルスなど）は、その関連性を簡潔に説明した上で回答を試みてください
"""
        }
    }
    
    def __init__(self):
        """初期化"""
        try:
            self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
            self.model = Settings.OPENAI_MODEL
            self.debug_collector = get_debug_collector()
            logger.info("SpecializedAgentService initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SpecializedAgentService: {e}")
            raise
    
    def generate_expert_response(
        self,
        agent_id: str,
        question: str,
        context: str
    ) -> Optional[str]:
        """
        特定の専門家エージェントから回答を生成
        
        Args:
            agent_id: エージェントID（clinical_psychologist など）
            question: 保護者からの質問
            context: 質問の背景情報
            
        Returns:
            専門家の回答
        """
        try:
            if agent_id not in self.AGENTS:
                logger.error(f"Invalid agent_id: {agent_id}")
                return None
            
            agent = self.AGENTS[agent_id]
            
            user_message = f"""
【質問の背景】
{context}

【保護者からの質問】
{question}

【あなたの役割】
{agent['role']}として、あなたの専門分野から見た回答を提供してください。

【回答形式】
## {agent['icon']} 専門的見解
（あなたの専門分野からの視点）

## 💡 具体的な方法
（今日から実践できること、ステップバイステップで）

## ⚠️ 注意点
（リスクや限界、こんな場合は専門家に相談を）

## 📚 参考情報
（理論名、研究者名、ガイドライン名など。可能であれば）

※他の専門家と意見が異なる可能性がある場合は、その旨を明記してください。
"""
            
            # API呼び出しの計測開始
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": agent['system_prompt']},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=Settings.MAX_TOKENS * 3,  # 詳細な回答のため多めに
                temperature=0.7
            )
            
            # デバッグ情報を記録
            response_time = time.time() - start_time
            self.debug_collector.add_api_call(
                model=self.model,
                agent_type=f"expert_{agent_id}",
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                response_time=response_time,
                temperature=0.7,
                max_tokens=Settings.MAX_TOKENS * 3,
                stream=False
            )
            
            expert_response = response.choices[0].message.content
            
            # 専門家回答の品質を評価（品質チェックエージェント）
            if Settings.DEBUG_MODE or Settings.DEBUG_LOG_ALWAYS:
                try:
                    from app.services.agent_coordinator import AgentCoordinator
                    coordinator = AgentCoordinator()
                    
                    quality_result = coordinator.validate_content_quality(
                        content_type="expert_response",
                        content={
                            "agent": agent['name'],
                            "question": question,
                            "response": expert_response
                        },
                        criteria={
                            "expertise": "専門性が反映されているか",
                            "clarity": "明確で理解しやすいか",
                            "practical": "実践的なアドバイスが含まれているか",
                            "empathy": "保護者に寄り添った内容か"
                        }
                    )
                    
                    # 品質スコアを記録（0-100）
                    self.debug_collector.add_evaluation(
                        evaluation_type=f"expert_quality_{agent_id}",
                        score=quality_result.get("score", 0),
                        criteria=f"{agent['name']}の回答品質評価",
                        details={
                            "is_valid": quality_result.get("is_valid", True),
                            "issues": quality_result.get("issues", []),
                            "suggestions": quality_result.get("suggestions", [])
                        }
                    )
                except Exception as e:
                    logger.warning(f"Quality check failed for {agent_id}: {e}")
            
            return expert_response
            
        except Exception as e:
            logger.error(f"Error generating expert response from {agent_id}: {e}")
            return None
    
    def generate_comprehensive_response(
        self,
        question: str,
        context: str,
        selected_agents: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        複数の専門家エージェントから回答を取得し、統合する
        
        Args:
            question: 保護者からの質問
            context: 質問の背景情報
            selected_agents: 使用するエージェントのリスト（Noneの場合は全エージェント）
            
        Returns:
            {
                "individual_responses": {"agent_id": "response", ...},
                "synthesized_response": "統合された回答"
            }
        """
        try:
            # 使用するエージェントを決定
            if selected_agents is None:
                selected_agents = list(self.AGENTS.keys())
            
            # 各エージェントから回答を取得
            individual_responses = {}
            for agent_id in selected_agents:
                logger.info(f"Generating response from {agent_id}...")
                response = self.generate_expert_response(agent_id, question, context)
                if response:
                    individual_responses[agent_id] = response
            
            # 回答を統合
            synthesized = self._synthesize_responses(
                question, 
                context, 
                individual_responses
            )
            
            return {
                "individual_responses": individual_responses,
                "synthesized_response": synthesized
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive response: {e}")
            return {
                "individual_responses": {},
                "synthesized_response": "申し訳ございません。回答の生成に失敗しました。"
            }
    
    def _synthesize_responses(
        self,
        question: str,
        context: str,
        responses: Dict[str, str]
    ) -> str:
        """
        各専門家の回答を統合して最終回答を生成
        
        Args:
            question: 元の質問
            context: 背景情報
            responses: 各エージェントの回答
            
        Returns:
            統合された最終回答
        """
        try:
            # 専門家の意見をまとめる
            expert_opinions = []
            for agent_id, response in responses.items():
                agent = self.AGENTS[agent_id]
                expert_opinions.append(f"""
◆ {agent['icon']} {agent['name']}の見解
{response}
""")
            
            synthesis_prompt = f"""
あなたは医療・教育・心理の統括コーディネーターです。
以下の専門家からの意見を統合し、保護者にとって分かりやすく、
実践的で、かつ専門性の高い回答を作成してください。

【元の質問】
{question}

【背景】
{context}

【専門家の意見】
{chr(10).join(expert_opinions)}

【統合の原則】
1. 共通点を強調：専門家間で一致している重要なポイントを明確に
2. 相違点を説明：異なる見解がある場合、その理由と文脈を説明
3. 優先順位：緊急性・重要性の高い順に整理
4. バランス：子ども支援と保護者支援の両方を考慮
5. 実践性：今日から使える具体的な方法を含める

【最終回答の構成】
必ず以下の構成で回答してください：

## 📋 専門家の共通見解
（全専門家が同意している最も重要なポイント）

## 🔍 それぞれの専門的視点

### {self.AGENTS['pediatrician']['icon']} 医学的観点
...

### {self.AGENTS['clinical_psychologist']['icon']} 心理・行動的観点
...

### {self.AGENTS['special_education_teacher']['icon']} 教育的観点
...

### {self.AGENTS['family_support_specialist']['icon']} 家族支援の観点
...

## 💡 具体的なアクションプラン
（優先順位順に、今日からできること）

1. **最優先：**
2. **次のステップ：**
3. **長期的に：**

## ⚠️ 注意点・専門家への相談が必要な場合
（この方法が適さないケース、医師・臨床心理士に相談すべき時）

## 📚 参考情報
（専門家が言及した理論、研究、ガイドライン）

---
💙 **保護者の皆さまへ**
（励ましのメッセージ）
"""
            
            # API呼び出しの計測開始
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは複数の専門家の意見を統合する優秀なコーディネーターです。"},
                    {"role": "user", "content": synthesis_prompt}
                ],
                max_tokens=Settings.MAX_TOKENS * 4,
                temperature=0.7
            )
            
            # デバッグ情報を記録
            response_time = time.time() - start_time
            self.debug_collector.add_api_call(
                model=self.model,
                agent_type="synthesizer",
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                response_time=response_time,
                temperature=0.7,
                max_tokens=Settings.MAX_TOKENS * 4,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error synthesizing responses: {e}")
            return "申し訳ございません。回答の統合に失敗しました。"
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """エージェント情報を取得"""
        return self.AGENTS.get(agent_id)
    
    def list_agents(self) -> List[Dict]:
        """全エージェントの情報を取得"""
        return [
            {
                "id": agent_id,
                "name": agent['name'],
                "icon": agent['icon'],
                "role": agent['role'],
                "expertise": agent['expertise']
            }
            for agent_id, agent in self.AGENTS.items()
        ]
    
    def get_agent_id_from_display_name(self, display_name: str) -> Optional[str]:
        """
        表示名からエージェントIDを取得
        
        Args:
            display_name: 表示名（例: "🧠 臨床心理士"）
            
        Returns:
            エージェントID（例: "clinical_psychologist"）
        """
        # 表示名からアイコンと名前を分離
        name_part = display_name.split(" ", 1)[-1] if " " in display_name else display_name
        
        # 各エージェントの名前と比較
        for agent_id, agent in self.AGENTS.items():
            if agent['name'] == name_part:
                return agent_id
        
        return None
    
    def generate_single_expert_response_stream(
        self,
        agent_id: str,
        question: str,
        context: str,
        tone: str = "friendly"
    ) -> Generator[str, None, None]:
        """
        特定の専門家による回答（ストリーミング）
        
        Args:
            agent_id: エージェントID（clinical_psychologist など）
            question: 保護者からの質問
            context: 質問の背景情報
            tone: 口調 ("friendly" or "standard")
            
        Yields:
            回答の断片（ストリーミング）
        """
        try:
            if agent_id not in self.AGENTS:
                logger.error(f"Invalid agent_id: {agent_id}")
                yield "エラー: 指定された専門家が見つかりません。"
                return
            
            agent = self.AGENTS[agent_id]
            
            # 口調に応じた追加指示
            if tone == "friendly":
                tone_instruction = """
【口調】
- 「〜ですね」「〜なんです」といった柔らかい語尾
- 「お子さん」「保護者の方」といった温かい呼びかけ
- 専門用語は使うが、必ずかみ砕いて説明
- 共感的で励ます姿勢
"""
            else:
                tone_instruction = """
【口調】
- 専門的で正確な表現
- エビデンスベース
- 実践的なアドバイス
"""
            
            user_message = f"""
【質問の背景】
{context if context else "（背景情報なし）"}

【保護者からの質問】
{question}

【あなたの役割】
{agent['role']}として、あなたの専門分野から見た回答を提供してください。

{tone_instruction}

【回答のお願い】
簡潔かつ分かりやすく、実践的なアドバイスをお願いします。
専門用語を使う場合は、必ず分かりやすく説明してください。
"""
            
            # API呼び出しの計測開始
            start_time = time.time()
            
            # ストリーミングで回答を生成
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": agent['system_prompt']},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=Settings.MAX_TOKENS * 2,
                temperature=0.8 if tone == "friendly" else 0.7,
                stream=True,
                stream_options={"include_usage": True}  # 使用情報を含める
            )
            
            usage_info = None
            collected_response = []
            try:
                for chunk in stream:
                    # choicesが空でないことを確認
                    if chunk.choices and len(chunk.choices) > 0:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            collected_response.append(content)
                            yield content
                    # 最後のチャンクに使用情報が含まれる
                    if hasattr(chunk, 'usage') and chunk.usage is not None:
                        usage_info = chunk.usage
            finally:
                # Generatorが終了した後、またはエラーが発生した後に必ず実行
                # finally内のエラーが外側のexceptに伝播しないようにする
                try:
                    response_time = time.time() - start_time
                    full_response = "".join(collected_response)
                    
                    # トークン数の取得または推定
                    try:
                        if usage_info:
                            prompt_tokens = usage_info.prompt_tokens
                            completion_tokens = usage_info.completion_tokens
                            logger.info(f"Usage info received: prompt={prompt_tokens}, completion={completion_tokens}")
                        else:
                            # APIからusage情報が取得できない場合、tiktokenで推定
                            logger.warning("No usage info from API, estimating with tiktoken")
                            token_counter = get_token_counter(self.model)
                            estimated = token_counter.estimate_streaming_tokens(
                                prompt=user_message,
                                response=full_response,
                                system_prompt=agent['system_prompt']
                            )
                            prompt_tokens = estimated['prompt_tokens']
                            completion_tokens = estimated['completion_tokens']
                    except Exception as e:
                        logger.error(f"Token estimation failed: {e}", exc_info=True)
                        # フォールバック：概算値を使用
                        prompt_tokens = len(user_message) // 4
                        completion_tokens = len(full_response) // 4
                    
                    if self.debug_collector:
                        self.debug_collector.add_api_call(
                            model=self.model,
                            agent_type=f"expert_stream_{agent_id}",
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            response_time=response_time,
                            temperature=0.8 if tone == "friendly" else 0.7,
                            max_tokens=Settings.MAX_TOKENS * 2,
                            stream=True
                        )
                    
                    # 品質評価（常に実行して安全性を確保）
                    if full_response and self.debug_collector:
                        try:
                            from app.services.agent_coordinator import AgentCoordinator
                            coordinator = AgentCoordinator()
                            
                            quality_result = coordinator.validate_content_quality(
                                content_type="expert_response",
                                content={
                                    "agent": agent['name'],
                                    "question": question,
                                    "response": full_response
                                },
                                criteria={
                                    "expertise": "専門性が反映されているか",
                                    "clarity": "明確で理解しやすいか",
                                    "practical": "実践的なアドバイスが含まれているか",
                                    "empathy": "保護者に寄り添った内容か",
                                    "safety": "倫理的に適切で安全な内容か"
                                }
                            )
                            
                            # 品質スコアを記録（0-100）
                            self.debug_collector.add_evaluation(
                                evaluation_type=f"expert_quality_{agent_id}",
                                score=quality_result.get("score", 0),
                                criteria=f"{agent['name']}の回答品質評価",
                                details={
                                    "is_valid": quality_result.get("is_valid", True),
                                    "issues": quality_result.get("issues", []),
                                    "suggestions": quality_result.get("suggestions", [])
                                }
                            )
                            
                            # 低スコアまたは無効な回答の場合、警告をログに記録
                            if not quality_result.get("is_valid", True) or quality_result.get("score", 100) < 60:
                                logger.warning(
                                    f"Low quality response detected: "
                                    f"score={quality_result.get('score', 0)}, "
                                    f"is_valid={quality_result.get('is_valid', True)}, "
                                    f"issues={quality_result.get('issues', [])}"
                                )
                        except Exception as eval_error:
                            logger.error(f"Quality check failed for {agent_id}: {eval_error}", exc_info=True)
                
                except Exception as finally_error:
                    logger.error(f"Error in finally block: {finally_error}", exc_info=True)
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error in generate_single_expert_response_stream: {e}\n{error_details}")
            yield f"\n\n[DEBUG] エラーが発生しました: {str(e)}\n詳細はログを確認してください。"
    
    def generate_quick_response_stream(
        self,
        question: str,
        context: str,
        tone: str = "friendly"
    ) -> Generator[str, None, None]:
        """
        簡易モード：1人の専門家による高速回答（ストリーミング）
        
        Args:
            question: 保護者からの質問
            context: 質問の背景情報
            tone: 口調 ("friendly" or "standard")
            
        Yields:
            回答の断片（ストリーミング）
        """
        try:
            # 口調に応じたプロンプト
            if tone == "friendly":
                system_prompt = """
あなたは子育て支援の経験が豊富な、やさしい専門家です。

【あなたの役割】
- ASD（自閉スペクトラム症）のお子さんを持つ保護者の相談相手
- 臨床心理士、小児科医、特別支援教育、家族支援の知識を総合的に持つ
- 専門的でありながら、親しみやすく分かりやすい説明

【口調の特徴】
- 「〜ですね」「〜なんです」といった柔らかい語尾
- 「お子さん」「保護者の方」といった温かい呼びかけ
- 「実は〜」「〜かもしれません」といった共感的な表現
- 専門用語は使うが、必ずかみ砕いた説明を付ける

【回答の原則】
1. まず共感：保護者の気持ちを受け止める
2. 分かりやすく：専門用語→かみ砕いた説明
3. 具体的に：今日からできることを提案
4. 励まし：保護者を責めず、前向きな言葉で

【回答の構成】
1. 共感の言葉（「〜なんですね」「大変でしたね」）
2. 分かりやすい説明（「実は〜」「〜ということなんです」）
3. 具体的な方法（「まず〜してみましょう」「次に〜」）
4. 励ましの言葉（「一緒に〜していきましょう」）

【禁止事項】
- 堅苦しい表現（「〜である」「〜のみならず」など）
- 専門用語の乱用（必ず説明を付ける）
- 保護者を責める表現
- 悲観的な表現

【質問の範囲について】
- ASD・発達障害と明らかに無関係な質問（一般的な料理レシピ、スポーツのルール、一般的な天気予報、政治的見解、ビジネス相談など）には、以下のお断りメッセージ**のみ**を返してください。お断り後に例示的な質問や追加の回答を一切含めないでください：
  「申し訳ございませんが、その質問はASD支援の専門範囲を超えているため、お答えを控えさせていただきます。ASDのお子さんの支援や、保護者の方のお悩みに関することであれば、喜んでお答えいたします。」
- ただし、一見無関係に見えても、ASDや発達支援と間接的に関連する可能性がある場合は、その関連性を簡潔に説明した上で回答を試みてください
"""
            else:  # standard
                system_prompt = """
あなたはASD支援の専門家チームの代表として回答します。

【専門知識】
- 臨床心理学（ABA、TEACCH、SST）
- 医学（神経学、発達評価、併存症）
- 特別支援教育（合理的配慮、IEP）
- 家族支援（ペアトレ、レジリエンス）

【回答の原則】
1. エビデンスベース：研究・理論に基づく
2. 実践的：今日から使える方法
3. 多角的：複数の専門分野から総合的に
4. 励まし：保護者を支援する姿勢

【回答の構成】
1. 状況の整理
2. 専門的見解
3. 具体的な方法
4. 注意点と参考情報

【質問の範囲について】
- ASD・発達障害と明らかに無関係な質問（一般的な料理レシピ、スポーツのルール、一般的な天気予報、政治的見解、ビジネス相談など）には、以下のお断りメッセージ**のみ**を返してください。お断り後に例示的な質問や追加の回答を一切含めないでください：
  「申し訳ございませんが、その質問はASD支援の専門範囲を超えているため、お答えを控えさせていただきます。ASDのお子さんの支援や、保護者の方のお悩みに関することであれば、喜んでお答えいたします。」
- ただし、一見無関係に見えても、ASDや発達支援と間接的に関連する可能性がある場合は、その関連性を簡潔に説明した上で回答を試みてください
"""
            
            user_message = f"""
【質問の背景】
{context if context else "（背景情報なし）"}

【保護者からの質問】
{question}

【回答のお願い】
簡潔かつ分かりやすく、実践的なアドバイスをお願いします。
"""
            
            # API呼び出しの計測開始
            start_time = time.time()
            
            # ストリーミングで回答を生成
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=Settings.MAX_TOKENS * 2,
                temperature=0.8 if tone == "friendly" else 0.7,
                stream=True,
                stream_options={"include_usage": True}  # 使用情報を含める
            )
            
            usage_info = None
            collected_response = []
            try:
                for chunk in stream:
                    # choicesが空でないことを確認
                    if chunk.choices and len(chunk.choices) > 0:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            collected_response.append(content)
                            yield content
                    # 最後のチャンクに使用情報が含まれる
                    if hasattr(chunk, 'usage') and chunk.usage is not None:
                        usage_info = chunk.usage
            finally:
                # Generatorが終了した後、またはエラーが発生した後に必ず実行
                # finally内のエラーが外側のexceptに伝播しないようにする
                try:
                    response_time = time.time() - start_time
                    full_response = "".join(collected_response)
                    
                    # トークン数の取得または推定
                    try:
                        if usage_info:
                            prompt_tokens = usage_info.prompt_tokens
                            completion_tokens = usage_info.completion_tokens
                        else:
                            # APIからusage情報が取得できない場合、tiktokenで推定
                            token_counter = get_token_counter(self.model)
                            estimated = token_counter.estimate_streaming_tokens(
                                prompt=user_message,
                                response=full_response,
                                system_prompt=system_prompt
                            )
                            prompt_tokens = estimated['prompt_tokens']
                            completion_tokens = estimated['completion_tokens']
                    except Exception as e:
                        logger.error(f"Token estimation failed: {e}", exc_info=True)
                        prompt_tokens = len(user_message) // 4
                        completion_tokens = len(full_response) // 4
                    
                    if self.debug_collector:
                        self.debug_collector.add_api_call(
                            model=self.model,
                            agent_type="quick_response",
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            response_time=response_time,
                            temperature=0.8 if tone == "friendly" else 0.7,
                            max_tokens=Settings.MAX_TOKENS * 2,
                            stream=True
                        )
                except Exception as finally_error:
                    logger.error(f"Error in finally block (quick_response): {finally_error}", exc_info=True)
                    
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error in generate_quick_response_stream: {e}\n{error_details}")
            yield f"\n\n[DEBUG] エラーが発生しました: {str(e)}\n詳細はログを確認してください。"
    
    def generate_comprehensive_response_stream(
        self,
        question: str,
        context: str,
        tone: str = "friendly"
    ) -> Generator[str, None, None]:
        """
        詳細モード：4人の専門家チームによる回答（統合回答のみストリーミング）
        
        Args:
            question: 保護者からの質問
            context: 質問の背景情報
            tone: 口調 ("friendly" or "standard")
            
        Yields:
            統合回答の断片（ストリーミング）
        """
        try:
            # まず各専門家から回答を取得（非ストリーミング）
            individual_responses = {}
            for agent_id in self.AGENTS.keys():
                logger.info(f"Generating response from {agent_id}...")
                response = self.generate_expert_response(agent_id, question, context)
                if response:
                    individual_responses[agent_id] = response
            
            # 統合回答をストリーミングで生成
            expert_opinions = []
            for agent_id, response in individual_responses.items():
                agent = self.AGENTS[agent_id]
                expert_opinions.append(f"""
◆ {agent['icon']} {agent['name']}の見解
{response}
""")
            
            # 口調に応じた統合プロンプト
            if tone == "friendly":
                synthesis_instruction = """
あなたは子育て支援の統括コーディネーターです。
以下の専門家の意見を統合し、保護者にとって分かりやすく、
親しみやすい言葉で回答を作成してください。

【口調】
- 「〜ですね」「〜なんです」といった柔らかい語尾
- 「お子さん」「保護者の方」といった温かい呼びかけ
- 専門用語は使うが、必ずかみ砕いて説明

【構成】
まず共感の言葉から始めて、分かりやすく説明し、
具体的な方法を提案し、最後に励ましの言葉で締めくくってください。
"""
            else:  # standard
                synthesis_instruction = """
あなたは医療・教育・心理の統括コーディネーターです。
以下の専門家の意見を統合し、専門性を保ちつつ、
保護者にとって実践的な回答を作成してください。
"""
            
            synthesis_prompt = f"""
{synthesis_instruction}

【元の質問】
{question}

【背景】
{context if context else "（背景情報なし）"}

【専門家の意見】
{chr(10).join(expert_opinions)}

【統合の原則】
1. 共通点を強調：専門家が一致している重要なポイント
2. 実践性：今日から使える具体的な方法
3. バランス：子ども支援と保護者支援の両方
4. 励まし：保護者を支援する姿勢
"""
            
            # API呼び出しの計測開始
            synthesis_start_time = time.time()
            
            # ストリーミングで統合回答を生成
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは複数の専門家の意見を統合する優秀なコーディネーターです。"},
                    {"role": "user", "content": synthesis_prompt}
                ],
                max_tokens=Settings.MAX_TOKENS * 4,
                temperature=0.8 if tone == "friendly" else 0.7,
                stream=True,
                stream_options={"include_usage": True}  # 使用情報を含める
            )
            
            usage_info = None
            collected_response = []
            try:
                for chunk in stream:
                    # choicesが空でないことを確認
                    if chunk.choices and len(chunk.choices) > 0:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            collected_response.append(content)
                            yield content
                    # 最後のチャンクに使用情報が含まれる
                    if hasattr(chunk, 'usage') and chunk.usage is not None:
                        usage_info = chunk.usage
            finally:
                # Generatorが終了した後、またはエラーが発生した後に必ず実行
                # finally内のエラーが外側のexceptに伝播しないようにする
                try:
                    response_time = time.time() - synthesis_start_time
                    full_response = "".join(collected_response)
                    
                    # トークン数の取得または推定
                    try:
                        if usage_info:
                            prompt_tokens = usage_info.prompt_tokens
                            completion_tokens = usage_info.completion_tokens
                        else:
                            # APIからusage情報が取得できない場合、tiktokenで推定
                            token_counter = get_token_counter(self.model)
                            estimated = token_counter.estimate_streaming_tokens(
                                prompt=synthesis_prompt,
                                response=full_response,
                                system_prompt="あなたは複数の専門家の意見を統合する優秀なコーディネーターです。"
                            )
                            prompt_tokens = estimated['prompt_tokens']
                            completion_tokens = estimated['completion_tokens']
                    except Exception as e:
                        logger.error(f"Token estimation failed: {e}", exc_info=True)
                        prompt_tokens = len(synthesis_prompt) // 4
                        completion_tokens = len(full_response) // 4
                    
                    if self.debug_collector:
                        self.debug_collector.add_api_call(
                            model=self.model,
                            agent_type="comprehensive_synthesis",
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            response_time=response_time,
                            temperature=0.8 if tone == "friendly" else 0.7,
                            max_tokens=Settings.MAX_TOKENS * 4,
                            stream=True
                        )
                except Exception as finally_error:
                    logger.error(f"Error in finally block (comprehensive): {finally_error}", exc_info=True)
                    
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error in generate_comprehensive_response_stream: {e}\n{error_details}")
            yield f"\n\n[DEBUG] エラーが発生しました: {str(e)}\n詳細はログを確認してください。"
    
    def generate_sequential_expert_responses_stream(
        self,
        question: str,
        context: str,
        tone: str = "friendly"
    ) -> Generator[Dict[str, str], None, None]:
        """
        各専門家が順番に回答（ストリーミング）
        
        Args:
            question: 保護者からの質問
            context: 質問の背景情報
            tone: 口調 ("friendly" or "standard")
            
        Yields:
            {"agent_id": str, "agent_name": str, "agent_icon": str, "chunk": str} の辞書
        """
        try:
            for agent_id in self.AGENTS.keys():
                agent = self.AGENTS[agent_id]
                logger.info(f"Streaming response from {agent_id}...")
                
                # 各専門家の情報をまず返す
                yield {
                    "agent_id": agent_id,
                    "agent_name": agent['name'],
                    "agent_icon": agent['icon'],
                    "chunk": "__START__"  # 開始マーカー
                }
                
                # 口調に応じたプロンプト調整
                if tone == "friendly":
                    tone_instruction = """
【口調】
- 「〜ですね」「〜なんです」といった柔らかい語尾
- 「お子さん」「保護者の方」といった温かい呼びかけ
- 専門用語は使うが、必ずかみ砕いて説明
- 共感的で励ます姿勢
"""
                else:
                    tone_instruction = """
【口調】
- 専門的で正確な表現
- エビデンスベース
- 実践的なアドバイス
"""
                
                user_message = f"""
【質問の背景】
{context if context else "（背景情報なし）"}

【保護者からの質問】
{question}

【あなたの役割】
{agent['role']}として、あなたの専門分野から見た回答を提供してください。

{tone_instruction}

【回答形式】
簡潔に、実践的に、保護者に寄り添って回答してください。
専門用語は使っても構いませんが、必ず分かりやすく説明してください。
"""
                
                # API呼び出しの計測開始
                start_time = time.time()
                
                # ストリーミングで回答を生成
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": agent['system_prompt']},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=Settings.MAX_TOKENS * 2,
                    temperature=0.8 if tone == "friendly" else 0.7,
                    stream=True,
                    stream_options={"include_usage": True}  # 使用情報を含める
                )
                
                usage_info = None
                collected_response = []
                try:
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            collected_response.append(content)
                            yield {
                                "agent_id": agent_id,
                                "agent_name": agent['name'],
                                "agent_icon": agent['icon'],
                                "chunk": content
                            }
                        # 最後のチャンクに使用情報が含まれる
                        if hasattr(chunk, 'usage') and chunk.usage is not None:
                            usage_info = chunk.usage
                finally:
                    # Generatorが終了した後、またはエラーが発生した後に必ず実行
                    # finally内のエラーが外側のexceptに伝播しないようにする
                    try:
                        response_time = time.time() - start_time
                        full_response = "".join(collected_response)
                        
                        # トークン数の取得または推定
                        try:
                            if usage_info:
                                prompt_tokens = usage_info.prompt_tokens
                                completion_tokens = usage_info.completion_tokens
                            else:
                                # APIからusage情報が取得できない場合、tiktokenで推定
                                token_counter = get_token_counter(self.model)
                                estimated = token_counter.estimate_streaming_tokens(
                                    prompt=user_message,
                                    response=full_response,
                                    system_prompt=agent['system_prompt']
                                )
                                prompt_tokens = estimated['prompt_tokens']
                                completion_tokens = estimated['completion_tokens']
                        except Exception as e:
                            logger.error(f"Token estimation failed: {e}", exc_info=True)
                            prompt_tokens = len(user_message) // 4
                            completion_tokens = len(full_response) // 4
                        
                        if self.debug_collector:
                            self.debug_collector.add_api_call(
                                model=self.model,
                                agent_type=f"sequential_{agent_id}",
                                prompt_tokens=prompt_tokens,
                                completion_tokens=completion_tokens,
                                response_time=response_time,
                                temperature=0.8 if tone == "friendly" else 0.7,
                                max_tokens=Settings.MAX_TOKENS * 2,
                                stream=True
                            )
                    except Exception as finally_error:
                        logger.error(f"Error in finally block (sequential_{agent_id}): {finally_error}", exc_info=True)
                
                # 終了マーカー
                yield {
                    "agent_id": agent_id,
                    "agent_name": agent['name'],
                    "agent_icon": agent['icon'],
                    "chunk": "__END__"
                }
                    
        except Exception as e:
            logger.error(f"Error in generate_sequential_expert_responses_stream: {e}")
            yield {
                "agent_id": "error",
                "agent_name": "エラー",
                "agent_icon": "❌",
                "chunk": "申し訳ございません。回答の生成に失敗しました。"
            }

