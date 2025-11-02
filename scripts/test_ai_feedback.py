#!/usr/bin/env python3
"""
保護者向けガイドのAIフィードバック機能をテストするスクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.ai_service import AIService
from app.config.settings import Settings

def test_brief_feedback():
    """簡易フィードバックのテスト"""
    print("=" * 80)
    print("簡易フィードバックのテスト")
    print("=" * 80)
    
    ai_service = AIService()
    
    # テストケース：床屋でバリカンの音にパニックになる場合
    event = "床屋"
    child_action = "バリカンの音を聞いてパニックになる"
    parent_action = "事前に「次はバリカンを使うよ」と予告し、イヤーマフやノイズキャンセリングイヤホンの使用を提案する"
    evaluation = "appropriate"
    
    print(f"\nイベント: {event}")
    print(f"子どもの行動: {child_action}")
    print(f"保護者の対応: {parent_action}")
    print(f"評価: {evaluation}")
    print("\n--- 簡易フィードバック（ロジカルドクター）---")
    
    feedback = ai_service.generate_parent_action_feedback(
        event=event,
        child_action=child_action,
        parent_action=parent_action,
        evaluation=evaluation,
        ai_mode="🩺 ロジカルドクター",
        detail_level="brief"
    )
    
    print(feedback)
    print("\n" + "=" * 80)


def test_detailed_feedback():
    """詳細フィードバックのテスト"""
    print("\n" + "=" * 80)
    print("詳細フィードバックのテスト")
    print("=" * 80)
    
    ai_service = AIService()
    
    # テストケース：床屋で椅子の上でじっと座っていられない場合
    event = "床屋"
    child_action = "椅子の上でじっと座っていられず、動き回ろうとする"
    parent_action = "「あと5分でおしまいだよ」とタイマーを見せて終わりを明確にし、「じっと座っていられたら好きなシールをあげるね」とご褒美を提示する"
    evaluation = "appropriate"
    
    print(f"\nイベント: {event}")
    print(f"子どもの行動: {child_action}")
    print(f"保護者の対応: {parent_action}")
    print(f"評価: {evaluation}")
    print("\n--- 詳細フィードバック（ロジカルドクター）---")
    
    # ストリーミング表示
    for chunk in ai_service.generate_parent_action_feedback_stream(
        event=event,
        child_action=child_action,
        parent_action=parent_action,
        evaluation=evaluation,
        ai_mode="🩺 ロジカルドクター",
        detail_level="detailed"
    ):
        print(chunk, end="", flush=True)
    
    print("\n\n" + "=" * 80)


def test_inappropriate_action():
    """不適切な対応のフィードバックテスト"""
    print("\n" + "=" * 80)
    print("不適切な対応のフィードバックテスト")
    print("=" * 80)
    
    ai_service = AIService()
    
    # テストケース：ドライヤーの音で泣き出す場合の不適切な対応
    event = "床屋"
    child_action = "ドライヤーの音で泣き出す"
    parent_action = "「少しずつ慣れていこうね」とドライヤーを続けてもらう"
    evaluation = "inappropriate"
    
    print(f"\nイベント: {event}")
    print(f"子どもの行動: {child_action}")
    print(f"保護者の対応: {parent_action}")
    print(f"評価: {evaluation}")
    print("\n--- 簡易フィードバック（やさしい先生）---")
    
    feedback = ai_service.generate_parent_action_feedback(
        event=event,
        child_action=child_action,
        parent_action=parent_action,
        evaluation=evaluation,
        ai_mode="🍀 やさしい先生",
        detail_level="brief"
    )
    
    print(feedback)
    print("\n" + "=" * 80)


def test_all_ai_modes():
    """全てのAI人格モードでテスト"""
    print("\n" + "=" * 80)
    print("全AI人格モードでのテスト")
    print("=" * 80)
    
    ai_service = AIService()
    
    event = "床屋"
    child_action = "鏡越しに自分を見るのを嫌がり、顔をそらす"
    parent_action = "「鏡を見なくても大丈夫だよ」と伝え、好きなおもちゃやタブレットを持たせて視線を別の場所に向けさせる"
    evaluation = "appropriate"
    
    ai_modes = ["🩺 ロジカルドクター", "🍀 やさしい先生", "🌞 応援コーチ"]
    
    for ai_mode in ai_modes:
        print(f"\n--- {ai_mode} ---")
        feedback = ai_service.generate_parent_action_feedback(
            event=event,
            child_action=child_action,
            parent_action=parent_action,
            evaluation=evaluation,
            ai_mode=ai_mode,
            detail_level="brief"
        )
        print(feedback)
    
    print("\n" + "=" * 80)


def main():
    """メイン関数"""
    print("\n🔧 保護者向けガイド AIフィードバック機能テスト\n")
    
    # API キーのチェック
    if not Settings.OPENAI_API_KEY:
        print("❌ エラー: OPENAI_API_KEY が設定されていません")
        print("環境変数またはsettings.pyで設定してください")
        return
    
    print(f"✅ OpenAI API Key: {Settings.OPENAI_API_KEY[:10]}...")
    print(f"✅ Model: {Settings.OPENAI_MODEL}\n")
    
    try:
        # 各種テストを実行
        test_brief_feedback()
        test_detailed_feedback()
        test_inappropriate_action()
        test_all_ai_modes()
        
        print("\n✅ 全てのテストが完了しました！\n")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

