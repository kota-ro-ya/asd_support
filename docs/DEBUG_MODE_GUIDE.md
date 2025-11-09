# デバッグモード利用ガイド

## 概要

本アプリケーションには、開発・デバッグを効率化するための包括的なデバッグ情報収集・表示機能が実装されています。

## デバッグモードの設定

### 環境変数での制御

`.env`ファイルで以下の変数を設定します：

```bash
# UI上にデバッグ情報を表示 + 詳細ログを出力
DEBUG_MODE=on

# UI上には表示しない（本番環境推奨）
DEBUG_MODE=off

# ログファイルには常に記録（推奨：True）
DEBUG_LOG_ALWAYS=True
```

### 推奨設定

| 環境           | DEBUG_MODE | DEBUG_LOG_ALWAYS | 説明                                 |
| -------------- | ---------- | ---------------- | ------------------------------------ |
| **開発環境**   | `on`       | `True`           | UI 表示 + 詳細ログで開発効率を最大化 |
| **テスト環境** | `off`      | `True`           | UI 非表示、ログは記録して問題追跡    |
| **本番環境**   | `off`      | `True`           | ユーザーに影響なし、ログで監視       |

## 収集されるデバッグ情報

### 1. パフォーマンス情報

#### API 呼び出し

- **モデル名**: 使用した OpenAI モデル（例：gpt-4o-mini）
- **エージェント種別**: 専門家エージェントのタイプ
- **トークン数**: 入力・出力・合計トークン数
- **応答時間**: API 呼び出しにかかった時間（秒）
- **推定コスト**: トークン数から計算した API 使用料金（USD）
- **設定パラメータ**: temperature, max_tokens, stream 有無

**例:**

```
API Call: expert_clinical_psychologist
- 応答時間: 2.34秒
- トークン数: 1,234 tokens (入力: 456, 出力: 778)
- 推定コスト: $0.0012
- Temperature: 0.7
```

#### 処理時間

- セッション開始からの経過時間
- 個別処理の所要時間

### 2. リファレンスデータ情報

使用されたデータソースを記録：

- **データタイプ**: event, scenario, cache, rag など
- **ソース**: ファイル名やデータ ID
- **説明**: データの内容説明
- **関連性スコア**: RAG 検索時の関連度（0.0-1.0）

**例:**

```
Reference Data:
- Type: event
- Source: morning_routine.json
- Description: Scene 3 - 朝の着替え
- Relevance: 0.95
```

### 3. 評価情報（スコア）

**品質管理エージェント**による AI 回答の評価結果：

- **評価タイプ**:
  - `feedback_quality`: フィードバックの品質評価
  - `expert_quality_[エージェントID]`: 専門家回答の品質評価
  - `content_quality`: シナリオなどのコンテンツ品質評価
- **スコア**: 0-100 点満点（品質管理エージェントが採点）
- **評価基準**: 明確性、専門性、実践性、共感性など
- **詳細情報**:
  - `is_valid`: 品質基準を満たしているか
  - `issues`: 発見された問題点のリスト
  - `suggestions`: 改善提案のリスト

**例:**

```
Evaluation:
- Type: expert_quality_clinical_psychologist
- Score: 87 / 100
- Criteria: 臨床心理士の回答品質評価
- Details:
  - is_valid: true
  - issues: []
  - suggestions: ["より具体的な事例を追加すると良い"]
```

> **注**: この評価は既存の`AgentCoordinator.validate_content_quality()`メソッドを使用して、
> AI が生成した回答を別の監視エージェントが客観的に評価したものです。

### 4. キャッシュ操作

キャッシュの効率性を監視：

- **キャッシュヒット率**: 何%がキャッシュから取得できたか
- **操作履歴**: hit（成功）、miss（失敗）、write（書込）
- **キャッシュタイプ**: scenario, response など

**例:**

```
Cache Operations:
- Hit: 8回
- Miss: 2回
- ヒット率: 80.0%
```

### 5. エラー情報

発生したエラーの詳細：

- **タイムスタンプ**: エラー発生時刻
- **エラータイプ**: 例外の種類
- **メッセージ**: エラーメッセージ
- **トレースバック**: スタックトレース（詳細モード）

## UI 上での表示方法

### サイドバーでの表示

`DEBUG_MODE=on`の場合、各ページのサイドバーに「🔧 デバッグ情報」セクションが表示されます。

#### 表示内容

1. **📊 パフォーマンス概要**

   - 処理時間、API 呼び出し回数、トークン数
   - 推定コスト、キャッシュヒット率、エラー数

2. **🔌 API 呼び出し詳細**

   - 各 API 呼び出しの詳細情報
   - 時系列で表示

3. **📚 リファレンスデータ**

   - 使用されたデータソースのリスト
   - 関連性スコア付き

4. **⭐ 評価情報**

   - AI による評価結果
   - スコアの視覚化（プログレスバー）

5. **💾 キャッシュ操作**

   - キャッシュの利用状況
   - ヒット/ミス/書込の内訳

6. **⚠️ エラー情報**

   - 発生したエラーの詳細
   - トレースバック表示

7. **📥 データエクスポート**
   - JSON 形式でダウンロード可能
   - 詳細分析用

### 表示例

```
🔧 デバッグ情報

📊 パフォーマンス概要
┌─────────────────────────────┐
│ 処理時間        5.67秒      │
│ API呼び出し     4回         │
│ 総トークン数    3,456       │
│ 推定コスト      $0.0042     │
│ キャッシュヒット率 75.0%   │
│ エラー数        0           │
└─────────────────────────────┘
```

## ログファイル

### ログの保存場所

```
logs/
├── app_YYYYMMDD.log          # 通常のアプリケーションログ
├── error_YYYYMMDD.log        # エラーのみ
├── performance_YYYYMMDD.log  # パフォーマンスログ（DEBUG_MODE時）
└── debug/
    └── debug_YYYYMMDD.jsonl  # デバッグセッション詳細（JSON Lines形式）
```

### ログレベル

| レベル  | DEBUG_MODE=on | DEBUG_MODE=off |
| ------- | ------------- | -------------- |
| DEBUG   | ✅ 出力       | ❌ 非出力      |
| INFO    | ✅ 出力       | ✅ 出力        |
| WARNING | ✅ 出力       | ✅ 出力        |
| ERROR   | ✅ 出力       | ✅ 出力        |

### ログフォーマット

```
2025-11-08 14:23:45 - app.services.specialized_agent_service - INFO - [specialized_agent_service.py:284] - API Call: expert_clinical_psychologist - 1234 tokens - 2.34s
```

### デバッグセッションログ（JSON Lines）

各セッションの詳細が JSON 形式で保存されます：

```json
{
  "session_id": "parent_guide_user123",
  "start_time": "2025-11-08T14:20:00",
  "end_time": "2025-11-08T14:25:30",
  "total_duration": 330.5,
  "total_api_calls": 4,
  "total_tokens": 3456,
  "total_cost": 0.0042,
  "cache_hit_rate": 75.0,
  "api_calls": [...],
  "references": [...],
  "evaluations": [...],
  "errors": []
}
```

## 実装詳細

### アーキテクチャ

```
┌─────────────────────────────────────────┐
│          DebugInfoCollector             │
│  (シングルトン・グローバルインスタンス)    │
└─────────────────────────────────────────┘
                    ↑
                    │ 収集
                    │
┌───────────────────┴─────────────────────┐
│                                         │
│  AIService                              │
│  SpecializedAgentService                │
│  ScenarioGenerator                      │
│  その他のサービス                       │
│                                         │
└─────────────────────────────────────────┘
                    ↓
                    │ 表示
                    │
┌─────────────────────────────────────────┐
│         DebugPanel (UI Component)       │
│  - display_debug_panel()                │
│  - サイドバーまたはメインエリアに表示   │
└─────────────────────────────────────────┘
```

### 主要クラス

#### 1. `DebugInfoCollector`

```python
from app.utils.debug_info import get_debug_collector

collector = get_debug_collector()

# セッション開始
collector.start_session(session_id="...", page="...", user_id="...")

# API呼び出し記録
collector.add_api_call(
    model="gpt-4o-mini",
    agent_type="expert_clinical_psychologist",
    prompt_tokens=456,
    completion_tokens=778,
    response_time=2.34
)

# 評価記録
collector.add_evaluation(
    evaluation_type="user_choice",
    score=5.0,
    criteria="appropriate"
)

# セッション終了
collector.end_session()
```

#### 2. `display_debug_panel()`

```python
from app.components.debug_panel import display_debug_panel

# サイドバーに表示
display_debug_panel(position="sidebar")

# メインエリアに表示
display_debug_panel(position="main")
```

## 使用例

### 開発時のデバッグ

1. `.env`で`DEBUG_MODE=on`に設定
2. アプリケーションを起動
3. サイドバーにデバッグ情報が表示される
4. 問題箇所の特定：
   - 応答が遅い → API 呼び出し時間を確認
   - 回答の質が低い → 評価スコアを確認
   - エラー発生 → エラー情報とトレースバックを確認

### 本番環境での監視

1. `.env`で`DEBUG_MODE=off`, `DEBUG_LOG_ALWAYS=True`に設定
2. ユーザーには影響なし（UI 非表示）
3. ログファイルで定期的に監視：

   ```bash
   # エラーログの確認
   tail -f logs/error_YYYYMMDD.log

   # パフォーマンスの確認
   grep "API_CALL" logs/app_YYYYMMDD.log

   # デバッグセッションの分析
   cat logs/debug/debug_YYYYMMDD.jsonl | jq '.'
   ```

### ログ分析

#### 高コスト API 呼び出しの特定

```bash
cat logs/debug/debug_YYYYMMDD.jsonl | jq 'select(.total_cost > 0.01)'
```

#### 低キャッシュヒット率のセッション

```bash
cat logs/debug/debug_YYYYMMDD.jsonl | jq 'select(.cache_hit_rate < 50)'
```

#### エラー発生セッション

```bash
cat logs/debug/debug_YYYYMMDD.jsonl | jq 'select(.errors | length > 0)'
```

## トラブルシューティング

### デバッグパネルが表示されない

**確認事項:**

1. `.env`で`DEBUG_MODE=on`になっているか
2. アプリケーションを再起動したか
3. ブラウザのキャッシュをクリアしたか

### ログファイルが作成されない

**確認事項:**

1. `logs/`ディレクトリの書込権限があるか
2. `logger_config.py`の`setup_logging()`が呼ばれているか
3. `main.py`で初期化されているか

### パフォーマンスが低下する

**対策:**

1. `DEBUG_MODE=off`に設定（UI 描画のオーバーヘッドを削減）
2. ログレベルを`WARNING`以上に制限
3. デバッグセッションの自動終了を確認

## まとめ

- **開発環境**: `DEBUG_MODE=on` で UI 表示 + 詳細ログ
- **本番環境**: `DEBUG_MODE=off` でログのみ記録
- **ログファイル**: 常に記録され、問題追跡に活用
- **評価スコア**: **品質管理エージェント**が AI の回答品質を 0-100 点で自動評価
- **リファレンスデータ**: どのデータが使われたか追跡

これにより、開発効率の向上と本番環境での安定した運用の両立が可能になります。

## 品質管理エージェントについて

本システムでは、`AgentCoordinator`の`validate_content_quality()`メソッドを使用して、
AI が生成したすべての回答を別の監視エージェントが自動的に評価します。

### 評価対象

- フィードバック生成（子ども向け）
- 専門家エージェントの回答（保護者向け）
- AI 生成シナリオ
- その他の動的コンテンツ

### 評価基準

- **明確性**: 理解しやすい表現か
- **専門性**: 専門知識が反映されているか
- **実践性**: 実践可能なアドバイスか
- **共感性**: 保護者に寄り添った内容か
- **教育的価値**: 学習効果があるか

### スコアリング

- **0-59 点**: 品質基準未達（改善が必要）
- **60-79 点**: 許容範囲（軽微な修正推奨）
- **80-100 点**: 高品質（基準を満たす）

デバッグモードでは、これらの評価結果がリアルタイムで確認でき、
AI の回答品質を継続的に監視・改善することができます。
