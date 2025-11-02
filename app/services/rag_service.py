"""
RAG (Retrieval-Augmented Generation) service for enhanced AI responses.
LangChain 0.3.x + ChromaDB実装
"""

from typing import Optional, List, Dict
import logging
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config.settings import Settings

logger = logging.getLogger(__name__)


class RAGService:
    """RAGサービス - LangChain 0.3.x + Chroma実装"""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        RAGServiceの初期化
        
        Args:
            persist_directory: Chromaデータベースの保存先（デフォルト: data/chroma_db）
        """
        try:
            # デフォルトの保存先
            if persist_directory is None:
                persist_directory = str(Settings.DATA_DIR / "chroma_db")
            
            # ディレクトリの作成
            Path(persist_directory).mkdir(parents=True, exist_ok=True)
            
            # OpenAI Embeddingsの初期化
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                openai_api_key=Settings.OPENAI_API_KEY
            )
            
            # Chromaベクトルストアの初期化
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
                collection_name="asd_knowledge"
            )
            
            logger.info(f"RAGService initialized with Chroma at {persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAGService: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, any]]) -> bool:
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
            
            logger.info(f"Added {len(split_docs)} documents to RAG")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def retrieve_relevant_context(
        self,
        query: str,
        event: Optional[str] = None,
        top_k: int = 3
    ) -> Optional[str]:
        """
        関連する専門知識を取得
        
        Args:
            query: 検索クエリ
            event: イベント名でフィルタリング（オプション）
            top_k: 取得する文書数
        
        Returns:
            関連するコンテキスト文字列。失敗時はNone
        """
        try:
            # フィルターの構築
            filter_dict = None
            if event:
                filter_dict = {"event": event}
            
            # セマンティック検索
            results = self.vectorstore.similarity_search(
                query=query,
                k=top_k,
                filter=filter_dict
            )
            
            if not results:
                logger.warning(f"No relevant documents found for query: {query}")
                return None
            
            # コンテキストの構築
            context_parts = []
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get("source", "不明")
                category = doc.metadata.get("category", "")
                content = doc.page_content
                
                context_part = f"【参考情報 {i}】"
                if category:
                    context_part += f"（{category}）"
                context_part += f"（出典: {source}）\n{content}"
                
                context_parts.append(context_part)
            
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
    
    def get_collection_count(self) -> int:
        """
        コレクション内の文書数を取得
        
        Returns:
            文書数
        """
        try:
            return self.vectorstore._collection.count()
        except Exception as e:
            logger.error(f"Error getting collection count: {e}")
            return 0


# 将来的なRAG実装のための参考情報
"""
推奨される実装アプローチ:

1. ベクトルデータベースの選択肢:
   - Pinecone: マネージドサービス、スケーラブル
   - Chroma: オープンソース、軽量
   - FAISS: Meta開発、高速
   - Weaviate: GraphQLサポート、豊富な機能

2. 知識ベースの構築:
   - ASD支援に関する専門文献
   - 臨床心理学の研究論文
   - 保護者向けガイドライン
   - 実践的な事例集
   - 療育機関の公開情報

3. エンベディングモデル:
   - OpenAI Embeddings API (text-embedding-ada-002)
   - 日本語特化モデル（intfloat/multilingual-e5-largeなど）

4. RAGパイプライン:
   a. クエリの前処理（キーワード抽出、意図理解）
   b. ベクトル検索（類似度計算）
   c. リランキング（関連性の再評価）
   d. コンテキストの統合（LLMへの入力形式に整形）

5. 評価指標:
   - 検索精度（Precision, Recall）
   - レスポンス品質（専門家評価）
   - ユーザー満足度（保護者フィードバック）

実装例:
```python
from openai import OpenAI
import chromadb

class RAGService:
    def __init__(self):
        self.client = OpenAI()
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection("asd_knowledge")
    
    def retrieve_relevant_context(self, query: str, top_k: int = 3):
        # クエリをベクトル化
        embedding = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        ).data[0].embedding
        
        # ベクトル検索
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        
        # コンテキストを整形
        context = "\n\n".join([doc for doc in results['documents'][0]])
        return context
```
"""

