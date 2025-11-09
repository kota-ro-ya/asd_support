# 📊 ASD 支援アプリ プロジェクト全体解析レポート

## 🎯 プロジェクト概要

### プロジェクト名

**ASD 支援アプリ（自閉スペクトラム症 学習支援アプリケーション）**

### 目的

- ASD（自閉スペクトラム症）や発達障害を持つ子どもが、日常生活の適切な行動を遊びながら学習
- 保護者が子どもへの対応方法をシチュエーション別に学習
- AI（GPT-4o-mini）を活用した個別フィードバックとガイダンス提供

### 技術スタック

- **フレームワーク**: Streamlit 1.41.1 以上
- **AI**: OpenAI GPT-4o-mini（メイン）、専門エージェントシステム
- **データベース**: ChromaDB（RAG 用ベクトル DB）
- **言語**: Python 3.8 以上
- **依存ライブラリ**:
  - LangChain 1.0.0（RAG 実装）
  - pandas, plotly（データ可視化）
  - python-dotenv（環境変数管理）

---

## 📁 フォルダ/ファイル一覧

```
プロジェクトルート/
├── app/                          # アプリケーション本体
│   ├── main.py                   # エントリーポイント
│   ├── config/                   # 設定
│   │   ├── constants.py          # 定数定義
│   │   ├── prompts.py            # AIプロンプト定義
│   │   └── settings.py           # 環境設定
│   ├── models/                   # データモデル
│   │   ├── conversation.py       # 会話履歴モデル
│   │   ├── event.py              # イベント/シーン/選択肢モデル
│   │   └── user.py               # ユーザー/進捗モデル
│   ├── services/                 # ビジネスロジック
│   │   ├── ai_service.py         # AI連携サービス
│   │   ├── agent_coordinator.py  # エージェント調整
│   │   ├── cache_manager.py      # キャッシュ管理
│   │   ├── progress_service.py   # 進捗管理
│   │   ├── rag_service.py        # RAG実装
│   │   ├── scenario_generator.py # シナリオ生成
│   │   ├── session_service.py    # セッション管理
│   │   └── specialized_agent_service.py # 専門家エージェント
│   ├── pages/                    # UIページ
│   │   ├── event_selection.py    # イベント選択
│   │   ├── mode_selection.py     # モード選択
│   │   ├── parent_guide.py       # 保護者ガイド
│   │   ├── review.py             # ふりかえり
│   │   └── story_mode.py         # ストーリーモード
│   ├── components/               # UIコンポーネント
│   │   ├── feedback_display.py   # フィードバック表示
│   │   ├── loading_animation.py  # ローディング演出
│   │   ├── progress_bar.py       # プログレスバー
│   │   ├── sidebar.py            # サイドバー
│   │   └── stamp_display.py      # スタンプ表示
│   └── utils/                    # ユーティリティ
│       ├── date_utils.py         # 日時処理
│       ├── error_handler.py      # エラー処理
│       ├── file_handler.py       # ファイル処理
│       └── validator.py          # バリデーション
├── data/                         # データファイル
│   ├── events/                   # イベント定義JSON
│   │   ├── toilet.json
│   │   ├── barber.json
│   │   ├── hospital.json
│   │   ├── park.json
│   │   └── morning_routine.json
│   ├── parent_guide_data.json    # 保護者ガイドデータ
│   ├── user_progress/            # ユーザー進捗（自動生成）
│   ├── cache/                    # AIキャッシュ
│   └── chroma_db/                # RAGベクトルDB
├── assets/                       # アセット
│   ├── images/                   # 画像
│   └── sounds/                   # 音声
├── docs/                         # ドキュメント
├── scripts/                      # スクリプト
│   ├── initialize_rag.py         # RAG初期化
│   └── test_ai_feedback.py       # AIテスト
├── tests/                        # テストコード
├── requirements.txt              # 依存パッケージ
└── README.md                     # プロジェクト説明
```

---

## 🗂️ ファイルごとの詳細解説

### **1. エントリーポイント**

#### **ファイル名**: `app/main.py`

- **役割**: アプリケーションのメインエントリーポイント
- **主な関数/クラス**:
  - `main()`: メイン処理、Streamlit ページ設定とルーティング
- **処理概要**:
  1. Streamlit ページ設定（タイトル、アイコン、レイアウト）
  2. カスタム CSS 適用（ボタンスタイル、アニメーション）
  3. 環境設定の検証（`Settings.validate()`）
  4. セッション初期化（`SessionService.initialize_session()`）
  5. サイドバー描画（保護者向け AI 質問モード）
  6. ページルーティング（現在のページに応じて適切な render 関数を呼び出し）
  7. エラーハンドリング（エラー時のリセット機能）
- **他ファイルとの関係**:
  - `services/session_service.py`: セッション管理
  - `pages/*.py`: 各ページモジュール
  - `config/settings.py`: 設定管理
  - `components/sidebar.py`: サイドバー UI

---

### **2. 設定ファイル**

#### **ファイル名**: `app/config/settings.py`

- **役割**: 環境変数と設定の一元管理
- **主な関数/クラス**:
  - `Settings`: 静的設定クラス
- **処理概要**:
  - 環境変数読み込み（`.env`ファイル）
  - パス設定（ベースディレクトリ、データディレクトリ、アセット）
  - OpenAI 設定（API キー、モデル名）
  - AI 生成設定（バリエーション有効化、品質閾値）
  - キャッシュ設定（有効期限、最大サイズ）
  - ローディングアニメーション設定
  - `validate()`: 設定検証とディレクトリ自動作成
- **他ファイルとの関係**: 全ファイルから参照される中心的な設定

#### **ファイル名**: `app/config/constants.py`

- **役割**: アプリケーション全体で使用する定数定義
- **主な定数**:
  - `EVENT_NAMES`: イベント名リスト（トイレ、床屋、病院、公園、身支度）
  - `EVENT_FILE_MAPPING`: イベント名 → ファイル名マッピング
  - `EVALUATION_TYPES`: 評価タイプ（適切/許容/不適切）
  - `STAMP_THRESHOLDS`: スタンプ獲得条件（ブロンズ/シルバー/ゴールド）
  - `AI_MODE_LIST`: AI 人格モードリスト
  - `SESSION_KEYS`: セッション状態キー
  - `PAGE_NAMES`: ページ名定数
  - `PARENT_ACTION_OPTIONS`: 保護者の行動選択肢（評価とヒント付き）
- **他ファイルとの関係**: 全体で使用される定数の単一の真実の源

#### **ファイル名**: `app/config/prompts.py`

- **役割**: AI プロンプトテンプレートと人格定義
- **主な関数/クラス**:
  - `AI_PERSONAS`: AI 人格モード定義（ロジカルドクター、やさしい先生、応援コーチ）
  - `get_feedback_system_prompt()`: 子ども向けフィードバックプロンプト生成
  - `get_situation_guide_system_prompt()`: 保護者向けガイドプロンプト生成
  - `get_parent_action_feedback_prompt()`: 保護者対応フィードバックプロンプト生成（簡易版・詳細版）
- **処理概要**:
  - 子どもの選択に対する評価別のフィードバックプロンプト生成
  - 保護者の対応に対する詳細なガイダンスプロンプト生成
  - RAG コンテキストの統合準備（将来的に専門知識を組み込む）
- **他ファイルとの関係**:
  - `services/ai_service.py`: AI サービスから呼び出される
  - `services/specialized_agent_service.py`: 専門家エージェントシステムで使用

---

### **3. データモデル**

#### **ファイル名**: `app/models/user.py`

- **役割**: ユーザー情報と進捗データのモデル定義
- **主なクラス**:
  - `EventProgress`: イベントごとの進捗（現在シーン、行動カウント、スタンプ、履歴）
  - `DailyActivity`: 日次活動記録（日付、プレイイベント、完了シーン数、スタンプ）
  - `User`: ユーザー情報（ID、ニックネーム、イベント進捗、会話履歴、日次活動）
- **処理概要**:
  - データクラス（`@dataclass`）で構造化
  - `to_dict()` / `from_dict()`: JSON 変換メソッド
  - `get_event_progress()`: 特定イベントの進捗取得
  - `update_last_access()`: 最終アクセス時刻更新
- **他ファイルとの関係**:
  - `services/progress_service.py`: 進捗管理で使用
  - `services/session_service.py`: セッション状態で保持

#### **ファイル名**: `app/models/event.py`

- **役割**: イベント、シーン、選択肢のデータモデル
- **主なクラス**:
  - `Choice`: 選択肢（テキスト、評価、AI ヒント）
  - `Scene`: シーン情報（番号、テキスト、選択肢リスト、画像、音声）
  - `Event`: イベント情報（名前、説明、シーンリスト、サムネイル）
- **処理概要**:
  - JSON 形式のイベントデータを構造化
  - `get_scene()`: シーン番号からシーン取得
  - `total_scenes()`: シーン総数取得
- **他ファイルとの関係**:
  - `pages/story_mode.py`: ストーリー進行で使用
  - `services/scenario_generator.py`: シナリオ生成で使用

#### **ファイル名**: `app/models/conversation.py`

- **役割**: AI 会話履歴のデータモデル
- **主なクラス**:
  - `Conversation`: 会話記録（タイムスタンプ、AI モード、質問、回答、トピックタグ）
- **処理概要**:
  - `create_new()`: 新しい会話レコード作成
  - `to_dict()` / `from_dict()`: JSON 変換
- **他ファイルとの関係**:
  - `services/progress_service.py`: 会話履歴保存
  - `models/user.py`: User の`ai_conversations`リストに格納

---

### **4. サービス層（ビジネスロジック）**

#### **ファイル名**: `app/services/session_service.py`

- **役割**: Streamlit セッション状態の管理
- **主な関数**:
  - `initialize_session()`: セッション初期化
  - `set_user()` / `get_user()`: ユーザー情報管理
  - `set_page()` / `get_page()`: ページ状態管理
  - `set_event()` / `get_event()`: イベント状態管理
  - `set_scene()` / `get_scene()` / `next_scene()`: シーン管理
  - `set_ai_mode()` / `get_ai_mode()`: AI 人格モード管理
  - `clear_session()`: セッションクリア
  - `set_value()` / `get_value()`: 汎用キー値管理
- **処理概要**:
  - Streamlit の`st.session_state`をラップし、型安全なアクセス提供
  - セッションキーの一元管理
  - ロギング機能内蔵
- **他ファイルとの関係**: 全ページとサービスから頻繁に呼び出される

#### **ファイル名**: `app/services/ai_service.py`

- **役割**: OpenAI API 連携と AI レスポンス生成
- **主な関数**:
  - `__init__()`: OpenAI クライアント初期化
  - `generate_feedback()`: 子ども向けフィードバック生成
  - `generate_feedback_stream()`: フィードバックのストリーミング生成
  - `answer_parent_question()`: 保護者からの質問回答
  - `answer_parent_question_stream()`: 質問回答のストリーミング生成
  - `generate_parent_action_feedback()`: 保護者対応フィードバック生成（簡易/詳細）
  - `generate_parent_action_feedback_stream()`: フィードバックのストリーミング生成（RAG 対応準備済み）
- **処理概要**:
  - `app/config/prompts.py`からプロンプト取得
  - OpenAI API コール（Chat Completions API 使用）
  - ストリーミングレスポンス対応（リアルタイム表示）
  - エラーハンドリング
- **他ファイルとの関係**:
  - `pages/story_mode.py`: 選択肢フィードバック生成
  - `pages/parent_guide.py`: 保護者ガイド生成
  - `components/sidebar.py`: サイドバーでの質問回答

#### **ファイル名**: `app/services/specialized_agent_service.py`

- **役割**: 専門家エージェントシステム（マルチエージェント協調）
- **主なクラス/関数**:
  - `AGENTS`: 4 人の専門家エージェント定義
    - 🧠 臨床心理士（ASD 専門、ABA/TEACCH/SST）
    - ⚕️ 小児科医（医学的見地、神経学、併存症）
    - 🏫 特別支援教育専門家（IEP、合理的配慮、UD）
    - 💙 家族支援専門家（ペアトレ、レジリエンス、きょうだい支援）
  - `generate_expert_response()`: 単一専門家の回答生成
  - `generate_comprehensive_response()`: 統合回答生成（4 人の意見統合）
  - `generate_quick_response_stream()`: 1 人の専門家による高速回答（ストリーミング）
  - `generate_sequential_expert_responses_stream()`: 4 人が順番にストリーミング表示
  - `generate_comprehensive_response_stream()`: 統合回答のストリーミング生成
- **処理概要**:
  - 各専門家に固有のシステムプロンプト（専門知識、引用すべき理論、禁止事項を明記）
  - 3 つの回答モード：
    1. **💬 1 人の専門家（早い・おすすめ）**: 3-5 秒で回答開始
    2. **👥 4 人の専門家（順番に回答）**: すぐ開始、順番に表示
    3. **🔄 統合回答（総合的）**: 15-20 秒後に統合回答
  - 口調選択機能（フレンドリー/標準）
  - ストリーミング表示で待ち時間を快適に
- **設計意図**:
  - RAG（専門知識ベース）を使わず、プロンプト設計のみで高精度な回答を実現
  - 複数の専門分野からの多角的な視点を提供
  - エビデンスベース（理論名、研究者名を明記）
- **他ファイルとの関係**:
  - `pages/parent_guide.py`: 保護者ガイドの詳細フィードバック
  - `components/sidebar.py`: サイドバーでの専門家相談

#### **ファイル名**: `app/services/progress_service.py`

- **役割**: ユーザー進捗データの永続化管理
- **主な関数**:
  - `load_user_progress()`: ユーザー進捗読み込み
  - `save_user_progress()`: ユーザー進捗保存
  - `create_new_user()`: 新規ユーザー作成
  - `update_scene_progress()`: シーン進捗更新
  - `complete_event()`: イベント完了処理
  - `add_conversation()`: AI 会話履歴追加
  - `reset_event_progress()`: イベント進捗リセット
- **処理概要**:
  - JSON ファイルベースの永続化（`data/user_progress/{user_id}.json`）
  - UUID 生成（8 桁 16 進数）
  - バリデーション（`Validator`クラス使用）
  - 最終アクセス時刻の自動更新
  - 日次活動の自動記録
- **他ファイルとの関係**:
  - `pages/event_selection.py`: ユーザー登録
  - `pages/story_mode.py`: シーン進捗更新
  - `pages/review.py`: イベント完了処理

#### **ファイル名**: `app/services/scenario_generator.py`

- **役割**: AI によるシナリオ動的生成とバリエーション管理
- **主な関数**:
  - `get_scene_with_variation()`: AI 生成または固定テンプレートのシーン取得
  - `generate_random_parent_situation()`: 保護者向けランダムシチュエーション生成
  - `_generate_with_ai()`: AI によるシーン生成
  - `_infer_learning_goal()`: 学習目標の推定
  - `_get_fallback_parent_situation()`: 既存データからランダム選択（フォールバック）
- **処理概要**:
  - キャッシュチェック（`CacheManager`使用）
  - `AgentCoordinator`を使用した AI 生成
  - 品質チェック（`validate_content_quality()`）
  - 品質閾値（デフォルト 80 点）を満たす場合のみキャッシュ
  - AI 生成失敗時は固定テンプレートにフォールバック
- **設計意図**:
  - 同じイベントでも異なる体験を提供（学習効果向上）
  - 品質管理による教育的適切性の担保
  - キャッシュによる API コスト削減
- **他ファイルとの関係**:
  - `pages/story_mode.py`: AI バリエーションモード
  - `pages/parent_guide.py`: 新規シチュエーション生成

#### **ファイル名**: `app/services/agent_coordinator.py`

- **役割**: 複数の AI エージェントの調整とタスク割り当て
- **主なクラス/関数**:
  - `AgentRole`: エージェント役割定義（Enum）
    - `SCENARIO_GENERATOR`: シナリオ生成
    - `EVALUATOR`: 評価・フィードバック
    - `GUIDE_GENERATOR`: 保護者向けガイド生成
    - `QUALITY_CHECKER`: 品質管理
  - `generate_scenario_variation()`: シナリオバリエーション生成
  - `generate_parent_situation()`: 保護者向けシチュエーション生成
  - `validate_content_quality()`: コンテンツ品質チェック
- **処理概要**:
  - 各エージェントに専用のシステムプロンプト
  - JSON 形式でのレスポンス構造化（`response_format={"type": "json_object"}`）
  - 温度パラメータの調整（創造性 vs 厳格性）
  - 品質スコア算出（0-100 点）
- **設計意図**:
  - 責務の分離（生成/評価/ガイド/品質管理）
  - 各エージェントが専門性を持つ
  - 品質管理エージェントによる二重チェック
- **他ファイルとの関係**:
  - `services/scenario_generator.py`: シナリオ生成で使用

#### **ファイル名**: `app/services/cache_manager.py`

- **役割**: AI 生成コンテンツの永続的キャッシュ管理
- **主な関数**:
  - `get_cached_scenario()`: キャッシュされたシナリオ取得
  - `save_scenario_cache()`: シナリオをキャッシュに保存
  - `get_cached_situation()`: 保護者向けシチュエーションのキャッシュ取得
  - `save_situation_cache()`: シチュエーションのキャッシュ保存
  - `clear_all_cache()`: 全キャッシュクリア
  - `clear_expired_cache()`: 期限切れキャッシュクリア
  - `get_cache_stats()`: キャッシュ統計情報取得
- **処理概要**:
  - 2 層キャッシュ（メモリ + ファイル）
  - 有効期限管理（デフォルト 24 時間）
  - 最大サイズ制限（デフォルト 100 エントリ）
  - LRU（Least Recently Used）戦略でエビクション
  - JSON ファイルベースの永続化
- **設計意図**:
  - API コスト削減
  - レスポンス速度向上
  - オフライン対応の準備
- **他ファイルとの関係**:
  - `services/scenario_generator.py`: シナリオ生成時に使用

#### **ファイル名**: `app/services/rag_service.py`

- **役割**: RAG（Retrieval-Augmented Generation）実装
- **主な関数**:
  - `__init__()`: LangChain + Chroma 初期化
  - `add_documents()`: 知識ベースに文書追加
  - `retrieve_relevant_context()`: 関連する専門知識取得
  - `search_with_score()`: スコア付き検索
  - `get_collection_count()`: 文書数取得
- **処理概要**:
  - OpenAI Embeddings（text-embedding-ada-002）
  - ChromaDB ベクトルストア
  - セマンティック検索（類似度ベース）
  - テキスト分割（RecursiveCharacterTextSplitter）
  - メタデータフィルタリング対応
- **設計意図**:
  - 専門知識ベースとの連携（将来的に実装）
  - エビデンスベースの回答生成
  - 出典明示による信頼性向上
- **現状**: 実装済みだが、専門エージェントシステム（プロンプト設計）で高精度な回答が得られるため、現在は非推奨
- **他ファイルとの関係**: 現在は直接使用されていないが、将来的な拡張に備えて実装済み

---

### **5. ページモジュール（UI）**

#### **ファイル名**: `app/pages/mode_selection.py`

- **役割**: メインモード選択画面
- **主な関数**:
  - `render_mode_selection()`: モード選択画面描画
  - `render_child_mode_card()`: 子供向けモードカード
  - `render_parent_mode_card()`: 保護者向けモードカード
- **処理概要**:
  - ユーザー未登録時は登録画面へリダイレクト
  - 2 カラムレイアウトで 2 つのモードを表示
  - グラデーション背景とアイコンで視覚的に魅力的な UI
  - ボタンクリックでページ遷移
- **他ファイルとの関係**:
  - `services/session_service.py`: ページ遷移
  - `pages/event_selection.py`: ユーザー登録

#### **ファイル名**: `app/pages/event_selection.py`

- **役割**: イベント選択画面とユーザー登録
- **主な関数**:
  - `render_event_selection()`: イベント選択画面描画
  - `render_user_registration()`: ユーザー登録画面
  - `render_event_card()`: イベントカード描画
- **処理概要**:
  - AI バリエーションモードの切り替え（目立つボックス表示）
  - 全体進捗表示（Expander 内）
  - イベントカード（2 カラムグリッド）
    - 完了状態（✅ アイコン、背景色変更）
    - プレイ回数、スタンプ表示
    - 「はじめる」「もう一度挑戦」ボタン
  - 新規ユーザー登録（ニックネーム入力）
- **他ファイルとの関係**:
  - `services/progress_service.py`: ユーザー作成、進捗管理
  - `pages/story_mode.py`: イベント開始時の遷移先

#### **ファイル名**: `app/pages/story_mode.py`

- **役割**: ストーリーモード（子供向けメイン学習画面）
- **主な関数**:
  - `render_story_mode()`: ストーリーモード画面描画
  - `handle_choice_selection()`: 選択肢選択時の処理
  - `get_scene_with_variation()`: AI 生成/固定テンプレートのシーン取得
  - `create_scene_from_dict()`: 辞書から Scene オブジェクト生成
- **処理概要**:
  1. シーン取得（AI バリエーション or 固定テンプレート）
  2. プログレスバー表示（現在シーン/総シーン数）
  3. 獲得スタンプ表示
  4. シーンテキスト表示（大きな青いボックス）
  5. 選択肢ボタン表示（選択前）
  6. 選択後の処理:
     - 楽しい待ち時間アニメーション（`LoadingAnimation`）
     - バックグラウンドで AI フィードバック生成（スレッド）
     - フィードバック表示（保存して再利用）
     - 進捗更新（`ProgressService`）
     - 「次へ」ボタンで次のシーンへ
  7. 全シーン完了後、ふりかえりページへ遷移
- **設計意図**:
  - 子供が楽しく待てるアニメーション
  - 非同期処理（UI blocking 回避）
  - セッション内キャッシュ（リロード対策）
  - AI バリエーションによる多様な学習体験
- **他ファイルとの関係**:
  - `services/ai_service.py`: フィードバック生成
  - `services/scenario_generator.py`: AI シナリオ生成
  - `components/loading_animation.py`: アニメーション表示
  - `pages/review.py`: 完了後の遷移先

#### **ファイル名**: `app/pages/parent_guide.py`

- **役割**: 保護者向けシチュエーション別ガイド
- **主な関数**:
  - `render_parent_guide()`: ガイド画面メイン
  - `render_situation_selection()`: シチュエーション選択画面
  - `render_situation_detail()`: シチュエーション詳細画面
  - `display_ai_feedback()`: AI フィードバック表示（簡易/詳細）
  - `handle_question_submission()`: 質問処理（専門家チームに質問）
- **処理概要**:
  1. **シチュエーション選択**:
     - イベント別にグループ化表示
     - AI 生成モード（新規シチュエーション生成ボタン）
  2. **シチュエーション詳細**:
     - 子どもの行動表示
     - 保護者の対応選択肢（3-5 個）
     - 評価別の色分け（✅ 適切/⚠️ 許容/❌ 不適切）
  3. **専門家選択**:
     - 4 人の専門家からラジオボタンで選択
     - 「この対応について詳しく知る」ボタン
  4. **簡易フィードバック**:
     - 選択した専門家による 2-3 文の簡潔なアドバイス
     - ストリーミング表示
     - 専門家切り替え機能
  5. **詳細解説**:
     - 回答モード選択（1 人/4 人/統合）
     - 口調選択（フレンドリー/標準）
     - 「詳しく聞く」ボタンで生成開始
     - ストリーミング表示
  6. **自由質問機能**:
     - 関連質問の候補表示（AI 生成）
     - 自由テキスト入力
     - 会話履歴表示
     - 質問後、候補質問を再生成
- **設計意図**:
  - 専門家チームによる多角的な視点
  - ストリーミング表示で待ち時間を快適に
  - 段階的な情報開示（簡易 → 詳細）
  - インタラクティブな学習体験
- **他ファイルとの関係**:
  - `services/specialized_agent_service.py`: 専門家回答生成
  - `services/scenario_generator.py`: 新規シチュエーション生成
  - `utils/file_handler.py`: ガイドデータ読み込み

#### **ファイル名**: `app/pages/review.py`

- **役割**: ふりかえり画面（イベント完了後）
- **主な関数**:
  - `render_review()`: ふりかえり画面描画
- **処理概要**:
  1. 結果表示（3 カラムメトリクス）
     - ✨ 適切な行動回数
     - 👍 許容される行動回数
     - 💭 不適切な行動回数
  2. スタンプ付与と表示
     - ゴールド（5 回以上）
     - シルバー（3 回以上）
     - ブロンズ（1 回以上）
  3. 励ましメッセージ
  4. 詳細な振り返り（Expander 内）
     - シーンごとの行動リスト
  5. アクションボタン
     - 🔄 もう一度挑戦
     - 🎯 イベント選択
     - 🏠 モード選択
- **他ファイルとの関係**:
  - `services/progress_service.py`: イベント完了処理
  - `components/stamp_display.py`: スタンプ表示

---

### **6. コンポーネント（UI パーツ）**

#### **ファイル名**: `app/components/sidebar.py`

- **役割**: サイドバー（保護者向け AI 相談）
- **主な関数**:
  - `render_sidebar()`: サイドバーメイン描画
  - `render_faq_mode()`: よくある質問モード
  - `display_sequential_responses()`: 4 人の専門家の順番表示
  - `save_conversation()`: 会話履歴保存
- **処理概要**:
  1. よくある質問リスト（ランダム 5 件表示）
  2. 質問リフレッシュボタン
  3. 回答モード選択（1 人/4 人/統合）
  4. 専門家選択（1 人モードの場合）
  5. 口調選択（フレンドリー/標準）
  6. 質問ボタン → ストリーミング表示
  7. 自由質問入力欄
- **設計意図**:
  - どのページからでもアクセス可能
  - 専門家チームによる高精度な回答
  - ストリーミング表示で待ち時間を快適に
- **他ファイルとの関係**:
  - `services/specialized_agent_service.py`: 専門家回答生成
  - `services/progress_service.py`: 会話履歴保存

#### **ファイル名**: `app/components/feedback_display.py`

- **役割**: AI フィードバックの表示コンポーネント
- **主な関数**:
  - `display_feedback()`: フィードバック表示（即座 or アニメーション）
  - `display_feedback_stream()`: ストリーミングフィードバック表示
- **処理概要**:
  - 評価別のアイコンと色（🌟 緑/👍 青/💭 オレンジ）
  - カスタム HTML/CSS でスタイリング
  - テキストアニメーション（1 文字ずつ表示）
  - ストリーミング対応（ジェネレーターから順次表示）
- **他ファイルとの関係**:
  - `pages/story_mode.py`: 選択後のフィードバック表示

#### **ファイル名**: `app/components/loading_animation.py`

- **役割**: 待ち時間を楽しくするアニメーション
- **主なクラス/関数**:
  - `LoadingAnimation`: アニメーションパターン管理クラス
  - `show_cute_spinner()`: かわいいスピナー
  - `show_progress_animation()`: プログレスバー付き
  - `show_animal_animation()`: 動物の応援
  - `show_emoji_animation()`: 回転絵文字
  - `show_fun_facts()`: 励ましの豆知識
  - `show_loading_with_animation()`: タイプ別アニメーション選択
- **アニメーションタイプ**:
  - `auto`: ランダムに変わる（おすすめ）
  - `progress`: ステップごとのプログレスバー
  - `animal`: かわいい動物の応援
  - `emoji`: くるくる回る絵文字
  - `facts`: 励ましの豆知識
- **処理概要**:
  - グラデーション背景、大きなアイコン
  - フレームアニメーション（0.3 秒間隔）
  - プログレスバー（0-100%）
  - ランダム要素で飽きない工夫
- **設計意図**:
  - 子供が待ち時間を楽しめる
  - 視覚的に魅力的
  - 設定で有効/無効切り替え可能
- **他ファイルとの関係**:
  - `pages/story_mode.py`: 選択肢選択後の待ち時間

#### **ファイル名**: `app/components/progress_bar.py`

- **役割**: プログレスバー表示
- 現在のシーン/総シーン数を視覚的に表示

#### **ファイル名**: `app/components/stamp_display.py`

- **役割**: スタンプ表示
- 獲得したスタンプを視覚的に表示（⭐ マーク）

---

### **7. ユーティリティ**

#### **ファイル名**: `app/utils/file_handler.py`

- **役割**: ファイル読み書き（JSON 特化）
- **主な関数**:
  - `read_json()`: JSON ファイル読み込み
  - `write_json()`: JSON ファイル書き込み
  - `file_exists()`: ファイル存在確認
  - `ensure_directory()`: ディレクトリ作成
  - `list_json_files()`: JSON ファイル一覧取得
- **処理概要**:
  - エラーハンドリング（存在確認、JSON decode）
  - UTF-8 エンコーディング
  - ロギング
- **他ファイルとの関係**: 全体で JSON 操作時に使用

#### **ファイル名**: `app/utils/error_handler.py`

- **役割**: エラーハンドリングとユーザー通知
- **主な関数**:
  - `handle_error()`: 一般エラー処理
  - `handle_api_error()`: API 関連エラー処理
  - `handle_file_error()`: ファイル操作エラー処理
  - `handle_validation_error()`: バリデーションエラー処理
  - `safe_execute()`: 安全な関数実行
  - `show_success()` / `show_info()` / `show_warning()`: 通知表示
- **処理概要**:
  - ロギング（traceback 含む）
  - Streamlit 通知（st.error, st.warning, st.info）
  - デフォルト値の返却（エラー時）
- **他ファイルとの関係**: 全体でエラー処理時に使用

#### **ファイル名**: `app/utils/validator.py`

- **役割**: データバリデーション
- **主な関数**:
  - `is_valid_user_id()`: ユーザー ID 検証（8 桁 16 進数）
  - `is_valid_nickname()`: ニックネーム検証（1-20 文字）
  - `is_valid_evaluation()`: 評価タイプ検証
  - `is_valid_event_name()`: イベント名検証
  - `is_valid_scene_number()`: シーン番号検証
  - `validate_progress_data()`: 進捗データ包括検証
  - `validate_event_data()`: イベントデータ包括検証
- **処理概要**:
  - 正規表現による形式チェック
  - 範囲チェック
  - 必須フィールドチェック
  - ロギング
- **他ファイルとの関係**:
  - `services/progress_service.py`: 進捗データ保存前のバリデーション

#### **ファイル名**: `app/utils/date_utils.py`

- **役割**: 日時処理ユーティリティ
- **主な関数**:
  - `get_current_datetime_iso()`: 現在日時（ISO 8601 形式）
  - `get_current_date_str()`: 現在日付（YYYY-MM-DD）
  - `parse_iso_datetime()`: ISO 文字列 →datetime オブジェクト
  - `format_datetime_display()`: 表示用フォーマット（日本語）
  - `format_date_display()`: 日付表示用フォーマット
  - `calculate_days_ago()`: 経過日数計算
  - `is_same_day()`: 同日判定
  - `get_week_range()`: 週の開始日/終了日取得
- **処理概要**:
  - ISO 8601 形式の統一
  - 日本語表示フォーマット
  - タイムゾーン非対応（ローカル時刻のみ）
- **他ファイルとの関係**:
  - `services/progress_service.py`: 日時記録

---

## 🔗 主要な依存関係とデータフロー

### **1. ユーザー登録〜イベント選択フロー**

```
main.py
  → mode_selection.py (モード選択)
    → event_selection.py (イベント選択)
      → progress_service.py (新規ユーザー作成)
        → file_handler.py (JSON保存)
      → session_service.py (セッション保存)
```

### **2. ストーリーモードフロー（子供向け）**

```
story_mode.py
  → scenario_generator.py (AIバリエーション)
    → cache_manager.py (キャッシュチェック)
    → agent_coordinator.py (シナリオ生成)
      → ai_service.py (OpenAI API)
    → cache_manager.py (キャッシュ保存)
  → loading_animation.py (待ち時間演出)
  → ai_service.py (フィードバック生成)
  → progress_service.py (進捗更新)
  → review.py (完了後)
```

### **3. 保護者向けガイドフロー**

```
parent_guide.py
  → scenario_generator.py (新規シチュエーション生成)
  → specialized_agent_service.py (専門家回答)
    - 簡易フィードバック（1人の専門家）
    - 詳細解説（1人/4人/統合）
    - 自由質問（会話履歴付き）
  → progress_service.py (会話履歴保存)
```

### **4. サイドバー AI 相談フロー**

```
sidebar.py
  → specialized_agent_service.py (専門家回答)
    - generate_quick_response_stream() (1人モード)
    - generate_sequential_expert_responses_stream() (4人モード)
    - generate_comprehensive_response_stream() (統合モード)
  → progress_service.py (会話履歴保存)
```

---

## 🎨 設計意図と特徴

### **1. アーキテクチャパターン**

- **レイヤードアーキテクチャ**: UI (pages/components) → Service → Model
- **責務の分離**: 各サービスが明確な役割を持つ
- **依存性注入**: 設定は`Settings`クラスで一元管理

### **2. AI 活用戦略**

- **専門エージェントシステム**: RAG なしで高精度な回答を実現
  - 4 人の専門家（臨床心理士、小児科医、特別支援教育、家族支援）
  - エビデンスベース（理論名、研究者名を明記）
  - 多角的な視点（複数の専門分野から）
- **動的コンテンツ生成**: AI によるシナリオバリエーション
- **品質管理**: AgentCoordinator による二重チェック
- **キャッシュ戦略**: API コスト削減とレスポンス速度向上

### **3. UX 設計**

- **子供向け UI**:
  - 楽しい待ち時間アニメーション
  - 大きなボタン、わかりやすいアイコン
  - ポジティブなフィードバック
  - スタンプによる達成感
- **保護者向け UI**:
  - 専門家による信頼性の高い回答
  - 段階的な情報開示（簡易 → 詳細）
  - ストリーミング表示で待ち時間を快適に
  - インタラクティブな学習体験

### **4. パフォーマンス最適化**

- **ストリーミング表示**: リアルタイムで回答を表示
- **非同期処理**: UI ブロッキングを回避（スレッド使用）
- **キャッシュ**: 2 層キャッシュ（メモリ + ファイル）
- **セッション内キャッシュ**: リロード対策

### **5. 拡張性**

- **RAG 準備完了**: 将来的な専門知識ベース統合に対応
- **プラグイン可能**: 新しいイベントやエージェントの追加が容易
- **設定駆動**: `.env`ファイルで動作をカスタマイズ可能

---

## 📊 データ構造

### **イベントデータ（JSON）**

```json
{
  "event_name": "トイレ",
  "description": "トイレでの行動を学ぶイベント",
  "scenes": [
    {
      "scene_number": 0,
      "text": "トイレに行きたくなったよ。どうする？",
      "choices": [
        {
          "text": "「トイレに行きたい」と伝える",
          "evaluation": "appropriate"
        }
      ]
    }
  ]
}
```

### **ユーザー進捗データ（JSON）**

```json
{
  "user_id": "a1b2c3d4",
  "nickname": "ぽんたくん",
  "events": [
    {
      "event_name": "トイレ",
      "current_scene": 3,
      "good_actions_count": 5,
      "stamps_earned": 3,
      "completed": true,
      "scene_history": [...]
    }
  ],
  "ai_conversations": [...]
}
```

### **保護者ガイドデータ（JSON）**

```json
{
  "faq_questions": ["...", "..."],
  "situation_guides": [
    {
      "event": "トイレ",
      "child_action": "我慢する",
      "parent_actions": [
        {
          "text": "「大丈夫だよ、トイレ行こうね」と優しく声をかける",
          "evaluation": "appropriate",
          "ai_hint": "..."
        }
      ]
    }
  ]
}
```

---

## 🚀 実行フロー

### **アプリ起動時**

1. `main.py` 実行
2. Streamlit 設定（ページ設定、CSS）
3. 環境変数検証（`Settings.validate()`）
4. セッション初期化（`SessionService.initialize_session()`）
5. サイドバー描画
6. 現在ページ描画（初回は`mode_selection`）

### **子供向けイベント実行時**

1. イベント選択（`event_selection.py`）
2. AI バリエーションモード選択
3. ストーリーモード開始（`story_mode.py`）
4. 各シーンでループ:
   - シーン表示（AI 生成 or 固定）
   - 選択肢ボタン表示
   - 選択後、ローディングアニメーション表示
   - バックグラウンドで AI フィードバック生成
   - フィードバック表示
   - 進捗更新
   - 「次へ」ボタンで次のシーンへ
5. 全シーン完了後、ふりかえり画面（`review.py`）
6. スタンプ付与、イベント完了処理

### **保護者向けガイド実行時**

1. シチュエーション選択（`parent_guide.py`）
2. AI 生成モードの場合、新規シチュエーション生成
3. シチュエーション詳細表示
4. 保護者の対応選択肢から 1 つ選択
5. 専門家選択（4 人から 1 人）
6. 「詳しく知る」ボタン
7. 簡易フィードバック（ストリーミング表示）
8. 「詳しく聞く」ボタン（任意）
9. 回答モード選択（1 人/4 人/統合）
10. 詳細解説（ストリーミング表示）
11. 自由質問（任意）
12. 関連質問候補表示
13. 質問入力 → 専門家回答（ストリーミング）

---

## 🔍 分かりにくい設計意図・処理の補足

### **1. なぜ専門エージェントシステムを採用したか？**

- **RAG の課題**: 専門知識ベースの構築とメンテナンスが大変
- **プロンプト設計の利点**:
  - システムプロンプトに専門知識を埋め込むことで、RAG なしで高精度な回答を実現
  - 各専門家の人格、専門分野、引用すべき理論、禁止事項を明記
  - GPT-4o-mini の高い性能を最大限活用
- **結果**: RAG よりもシンプルで、高品質な回答が得られる

### **2. なぜストリーミング表示を重視したか？**

- **待ち時間の問題**: AI 生成には 5-20 秒かかる
- **ストリーミングの利点**:
  - ユーザーは最初の数文字がすぐに表示される
  - 待ち時間が短く感じられる
  - 読みながら次の文が表示されるため、退屈しない
- **実装**: `st.write_stream(generator)` でリアルタイム表示

### **3. なぜキャッシュが 2 層（メモリ + ファイル）なのか？**

- **メモリキャッシュ**: 高速アクセス（同一セッション内）
- **ファイルキャッシュ**: 永続化（セッションをまたいで再利用）
- **利点**:
  - 同じシナリオを何度も生成しない（API コスト削減）
  - レスポンス速度向上
  - オフライン対応の準備

### **4. なぜ`SceneVariation`クラスを動的に生成するのか？**

- **問題**: AI 生成のシーンは辞書形式だが、既存コードは`Scene`オブジェクトを期待
- **解決策**:
  - `create_scene_from_dict()`で辞書から`Scene`互換のオブジェクトを生成
  - 既存コードの変更を最小限に抑える
- **利点**:
  - 後方互換性維持
  - AI 生成と固定テンプレートの透過的な切り替え

### **5. なぜセッション内キャッシュを使うのか？**

- **問題**: Streamlit はページ再描画時に関数が再実行される
- **解決策**:
  - `st.session_state`に AI 生成シーンをキャッシュ
  - 同じシーン番号の場合、再生成せずにキャッシュを返す
- **利点**:
  - リロードしても同じ内容が表示される
  - API コスト削減

### **6. なぜバックグラウンドスレッドで AI 生成するのか？**

- **問題**: AI 生成は時間がかかり、UI がブロックされる
- **解決策**:
  - `threading.Thread`でバックグラウンド実行
  - メインスレッドはアニメーション表示
- **利点**:
  - ユーザーは待ち時間を楽しめる
  - UI の応答性向上

---

## 💡 今後の拡張可能性

### **1. RAG 統合**

- `rag_service.py`は実装済み
- 専門文献、研究論文、ガイドラインをベクトル化
- 専門エージェントシステムのプロンプトに専門知識を統合
- より根拠のある回答生成

### **2. 画像・音声対応**

- イベントデータに画像パスが定義済み
- `assets/images/events/`に画像配置
- 音声ファイルの再生機能追加

### **3. 多言語対応**

- プロンプトの多言語化
- UI テキストの国際化（i18n）

### **4. 学習分析**

- ユーザーの行動パターン分析
- 推奨イベントの提案
- 進捗レポート生成

### **5. 保護者ダッシュボード**

- 子どもの成長記録
- 専門家相談履歴
- きょうだい支援情報

---

## ✅ まとめ

このプロジェクトは、**ASD 支援に特化した教育アプリケーション**であり、以下の特徴を持ちます：

1. **子供向けと保護者向けの 2 つのモード**を提供
2. **AI（GPT-4o-mini）を活用**した個別フィードバック
3. **専門エージェントシステム**による高精度な保護者向けガイダンス
4. **動的コンテンツ生成**によるバリエーション豊富な学習体験
5. **ストリーミング表示**による快適な UX
6. **キャッシュ戦略**によるパフォーマンス最適化
7. **楽しい待ち時間演出**による子供のエンゲージメント向上

アーキテクチャは**レイヤードアーキテクチャ**を採用し、各層が明確な責務を持ち、拡張性と保守性に優れた設計となっています。

---

**生成日時**: 2025 年 11 月 3 日  
**バージョン**: 0.5  
**分析者**: AI Assistant
