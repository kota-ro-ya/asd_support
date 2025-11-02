# トラブルシューティングガイド

## 🚨 「解答を選択しても何も反応がない」問題

### 症状

- 床屋などで選択肢をクリックしても画面が変わらない
- フィードバックが表示されない
- エラーメッセージも出ない

### 原因の可能性

1. **OpenAI API キーの問題**

   - API キーが設定されていない
   - API キーが無効
   - API の利用制限に達している

2. **AI 生成シナリオのデータ構造の問題**

   - AI が生成したデータの形式が不正
   - 必要な属性が欠けている

3. **ネットワークの問題**
   - インターネット接続が切れている
   - OpenAI API にアクセスできない

### 確認方法

#### ステップ 1：エラーメッセージを確認

選択肢をクリックした後、画面に以下のいずれかが表示されていないか確認：

```
⚠️ エラーが発生しました: ...
デバッグ情報:
...
```

表示されている場合 → エラー内容を確認してください

#### ステップ 2：ブラウザのコンソールを確認

1. **F12 キーを押す**（または右クリック → 検証）
2. **Console タブ**を開く
3. 赤いエラーメッセージがないか確認

#### ステップ 3：ターミナルを確認

アプリを起動しているターミナルを見て、以下のようなエラーが出ていないか確認：

```
Error: OpenAI API key not set
ConnectionError: Failed to connect to OpenAI
...
```

---

## 🔧 解決方法

### 解決策 1：OpenAI API キーを確認

#### 1-1. `.env` ファイルの確認

```bash
# プロジェクトのルートディレクトリで
cat .env
```

以下のように表示されるはず：

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxx
```

**問題がある場合**：

- `OPENAI_API_KEY` の行がない → 追加する
- `sk-proj-...` が空 → 有効な API キーを設定する

#### 1-2. API キーの有効性を確認

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

`YOUR_API_KEY` を実際の API キーに置き換えて実行。

**正常な場合**：モデルのリストが返ってくる  
**エラーの場合**：`401 Unauthorized` → API キーが無効

### 解決策 2：アプリを再起動

```bash
# 1. Ctrl+C でアプリを停止
# 2. もう一度起動
streamlit run app/main.py
```

### 解決策 3：キャッシュをクリア

```bash
# キャッシュファイルを削除
rm -rf data/cache/*.json

# Streamlit のキャッシュもクリア
rm -rf .streamlit/cache
```

### 解決策 4：AI バリエーションをオフにする

一時的に AI 機能をオフにして、固定テンプレートで動作するか確認：

1. イベント選択画面で「🤖 AI バリエーション」を**オフ**にする
2. 床屋を選択
3. 選択肢をクリック

**正常に動作する場合** → AI 生成の問題  
**動作しない場合** → 別の問題

### 解決策 5：デバッグモードで起動

`.env` ファイルに以下を追加：

```env
DEBUG_MODE=True
```

再起動すると、詳細なログが出力されます。

---

## 📊 よくあるエラーと対処法

### エラー 1：`AttributeError: 'Choice' object has no attribute 'ai_feedback_hint'`

**原因**：AI 生成されたシナリオのデータ構造が不正

**対処法**：

1. キャッシュをクリア
   ```bash
   rm data/cache/scenario_cache.json
   ```
2. アプリを再起動
3. AI バリエーションをオンにして再度試す

### エラー 2：`OpenAI API key not set`

**原因**：`.env` ファイルに API キーが設定されていない

**対処法**：

1. `.env` ファイルを開く
2. 以下を追加（YOUR_API_KEY を実際の値に置き換え）
   ```
   OPENAI_API_KEY=sk-proj-YOUR_API_KEY
   ```
3. アプリを再起動

### エラー 3：`RateLimitError: Rate limit exceeded`

**原因**：OpenAI の API 使用制限に達した

**対処法**：

1. しばらく待つ（5-10 分）
2. または AI バリエーションをオフにする
3. または「🔄 毎回新しく生成」をオフにしてキャッシュを活用

### エラー 4：`ConnectionError: Failed to connect`

**原因**：インターネット接続の問題

**対処法**：

1. インターネット接続を確認
2. VPN を使用している場合はオフにしてみる
3. ファイアウォール設定を確認

---

## 🐛 デバッグ情報の収集方法

問題が解決しない場合、以下の情報を収集してください：

### 1. エラーメッセージ全文

画面に表示されているエラーメッセージをコピー

### 2. ターミナルのログ

```bash
# ログをファイルに保存
streamlit run app/main.py > debug.log 2>&1
```

問題が発生したら `debug.log` ファイルを確認

### 3. ブラウザのコンソールログ

1. F12 → Console タブ
2. 右クリック → Save as... でログを保存

### 4. 環境情報

```bash
# Python バージョン
python --version

# パッケージバージョン
pip list | grep -E "streamlit|openai"

# OS 情報
uname -a  # Mac/Linux
ver       # Windows
```

---

## 💡 予防策

### 推奨設定（エラーを減らす）

`.env` ファイル：

```env
# API キー（必須）
OPENAI_API_KEY=sk-proj-xxxxx

# AI 生成設定（エラーを減らす）
AI_GENERATION_MAX_ATTEMPTS=2        # 試行回数を減らす
AI_QUALITY_THRESHOLD=75             # 品質閾値を下げる

# キャッシュ設定（API 呼び出しを減らす）
ENABLE_SCENARIO_CACHE=True
CACHE_EXPIRY_HOURS=48               # 長めに保持
```

### 安定動作のコツ

1. **AI バリエーションと毎回生成を両方オンにしない**

   - 片方だけオンにする
   - または両方オフにする

2. **初回は固定テンプレートで試す**

   - まず AI バリエーションをオフで動作確認
   - 動作したら AI バリエーションをオンにする

3. **ネット環境の良い場所で使う**
   - Wi-Fi が安定している場所
   - VPN はオフ

---

## 🔍 詳細デバッグ手順

### 手順 1：最小構成で動作確認

```bash
# 1. すべてのキャッシュをクリア
rm -rf data/cache/*.json
rm -rf .streamlit/cache

# 2. .env を確認
cat .env

# 3. 最小設定で起動
streamlit run app/main.py
```

### 手順 2：段階的に機能を有効化

1. まず **AI バリエーションオフ**で動作確認
2. 動作したら **AI バリエーションオン + 毎回生成オフ**
3. 動作したら **両方オン**

### 手順 3：ログを詳細に確認

`.env` に追加：

```env
DEBUG_MODE=True
```

ターミナルに詳細なログが出力されるので、エラー箇所を特定

---

## 📞 サポート

### 問題が解決しない場合

以下の情報と一緒にお問い合わせください：

1. **症状の詳細**

   - いつ発生するか
   - どのボタンをクリックしたか
   - エラーメッセージ

2. **環境情報**

   - OS（Mac/Windows/Linux）
   - Python バージョン
   - ブラウザ（Chrome/Firefox/Safari/Edge）

3. **デバッグ情報**
   - ターミナルのログ
   - ブラウザのコンソールログ
   - `.env` ファイルの内容（API キーは隠す）

---

## 📚 関連ドキュメント

- [AI_VARIATION_USAGE.md](./AI_VARIATION_USAGE.md) - AI 機能の使い方
- [UI_LOCATION_GUIDE.md](./UI_LOCATION_GUIDE.md) - UI の操作方法
- [QUICKSTART.md](../QUICKSTART.md) - 基本的な使い方

---

**最終更新**: 2025 年 11 月 1 日  
**バージョン**: 1.0
