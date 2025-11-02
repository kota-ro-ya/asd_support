"""
Loading animations for better user experience.
子供向けの楽しい待ち時間演出
"""

import streamlit as st
import time
import random
from typing import List, Dict


class LoadingAnimation:
    """待ち時間を楽しくするアニメーション"""
    
    # アニメーションパターン
    THINKING_MESSAGES = [
        "🤔 AIがかんがえています...",
        "💭 どんなコメントがいいかな...",
        "✨ すてきなメッセージをつくっています...",
        "🎨 あなたにぴったりの言葉をえらんでいます...",
        "🌟 もうすこしだよ！",
        "🎯 いいコメントがみつかりました！",
    ]
    
    # 動物の応援メッセージ
    ANIMAL_CHEERS = [
        {"emoji": "🐰", "message": "うさぎさんが応援してるよ！"},
        {"emoji": "🐼", "message": "パンダさんがみてるよ！"},
        {"emoji": "🐻", "message": "くまさんも待ってるよ！"},
        {"emoji": "🦁", "message": "ライオンさんがおうえん！"},
        {"emoji": "🐸", "message": "かえるさんも一緒だよ！"},
        {"emoji": "🐶", "message": "わんちゃんがしっぽふってる！"},
        {"emoji": "🐱", "message": "ねこちゃんがにゃーん！"},
    ]
    
    # プログレスバーのステップメッセージ
    PROGRESS_STEPS = [
        "📝 あなたのこたえをよんでいます...",
        "🔍 どこがよかったかさがしています...",
        "💡 アドバイスをかんがえています...",
        "✏️ メッセージをかいています...",
        "✅ できあがり！",
    ]
    
    @staticmethod
    def show_cute_spinner(placeholder):
        """かわいいスピナーアニメーション"""
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        emojis = ["🌟", "✨", "💫", "⭐"]
        
        for i in range(10):  # 短いループ
            frame = spinner_frames[i % len(spinner_frames)]
            emoji = emojis[i % len(emojis)]
            message_idx = min(i // 2, len(LoadingAnimation.THINKING_MESSAGES) - 1)
            message = LoadingAnimation.THINKING_MESSAGES[message_idx]
            
            placeholder.markdown(
                f"""
                <div style="text-align: center; padding: 2rem; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 1rem; color: white; font-size: 1.3rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">
                        {emoji} {frame} {emoji}
                    </div>
                    <div>{message}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(0.3)
    
    @staticmethod
    def show_progress_animation(placeholder):
        """プログレスバー付きアニメーション"""
        total_steps = len(LoadingAnimation.PROGRESS_STEPS)
        
        for i, step_message in enumerate(LoadingAnimation.PROGRESS_STEPS):
            progress = (i + 1) / total_steps
            progress_percent = int(progress * 100)
            
            # プログレスバーのHTMLを生成
            progress_bar_html = f"""
            <div style="padding: 2rem; background-color: #F0F8FF; 
            border-radius: 1rem; border: 3px solid #4169E1;">
                <div style="text-align: center; font-size: 1.2rem; 
                margin-bottom: 1rem; color: #4169E1;">
                    {step_message}
                </div>
                <div style="background-color: #E0E0E0; border-radius: 1rem; 
                height: 30px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #4169E1, #00BFFF); 
                    width: {progress_percent}%; height: 100%; 
                    transition: width 0.3s ease;
                    display: flex; align-items: center; justify-content: center;
                    color: white; font-weight: bold;">
                        {progress_percent}%
                    </div>
                </div>
                <div style="text-align: center; margin-top: 1rem; font-size: 2rem;">
                    {'✨' * (i + 1)}
                </div>
            </div>
            """
            
            placeholder.markdown(progress_bar_html, unsafe_allow_html=True)
            time.sleep(0.6)
    
    @staticmethod
    def show_animal_cheer(placeholder):
        """動物の応援アニメーション"""
        # ランダムに動物を選択
        animal = random.choice(LoadingAnimation.ANIMAL_CHEERS)
        
        # アニメーション効果
        for size in [2, 3, 4, 5, 4, 3]:
            placeholder.markdown(
                f"""
                <div style="text-align: center; padding: 2rem; 
                background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
                border-radius: 1rem;">
                    <div style="font-size: {size}rem; margin-bottom: 0.5rem;">
                        {animal['emoji']}
                    </div>
                    <div style="font-size: 1.2rem; color: #2d3436; font-weight: bold;">
                        {animal['message']}
                    </div>
                    <div style="margin-top: 1rem; font-size: 1rem; color: #636e72;">
                        もうすこしまってね...
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(0.2)
    
    @staticmethod
    def show_countdown_animation(placeholder, seconds: int = 3):
        """カウントダウンアニメーション"""
        messages = [
            "🎈 あと3びょう...",
            "🎉 あと2びょう...",
            "🎊 あと1びょう...",
            "✨ できた！"
        ]
        
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
        
        for i, message in enumerate(messages):
            placeholder.markdown(
                f"""
                <div style="text-align: center; padding: 2rem; 
                background-color: {colors[i]}; border-radius: 1rem; 
                color: white; font-size: 1.5rem; font-weight: bold;
                animation: pulse 0.5s ease;">
                    {message}
                </div>
                <style>
                @keyframes pulse {{
                    0% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.1); }}
                    100% {{ transform: scale(1); }}
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
            time.sleep(1)
    
    @staticmethod
    def show_rotating_emojis(placeholder):
        """回転する絵文字アニメーション"""
        emoji_sets = [
            ["🌟", "⭐", "✨", "💫"],
            ["🎈", "🎉", "🎊", "🎁"],
            ["🌈", "🦄", "🎪", "🎨"],
        ]
        
        selected_set = random.choice(emoji_sets)
        
        for _ in range(8):  # 2回転
            for emoji in selected_set:
                placeholder.markdown(
                    f"""
                    <div style="text-align: center; padding: 2rem; 
                    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                    border-radius: 1rem;">
                        <div style="font-size: 4rem; animation: rotate 0.5s linear;">
                            {emoji}
                        </div>
                        <div style="font-size: 1.1rem; color: #2d3436; margin-top: 1rem;">
                            もうちょっとだよ！
                        </div>
                    </div>
                    <style>
                    @keyframes rotate {{
                        from {{ transform: rotate(0deg); }}
                        to {{ transform: rotate(360deg); }}
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                time.sleep(0.25)
    
    @staticmethod
    def show_fun_facts(placeholder):
        """豆知識を表示しながら待つ"""
        fun_facts = [
            {"emoji": "🧠", "fact": "かんがえることは、あたまのうんどうだよ！"},
            {"emoji": "💪", "fact": "まちがえても、それがべんきょうになるよ！"},
            {"emoji": "🌱", "fact": "まいにちすこしずつ、じょうずになっていくよ！"},
            {"emoji": "🌟", "fact": "あなたはとってもがんばりやさんだね！"},
            {"emoji": "🎯", "fact": "れんしゅうすると、できることがふえるよ！"},
        ]
        
        fact = random.choice(fun_facts)
        
        placeholder.markdown(
            f"""
            <div style="padding: 2rem; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 1rem; border: 3px dashed #FF6B9D;">
                <div style="text-align: center; font-size: 3rem; margin-bottom: 1rem;">
                    {fact['emoji']}
                </div>
                <div style="text-align: center; font-size: 1.2rem; 
                color: #2d3436; line-height: 1.6; font-weight: bold;">
                    {fact['fact']}
                </div>
                <div style="text-align: center; margin-top: 1rem; font-size: 0.9rem; color: #636e72;">
                    AIがメッセージをつくっています...
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def show_loading_with_animation(animation_type: str = "auto"):
    """
    待ち時間を楽しくするアニメーションを表示
    
    Args:
        animation_type: アニメーションのタイプ
            - "auto": ランダムに選択
            - "progress": プログレスバー
            - "animal": 動物の応援
            - "countdown": カウントダウン
            - "emoji": 絵文字回転
            - "facts": 豆知識
    """
    placeholder = st.empty()
    
    # アニメーションタイプが"auto"の場合、ランダムに選択
    if animation_type == "auto":
        animation_type = random.choice(["progress", "animal", "emoji", "facts"])
    
    try:
        if animation_type == "progress":
            LoadingAnimation.show_progress_animation(placeholder)
        elif animation_type == "animal":
            LoadingAnimation.show_animal_cheer(placeholder)
        elif animation_type == "countdown":
            LoadingAnimation.show_countdown_animation(placeholder)
        elif animation_type == "emoji":
            LoadingAnimation.show_rotating_emojis(placeholder)
        elif animation_type == "facts":
            LoadingAnimation.show_fun_facts(placeholder)
        else:
            # デフォルトはプログレスバー
            LoadingAnimation.show_progress_animation(placeholder)
    except Exception as e:
        # エラーが発生しても、シンプルなメッセージを表示
        placeholder.info("🤔 AIがかんがえています...")
    finally:
        placeholder.empty()


def show_simple_loading(message: str = "🤔 かんがえています..."):
    """シンプルな待ち時間表示（フォールバック用）"""
    return st.spinner(message)

