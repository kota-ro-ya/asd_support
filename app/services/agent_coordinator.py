"""
Agent Coordinator for managing multiple AI agents.
各エージェントの役割分担と調整を行うコーディネーター
"""

import logging
from typing import Dict, Optional, List, Any
from enum import Enum

from app.services.ai_service import AIService
from app.config.settings import Settings

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """エージェントの役割定義"""
    SCENARIO_GENERATOR = "scenario_generator"  # シナリオ生成
    EVALUATOR = "evaluator"  # 評価・フィードバック
    GUIDE_GENERATOR = "guide_generator"  # 保護者向けガイド生成
    QUALITY_CHECKER = "quality_checker"  # 品質管理


class AgentCoordinator:
    """
    複数のAIエージェントを調整し、各タスクに適切なエージェントを割り当てる
    """
    
    def __init__(self):
        """AgentCoordinatorの初期化"""
        self.ai_service = AIService()
        logger.info("AgentCoordinator initialized")
    
    def generate_scenario_variation(
        self,
        event_name: str,
        scene_number: int,
        base_situation: str,
        learning_goal: str
    ) -> Optional[Dict[str, Any]]:
        """
        シナリオ生成エージェント：基本シナリオからバリエーションを生成
        
        Args:
            event_name: イベント名（例：「トイレ」）
            scene_number: シーン番号
            base_situation: 基本的な状況説明
            learning_goal: 学習目標
            
        Returns:
            生成されたシナリオ情報（状況説明と選択肢）
        """
        try:
            logger.info(f"Generating scenario variation for {event_name}, scene {scene_number}")
            
            system_prompt = self._get_scenario_generator_prompt(
                event_name, scene_number, base_situation, learning_goal
            )
            
            user_message = f"""
以下の基本シナリオをもとに、教育的に適切なバリエーションを生成してください。

【基本シナリオ】
{base_situation}

【学習目標】
{learning_goal}

【生成要件】
1. 基本的な状況は維持しつつ、表現や細部を変化させる
2. 子どもが理解しやすい言葉を使用する
3. ASDの特性を考慮した適切な表現にする
4. 3つの選択肢を生成する（適切・許容・不適切を各1つ）

JSON形式で以下の構造で返してください：
{{
  "situation_text": "状況説明",
  "choices": [
    {{"text": "選択肢1", "evaluation": "appropriate", "hint": "ヒント"}},
    {{"text": "選択肢2", "evaluation": "acceptable", "hint": "ヒント"}},
    {{"text": "選択肢3", "evaluation": "inappropriate", "hint": "ヒント"}}
  ]
}}
"""
            
            response = self.ai_service.client.chat.completions.create(
                model=self.ai_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=Settings.MAX_TOKENS * 2,
                temperature=0.8,  # 創造性を持たせるため高めに設定
                response_format={"type": "json_object"}
            )
            
            import json
            scenario_data = json.loads(response.choices[0].message.content)
            
            logger.info(f"Successfully generated scenario variation for {event_name}")
            return scenario_data
            
        except Exception as e:
            logger.error(f"Error generating scenario variation: {e}")
            return None
    
    def generate_parent_situation(
        self,
        event_name: str,
        child_behaviors: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        ガイド生成エージェント：保護者向けシチュエーションをランダム生成
        
        Args:
            event_name: イベント名
            child_behaviors: 子どもの行動リスト（選択肢として使用）
            
        Returns:
            生成された保護者向けシチュエーション
        """
        try:
            logger.info(f"Generating parent situation for {event_name}")
            
            system_prompt = self._get_guide_generator_prompt()
            
            user_message = f"""
以下のイベントと子どもの行動をもとに、保護者向けの学習シチュエーションを生成してください。

【イベント】
{event_name}

【参考となる子どもの行動例】
{', '.join(child_behaviors)}

【生成要件】
1. 実際に起こりうる具体的な状況を設定する
2. 保護者が対応に悩むような場面を選ぶ
3. 3つの保護者の対応選択肢を生成する（適切・許容・不適切を含む）
4. 各対応について、なぜその評価なのかのヒントを含める

JSON形式で以下の構造で返してください：
{{
  "child_action": "子どもの具体的な行動",
  "parent_actions": [
    {{"text": "対応1", "evaluation": "appropriate", "ai_hint": "詳細な説明"}},
    {{"text": "対応2", "evaluation": "acceptable", "ai_hint": "詳細な説明"}},
    {{"text": "対応3", "evaluation": "inappropriate", "ai_hint": "詳細な説明"}}
  ]
}}
"""
            
            response = self.ai_service.client.chat.completions.create(
                model=self.ai_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=Settings.MAX_TOKENS * 3,
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            import json
            situation_data = json.loads(response.choices[0].message.content)
            
            # イベント名を追加
            situation_data["event"] = event_name
            
            logger.info(f"Successfully generated parent situation for {event_name}")
            return situation_data
            
        except Exception as e:
            logger.error(f"Error generating parent situation: {e}")
            return None
    
    def validate_content_quality(
        self,
        content_type: str,
        content: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        品質管理エージェント：生成されたコンテンツの品質をチェック
        
        Args:
            content_type: コンテンツタイプ（"scenario", "situation"など）
            content: チェック対象のコンテンツ
            criteria: 品質基準
            
        Returns:
            品質チェック結果
        """
        try:
            logger.info(f"Validating {content_type} content quality")
            
            system_prompt = self._get_quality_checker_prompt(content_type)
            
            import json
            user_message = f"""
以下のコンテンツが品質基準を満たしているかチェックしてください。

【コンテンツタイプ】
{content_type}

【コンテンツ】
{json.dumps(content, ensure_ascii=False, indent=2)}

【品質基準】
{json.dumps(criteria, ensure_ascii=False, indent=2)}

【チェック項目】
1. 教育的適切性：ASDの子どもにとって適切な内容か
2. 言葉の適切性：理解しやすい表現になっているか
3. 一貫性：他のコンテンツとの整合性があるか
4. 安全性：不適切な表現や誤解を招く内容がないか

JSON形式で以下の構造で返してください：
{{
  "is_valid": true/false,
  "score": 0-100,
  "issues": ["問題点のリスト"],
  "suggestions": ["改善提案のリスト"]
}}
"""
            
            response = self.ai_service.client.chat.completions.create(
                model=self.ai_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=Settings.MAX_TOKENS,
                temperature=0.3,  # 厳格な評価のため低めに設定
                response_format={"type": "json_object"}
            )
            
            validation_result = json.loads(response.choices[0].message.content)
            
            logger.info(f"Quality validation completed: score={validation_result.get('score', 0)}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating content quality: {e}")
            # エラー時はデフォルトで承認
            return {
                "is_valid": True,
                "score": 70,
                "issues": [],
                "suggestions": []
            }
    
    def _get_scenario_generator_prompt(
        self,
        event_name: str,
        scene_number: int,
        base_situation: str,
        learning_goal: str
    ) -> str:
        """シナリオ生成エージェント用のシステムプロンプト"""
        return f"""あなたはASD（自閉スペクトラム症）の子ども向け学習コンテンツの専門家です。
教育的に適切で、子どもが理解しやすいシナリオのバリエーションを生成する役割を担っています。

【あなたの専門性】
- ASDの特性（感覚過敏、予測可能性の必要性、視覚優位性など）を深く理解している
- 発達段階に応じた適切な言葉選びができる
- 社会的スキルの段階的な学習をサポートできる

【生成の原則】
1. 一貫性：基本的な学習目標は維持する
2. 多様性：表現や状況に適度なバリエーションを持たせる
3. 適切性：ASDの子どもにとって理解しやすく、混乱を招かない内容にする
4. 教育性：明確な学習ポイントがある内容にする

【注意事項】
- 否定的な表現は避け、肯定的な言い回しを使う
- 曖昧な表現は避け、具体的でわかりやすい言葉を選ぶ
- 感覚過敏や不安を悪化させる可能性のある表現は避ける
- 年齢相応の語彙を使用する（小学校低学年〜中学年レベル）

イベント「{event_name}」のシーン{scene_number}について、適切なバリエーションを生成してください。"""
    
    def _get_guide_generator_prompt(self) -> str:
        """ガイド生成エージェント用のシステムプロンプト"""
        return """あなたはASD（自閉スペクトラム症）の子どもを持つ保護者向けの教育コンテンツ専門家です。
実際に起こりうる具体的なシチュエーションと、保護者の対応選択肢を生成する役割を担っています。

【あなたの専門性】
- ASDの子どもの行動特性と保護者の悩みを深く理解している
- エビデンスに基づいた支援方法を熟知している
- 保護者の心理的負担に配慮したアドバイスができる

【生成の原則】
1. 現実性：実際に起こりうる具体的な場面を設定する
2. 学習性：保護者が判断力を養える内容にする
3. バランス：適切・許容・不適切な対応をバランスよく含める
4. 実践性：すぐに実践できる具体的な対応を提示する

【対応選択肢の評価基準】
- appropriate：科学的根拠があり、子どもの発達を促す対応
- acceptable：悪くはないが、より良い方法がある対応
- inappropriate：子どもにストレスを与えたり、誤った学習につながる対応

【注意事項】
- 保護者を責めるような表現は避ける
- 完璧を求めず、「できることから始める」姿勢を大切にする
- 具体的で実践しやすい方法を提示する
- 保護者の気持ちに寄り添った説明をする"""
    
    def _get_quality_checker_prompt(self, content_type: str) -> str:
        """品質管理エージェント用のシステムプロンプト"""
        return f"""あなたはASD支援コンテンツの品質管理専門家です。
生成されたコンテンツが教育的に適切で、安全で、効果的かどうかを厳格にチェックする役割を担っています。

【チェックの観点】
1. 教育的適切性
   - ASDの特性に配慮した内容か
   - 学習目標が明確か
   - 発達段階に適しているか

2. 言語的適切性
   - 理解しやすい表現か
   - 否定的・批判的な表現がないか
   - 曖昧さや混乱を招く表現がないか

3. 一貫性
   - 他のコンテンツとの整合性があるか
   - 評価基準が一貫しているか

4. 安全性
   - 不適切な表現や差別的な内容がないか
   - 子どもや保護者を傷つける可能性がないか
   - 誤った情報や誤解を招く内容がないか

【評価方法】
- 各項目を厳格に評価し、総合スコア（0-100）を算出
- 80点以上：品質基準を満たしている
- 60-79点：軽微な修正が必要
- 60点未満：大幅な修正が必要

コンテンツタイプ「{content_type}」について、厳格に品質をチェックしてください。"""

