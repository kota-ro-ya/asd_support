# パッケージバージョン管理

## 📊 現在の環境

### Python

- **現在**: Python 3.13.2（2025 年 2 月 4 日リリース）
- **最新安定版**: Python 3.13.7（2025 年 8 月 14 日リリース）
- **推奨**: Python 3.13.x 系は問題なし（最新版へのアップデートは任意）

### 既存パッケージの状況

| パッケージ    | 現在のバージョン | 最新版     | 状態            | 推奨アクション   |
| ------------- | ---------------- | ---------- | --------------- | ---------------- |
| streamlit     | 1.41.1           | 1.50.0     | ⚠️ 更新推奨     | アップデート推奨 |
| openai        | 2.6.1            | 最新に近い | ✅ OK           | そのままで OK    |
| python-dotenv | 1.1.1            | 1.2.1      | ⚠️ マイナー更新 | アップデート推奨 |
| pandas        | -                | 2.0.0+     | ✅ OK           | 確認済み         |
| plotly        | -                | 5.17.0+    | ✅ OK           | 確認済み         |
| pytest        | -                | 8.0.0+     | ⚠️ 更新推奨     | アップデート推奨 |

## 🆕 RAG 関連パッケージ（追加予定）

### 推奨バージョン（2025 年 10 月時点）

| パッケージ              | 推奨バージョン | 理由                             |
| ----------------------- | -------------- | -------------------------------- |
| **langchain**           | >=0.3.0        | 最新の安定版、豊富な機能         |
| **langchain-openai**    | >=0.2.0        | OpenAI 統合の公式パッケージ      |
| **langchain-community** | >=0.3.0        | コミュニティ拡張機能             |
| **chromadb**            | >=0.5.0        | 最新の安定版、パフォーマンス向上 |
| **tiktoken**            | >=0.8.0        | OpenAI 公式トークナイザー        |

### LangChain のバージョン戦略

LangChain は 2024 年から**モジュール分割**されています：

```
langchain (コア)
├── langchain-openai (OpenAI統合)
├── langchain-community (コミュニティパッケージ)
├── langchain-core (基本機能)
└── langchain-text-splitters (テキスト分割)
```

**推奨インストール方法：**

```bash
# コアパッケージ
pip install langchain>=0.3.0

# OpenAI統合（必須）
pip install langchain-openai>=0.2.0

# コミュニティパッケージ（オプション、便利な機能が多い）
pip install langchain-community>=0.3.0
```

## 🔄 アップデート手順

### 1. 既存パッケージのアップデート

```bash
# 仮想環境を有効化
cd /path/to/ASD_support_practice
source env_a/bin/activate

# 主要パッケージの個別アップデート（推奨）
pip install --upgrade streamlit
pip install --upgrade python-dotenv
pip install --upgrade pytest

# または、requirements.txtから一括更新
pip install --upgrade -r requirements.txt
```

### 2. RAG パッケージの新規インストール

```bash
# 仮想環境内で実行
source env_a/bin/activate

# RAG関連パッケージのインストール
pip install langchain>=0.3.0
pip install langchain-openai>=0.2.0
pip install langchain-community>=0.3.0
pip install chromadb>=0.5.0
pip install tiktoken>=0.8.0
```

### 3. インストールの確認

```bash
# インストール済みパッケージの確認
pip list | grep -E "(langchain|chroma|tiktoken)"

# 期待される出力例：
# langchain              0.3.0
# langchain-openai       0.2.0
# langchain-community    0.3.0
# langchain-core         0.3.0
# chromadb               0.5.0
# tiktoken               0.8.0
```

## ⚠️ 互換性の注意点

### Streamlit のバージョン

- **1.41.1 → 1.50.0**
  - UI コンポーネントの改善
  - パフォーマンス向上
  - **破壊的変更なし**（アップデート安全）

### OpenAI

- **2.6.1**
  - 十分に新しい
  - 現在のコードと互換性あり
  - **アップデート不要**（任意）

### LangChain

- **0.3.x 系**
  - モジュール分割後の最新安定版
  - 後方互換性に配慮
  - 推奨：個別モジュールのインストール

### ChromaDB

- **0.5.x 系**
  - パフォーマンスが大幅向上
  - API に若干の変更あり
  - **注意**: 0.4.x 以前と一部非互換

## 🎯 推奨アップデート戦略

### 段階的アップデート（推奨）

```bash
# ステップ1: 既存パッケージの更新
pip install --upgrade streamlit python-dotenv pytest

# ステップ2: 動作確認
streamlit run app/main.py

# ステップ3: RAGパッケージの追加
pip install langchain>=0.3.0 langchain-openai>=0.2.0 chromadb>=0.5.0 tiktoken>=0.8.0

# ステップ4: RAG機能のテスト
python scripts/initialize_rag.py
```

### 一括アップデート（慎重に）

```bash
# requirements.txtから全パッケージを最新版に更新
pip install --upgrade -r requirements.txt
```

## 📦 requirements.txt（更新版）

```txt
# 基本パッケージ（更新版）
streamlit>=1.50.0
openai>=1.0.0
python-dotenv>=1.2.0
pandas>=2.0.0
plotly>=5.17.0
pytest>=8.0.0

# RAG関連パッケージ（新規追加）
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
chromadb>=0.5.0
tiktoken>=0.8.0
```

## 🔍 バージョン確認コマンド

```bash
# 仮想環境を有効化
source env_a/bin/activate

# 全パッケージのバージョン確認
pip list

# 特定のパッケージのバージョン確認
pip show langchain
pip show chromadb
pip show streamlit

# 更新可能なパッケージの確認
pip list --outdated
```

## 🚨 トラブルシューティング

### 依存関係の競合が発生した場合

```bash
# 依存関係の確認
pip check

# 問題のあるパッケージの再インストール
pip uninstall <package-name>
pip install <package-name>

# 最終手段：仮想環境の再構築
deactivate
rm -rf env_a
python3 -m venv env_a
source env_a/bin/activate
pip install -r requirements.txt
```

### インポートエラーが発生した場合

```python
# モジュール分割後のLangChainのインポート方法
# ❌ 古い方法（0.2.x以前）
from langchain.embeddings import OpenAIEmbeddings

# ✅ 新しい方法（0.3.x以降）
from langchain_openai import OpenAIEmbeddings

# ❌ 古い方法
from langchain.vectorstores import Chroma

# ✅ 新しい方法
from langchain_community.vectorstores import Chroma
```

## 📅 更新履歴

| 日付       | 変更内容                                  |
| ---------- | ----------------------------------------- |
| 2025-10-27 | 初版作成、RAG 関連パッケージの追加        |
| -          | Streamlit 1.50.0、pytest 8.0.0 に更新推奨 |
| -          | LangChain 0.3.x 系の採用決定              |

## 🔗 参考リンク

- [LangChain 公式ドキュメント](https://python.langchain.com/)
- [ChromaDB 公式サイト](https://www.trychroma.com/)
- [Streamlit 公式ドキュメント](https://docs.streamlit.io/)
- [OpenAI Python Library](https://github.com/openai/openai-python)
- [Python 公式ダウンロード](https://www.python.org/downloads/)

## ✅ まとめ

### 現在の状態

- ✅ Python 3.13.2 は十分に新しい
- ⚠️ Streamlit、pytest は更新推奨
- ✅ OpenAI ライブラリは最新に近い
- ❌ RAG 関連パッケージは未インストール

### 推奨アクション

1. **既存パッケージの更新**（オプション、推奨）

   ```bash
   pip install --upgrade streamlit python-dotenv pytest
   ```

2. **RAG パッケージの追加**（必須、RAG 機能を使う場合）

   ```bash
   pip install langchain>=0.3.0 langchain-openai>=0.2.0 chromadb>=0.5.0 tiktoken>=0.8.0
   ```

3. **動作確認**
   ```bash
   streamlit run app/main.py
   python scripts/initialize_rag.py
   ```

### セキュリティ

- すべての推奨バージョンはセキュリティパッチ適用済み
- 定期的な更新を推奨（3-6 ヶ月ごと）
