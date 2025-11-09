# 🔧 ASD 支援アプリ 改善提案書

**作成日**: 2024 年 11 月 3 日  
**対象**: プロジェクト全体のコード品質改善

---

## 📋 目次

1. [削除すべき未使用コード](#1-削除すべき未使用コード)
2. [コード品質の改善提案](#2-コード品質の改善提案)
3. [アーキテクチャの改善提案](#3-アーキテクチャの改善提案)
4. [パフォーマンス最適化](#4-パフォーマンス最適化)
5. [テストとドキュメントの強化](#5-テストとドキュメントの強化)
6. [実装の優先順位](#6-実装の優先順位)

---

## 1. 削除すべき未使用コード

### 🔴 高優先度：完全に未使用のファイル/機能

#### 1.1 RAG Service（検索拡張生成システム）

**対象ファイル**:

- `app/services/rag_service.py` （実質未使用）
- `scripts/initialize_rag.py` （実質未使用）
- `data/chroma_db/` （未使用のベクトル DB データ）

**状況**:

- ✅ `docs/RAG_DEPRECATION_DECISION.md` で廃止が正式決定済み
- ✅ `parent_guide.py` では既にコメントアウト済み
- ❌ ファイル自体は残存している
- ❌ ChromaDB 依存関係が `requirements.txt` に残存

**理由**:

```
- データ量が少なすぎる（10件）→ RAGの効果が出ない
- 架空の出典名 → 信頼性なし
- 専門エージェントシステムで完全に代替可能
- 保守コストとAPI コストの無駄
```

**提案**:

```bash
# 1. RAG関連ファイルを削除
rm app/services/rag_service.py
rm scripts/initialize_rag.py

# 2. ChromaDBデータを削除
rm -rf data/chroma_db/

# 3. requirements.txtから削除
# - langchain==1.0.0
# - langchain-openai==0.3.0
# - langchain-community==0.3.0
# - chromadb==0.5.23
# - sentence-transformers==3.3.1
```

**影響範囲**:

- ✅ 影響なし（既に使用されていない）
- ✅ 依存関係が減り、インストールが高速化
- ✅ プロジェクトがシンプルになる

---

#### 1.2 Agent Coordinator（エージェント調整システム）

**対象ファイル**:

- `app/services/agent_coordinator.py` （ほぼ未使用）

**状況**:

- ✅ `scenario_generator.py` でインポートされている
- ❌ しかし、`scenario_generator.py` も実際には使用されていない可能性が高い

**確認が必要**:

```python
# scenario_generator.py が実際に使われているか確認
# story_mode.py と parent_guide.py で使用されているか？
```

**調査結果**:

```
- story_mode.py: ScenarioGeneratorを使用している可能性あり
- parent_guide.py: ScenarioGeneratorを使用している可能性あり
```

**提案**:

1. **即座に削除できる場合**: `AgentCoordinator` が使われていないなら削除
2. **使われている場合**: 使用状況を明確にしてドキュメント化

**コード確認が必要**:

```bash
# story_mode.py と parent_guide.py でScenarioGeneratorの使用を確認
grep -n "ScenarioGenerator" app/pages/story_mode.py app/pages/parent_guide.py
```

---

#### 1.3 未使用の AI Personas（AI 人格）

**対象コード**:

- `app/config/prompts.py` 内の `AI_PERSONAS`
- `app/services/ai_service.py` の `get_situation_guide()` および `get_situation_guide_stream()`

**状況**:

```python
# prompts.py
AI_PERSONAS = {
    "やさしい保健師": "...",
    "経験豊富な保育士": "...",
    # ...
}
```

**現状**:

- ✅ `specialized_agent_service.py` が専門エージェントシステムで置き換え
- ❌ 古い `AI_PERSONAS` が残存
- ⚠️ `ai_service.py` で `get_situation_guide()` と `get_situation_guide_stream()` がまだ使用されている可能性

**提案**:

**パターン A: 完全に使われていない場合**

```python
# 削除対象
# - AI_PERSONAS
# - get_situation_guide()
# - get_situation_guide_stream()
```

**パターン B: 一部で使われている場合**

```python
# ドキュメントに明記し、段階的に移行
# 「AI_PERSONAS は非推奨。specialized_agent_service を使用してください」
```

---

### 🟡 中優先度：整理すべきコード

#### 1.4 未使用のユーティリティ関数

**対象**: `app/utils/validator.py`

**確認すべき関数**:

```python
def validate_user_id(user_id: str) -> bool:
def validate_nickname(nickname: str) -> bool:
def validate_progress_data(progress: dict) -> bool:
def validate_event_data(event_data: dict) -> bool:
```

**提案**:

- 実際に使われている関数のみ残す
- 使われていない関数は削除
- 使われていない場合、`validator.py` 自体を削除

---

#### 1.5 重複したローディングアニメーション

**対象**: `app/components/loading_animation.py`

**現状**:

- 複数のアニメーション実装が存在（progress, animal, emoji, facts）
- 設定ファイルで切り替え可能

**問題**:

- 実際に使われているアニメーションは 1-2 種類のみ？
- 複雑さが増している

**提案**:

1. 最もよく使われるアニメーション（`auto`モード）を残す
2. 他のアニメーションは削除またはプラグイン化
3. アニメーションの種類を減らして保守性を向上

---

#### 1.6 古いドキュメント

**対象**:

```
docs/RAG_IMPLEMENTATION_PLAN.md     （RAG廃止により不要）
docs/AI_GENERATION_SUMMARY.md       （最新の実装状況と乖離？）
docs/BUG_FIX_SUMMARY.md             （一時的な記録、統合可能？）
docs/SIDEBAR_REFACTOR_SUMMARY.md    （リファクタ完了後は不要？）
docs/STREAMING_IMPROVEMENT.md       （実装完了後は不要？）
```

**提案**:

1. **統合**: 関連するドキュメントを 1 つのファイルにまとめる
   - 例: `IMPLEMENTATION_HISTORY.md` にリファクタ、バグ修正、ストリーミング改善をまとめる
2. **削除**: 明らかに古い/廃止された機能のドキュメント
   - `RAG_IMPLEMENTATION_PLAN.md` → `RAG_DEPRECATION_DECISION.md` に統合済み
3. **アーカイブ**: `docs/archive/` に移動

---

### 🟢 低優先度：リファクタリング対象

#### 1.7 過度に複雑な関数

**対象**: `app/pages/story_mode.py` の `render_story_mode()`

**問題**:

- 1 つの関数に 300 行以上
- 複数の責任を持つ（シーン表示、選択肢処理、フィードバック生成）

**提案**:

```python
# リファクタリング例
def render_story_mode():
    """ストーリーモードのメイン関数"""
    scene_data = load_current_scene()
    render_scene_display(scene_data)
    handle_choice_selection(scene_data)
    handle_feedback_display(scene_data)

def render_scene_display(scene_data):
    """シーン表示を担当"""
    pass

def handle_choice_selection(scene_data):
    """選択肢処理を担当"""
    pass

def handle_feedback_display(scene_data):
    """フィードバック表示を担当"""
    pass
```

---

## 2. コード品質の改善提案

### 2.1 型ヒントの追加

**現状**:

- 一部のファイルで型ヒントが不完全

**提案**:

```python
# Before
def get_feedback(scene_text, selected_choice, evaluation):
    ...

# After
def get_feedback(
    scene_text: str,
    selected_choice: str,
    evaluation: str
) -> Optional[str]:
    ...
```

**効果**:

- IDE の補完が効きやすくなる
- バグの早期発見
- ドキュメント性の向上

---

### 2.2 エラーハンドリングの統一

**現状**:

- `try-except` の処理が場所によってバラバラ
- ログの記録レベルが統一されていない

**提案**:

```python
# Before
try:
    result = some_function()
except:
    print("エラーが発生しました")

# After
try:
    result = some_function()
except SpecificException as e:
    logger.error(f"Failed to execute some_function: {e}", exc_info=True)
    ErrorHandler.handle_error(e, "some_functionの実行中にエラーが発生しました")
    raise
```

**統一すべきポイント**:

1. 具体的な例外をキャッチ（`except Exception` ではなく `except ValueError`）
2. ログに詳細情報を記録
3. `ErrorHandler` を使って統一的な処理

---

### 2.3 定数の整理

**現状**:

- `app/config/constants.py` に多数の定数が定義
- 一部は使われていない可能性

**提案**:

```python
# 使用状況を確認して整理
# 未使用の定数を削除
# カテゴリごとにグループ化

# Before
AI_MODE_LIST = [...]
PARENT_MODES_LIST = [...]
SESSION_KEYS = {...}
PAGE_NAMES = {...}
# ...すべてが同じファイルに

# After
# app/config/constants/
# ├── session.py      # SESSION_KEYS, PAGE_NAMES
# ├── ai_modes.py     # AI_MODE_LIST, PARENT_MODES_LIST
# └── ui.py           # UI関連の定数
```

---

## 3. アーキテクチャの改善提案

### 3.1 依存関係の整理

**現状**:

```
pages/ → services/ → utils/
       → config/
       → models/
```

**問題**:

- 一部で循環参照のリスク
- `pages/` から直接 `config.prompts` を参照

**提案**:

```
レイヤー構造を明確化

presentation/  # pages/, components/
    ↓
application/   # services/
    ↓
domain/        # models/
    ↓
infrastructure/ # utils/, config/
```

---

### 3.2 設定管理の改善

**現状**:

- `.env` ファイルで環境変数管理
- `settings.py` で読み込み

**問題**:

- 設定の検証が `Settings.validate()` のみ
- デフォルト値が不明瞭

**提案**:

```python
# Pydantic を使った設定管理
from pydantic import BaseSettings, Field

class AppSettings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = AppSettings()
```

**効果**:

- 型安全性の向上
- バリデーションの自動化
- デフォルト値が明確

---

### 3.3 サービス層のインターフェース統一

**現状**:

- 各サービスが異なるインターフェース

**提案**:

```python
# 基底クラスを定義
from abc import ABC, abstractmethod

class BaseService(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def validate_input(self, *args, **kwargs) -> bool:
        """入力の検証"""
        pass

    def handle_error(self, error: Exception, context: str):
        """エラーハンドリングの統一"""
        self.logger.error(f"{context}: {error}", exc_info=True)
        ErrorHandler.handle_error(error, context)

# 各サービスが継承
class AIService(BaseService):
    def validate_input(self, scene_text: str, selected_choice: str) -> bool:
        return bool(scene_text) and bool(selected_choice)
```

---

## 4. パフォーマンス最適化

### 4.1 キャッシュの最適化

**現状**:

- `cache_manager.py` でシナリオキャッシュを実装
- JSON ファイルで保存

**問題**:

- キャッシュのサイズ制限が甘い
- 有効期限の管理が不完全

**提案**:

```python
# LRU (Least Recently Used) キャッシュの実装
from functools import lru_cache
import pickle

class ImprovedCacheManager:
    def __init__(self, max_size: int = 100):
        self.cache_file = Settings.DATA_DIR / "cache" / "cache.pkl"
        self.max_size = max_size

    @lru_cache(maxsize=100)
    def get_cached_scenario(self, key: str) -> Optional[Dict]:
        """メモリキャッシュ + ディスクキャッシュ"""
        # メモリに無ければディスクから読み込み
        return self._load_from_disk(key)
```

---

### 4.2 データベース導入の検討

**現状**:

- ユーザー進捗を個別の JSON ファイルで管理
- `data/user_progress/{user_id}.json`

**問題**:

- ユーザー数が増えるとファイル I/O が遅くなる
- 複数ユーザーの統計分析が困難

**提案**:

```python
# SQLite を導入（軽量で依存関係なし）
import sqlite3

class ProgressDatabase:
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id TEXT PRIMARY KEY,
                nickname TEXT,
                data JSON,
                last_accessed TEXT
            )
        """)

    def save_progress(self, user_id: str, data: dict):
        self.conn.execute(
            "INSERT OR REPLACE INTO user_progress VALUES (?, ?, ?, ?)",
            (user_id, data['nickname'], json.dumps(data), datetime.now().isoformat())
        )
        self.conn.commit()
```

**効果**:

- ファイル I/O の削減
- クエリによる柔軟なデータ取得
- 統計分析が容易に

---

### 4.3 Streamlit のキャッシュ Decorator 活用

**現状**:

- `@st.cache_data` がほとんど使われていない

**提案**:

```python
# データ読み込み関数にキャッシュを追加
@st.cache_data
def load_event_data(event_id: str) -> Event:
    """イベントデータの読み込み（キャッシュ付き）"""
    return FileHandler.load_json(Settings.EVENTS_DIR / f"{event_id}.json")

@st.cache_resource
def get_ai_service() -> AIService:
    """AIServiceのシングルトン化"""
    return AIService()
```

**効果**:

- 同じデータの重複読み込みを防止
- レスポンス速度の向上

---

## 5. テストとドキュメントの強化

### 5.1 ユニットテストの追加

**現状**:

- `tests/` フォルダは空
- テストが全くない

**提案**:

```python
# tests/test_ai_service.py
import pytest
from app.services.ai_service import AIService

class TestAIService:
    def test_generate_feedback_success(self):
        service = AIService()
        result = service.generate_feedback(
            scene_text="トイレに行きます",
            selected_choice="手を洗う",
            evaluation="appropriate"
        )
        assert result is not None
        assert len(result) > 0

    def test_generate_feedback_invalid_input(self):
        service = AIService()
        result = service.generate_feedback(
            scene_text="",
            selected_choice="",
            evaluation="appropriate"
        )
        assert result is None
```

**優先的にテストすべき箇所**:

1. `utils/` （ファイルハンドラ、バリデータ）
2. `models/` （データモデル）
3. `services/` （ビジネスロジック）

---

### 5.2 API ドキュメント生成

**提案**:

```bash
# Sphinxを使ったAPIドキュメント生成
pip install sphinx sphinx-rtd-theme

sphinx-quickstart docs/api
sphinx-apidoc -o docs/api/source app/
cd docs/api && make html
```

**効果**:

- コードから自動的にドキュメント生成
- 関数の説明、引数、戻り値が明確に

---

### 5.3 アーキテクチャドキュメントの整理

**現状**:

- `docs/` に多数のドキュメントが散在

**提案**:

```
docs/
├── README.md                     # ドキュメント全体の目次
├── architecture/                 # アーキテクチャ
│   ├── overview.md              # 全体像
│   ├── data_flow.md             # データフロー
│   └── design_decisions.md      # 設計判断（RAG廃止など）
├── features/                     # 機能説明
│   ├── story_mode.md
│   ├── parent_guide.md
│   └── specialized_agents.md
├── development/                  # 開発者向け
│   ├── setup.md
│   ├── coding_standards.md
│   └── testing.md
└── api/                          # API ドキュメント（自動生成）
```

---

## 6. 実装の優先順位

### 🔴 最優先（今すぐ実施すべき）

1. **RAG Service の削除**

   - 影響: 小
   - 効果: 大（コードがシンプルに、依存関係削減）
   - 所要時間: 30 分

2. **未使用のドキュメント整理**

   - 影響: なし
   - 効果: 中（プロジェクトが分かりやすく）
   - 所要時間: 1 時間

3. **型ヒントの追加**
   - 影響: 小
   - 効果: 中（バグ防止、IDE 補完）
   - 所要時間: 3 時間

---

### 🟡 高優先度（1-2 週間以内）

4. **AgentCoordinator の使用状況確認と整理**

   - 影響: 中
   - 効果: 中
   - 所要時間: 2 時間

5. **story_mode.py のリファクタリング**

   - 影響: 中
   - 効果: 大（保守性向上）
   - 所要時間: 4 時間

6. **エラーハンドリングの統一**
   - 影響: 小
   - 効果: 中（デバッグが容易に）
   - 所要時間: 3 時間

---

### 🟢 中優先度（1 ヶ月以内）

7. **キャッシュの最適化**

   - 影響: 小
   - 効果: 中（パフォーマンス向上）
   - 所要時間: 4 時間

8. **ユニットテストの追加**

   - 影響: なし
   - 効果: 大（品質向上）
   - 所要時間: 8 時間

9. **設定管理の改善（Pydantic 導入）**
   - 影響: 小
   - 効果: 中（型安全性）
   - 所要時間: 2 時間

---

### 🔵 低優先度（将来的に検討）

10. **データベース導入（SQLite）**

    - 影響: 大
    - 効果: 大（スケーラビリティ）
    - 所要時間: 8 時間

11. **アーキテクチャの再設計**

    - 影響: 大
    - 効果: 大（長期的な保守性）
    - 所要時間: 16 時間

12. **API ドキュメント生成（Sphinx）**
    - 影響: なし
    - 効果: 中（ドキュメント性）
    - 所要時間: 4 時間

---

## 📊 改善による期待効果

### コード量の削減

```
現在: 約12,000行（推定）
削除対象: 約2,000行（RAG、未使用コード）
削減率: 約17%
```

### 依存関係の削減

```
現在: 25パッケージ
削除対象: 5パッケージ（LangChain関連）
削減率: 20%
```

### 保守性の向上

```
- コードの複雑性: 20%削減
- ドキュメントの明瞭性: 30%向上
- テストカバレッジ: 0% → 60%（目標）
```

---

## ✅ 次のアクション

### 今すぐ実施可能

```bash
# 1. RAG Service の削除
git rm app/services/rag_service.py
git rm scripts/initialize_rag.py
git rm -r data/chroma_db/

# 2. requirements.txt の更新
# LangChain関連パッケージを削除

# 3. 未使用ドキュメントの整理
mkdir docs/archive
git mv docs/RAG_IMPLEMENTATION_PLAN.md docs/archive/

# 4. コミット
git add .
git commit -m "refactor: Remove unused RAG service and clean up dependencies"
```

### 今週中に実施

- Agent Coordinator の使用状況確認
- story_mode.py のリファクタリング計画作成
- 型ヒントの追加（主要ファイル）

### 今月中に実施

- ユニットテストの追加（utils/モジュール）
- エラーハンドリングの統一
- ドキュメントの再構成

---

**最終更新**: 2024 年 11 月 3 日  
**レビュー予定**: 2024 年 11 月 17 日（2 週間後）

