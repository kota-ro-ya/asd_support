# ファイル構成と役割概要

本ドキュメントでは、ASD 支援アプリの各ファイルがどのような役割を担っているかを説明します。

## 📁 プロジェクト構造

```
ASD_support_practice/
├── app/                    # アプリケーション本体
│   ├── main.py            # エントリーポイント
│   ├── config/            # 設定・プロンプト・定数
│   ├── models/            # データモデル
│   ├── services/          # ビジネスロジック
│   ├── utils/             # ユーティリティ
│   ├── components/        # UIコンポーネント
│   └── pages/             # ページモジュール
├── data/                  # データファイル
│   ├── events/            # イベント定義（JSON）
│   ├── user_progress/     # ユーザー進捗（自動生成）
│   ├── chroma_db/         # RAGベクトルデータベース
│   └── parent_guide_data.json  # 保護者ガイドデータ
├── assets/                # アセット（画像・音声）
│   ├── images/            # 画像ファイル
│   └── sounds/            # 音声ファイル
├── docs/                  # ドキュメント
├── scripts/               # 初期化・テストスクリプト
├── tests/                 # テストコード
└── env_a/                 # Python仮想環境
```

---

## 🎯 主要ファイルの役割

### 🔧 エントリーポイント

#### `app/main.py`

**役割**: アプリケーションのメインエントリーポイント

- Streamlit アプリケーションの起動と初期化
- ページ設定（タイトル、アイコン、レイアウト）
- カスタム CSS の適用
- 環境変数と設定の検証
- セッション状態の初期化
- ページルーティング（モード選択、イベント選択、ストーリーモード、ふりかえり、保護者ガイド）
- エラーハンドリングとアプリケーションのリセット機能

**主な処理**:

```python
# ページごとの描画を制御
if current_page == "mode_selection":
    render_mode_selection()
elif current_page == "event_selection":
    render_event_selection()
# ...
```

---

## ⚙️ 設定・定数・プロンプト（`app/config/`）

### `app/config/settings.py`

**役割**: アプリケーション全体の設定管理

- 環境変数の読み込み（`.env`ファイルから）
- ディレクトリパスの管理（データ、進捗、イベント、アセット）
- OpenAI API 設定（API キー、モデル名）
- アプリケーション設定（タイトル、バージョン、デバッグモード）
- AI 応答設定（最大トークン数、温度、ストリーミング）
- 設定の検証とディレクトリの自動作成

**重要な設定**:

- `OPENAI_API_KEY`: OpenAI API キー
- `OPENAI_MODEL`: 使用する AI モデル（デフォルト: gpt-4o-mini）
- `DATA_DIR`: データファイルの保存先
- `USER_PROGRESS_DIR`: ユーザー進捗の保存先

### `app/config/constants.py`

**役割**: アプリケーション全体で使用する定数の定義

- イベント名リストとファイルマッピング
- 評価タイプ（適切、許容、不適切）
- スタンプ獲得条件と画像マッピング
- AI 人格モードリスト
- セッション状態キー
- ページ名定義
- UI 設定（選択肢表示数、フィードバック遅延など）
- 保護者の行動オプションと AI ヒント

**主要な定数**:

```python
EVENT_NAMES = ["トイレ", "床屋", "病院", "公園", "身支度"]
AI_MODE_LIST = ["🩺 ロジカルドクター", "🍀 やさしい先生", "🌞 応援コーチ"]
```

### `app/config/prompts.py`

**役割**: AI プロンプトテンプレートとペルソナ定義

- AI 人格モードごとのペルソナ定義（ロジカルドクター、やさしい先生、応援コーチ）
- 子ども向けフィードバック生成用プロンプト
- 保護者向けシチュエーション別ガイド用プロンプト
- 保護者の対応選択に対するフィードバック用プロンプト（簡易版・詳細版）
- RAG コンテキスト対応準備済み

**プロンプト関数**:

- `get_feedback_system_prompt()`: 子どもの行動選択へのフィードバック
- `get_situation_guide_system_prompt()`: 保護者向けガイド
- `get_parent_action_feedback_prompt()`: 保護者の対応評価

---

## 📊 データモデル（`app/models/`）

### `app/models/user.py`

**役割**: ユーザー関連データモデル

- **`User`**: ユーザー情報（ID、ニックネーム、作成日時、最終アクセス）
- **`EventProgress`**: イベントごとの進捗情報
  - 現在のシーン番号
  - 行動カウント（適切、許容、不適切）
  - 獲得スタンプ数
  - 完了状態
  - プレイ履歴
- **`DailyActivity`**: 日次活動記録（日付、プレイしたイベント、完了シーン数、スタンプ数）

**データ永続化**:

- `to_dict()`: オブジェクトを辞書形式に変換（JSON 保存用）
- `from_dict()`: 辞書からオブジェクトを生成（JSON 読み込み用）

### `app/models/event.py`

**役割**: イベント、シーン、選択肢のデータモデル

- **`Event`**: イベント情報（イベント名、説明、サムネイル、シーンリスト）
- **`Scene`**: シーン情報（シーン番号、テキスト、選択肢、画像、音声）
- **`Choice`**: 選択肢情報（テキスト、評価、AI フィードバックヒント）

**主要メソッド**:

- `get_scene()`: 特定のシーン番号のシーンを取得
- `total_scenes()`: イベントの総シーン数を取得

### `app/models/conversation.py`

**役割**: AI 会話履歴のデータモデル

- **`Conversation`**: AI 会話記録（タイムスタンプ、AI 人格モード、質問、回答、トピックタグ）
- `create_new()`: 新しい会話レコードを作成

---

## 🔧 サービス層（`app/services/`）

### `app/services/ai_service.py`

**役割**: OpenAI API とのやり取りを管理

- **子ども向け機能**:

  - `generate_feedback()`: 行動選択へのフィードバック生成
  - `generate_feedback_stream()`: ストリーミング形式でフィードバック生成

- **保護者向け機能**:
  - `answer_parent_question()`: 保護者からの質問への回答
  - `answer_parent_question_stream()`: ストリーミング形式で回答生成
  - `get_situation_guide()`: シチュエーション別ガイド生成
  - `get_situation_guide_stream()`: ストリーミング形式でガイド生成
  - `generate_parent_action_feedback()`: 保護者の対応評価（簡易版・詳細版）
  - `generate_parent_action_feedback_stream()`: ストリーミング形式で評価生成

**特徴**:

- プロンプト管理を`prompts.py`に委譲
- エラーハンドリングとログ記録
- ストリーミング対応でリアルタイム表示が可能

### `app/services/session_service.py`

**役割**: Streamlit のセッション状態を管理

- セッション状態の初期化と管理
- ユーザー情報の保存・取得
- ページ遷移の管理
- イベント・シーン情報の管理
- AI 人格モードの管理
- セッションのクリア

**主要メソッド**:

- `initialize_session()`: セッション初期化
- `set_user()` / `get_user()`: ユーザー情報の管理
- `set_page()` / `get_page()`: ページ遷移の管理
- `set_event()` / `get_event()`: イベント情報の管理
- `set_scene()` / `get_scene()`: シーン番号の管理
- `next_scene()`: 次のシーンに進む

### `app/services/progress_service.py`

**役割**: ユーザー進捗データの管理

- ユーザー進捗データの読み込み・保存
- 新しいユーザーの作成
- シーン進捗の更新
- イベント完了の記録
- AI 会話履歴の追加
- 日次活動の記録と更新
- イベント進捗のリセット

**データ管理**:

- JSON ファイルとしてユーザーごとに保存（`data/user_progress/{user_id}.json`）
- 自動的に最終アクセス時刻を更新
- 日次活動を自動集計

### `app/services/rag_service.py`

**役割**: RAG（Retrieval-Augmented Generation）による知識ベース検索

- LangChain 0.3.x + ChromaDB を使用
- OpenAI Embeddings でベクトル化
- セマンティック検索による関連知識の取得
- 専門知識ベースの構築と管理

**主要メソッド**:

- `add_documents()`: 知識ベースに文書を追加
- `retrieve_relevant_context()`: 関連する専門知識を検索
- `search_with_score()`: スコア付きで検索
- `get_collection_count()`: 知識ベース内の文書数取得

**将来的な活用**:

- 保護者向けガイドでの専門的根拠提供
- より精度の高い AI フィードバック生成

---

## 🛠️ ユーティリティ（`app/utils/`）

### `app/utils/file_handler.py`

**役割**: ファイルの読み書き処理

- JSON ファイルの読み込み
- JSON ファイルへの書き込み
- ファイル存在確認
- ディレクトリの作成
- JSON ファイル一覧の取得

**エラーハンドリング**:

- 存在しないファイルへの対応
- JSON デコードエラーの処理
- ログ記録

### `app/utils/validator.py`

**役割**: データ検証

- ユーザー ID の検証
- ニックネームの検証
- 進捗データの検証
- イベントデータの検証

### `app/utils/date_utils.py`

**役割**: 日付・時刻処理

- 現在時刻の ISO 形式取得
- 日付文字列の生成
- タイムスタンプの整形

### `app/utils/error_handler.py`

**役割**: エラーハンドリングと表示

- 一般的なエラー処理
- API エラー処理
- 検証エラー処理
- ユーザーフレンドリーなエラーメッセージ表示
- ログ記録

---

## 🎨 UI コンポーネント（`app/components/`）

### `app/components/sidebar.py`

**役割**: サイドバーの描画（保護者向け AI 質問機能）

- AI 人格モード選択
- よくある質問の表示
- 自由質問入力
- AI 回答のストリーミング表示

### `app/components/progress_bar.py`

**役割**: 進捗バーの表示

- イベント進行状況の可視化
- 現在のシーン番号と総シーン数の表示

### `app/components/stamp_display.py`

**役割**: スタンプ表示

- 獲得スタンプの表示
- スタンプレベルの判定（ブロンズ、シルバー、ゴールド）
- ミニスタンプ表示（ストーリーモード中）

### `app/components/feedback_display.py`

**役割**: AI フィードバックの表示

- ストリーミング形式でのフィードバック表示
- アニメーション効果
- 評価タイプに応じたスタイリング

---

## 📄 ページモジュール（`app/pages/`）

### `app/pages/mode_selection.py`

**役割**: モード選択画面

- 子ども向けモードと保護者向けモードの選択
- ニックネーム入力（初回起動時）
- ユーザー作成とログイン処理

### `app/pages/event_selection.py`

**役割**: イベント選択画面（子ども向けモード）

- 利用可能なイベント一覧の表示
- イベントの説明とサムネイル
- イベントデータの読み込み
- ストーリーモードへの遷移

### `app/pages/story_mode.py`

**役割**: ストーリーモード画面（メイン学習画面）

- シーンの説明表示
- 選択肢ボタンの表示
- 行動選択の処理
- AI フィードバックのストリーミング表示
- 進捗の記録
- 次のシーンへの遷移
- イベント完了判定

**処理フロー**:

1. シーンの説明を表示
2. 選択肢をボタンで表示
3. ユーザーが選択
4. AI がフィードバックを生成（ストリーミング）
5. 進捗を保存
6. 次のシーンへ

### `app/pages/review.py`

**役割**: ふりかえり画面

- イベント完了後の結果表示
- 獲得スタンプの表示
- 行動評価の集計（適切、許容、不適切）
- イベント選択画面への戻るボタン
- 再チャレンジ機能

### `app/pages/parent_guide.py`

**役割**: 保護者向けシチュエーション別ガイド画面

- シチュエーション一覧の表示（イベント別グループ化）
- シチュエーション詳細の表示
- 子どもの行動パターンの説明
- 保護者の対応選択肢の提示
- 対応選択に対する AI 評価とフィードバック
  - 簡易フィードバック（自動表示）
  - 詳細フィードバック（ボタンで表示）
- 追加質問機能
- RAG 連携準備済み

**機能の流れ**:

1. シチュエーション選択
2. 子どもの行動を確認
3. 保護者の対応を選択
4. AI 評価とアドバイスを表示
5. さらに詳しい解説を表示（オプション）
6. 追加質問が可能

---

## 📦 データファイル（`data/`）

### `data/events/*.json`

**役割**: イベント定義ファイル

各イベント（トイレ、床屋、病院、公園、身支度）のシナリオデータ:

- イベント名と説明
- シーンごとのテキスト
- 選択肢とその評価
- AI フィードバックヒント
- 画像・音声ファイルの指定（オプション）

**ファイル例**:

- `toilet.json`: トイレのイベント
- `barber.json`: 床屋のイベント
- `hospital.json`: 病院のイベント
- `park.json`: 公園のイベント
- `morning_routine.json`: 身支度のイベント

### `data/parent_guide_data.json`

**役割**: 保護者向けガイドデータ

- シチュエーション一覧
- 各シチュエーションの詳細情報
- 子どもの行動パターン
- 保護者の対応選択肢
- 対応の評価とヒント

### `data/user_progress/{user_id}.json`

**役割**: ユーザー進捗データ（自動生成）

各ユーザーごとの進捗情報:

- ユーザー ID、ニックネーム
- イベントごとの進捗
- シーン履歴
- 獲得スタンプ
- AI 会話履歴
- 日次活動記録

### `data/chroma_db/`

**役割**: RAG 用ベクトルデータベース（ChromaDB）

- ASD 支援に関する専門知識のベクトル化データ
- セマンティック検索用インデックス

---

## 🖼️ アセット（`assets/`）

### `assets/images/`

**役割**: 画像ファイル

- `events/`: イベントごとの画像フォルダ
  - `barber/`: 床屋のシーン画像
  - `hospital/`: 病院のシーン画像
  - `morning/`: 身支度のシーン画像
  - `park/`: 公園のシーン画像
  - `toilet/`: トイレのシーン画像
- `stamps/`: スタンプ画像
  - `stamp_smile.png`: ブロンズスタンプ
  - `stamp_star.png`: シルバースタンプ
  - `stamp_heart.png`: ゴールドスタンプ
- `ui/`: UI 用画像

### `assets/sounds/`

**役割**: 音声ファイル

- イベントで使用する効果音や BGM（将来的な使用）

---

## 📜 スクリプト（`scripts/`）

### `scripts/initialize_rag.py`

**役割**: RAG システムの初期化スクリプト

- ChromaDB の初期化
- 専門知識ベースの構築
- ベクトルデータの生成

### `scripts/test_ai_feedback.py`

**役割**: AI フィードバック機能のテストスクリプト

- AI 応答の動作確認
- プロンプトのテスト

---

## 📚 ドキュメント（`docs/`）

### `docs/IMPLEMENTATION_SUMMARY.md`

**役割**: 実装概要ドキュメント

- プロジェクトの実装状況
- 完成した機能の説明
- 今後の改善点

### `docs/PACKAGE_VERSIONS.md`

**役割**: パッケージバージョン管理

- 使用している主要パッケージのバージョン情報
- 依存関係の記録

### `docs/parent_guide_ai_integration.md`

**役割**: 保護者ガイド AI 連携の設計書

- 保護者向けガイドの AI 機能の詳細
- RAG 連携の設計

### `docs/RAG_IMPLEMENTATION_PLAN.md`

**役割**: RAG 実装計画

- RAG システムの設計と実装計画
- 知識ベースの構築方針

### `docs/FILE_OVERVIEW.md`（本ファイル）

**役割**: ファイル構成と役割の概要

- プロジェクト全体のファイル構成説明
- 各ファイルの役割と責任範囲

---

## 🔄 データフロー

### 子ども向けモード（ストーリーモード）

```
1. ユーザーがニックネームを入力
   └→ ProgressService.create_new_user()
      └→ User データを生成し保存

2. イベントを選択
   └→ FileHandler.read_json() でイベントデータを読み込み
      └→ Event オブジェクトに変換
         └→ SessionService.set_event() でセッションに保存

3. シーンで選択肢を選ぶ
   └→ AIService.generate_feedback_stream() でフィードバック生成
      └→ ProgressService.update_scene_progress() で進捗を保存
         └→ SessionService.next_scene() で次のシーンへ

4. イベント完了
   └→ ProgressService.complete_event() で完了を記録
      └→ ふりかえり画面へ遷移
```

### 保護者向けモード（ガイドモード）

```
1. シチュエーションを選択
   └→ FileHandler.read_json() でガイドデータを読み込み
      └→ シチュエーション詳細を表示

2. 保護者の対応を選択
   └→ AIService.generate_parent_action_feedback_stream() で簡易評価生成
      └→ ユーザーが「詳細を見る」をクリック
         └→ AIService.generate_parent_action_feedback_stream() で詳細評価生成

3. 追加質問をする
   └→ RAGService.retrieve_relevant_context() で関連知識を検索
      └→ AIService.answer_parent_question_stream() で回答生成
         └→ ProgressService.add_conversation() で会話履歴を保存
```

---

## 🧩 主要な技術スタック

- **フレームワーク**: Streamlit（Web アプリケーション）
- **AI**: OpenAI API（GPT-4o-mini）
- **RAG**: LangChain 0.3.x + ChromaDB
- **データ形式**: JSON
- **言語**: Python 3.8+

---

## 🔐 環境変数（`.env`ファイル）

以下の環境変数が必要です:

```env
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-4o-mini
APP_TITLE=ASD支援アプリ
APP_VERSION=0.5
DEBUG_MODE=False
DATA_DIR=./data
USER_PROGRESS_DIR=./data/user_progress
```

---

## 📝 まとめ

本プロジェクトは、以下の 3 層アーキテクチャで構成されています:

1. **プレゼンテーション層**（`pages/`, `components/`）

   - ユーザーインターフェースの描画と操作

2. **ビジネスロジック層**（`services/`）

   - AI 応答生成、セッション管理、進捗管理、RAG 検索

3. **データ層**（`models/`, `utils/`, `data/`）
   - データモデル定義、ファイル操作、データ永続化

この設計により、各モジュールの責任が明確に分離され、保守性と拡張性が高いアプリケーションになっています。

---

**最終更新**: 2025 年 10 月 26 日
