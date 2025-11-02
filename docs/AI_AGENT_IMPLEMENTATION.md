# AI Agent Implementation Guide

## AI エージェント実装ガイド

### 概要

このドキュメントでは、ASD 支援アプリに実装された AI エージェントシステムについて説明します。

---

## システムアーキテクチャ

### ハイブリッドアプローチ

本実装では、**固定テンプレート** と **AI 動的生成** のハイブリッド方式を採用しています。

```
【固定要素】
├── イベントの基本構造（トイレ、床屋など）
├── 学習目標
└── 評価基準（appropriate/acceptable/inappropriate）

【AI生成要素】
├── シーンの状況説明のバリエーション
├── 選択肢の表現方法
├── フィードバックの内容
└── 保護者向けガイドのシチュエーション
```

---

## コンポーネント構成

### 1. エージェントコーディネーター (`agent_coordinator.py`)

複数の AI エージェントを管理し、各タスクに適切なエージェントを割り当てます。

#### エージェントの役割

| エージェント                 | 役割                                 | 主な機能                                 |
| ---------------------------- | ------------------------------------ | ---------------------------------------- |
| **シナリオ生成エージェント** | 子供向けシナリオのバリエーション生成 | 状況説明と選択肢を動的に生成             |
| **評価エージェント**         | 子供の選択を評価                     | 教育的に適切なフィードバックを生成       |
| **ガイド生成エージェント**   | 保護者向けガイドを生成               | 実際のシチュエーションと対応を生成       |
| **品質管理エージェント**     | コンテンツの品質をチェック           | 教育的適切性、言語、一貫性、安全性を評価 |

#### 主要メソッド

```python
# シナリオバリエーションの生成
generate_scenario_variation(event_name, scene_number, base_situation, learning_goal)

# 保護者向けシチュエーション生成
generate_parent_situation(event_name, child_behaviors)

# コンテンツ品質検証
validate_content_quality(content_type, content, criteria)
```

---

### 2. シナリオジェネレーター (`scenario_generator.py`)

シナリオの動的生成とバリエーション管理を担当します。

#### 主要機能

- **シーンバリエーション生成**: 固定テンプレートから多様なバリエーションを生成
- **保護者シチュエーション生成**: ランダムな学習シチュエーションを生成
- **キャッシュ管理**: 生成済みコンテンツを効率的に管理
- **フォールバック機構**: AI 生成失敗時に固定テンプレートを使用

#### 使用例

```python
from app.services.scenario_generator import ScenarioGenerator

generator = ScenarioGenerator()

# シーンのバリエーション取得
scene = generator.get_scene_with_variation(
    event_name="トイレ",
    scene_number=0,
    use_ai_generation=True
)

# 保護者向けシチュエーション生成
situation = generator.generate_random_parent_situation(
    event_name="床屋"
)
```

---

### 3. キャッシュマネージャー (`cache_manager.py`)

AI 生成コンテンツの永続的なキャッシュを管理します。

#### キャッシュ戦略

- **二段階キャッシュ**: メモリキャッシュ + ファイルキャッシュ
- **有効期限管理**: デフォルト 24 時間（設定可能）
- **サイズ制限**: 最大 100 エントリ（設定可能）
- **自動クリーンアップ**: 期限切れエントリの自動削除

#### 主要メソッド

```python
from app.services.cache_manager import CacheManager

cache = CacheManager()

# キャッシュの取得
cached = cache.get_cached_scenario("トイレ", 0)

# キャッシュの保存
cache.save_scenario_cache("トイレ", 0, content)

# 統計情報
stats = cache.get_cache_stats()
```

---

## 設定項目

### 環境変数（`.env`ファイル）

```bash
# AI生成機能の設定
USE_AI_GENERATION=True                  # AI生成機能の有効化
AI_GENERATION_MAX_ATTEMPTS=3            # 生成試行の最大回数
AI_QUALITY_THRESHOLD=80                 # 品質スコアの閾値（0-100）

# キャッシュ設定
ENABLE_SCENARIO_CACHE=True              # キャッシュ機能の有効化
CACHE_EXPIRY_HOURS=24                   # キャッシュの有効期限（時間）
MAX_CACHE_SIZE=100                      # 最大キャッシュエントリ数
```

---

## ユーザーインターフェース

### 子供向けモード（ストーリーモード）

#### AI バリエーション切り替え

イベント選択画面に「🤖 AI バリエーション」チェックボックスが追加されています。

- **オフ**: 固定テンプレートを使用（一貫性重視）
- **オン**: AI 生成バリエーションを使用（多様性重視）

#### 動作フロー

```
1. イベント選択
2. AIバリエーションモードの選択
3. シーン表示（AI生成 or 固定）
4. 選択肢を選ぶ
5. AIフィードバックを受け取る
```

### 保護者向けモード（保護者ガイド）

#### AI 生成シチュエーション

各イベントに「✨ 新規生成」ボタンが追加されています。

- **既存シチュエーション**: 事前定義されたシチュエーションから選択
- **新規生成**: AI が新しいシチュエーションを生成

#### 動作フロー

```
1. イベント選択
2. 「AI生成」チェックボックスをオン
3. 「新規生成」ボタンをクリック
4. AIが新しいシチュエーションを生成
5. 対応選択肢を確認
6. AIからの詳細なフィードバックを受け取る
```

---

## 品質保証

### AI コンテンツの品質基準

生成されたコンテンツは以下の基準で評価されます：

1. **教育的適切性** (25 点)

   - ASD の特性に配慮しているか
   - 学習目標が明確か
   - 発達段階に適しているか

2. **言語的適切性** (25 点)

   - 理解しやすい表現か
   - 否定的・批判的な表現がないか
   - 曖昧さがないか

3. **一貫性** (25 点)

   - 他のコンテンツとの整合性
   - 評価基準の一貫性

4. **安全性** (25 点)
   - 不適切な表現がないか
   - 誤った情報がないか

**合格基準**: 80 点以上（デフォルト）

---

## フォールバック機構

AI 生成が失敗した場合、以下の段階的なフォールバック機構が作動します：

### レベル 1: 再試行

- 最大 3 回まで生成を試行
- 品質スコアが閾値未満の場合は再生成

### レベル 2: キャッシュ利用

- 過去に生成された高品質コンテンツを使用
- 有効期限内のキャッシュを優先

### レベル 3: 固定テンプレート

- すべての試行が失敗した場合
- 元の固定テンプレートにフォールバック

---

## パフォーマンス最適化

### キャッシング戦略

1. **メモリキャッシュ**: 即座のアクセス
2. **ファイルキャッシュ**: セッション間の永続化
3. **自動クリーンアップ**: 期限切れエントリの削除

### API 呼び出しの最適化

- 高品質なコンテンツのキャッシュ再利用
- バッチ処理による効率化
- 品質チェックによる無駄な生成の回避

---

## トラブルシューティング

### よくある問題と解決方法

#### 問題 1: AI 生成が遅い

**原因**: API レスポンス時間、品質チェックの厳格さ

**解決策**:

```python
# AI_QUALITY_THRESHOLDを下げる（例: 80 → 70）
AI_QUALITY_THRESHOLD=70

# 最大試行回数を減らす
AI_GENERATION_MAX_ATTEMPTS=2
```

#### 問題 2: 同じコンテンツばかり生成される

**原因**: キャッシュの長期保持

**解決策**:

```python
# キャッシュ有効期限を短くする
CACHE_EXPIRY_HOURS=1

# または手動でキャッシュをクリア
from app.services.scenario_generator import ScenarioGenerator
generator = ScenarioGenerator()
generator.clear_cache()
```

#### 問題 3: コンテンツの品質が低い

**原因**: 品質閾値が低すぎる、プロンプトの最適化不足

**解決策**:

```python
# 品質閾値を上げる
AI_QUALITY_THRESHOLD=85

# フォールバックに頼る
USE_AI_GENERATION=False
```

---

## 今後の拡張可能性

### 推奨される改善項目

1. **RAG 統合の強化**

   - 専門知識データベースの活用
   - コンテキスト精度の向上

2. **ユーザー適応型生成**

   - 個別の学習進捗に基づいた難易度調整
   - 過去の選択パターンからの学習

3. **マルチモーダル対応**

   - 画像生成の統合
   - 音声フィードバック

4. **A/B テスト機能**
   - AI 生成 vs 固定テンプレートの効果測定
   - 最適なプロンプトの自動選択

---

## 参考情報

### 関連ファイル

- `app/services/agent_coordinator.py`: エージェント管理
- `app/services/scenario_generator.py`: シナリオ生成
- `app/services/cache_manager.py`: キャッシュ管理
- `app/pages/story_mode.py`: 子供向け UI 統合
- `app/pages/parent_guide.py`: 保護者向け UI 統合
- `app/config/settings.py`: 設定管理
- `app/config/prompts.py`: プロンプトテンプレート

### 外部ドキュメント

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 開発者向けメモ

### テスト方法

```bash
# AI生成のテスト
python -c "
from app.services.scenario_generator import ScenarioGenerator
gen = ScenarioGenerator()
result = gen.get_scene_with_variation('トイレ', 0, True, True)
print(result)
"

# キャッシュのテスト
python -c "
from app.services.cache_manager import CacheManager
cache = CacheManager()
stats = cache.get_cache_stats()
print(stats)
"
```

### デバッグモード

```bash
# デバッグログを有効化
export DEBUG_MODE=True

# アプリを起動
streamlit run app/main.py
```

---

**最終更新**: 2025 年 11 月 1 日  
**バージョン**: 1.0
