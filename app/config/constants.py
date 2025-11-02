"""
Application constants and enums.
"""

# イベント名リスト
EVENT_NAMES = [
    "トイレ",
    "床屋",
    "病院",
    "公園",
    "身支度"
]

# イベント名からファイル名へのマッピング
EVENT_FILE_MAPPING = {
    "トイレ": "toilet.json",
    "床屋": "barber.json",
    "病院": "hospital.json",
    "公園": "park.json",
    "身支度": "morning_routine.json"
}

# 評価タイプ
EVALUATION_TYPES = {
    "appropriate": "適切な行動",
    "acceptable": "許容される行動",
    "inappropriate": "不適切な行動"
}

# スタンプ獲得条件
STAMP_THRESHOLDS = {
    "bronze": 1,    # 1つ以上の適切な行動でブロンズ
    "silver": 3,    # 3つ以上の適切な行動でシルバー
    "gold": 5       # 5つ以上の適切な行動でゴールド
}

# スタンプ画像のマッピング
STAMP_IMAGES = {
    "bronze": "stamp_smile.png",
    "silver": "stamp_star.png",
    "gold": "stamp_heart.png"
}

# AI人格モードリスト
AI_MODE_LIST = [
    "🩺 ロジカルドクター",
    "🍀 やさしい先生",
    "🌞 応援コーチ"
]

# 保護者モードリスト
PARENT_MODES_LIST = [
    "よくある質問モード",
    "シチュエーション別ガイドモード"
]

# セッション状態キー
SESSION_KEYS = {
    "USER_ID": "user_id",
    "NICKNAME": "nickname",
    "CURRENT_PAGE": "current_page",
    "CURRENT_EVENT": "current_event",
    "CURRENT_SCENE": "current_scene",
    "EVENT_DATA": "event_data",
    "PROGRESS_DATA": "progress_data",
    "AI_MODE": "ai_mode",
    "SELECTED_QUESTION": "selected_question",
    "PARENT_MODE": "parent_mode", # 保護者モードの切り替え
    "PARENT_GUIDE_EVENT": "parent_guide_event",
    "PARENT_GUIDE_SCENE": "parent_guide_scene",
    "PARENT_GUIDE_CHILD_ACTION": "parent_guide_child_action",
    "PARENT_GUIDE_PARENT_ACTION": "parent_guide_parent_action"
}

# ページ名
PAGE_NAMES = {
    "MODE_SELECTION": "mode_selection",  # メインモード選択画面
    "EVENT_SELECTION": "event_selection",  # 子供向けイベント選択
    "STORY_MODE": "story_mode",
    "REVIEW": "review",
    "PARENT_GUIDE": "parent_guide",  # 保護者向けガイド
    "PARENT_DASHBOARD": "parent_dashboard"
}

# UI設定
UI_CONFIG = {
    "MAX_CHOICE_DISPLAY": 4,  # 選択肢の最大表示数
    "FEEDBACK_DELAY": 2,       # フィードバック表示後の遅延（秒）
    "ANIMATION_DURATION": 0.5  # アニメーション時間（秒）
}

# 保護者の行動タイプとそれに関連するAIフィードバックのヒント
PARENT_ACTION_OPTIONS = [
    {
        "text": "「やめなさい！」と強く叱る",
        "evaluation": "inappropriate",
        "ai_hint": "子どもを強く叱るだけでは、問題行動の根本的な解決にはつながりにくいです。なぜそのような行動をとったのかを理解し、より建設的なアプローチを検討しましょう。"
    },
    {
        "text": "理由を尋ねてから、落ち着いて説明する",
        "evaluation": "appropriate",
        "ai_hint": "子どもの行動の背景にある理由を理解しようとすることは、適切な支援の第一歩です。落ち着いて対話することで、子どもも安心して自分の気持ちを伝えやすくなります。"
    },
    {
        "text": "他の子に目を向けるように促す",
        "evaluation": "acceptable",
        "ai_hint": "一時的に注意をそらすことは有効な場合がありますが、根本的な解決にはなりません。子どもの状況を把握し、より良い行動を促すための具体的な方法を考えましょう。"
    },
    {
        "text": "抱きしめて気持ちを受け止める",
        "evaluation": "appropriate",
        "ai_hint": "子どもが感情的になっている時は、まず気持ちを受け止めることが大切です。安心感を与えることで、落ち着きを取り戻し、次のステップに進む準備ができます。"
    },
    {
        "text": "選択肢をいくつか示し、自分で選ばせる",
        "evaluation": "appropriate",
        "ai_hint": "子どもに選択肢を与えることで、自主性や問題解決能力を育むことができます。自分で選ぶ経験は、成功体験となり自己肯定感を高めます。"
    }
]

