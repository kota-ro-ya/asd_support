# 順番回答 UI 実装ガイド

## 📋 概要

このドキュメントは、専門家が順番に回答する UI の実装について説明します。

**実装日**: 2025 年 11 月 1 日  
**背景**: ユーザーからの「統合待ち時間が長すぎる」「簡易回答を選んでいるのか分かりにくい」というフィードバックを受けて実装

---

## 🎯 実装の目的

### 問題点

1. **UI が分かりにくい**

   - メインページで「簡易モード」か「詳細モード」か明確に選択できない
   - 「より詳細な解説を聞く」と「複数の専門家に詳しく質問する」の 2 つがあり混乱

2. **統合回答の待ち時間が長すぎる**
   - 詳細モード：15-20 秒待ってからストリーミング開始
   - ユーザーにとって苦痛

### 解決策

- **3 つのモード**を明確に分離：
  1. **💬 1 人の専門家（早い・おすすめ）** - 3-5 秒で回答開始
  2. **👥 4 人の専門家（順番に回答）** - すぐに開始、4 人が順番に表示
  3. **🔄 統合回答（総合的）** - 15-20 秒後に統合した回答

---

## 🔧 実装内容

### 1. SpecializedAgentService の拡張

新しいメソッド `generate_sequential_expert_responses_stream()` を追加：

```python
def generate_sequential_expert_responses_stream(
    self,
    question: str,
    context: str,
    tone: str = "friendly"
) -> Generator[Dict[str, str], None, None]:
    """
    各専門家が順番に回答（ストリーミング）

    Yields:
        {"agent_id": str, "agent_name": str, "agent_icon": str, "chunk": str}
    """
```

**特徴**:

- 4 人の専門家が順番に回答
- 各専門家の回答を個別にストリーミング
- `__START__` と `__END__` マーカーで各専門家の開始/終了を制御

---

### 2. メインページ（parent_guide.py）の更新

#### 「より詳細に知りたい方へ」セクション

```python
# 回答モードの選択
response_mode = st.radio(
    "回答モード",
    [
        "💬 1人の専門家（早い・おすすめ）",
        "👥 4人の専門家（順番に回答）",
        "🔄 統合回答（総合的）"
    ],
    help="1人の専門家：3-5秒で回答開始\n4人の専門家：すぐに開始、順番に表示\n統合回答：15-20秒後に統合した回答"
)

# 口調の選択
tone_mode = st.radio(
    "口調",
    ["😊 フレンドリー（おすすめ）", "📖 標準"],
    help="フレンドリー：親しみやすく柔らかい表現\n標準：専門的で形式的な表現"
)

if st.button("📚 詳しく聞く", type="primary"):
    if "1人の専門家" in response_mode:
        # 簡易モード
        stream_generator = specialized_service.generate_quick_response_stream(...)
        full_answer = st.write_stream(stream_generator)

    elif "4人の専門家" in response_mode:
        # 順番モード
        full_answer = display_sequential_responses(
            specialized_service,
            question,
            context,
            tone
        )

    else:  # 統合回答
        # 統合モード
        stream_generator = specialized_service.generate_comprehensive_response_stream(...)
        full_answer = st.write_stream(stream_generator)
```

#### 「自由に質問する」セクション

同様の 3 モード選択 UI を実装。

---

### 3. サイドバー（sidebar.py）の更新

よくある質問モードとカスタム質問モードの両方で、同じ 3 モード選択 UI を実装：

```python
response_mode = st.radio(
    "回答モード",
    [
        "💬 1人の専門家（早い・おすすめ）",
        "👥 4人の専門家（順番に回答）",
        "🔄 統合回答（総合的）"
    ],
    ...
)

tone_mode = st.radio(
    "口調",
    ["😊 フレンドリー（おすすめ）", "📖 標準"],
    ...
)
```

---

### 4. 順番表示のヘルパー関数

`display_sequential_responses()` 関数をメインページとサイドバーに追加：

```python
def display_sequential_responses(service, question, context, tone):
    """各専門家が順番にストリーミング表示"""
    full_answer = ""
    current_agent = None
    current_response = ""
    placeholder = None

    for chunk_data in service.generate_sequential_expert_responses_stream(question, context, tone):
        if chunk_data["chunk"] == "__START__":
            # 新しい専門家の開始
            current_agent = chunk_data
            current_response = ""

            # ヘッダー表示
            st.markdown(f"### {chunk_data['agent_icon']} {chunk_data['agent_name']}の見解")
            placeholder = st.empty()

        elif chunk_data["chunk"] == "__END__":
            # 現在の専門家の回答終了
            full_answer += f"\n\n### {current_agent['agent_icon']} {current_agent['agent_name']}の見解\n{current_response}\n"
            current_agent = None
            current_response = ""
            placeholder = None

        else:
            # ストリーミング表示
            current_response += chunk_data["chunk"]
            if placeholder:
                placeholder.markdown(current_response)

    return full_answer
```

---

## 📊 ユーザー体験の比較

### Before（旧 UI）

```
[より詳細な解説を聞く] ボタン
   ↓
（何が起きるか不明、15-20秒待つ）
   ↓
統合回答が表示される
```

**問題**：

- ❌ 何が起きるか分からない
- ❌ 長い待ち時間
- ❌ モード選択ができない

---

### After（新 UI）

```
【回答モード】
○ 💬 1人の専門家（早い・おすすめ）
○ 👥 4人の専門家（順番に回答）
○ 🔄 統合回答（総合的）

【口調】
○ 😊 フレンドリー（おすすめ）
○ 📖 標準

[📚 詳しく聞く]
```

#### モード 1: 1 人の専門家（3-5 秒）

```
[ボタンクリック]
   ↓（3秒）
💬 専門家からの回答
[ストリーミング表示]
```

#### モード 2: 4 人の専門家（すぐ開始）

```
[ボタンクリック]
   ↓（すぐ）
🧠 臨床心理士の見解
[ストリーミング表示] → 完了
   ↓
⚕️ 小児科医の見解
[ストリーミング表示] → 完了
   ↓
🏫 特別支援教育専門家の見解
[ストリーミング表示] → 完了
   ↓
💙 家族支援専門家の見解
[ストリーミング表示] → 完了
```

#### モード 3: 統合回答（15-20 秒）

```
[ボタンクリック]
   ↓（15-20秒、各専門家から意見収集）
👥 統合回答
[ストリーミング表示]
```

**改善**：

- ✅ 何が起きるか明確
- ✅ モードを選択できる
- ✅ 待ち時間ゼロ（モード 2）またはすぐ開始（モード 1）
- ✅ 多様な視点（モード 2）
- ✅ 統合的な判断（モード 3）

---

## 🎨 UI デザイン原則

### 1. 明確性

- 3 つのモードを明確に区別
- 各モードの特徴（速さ、内容）を説明

### 2. デフォルト値

- **1 人の専門家（早い・おすすめ）**をデフォルトに
- **フレンドリー**口調をデフォルトに

### 3. ヘルプテキスト

- 各モードに具体的な時間を表示（3-5 秒、15-20 秒など）
- 「おすすめ」ラベルでユーザーをガイド

---

## 🔄 データフロー

### モード 2（順番回答）のフロー

```
[ユーザー]
   ↓
[display_sequential_responses]
   ↓
[SpecializedAgentService.generate_sequential_expert_responses_stream]
   ↓
for each agent (4人):
    1. yield {"chunk": "__START__", "agent_name": ..., "agent_icon": ...}
    2. OpenAI API にリクエスト（ストリーミング）
    3. for each chunk in stream:
         yield {"chunk": chunk_content, ...}
    4. yield {"chunk": "__END__", ...}
   ↓
[display_sequential_responses でストリーミング表示]
   ↓
[full_answer を返す]
```

---

## 📝 コード変更サマリー

### 変更したファイル

1. **`app/services/specialized_agent_service.py`**

   - `generate_sequential_expert_responses_stream()` メソッド追加

2. **`app/pages/parent_guide.py`**

   - `display_sequential_responses()` ヘルパー関数追加
   - 「より詳細に知りたい方へ」セクションを 3 モード UI に変更
   - 「自由に質問する」セクションを 3 モード UI に変更

3. **`app/components/sidebar.py`**
   - `display_sequential_responses()` ヘルパー関数追加
   - よくある質問モードを 3 モード UI に変更
   - カスタム質問モードを 3 モード UI に変更

---

## 🧪 テスト方法

### 1. メインページのテスト

1. アプリを起動：`streamlit run app.py`
2. 保護者向けシチュエーション別ガイドを選択
3. イベントと子どもの行動を選択
4. 保護者の対応を選択
5. 「より詳細に知りたい方へ」セクションで以下を確認：

**テストケース 1: 1 人の専門家モード**

- [ ] 「💬 1 人の専門家（早い・おすすめ）」を選択
- [ ] 「📚 詳しく聞く」をクリック
- [ ] 3-5 秒以内にストリーミング開始
- [ ] 1 人の専門家からの回答が表示される

**テストケース 2: 4 人の専門家モード**

- [ ] 「👥 4 人の専門家（順番に回答）」を選択
- [ ] 「📚 詳しく聞く」をクリック
- [ ] すぐにストリーミング開始
- [ ] 4 人の専門家が順番に回答（各ヘッダー付き）
- [ ] 各専門家の回答がストリーミング表示される

**テストケース 3: 統合回答モード**

- [ ] 「🔄 統合回答（総合的）」を選択
- [ ] 「📚 詳しく聞く」をクリック
- [ ] 15-20 秒待つ
- [ ] 統合回答がストリーミング表示される

**テストケース 4: 口調変更**

- [ ] 「😊 フレンドリー」を選択 → 柔らかい表現で回答
- [ ] 「📖 標準」を選択 → 専門的な表現で回答

### 2. サイドバーのテスト

1. サイドバーで「保護者向け AI 相談」を開く
2. よくある質問を選択
3. 上記と同様の 3 モードをテスト
4. カスタム質問でも同様にテスト

---

## 🎉 期待される効果

### ユーザー体験の向上

- ✅ **待ち時間ゼロ**（順番モード）
- ✅ **明確な選択肢**（3 モード）
- ✅ **多様な視点**（4 人の専門家）
- ✅ **柔軟性**（口調選択）

### システムの改善

- ✅ **スケーラビリティ**（各専門家が独立）
- ✅ **保守性**（明確なインターフェース）
- ✅ **拡張性**（専門家の追加が容易）

---

## 🔮 将来の拡張案

### 1. 統合回答の改善

- 統合回答生成中に「各専門家の意見を収集中...」などの進捗表示

### 2. 専門家の選択

- ユーザーが特定の専門家（例：小児科医のみ）を選択できる機能

### 3. 回答の比較

- 各専門家の回答を並べて比較表示する機能

### 4. お気に入り

- 各専門家の回答を「お気に入り」として保存

---

## 📚 関連ドキュメント

- `SPECIALIZED_AGENT_SYSTEM.md` - 専門エージェントシステムの詳細
- `STREAMING_IMPROVEMENT.md` - ストリーミング実装の詳細
- `SIDEBAR_REFACTOR_SUMMARY.md` - サイドバーリファクタリングの詳細

---

## 📞 サポート

質問やフィードバックがある場合は、開発チームまでお問い合わせください。
