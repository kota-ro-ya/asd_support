"""
Feedback display component for AI responses.
"""

import streamlit as st
import time


def display_feedback(feedback_text: str, evaluation: str, show_animation: bool = True):
    """
    AIフィードバックを表示する
    
    Args:
        feedback_text: フィードバックテキスト
        evaluation: 評価タイプ（appropriate/acceptable/inappropriate）
        show_animation: アニメーション表示するかどうか
    """
    
    # 評価に応じた表示スタイル
    if evaluation == "appropriate":
        icon = "🌟"
        color = "green"
        title = "素晴らしい！"
    elif evaluation == "acceptable":
        icon = "👍"
        color = "blue"
        title = "いいね！"
    else:  # inappropriate
        icon = "💭"
        color = "orange"
        title = "考えてみよう"
    
    # フィードバック表示
    if show_animation:
        # アニメーション付きで表示
        with st.container():
            st.markdown(f"### {icon} {title}")
            
            # テキストを徐々に表示（ストリーミング風）
            placeholder = st.empty()
            displayed_text = ""
            
            for char in feedback_text:
                displayed_text += char
                placeholder.markdown(
                    f'<div style="padding: 1rem; border-radius: 0.5rem; '
                    f'background-color: rgba({"0,255,0" if color == "green" else "0,0,255" if color == "blue" else "255,165,0"}, 0.1); '
                    f'border-left: 4px solid {color};">'
                    f'{displayed_text}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                time.sleep(0.02)  # 文字表示の遅延
    else:
        # 即座に表示
        st.markdown(f"### {icon} {title}")
        st.markdown(
            f'<div style="padding: 1rem; border-radius: 0.5rem; '
            f'background-color: rgba({"0,255,0" if color == "green" else "0,0,255" if color == "blue" else "255,165,0"}, 0.1); '
            f'border-left: 4px solid {color};">'
            f'{feedback_text}'
            f'</div>',
            unsafe_allow_html=True
        )


def display_feedback_stream(feedback_generator, evaluation: str):
    """
    AIフィードバックをストリーミング表示する
    
    Args:
        feedback_generator: フィードバックのジェネレーター
        evaluation: 評価タイプ
    """
    
    # 評価に応じた表示スタイル
    if evaluation == "appropriate":
        icon = "🌟"
        color = "green"
        title = "素晴らしい！"
    elif evaluation == "acceptable":
        icon = "👍"
        color = "blue"
        title = "いいね！"
    else:  # inappropriate
        icon = "💭"
        color = "orange"
        title = "考えてみよう"
    
    st.markdown(f"### {icon} {title}")
    
    # ストリーミング表示用プレースホルダー
    placeholder = st.empty()
    full_text = ""
    
    for chunk in feedback_generator:
        full_text += chunk
        placeholder.markdown(
            f'<div style="padding: 1rem; border-radius: 0.5rem; '
            f'background-color: rgba({"0,255,0" if color == "green" else "0,0,255" if color == "blue" else "255,165,0"}, 0.1); '
            f'border-left: 4px solid {color};">'
            f'{full_text}'
            f'</div>',
            unsafe_allow_html=True
        )
    
    return full_text

