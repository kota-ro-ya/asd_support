# 保護者向けガイド AI 統合仕様

## 概要

保護者向けシチュエーション別ガイドにおいて、従来の JSON 保存方式から AI 動的生成方式への移行を実装しました。

## 主な機能

### 1. AI による動的フィードバック生成

従来は JSON ファイルに固定の`ai_hint`を保存していましたが、以下のように変更しました：

- **簡易フィードバック（brief）**: 2-3 文程度の簡潔なアドバイス
- **詳細フィードバック（detailed）**: 根拠を含む詳細な解説（300-500 文字程度）

### 2. ユーザーインターフェース

#### 2.1 簡易フィードバック

- 保護者が対応を選択すると、自動的に AI が簡易フィードバックを生成
- セッションキャッシュを使用して、同じ内容の再生成を防止
- 評価（appropriate/acceptable/inappropriate）に応じた色分け表示

#### 2.2 詳細フィードバック

- 「📚 より詳細な解説を聞く」ボタンをクリックすると表示
- ストリーミング形式で逐次表示（リアルタイム感の向上）
- 以下の構造で詳細な解説を提供：
  1. 対応の評価
  2. ASD の特性との関連
  3. 具体的な理由と背景
  4. 実践的なアドバイス

#### 2.3 自由質問機能

- 既存機能を維持：保護者が自由に質問できる
- コンテキストを含めて AI に質問を送信

## 技術実装

### アーキテクチャ

```
parent_guide.py (UI層)
    ↓
ai_service.py (サービス層)
    ↓
prompts.py (プロンプト管理)
    ↓
OpenAI API
```

### 新規追加メソッド

#### ai_service.py

```python
def generate_parent_action_feedback(
    event: str,
    child_action: str,
    parent_action: str,
    evaluation: str,
    ai_mode: str,
    detail_level: str  # "brief" or "detailed"
) -> Optional[str]
```

```python
def generate_parent_action_feedback_stream(
    event: str,
    child_action: str,
    parent_action: str,
    evaluation: str,
    ai_mode: str,
    detail_level: str,
    rag_context: Optional[str] = None  # 将来的なRAG対応
) -> Generator[str, None, None]
```

#### prompts.py

```python
def get_parent_action_feedback_prompt(
    event: str,
    child_action: str,
    parent_action: str,
    evaluation: str,
    ai_mode: str,
    detail_level: str,
    rag_context: Optional[str] = None
) -> str
```

### データフロー

1. **ユーザーアクション**: 保護者が対応を選択
2. **簡易フィードバック生成**: AI が短いアドバイスを生成（キャッシュあり）
3. **詳細フィードバック生成**（オプション）: ボタンクリックで詳細解説を生成
4. **自由質問**（オプション）: テキスト入力で AI に質問

### キャッシング戦略

セッションごとに以下のキーでキャッシュ：

```python
brief_feedback_key = f"brief_feedback_{event}_{child_action}_{action_text}_{ai_mode}"
detailed_feedback_key = f"detailed_feedback_{event}_{child_action}_{action_text}_{ai_mode}"
```

これにより：

- 同じシチュエーションを再度見る際に即座に表示
- API 呼び出しコストの削減
- ユーザー体験の向上

## JSON データ構造の変更

### 従来の構造

```json
{
  "event": "床屋",
  "child_action": "バリカンの音を聞いてパニックになる",
  "parent_actions": [
    {
      "text": "事前に予告し、イヤーマフの使用を提案する",
      "evaluation": "appropriate",
      "ai_hint": "ASDのお子さんは予測できない音に強い不安を感じます..."
    }
  ]
}
```

### 新しい構造

```json
{
  "event": "床屋",
  "child_action": "バリカンの音を聞いてパニックになる",
  "parent_actions": [
    {
      "text": "事前に予告し、イヤーマフの使用を提案する",
      "evaluation": "appropriate"
    }
  ]
}
```

**重要**: `ai_hint`フィールドは現在も互換性のため残していますが、実際には使用されません。AI が動的に生成します。

## 将来的な RAG 統合

### 準備済みの機能

1. **RAGService クラス**: `app/services/rag_service.py`に実装済み（プレースホルダー）
2. **RAG コンテキストパラメータ**: AI 生成メソッドに`rag_context`パラメータを追加済み
3. **プロンプトへの RAG 統合**: RAG から取得した情報をプロンプトに含める構造を実装済み

### 実装予定の機能

1. **ベクトルデータベース統合**

   - Pinecone、Chroma、FAISS などの選択
   - ASD 支援に関する専門知識のインデックス化

2. **知識ベースの構築**

   - 専門文献
   - 臨床心理学の研究
   - 実践的な事例集

3. **検索とリランキング**
   - セマンティック検索
   - 関連性スコアリング
   - コンテキストの最適化

### RAG 統合後の使用例

```python
# RAGサービスの初期化
rag_service = RAGService()

# 関連コンテキストの取得
rag_context = rag_service.retrieve_relevant_context(
    query=f"{event}で{child_action}",
    event=event,
    child_action=child_action,
    top_k=3
)

# AI生成時にRAGコンテキストを使用
feedback = ai_service.generate_parent_action_feedback_stream(
    event=event,
    child_action=child_action,
    parent_action=parent_action,
    evaluation=evaluation,
    ai_mode=ai_mode,
    detail_level="detailed",
    rag_context=rag_context  # RAGから取得した専門知識
)
```

## パフォーマンス最適化

### 現在の最適化

1. **セッションキャッシング**: 同じ内容の再生成を防止
2. **ストリーミング**: 長文生成時のリアルタイム表示
3. **段階的表示**: 簡易 → 詳細の 2 段階表示でユーザー選択を可能に

### 将来的な最適化

1. **永続キャッシュ**: Redis などを使用した複数セッション間でのキャッシュ
2. **プリロード**: よく使われるシチュエーションの事前生成
3. **並列処理**: 複数のフィードバックを並行生成

## AI 人格モード対応

現在 3 つの AI 人格に対応：

1. **🩺 ロジカルドクター**: 科学的根拠重視
2. **🍀 やさしい先生**: 優しい言葉で説明
3. **🌞 応援コーチ**: 励ましながら前向きに

各モードに応じてフィードバックのトーンと内容が自動調整されます。

## エラーハンドリング

1. **API 呼び出し失敗**: ユーザーフレンドリーなエラーメッセージ
2. **タイムアウト**: 適切なタイムアウト設定
3. **キャッシュ失敗**: フォールバック処理

## テスト推奨事項

1. **異なる AI 人格での生成テスト**
2. **長文生成時のストリーミング表示確認**
3. **キャッシュの動作確認**
4. **エラーケースのテスト**
5. **複数シチュエーションの連続操作テスト**

## メンテナンスガイド

### プロンプトの調整

`app/config/prompts.py`の`get_parent_action_feedback_prompt`関数を編集：

- フィードバックの長さ調整
- 構造の変更
- トーンの調整

### AI 生成パラメータの調整

`app/config/settings.py`で以下を調整可能：

- `MAX_TOKENS`: 生成する最大トークン数
- `TEMPERATURE`: 生成の多様性（0-1）
- `OPENAI_MODEL`: 使用するモデル

## セキュリティとプライバシー

1. **API キーの管理**: 環境変数で管理
2. **ユーザーデータ**: セッション内でのみ保持
3. **ログ管理**: 個人情報を含まないログ記録

## まとめ

この実装により：

✅ JSON 固定データから AI 動的生成への移行完了
✅ 簡易版と詳細版の 2 段階フィードバック提供
✅ 将来的な RAG 統合の準備完了
✅ ユーザー体験の大幅な向上
✅ 柔軟な拡張性の確保
