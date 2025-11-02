# バグ修正サマリー - フィードバック表示問題

## 🐛 問題：「フィードバックが表示されず場面 1 に戻る」

### 症状

1. 選択肢をクリック
2. フィードバックが表示されない
3. 場面 1 が再表示される
4. 同じ質問が繰り返される

---

## 🔍 原因

### 根本原因：キャッシュキーの管理不足

```python
# 問題のあったコード
cache_key = f"ai_scene_{event.event_name}_{scene_number}"

# st.rerun()のたびにAI生成が走る
# → 異なるシナリオが生成される
# → セッション状態（フィードバック）と不整合
```

**何が起きていたか**：

1. ユーザーが選択肢をクリック
2. `handle_choice_selection()`でフィードバックを生成
3. `st.session_state[feedback_key]`に保存
4. `st.session_state[choice_made_key] = True`
5. `st.rerun()`を実行
6. **ページ再描画時に`get_scene_with_variation()`が再実行される**
7. **`force_new=True`なので新しいシーンを生成**
8. **キャッシュキーが存在しないので再生成**
9. **別のシナリオが表示される**
10. **`feedback_key`が一致しない（シナリオが変わったため）**
11. **フィードバックが表示されない**

---

## ✅ 修正内容

### 修正 1：セッション内キャッシュの導入

```python
# 修正後
session_cache_key = f"ai_scene_{event.event_name}_{scene_number}_session"

# 同じセッション内では同じシーンを返す
if session_cache_key in st.session_state:
    return create_scene_from_dict(st.session_state[session_cache_key])
```

**効果**：

- `st.rerun()`されても同じシーンを表示
- フィードバックとシーンの整合性を保つ

### 修正 2：明示的なキャッシュクリア

```python
# 「次へ」ボタンを押したとき
if st.button("次へ ➡️", ...):
    # 現在のシーンのキャッシュをクリア
    current_cache_key = f"ai_scene_{event.event_name}_{current_scene_number}_session"
    if current_cache_key in st.session_state:
        del st.session_state[current_cache_key]

    # 次のシーンへ
    SessionService.next_scene()
    st.rerun()
```

**効果**：

- 次のシーンでは新しいシナリオを生成
- 意図的にキャッシュをクリア

### 修正 3：イベント選択に戻るときのクリア

```python
# 「イベント選択に戻る」ボタン
if st.button("🏠 イベント選択に戻る", ...):
    # すべてのAI生成シーンのキャッシュをクリア
    for key in list(st.session_state.keys()):
        if key.startswith(f"ai_scene_{event.event_name}_"):
            del st.session_state[key]

    SessionService.set_page(PAGE_NAMES["EVENT_SELECTION"])
    st.rerun()
```

**効果**：

- 次回のプレイでは完全に新しいシナリオ
- キャッシュの蓄積を防ぐ

### 修正 4：デバッグ情報の追加

```python
if Settings.DEBUG_MODE:
    with st.expander("🐛 デバッグ情報", expanded=False):
        st.write(f"現在のシーン番号: {current_scene_number}")
        st.write(f"選択済みフラグ: {st.session_state.get(choice_made_key, False)}")
        st.write(f"フィードバック有無: {st.session_state.get(feedback_key) is not None}")
```

**効果**：

- 問題の早期発見
- 動作状態の可視化

---

## 🔄 修正後の動作フロー

### 正常な流れ

```
1. 場面1が表示される
   ├─ AI生成（force_new=True）
   └─ session_cache_keyに保存

2. ユーザーが選択肢をクリック
   ├─ handle_choice_selection()
   ├─ フィードバック生成
   ├─ st.session_state[feedback_key]に保存
   ├─ st.session_state[choice_made_key] = True
   └─ st.rerun()

3. ページ再描画（st.rerun()後）
   ├─ get_scene_with_variation()
   ├─ session_cache_keyから取得 ← ★同じシーン★
   ├─ choice_made_key = True
   └─ フィードバック表示

4. 「次へ」ボタンをクリック
   ├─ session_cache_keyを削除 ← ★重要★
   ├─ feedback_keyをクリア
   ├─ choice_made_keyをクリア
   ├─ SessionService.next_scene()
   └─ st.rerun()

5. 場面2が表示される
   ├─ AI生成（新しいシナリオ）
   └─ 新しいsession_cache_keyに保存
```

---

## 📊 Before & After

### Before（バグあり）

```
[場面1表示]
  ↓ クリック
[AI生成（シナリオA）] → フィードバック保存
  ↓ st.rerun()
[AI生成（シナリオB）] ← 別のシナリオ！
  ↓
[フィードバック表示できず] ← キーが合わない
  ↓
[場面1が再表示される]
```

### After（修正後）

```
[場面1表示]
  ↓ クリック
[AI生成（シナリオA）] → session_cacheに保存
                     → フィードバック保存
  ↓ st.rerun()
[session_cacheから取得（シナリオA）] ← 同じシナリオ！
  ↓
[フィードバック表示成功] ← キーが一致
  ↓ 「次へ」クリック
[session_cacheクリア]
  ↓
[場面2表示（新シナリオ）]
```

---

## 🎯 キーポイント

### 1. Streamlit の再描画の理解

Streamlit は`st.rerun()`を呼ぶと、**スクリプト全体を最初から実行し直します**。

そのため：

- すべての関数が再実行される
- `get_scene_with_variation()`も再実行される
- キャッシュがないと毎回新しいシーンを生成

### 2. キャッシュの 2 レイヤー

```
レイヤー1：永続キャッシュ（ファイル）
  └─ scenario_generator.py内で管理
  └─ 24時間有効

レイヤー2：セッションキャッシュ（st.session_state）
  └─ story_mode.py内で管理 ← ★今回追加★
  └─ 同じシーン内では同じ内容
```

### 3. 明示的なクリア

```python
# Good: 明示的にクリアするタイミングを制御
if st.button("次へ"):
    del st.session_state[cache_key]  # クリア
    SessionService.next_scene()

# Bad: 自動的にクリアされると困る
# （st.rerun()のたびにクリアされてしまう）
```

---

## 🧪 テスト方法

### テストケース 1：通常の流れ

1. 床屋を選択
2. 場面 1 で選択肢をクリック
3. ✅ フィードバックが表示される
4. 「次へ」をクリック
5. ✅ 場面 2 が表示される

### テストケース 2：毎回新しく生成

1. 「🔄 毎回新しく生成」をオン
2. 床屋を選択
3. 場面 1 を完了
4. イベント選択に戻る
5. もう一度床屋を選択
6. ✅ 前回と異なる場面 1 が表示される

### テストケース 3：デバッグ情報

1. `.env`に`DEBUG_MODE=True`を追加
2. アプリを再起動
3. ✅ デバッグ情報が表示される
4. 選択肢をクリック後、デバッグ情報を確認
   - 選択済みフラグ: True
   - フィードバック有無: True

---

## 🔍 デバッグ方法（今後のため）

### デバッグモードの有効化

`.env`ファイル：

```env
DEBUG_MODE=True
```

再起動後、ストーリーモード画面に「🐛 デバッグ情報」が表示されます。

### 確認項目

- **現在のシーン番号**: 正しいシーンを表示しているか
- **選択済みフラグ**: 選択後に True になっているか
- **フィードバック有無**: フィードバックが保存されているか
- **AI バリエーション**: オン/オフの状態
- **毎回新規生成**: オン/オフの状態

---

## 📝 学んだこと

### 1. Streamlit の状態管理の重要性

- `st.rerun()`は全てをリセットする
- `st.session_state`で状態を保持する必要がある
- キャッシュキーの設計が重要

### 2. デバッグ情報の価値

- 問題の早期発見
- ユーザーからの報告時に詳細が分かる
- 本番環境では非表示にできる

### 3. 明示的な制御

- 自動的な動作に頼らない
- いつキャッシュをクリアするか明示する
- 予期しない動作を防ぐ

---

## 🚀 今後の改善案

### 1. より強固なキャッシュ管理

```python
class SceneCacheManager:
    """シーンキャッシュを一元管理するクラス"""

    @staticmethod
    def get_cache_key(event_name, scene_number, session=True):
        suffix = "_session" if session else ""
        return f"ai_scene_{event_name}_{scene_number}{suffix}"

    @staticmethod
    def clear_event_cache(event_name):
        """特定イベントのキャッシュをすべてクリア"""
        for key in list(st.session_state.keys()):
            if key.startswith(f"ai_scene_{event_name}_"):
                del st.session_state[key]
```

### 2. タイムスタンプ付きキャッシュ

```python
# キャッシュに生成日時を保存
cached_data = {
    "scene": scene_dict,
    "generated_at": datetime.now().isoformat()
}

# 一定時間経過したらキャッシュを無効化
```

### 3. ユーザー設定でキャッシュ戦略を選択

```
[ ] シーン内は同じ内容を表示（現在の動作）
[ ] ページを戻ったら新しい内容を生成
[ ] 完全にランダム（リロードのたびに変わる）
```

---

**最終更新**: 2025 年 11 月 1 日  
**バージョン**: 2.0  
**修正**: フィードバック表示問題の完全解決
