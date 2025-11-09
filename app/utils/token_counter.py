"""
トークン数のカウント・推定ユーティリティ
OpenAI APIのストリーミングでusage情報が取得できない場合の代替手段
"""

import logging
from typing import List, Dict, Optional
import tiktoken

logger = logging.getLogger(__name__)


class TokenCounter:
    """トークン数をカウント・推定するクラス"""
    
    # モデルごとのエンコーディング
    MODEL_ENCODINGS = {
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "gpt-4": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
    }
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        初期化
        
        Args:
            model: OpenAIのモデル名
        """
        self.model = model
        self.encoding = self._get_encoding(model)
    
    def _get_encoding(self, model: str) -> tiktoken.Encoding:
        """モデルに応じたエンコーディングを取得"""
        try:
            # モデル名から直接取得を試みる
            return tiktoken.encoding_for_model(model)
        except KeyError:
            # モデル名が見つからない場合、マッピングから取得
            encoding_name = self.MODEL_ENCODINGS.get(model, "cl100k_base")
            logger.warning(f"Model {model} not found, using {encoding_name}")
            return tiktoken.get_encoding(encoding_name)
    
    def count_tokens(self, text: str) -> int:
        """
        テキストのトークン数をカウント
        
        Args:
            text: カウント対象のテキスト
            
        Returns:
            トークン数
        """
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # エラー時は文字数を4で割った概算値を返す
            return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        メッセージリストの合計トークン数を推定
        
        Args:
            messages: OpenAI API形式のメッセージリスト
                      [{"role": "system", "content": "..."}, ...]
        
        Returns:
            推定トークン数
        """
        try:
            # メッセージごとのオーバーヘッド
            # 参考: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
            tokens_per_message = 3  # role, content, nameなど
            tokens_per_name = 1
            
            total_tokens = 0
            for message in messages:
                total_tokens += tokens_per_message
                for key, value in message.items():
                    total_tokens += self.count_tokens(str(value))
                    if key == "name":
                        total_tokens += tokens_per_name
            
            # リクエスト全体のオーバーヘッド
            total_tokens += 3
            
            return total_tokens
            
        except Exception as e:
            logger.error(f"Error counting message tokens: {e}")
            # エラー時は単純な合計
            return sum(self.count_tokens(msg.get("content", "")) for msg in messages)
    
    def estimate_streaming_tokens(
        self,
        prompt: str,
        response: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, int]:
        """
        ストリーミングレスポンスのトークン数を推定
        
        Args:
            prompt: ユーザーのプロンプト
            response: AIの応答
            system_prompt: システムプロンプト（オプション）
        
        Returns:
            {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int}
        """
        try:
            prompt_tokens = self.count_tokens(prompt)
            completion_tokens = self.count_tokens(response)
            
            # システムプロンプトがある場合
            if system_prompt:
                prompt_tokens += self.count_tokens(system_prompt)
            
            # メッセージのオーバーヘッド（3トークン/メッセージ）
            num_messages = 2 if system_prompt else 1
            prompt_tokens += num_messages * 3 + 3  # リクエスト全体のオーバーヘッド
            
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
            
        except Exception as e:
            logger.error(f"Error estimating streaming tokens: {e}")
            return {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }


# グローバルインスタンス（シングルトン）
_token_counter: Optional[TokenCounter] = None


def get_token_counter(model: str = "gpt-4o-mini") -> TokenCounter:
    """
    TokenCounterのシングルトンインスタンスを取得
    
    Args:
        model: モデル名
    
    Returns:
        TokenCounterインスタンス
    """
    global _token_counter
    if _token_counter is None or _token_counter.model != model:
        _token_counter = TokenCounter(model)
    return _token_counter

