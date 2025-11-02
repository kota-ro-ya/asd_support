# RAG 実装プラン

## 📊 推奨アプローチの比較

### Option 1: LangChain（推奨）

**メリット：**

- ✅ 最も成熟したエコシステム
- ✅ OpenAI との統合が簡単
- ✅ 豊富なドキュメントと事例
- ✅ ベクトルデータベースの選択肢が多い
- ✅ 日本語コミュニティが活発

**デメリット：**

- ⚠️ 依存関係が多い
- ⚠️ 学習曲線がやや急

**推奨ベクトル DB：**

- **Chroma**: 軽量、ローカル開発に最適
- **Pinecone**: 本番環境向け、マネージドサービス
- **FAISS**: 高速、メモリ効率的

### Option 2: LlamaIndex

**メリット：**

- ✅ データ接続に特化
- ✅ シンプルな API
- ✅ RAG に最適化された設計

**デメリット：**

- ⚠️ LangChain よりエコシステムが小さい

### Option 3: カスタム実装

**メリット：**

- ✅ 完全なコントロール
- ✅ 軽量な依存関係

**デメリット：**

- ❌ 開発時間が長い
- ❌ メンテナンスコストが高い

## 🎯 推奨：LangChain + Chroma

本プロジェクトには **LangChain + Chroma** の組み合わせを推奨します。

### 理由

1. **開発効率**: すぐに使い始められる
2. **コスト**: Chroma は無料で使える
3. **スケーラビリティ**: 将来的に Pinecone などに移行可能
4. **日本語対応**: 日本語の埋め込みモデルに対応

## 🚀 実装ステップ

### Phase 1: 基本セットアップ（1-2 日）

```bash
# 必要なライブラリのインストール
pip install langchain chromadb tiktoken
```

**実装内容：**

- RAGService の基本実装
- Chroma データベースの初期化
- OpenAI Embeddings の統合

### Phase 2: 知識ベースの構築（3-5 日）

**データソース：**

1. ASD 支援に関する公開文献
2. 厚生労働省のガイドライン
3. 療育機関の公開情報
4. 専門書籍の要約

**データ準備：**

```python
# 例：テキストファイルから知識ベースを構築
documents = [
    {
        "content": "ASDの感覚過敏について...",
        "metadata": {
            "event": "床屋",
            "category": "感覚過敏",
            "source": "厚生労働省ガイドライン"
        }
    },
    # ...
]
```

### Phase 3: 検索・統合（2-3 日）

**実装内容：**

- セマンティック検索の実装
- AI 生成との統合
- 検索精度の評価

### Phase 4: 最適化（継続的）

- リランキングの実装
- キャッシング戦略
- パフォーマンスチューニング

## 💻 実装例

### 1. requirements.txt の更新

```txt
# 既存のライブラリ
streamlit>=1.28.0
openai>=1.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
plotly>=5.17.0
pytest>=7.4.0

# RAG関連の追加
langchain>=0.1.0
chromadb>=0.4.0
tiktoken>=0.5.0
```

### 2. RAGService の実装

```python
# app/services/rag_service.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """RAGサービス - LangChain + Chroma実装"""

    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """
        RAGServiceの初期化

        Args:
            persist_directory: Chromaデータベースの保存先
        """
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002"
        )

        # Chromaベクトルストアの初期化
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="asd_knowledge"
        )

        logger.info("RAGService initialized with LangChain + Chroma")

    def add_documents(self, documents: List[Dict[str, str]]) -> bool:
        """
        知識ベースに文書を追加

        Args:
            documents: 追加する文書のリスト
                [{"content": str, "metadata": dict}, ...]

        Returns:
            成功した場合True
        """
        try:
            # Documentオブジェクトに変換
            docs = [
                Document(
                    page_content=doc["content"],
                    metadata=doc.get("metadata", {})
                )
                for doc in documents
            ]

            # テキスト分割（長文の場合）
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", "。", "、", " "]
            )
            split_docs = text_splitter.split_documents(docs)

            # ベクトルストアに追加
            self.vectorstore.add_documents(split_docs)
            self.vectorstore.persist()

            logger.info(f"Added {len(split_docs)} documents to RAG")
            return True

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False

    def retrieve_relevant_context(
        self,
        query: str,
        event: str = None,
        top_k: int = 3
    ) -> Optional[str]:
        """
        関連する専門知識を取得

        Args:
            query: 検索クエリ
            event: イベント名でフィルタリング（オプション）
            top_k: 取得する文書数

        Returns:
            関連するコンテキスト文字列
        """
        try:
            # フィルターの構築
            filter_dict = {}
            if event:
                filter_dict["event"] = event

            # セマンティック検索
            results = self.vectorstore.similarity_search(
                query=query,
                k=top_k,
                filter=filter_dict if filter_dict else None
            )

            if not results:
                logger.warning(f"No relevant documents found for query: {query}")
                return None

            # コンテキストの構築
            context_parts = []
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get("source", "不明")
                content = doc.page_content
                context_parts.append(
                    f"【参考情報 {i}】（出典: {source}）\n{content}"
                )

            context = "\n\n".join(context_parts)
            logger.info(f"Retrieved {len(results)} relevant documents")

            return context

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return None

    def search_with_score(
        self,
        query: str,
        k: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict]:
        """
        スコア付きで検索

        Args:
            query: 検索クエリ
            k: 取得する結果数
            score_threshold: 最小スコア閾値

        Returns:
            検索結果のリスト
        """
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k
            )

            # スコアでフィルタリング
            filtered_results = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
                if score >= score_threshold
            ]

            return filtered_results

        except Exception as e:
            logger.error(f"Error in search_with_score: {e}")
            return []
```

### 3. 知識ベースの初期化スクリプト

```python
# scripts/initialize_rag.py
"""
RAG知識ベースを初期化するスクリプト
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.rag_service import RAGService

def load_initial_knowledge():
    """初期知識を読み込む"""

    # ASD支援に関する基礎知識
    knowledge_base = [
        {
            "content": """
ASDの感覚過敏について：
ASD（自閉スペクトラム症）のお子さんは、聴覚、触覚、視覚などの感覚が
通常よりも敏感であることが多く、日常的な音や刺激が苦痛に感じられることがあります。
特に予測できない大きな音（バリカン、ドライヤーなど）は強い不安やパニックを
引き起こす可能性があります。
            """.strip(),
            "metadata": {
                "event": "床屋",
                "category": "感覚過敏",
                "source": "ASD支援ガイドライン"
            }
        },
        {
            "content": """
事前予告の重要性：
ASDのお子さんは、予測可能性があると安心します。これから何が起こるかを
事前に伝えることで、不安を大幅に軽減できます。視覚的な手順書や
タイムタイマーなどの視覚支援を併用すると、さらに効果的です。
            """.strip(),
            "metadata": {
                "event": "床屋",
                "category": "事前予告",
                "source": "療育実践ガイド"
            }
        },
        {
            "content": """
視覚支援の効果：
ASDのお子さんの多くは視覚情報の処理が得意です。手順を絵カードやイラストで
示すことで、理解が深まり、見通しが持てるようになります。これにより
不安が軽減され、適切な行動をとりやすくなります。
            """.strip(),
            "metadata": {
                "event": "床屋",
                "category": "視覚支援",
                "source": "TEACCH プログラム"
            }
        },
        {
            "content": """
ご褒美システム（トークンエコノミー）：
適切な行動に対して即座にご褒美を提供することで、その行動が強化されます。
シールやスタンプなど視覚的に分かりやすいご褒美は、ASDのお子さんに
特に効果的です。小さな成功体験を積み重ねることが重要です。
            """.strip(),
            "metadata": {
                "event": "床屋",
                "category": "行動強化",
                "source": "応用行動分析（ABA）"
            }
        },
        {
            "content": """
環境調整の重要性：
無理に慣れさせるよりも、まず環境を調整することが優先です。
イヤーマフでの音の軽減、タオルドライでのドライヤー回避など、
子どもの感覚特性に合わせた配慮が、長期的な適応につながります。
            """.strip(),
            "metadata": {
                "event": "床屋",
                "category": "環境調整",
                "source": "感覚統合療法"
            }
        }
    ]

    return knowledge_base


def main():
    """メイン処理"""
    print("🚀 RAG知識ベースを初期化します...")

    # RAGサービスの初期化
    rag_service = RAGService()

    # 初期知識の読み込み
    knowledge = load_initial_knowledge()
    print(f"📚 {len(knowledge)}件の知識を読み込みました")

    # 知識ベースに追加
    success = rag_service.add_documents(knowledge)

    if success:
        print("✅ RAG知識ベースの初期化が完了しました！")

        # テスト検索
        print("\n🔍 テスト検索を実行...")
        context = rag_service.retrieve_relevant_context(
            query="バリカンの音で子どもがパニックになる",
            event="床屋",
            top_k=2
        )

        if context:
            print("\n--- 検索結果 ---")
            print(context)
        else:
            print("検索結果が見つかりませんでした")
    else:
        print("❌ 初期化に失敗しました")


if __name__ == "__main__":
    main()
```

### 4. AI 生成への統合

```python
# app/pages/parent_guide.pyの修正例

# RAGサービスのインポート
from app.services.rag_service import RAGService

def display_ai_feedback(
    action_text: str,
    evaluation: str,
    event: str,
    child_action: str,
    action_idx: int
):
    """AIのフィードバックを表示（RAG統合版）"""

    # ... 既存のコード ...

    # RAGサービスの初期化
    try:
        rag_service = RAGService()

        # 関連する専門知識を取得
        rag_context = rag_service.retrieve_relevant_context(
            query=f"{event}で{child_action}への対応",
            event=event,
            top_k=2
        )
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
        rag_context = None

    # 詳細フィードバックの表示（RAGコンテキスト付き）
    if show_detailed:
        detailed_feedback_key = f"detailed_feedback_{event}_{child_action}_{action_text}_{ai_mode}"

        if detailed_feedback_key not in st.session_state:
            with st.spinner("AIが詳細な解説を生成中（専門知識を参照中）..."):
                ai_service = AIService()

                detailed_placeholder = st.empty()
                detailed_content = ""

                try:
                    for chunk in ai_service.generate_parent_action_feedback_stream(
                        event=event,
                        child_action=child_action,
                        parent_action=action_text,
                        evaluation=evaluation,
                        ai_mode=ai_mode,
                        detail_level="detailed",
                        rag_context=rag_context  # RAGコンテキストを渡す
                    ):
                        detailed_content += chunk
                        detailed_placeholder.markdown(
                            f"""
                            <div style="padding: 1.5rem; background-color: #F3E5F5;
                            border-radius: 0.5rem; border-left: 4px solid #9C27B0; margin-top: 1rem;">
                                <h4 style="margin-top: 0; color: #6A1B9A;">📚 詳細な解説</h4>
                                <div style="white-space: pre-wrap; margin-bottom: 0;">{detailed_content}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    st.session_state[detailed_feedback_key] = detailed_content

                except Exception as e:
                    ErrorHandler.handle_error(e, "詳細な解説の生成中にエラーが発生しました")
                    st.error("申し訳ございません。詳細な解説の生成に失敗しました。")
```

## 📦 必要な追加パッケージ

```txt
# RAG実装に必要なパッケージ
langchain>=0.1.0          # RAGフレームワーク
chromadb>=0.4.0           # ベクトルデータベース
tiktoken>=0.5.0           # トークンカウンター
```

## 🎯 実装の優先順位

### Phase 1（今すぐ可能）

- ✅ requirements.txt の更新
- ✅ RAGService の実装（LangChain 版）
- ✅ 初期知識ベースの構築

### Phase 2（1-2 週間後）

- ⏳ より多くの専門知識の追加
- ⏳ 検索精度の評価と改善
- ⏳ リランキングの実装

### Phase 3（1 ヶ月後）

- ⏳ 本番環境への展開
- ⏳ パフォーマンス最適化
- ⏳ ユーザーフィードバックの収集

## 💰 コスト見積もり

### OpenAI Embeddings API

- **モデル**: text-embedding-ada-002
- **コスト**: $0.0001 / 1K tokens
- **初期インデックス**: 約 10,000 トークン = $0.001
- **検索クエリ**: 約 100 トークン/回 = $0.00001/回

### Chroma（ローカル）

- **コスト**: 無料
- **ストレージ**: ローカルディスク

### 月間コスト見積もり（1000 ユーザー）

- 検索: 1000 回 × $0.00001 = $0.01
- 新規インデックス: 月 1 回更新 = $0.001
- **合計**: 約 $0.01/月（無視できるレベル）

## 🔄 代替案：Pinecone（本番環境向け）

将来的にスケールする場合：

```python
from langchain.vectorstores import Pinecone
import pinecone

# Pineconeの初期化
pinecone.init(
    api_key="YOUR_API_KEY",
    environment="us-east-1-aws"
)

vectorstore = Pinecone.from_existing_index(
    index_name="asd-knowledge",
    embedding=embeddings
)
```

**Pinecone のメリット：**

- マネージドサービス（運用不要）
- 高速・高可用性
- 自動スケーリング

**コスト：**

- 無料枠: 1 インデックス、100 万ベクトル
- 有料: $70/月〜

## 📚 参考リソース

- [LangChain 公式ドキュメント](https://python.langchain.com/)
- [Chroma 公式サイト](https://www.trychroma.com/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [RAG ベストプラクティス](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## ✅ まとめ

**推奨実装：LangChain + Chroma**

- すぐに使い始められる
- コストが低い（ほぼ無料）
- 将来的な拡張性がある
- 日本語に対応

実装を開始する場合は、まず`requirements.txt`を更新して、基本的な RAGService を実装することをお勧めします。
