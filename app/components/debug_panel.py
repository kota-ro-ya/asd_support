"""
デバッグ情報表示パネル
DEBUG_MODE=onの時のみ表示
"""

import streamlit as st
from typing import Dict, Any, Optional
import json

from app.config.settings import Settings
from app.utils.debug_info import get_debug_collector, DebugSession


def display_debug_panel(position: str = "sidebar"):
    """
    デバッグパネルを表示
    
    Args:
        position: "sidebar" または "main" - 表示位置
    """
    if not Settings.DEBUG_MODE:
        return
    
    collector = get_debug_collector()
    session_summary = collector.get_current_session_summary()
    
    if session_summary is None:
        return
    
    # 表示位置に応じてコンテナを選択
    if position == "sidebar":
        with st.sidebar:
            _render_debug_content(session_summary, collector)
    else:
        _render_debug_content(session_summary, collector)


def _render_debug_content(session_summary: Dict[str, Any], collector):
    """デバッグ情報の内容を描画"""
    
    st.markdown("---")
    st.markdown("### 🔧 デバッグ情報")
    
    # 折りたたみ可能なセクション
    with st.expander("📊 パフォーマンス概要", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "処理時間",
                f"{session_summary['duration']:.2f}秒",
                help="セッション開始からの経過時間"
            )
            st.metric(
                "API呼び出し",
                session_summary['api_calls'],
                help="OpenAI APIの呼び出し回数"
            )
        
        with col2:
            st.metric(
                "総トークン数",
                f"{session_summary['total_tokens']:,}",
                help="入力+出力の合計トークン数"
            )
            st.metric(
                "推定コスト",
                session_summary['estimated_cost'],
                help="API使用料金の概算（USD）"
            )
        
        with col3:
            st.metric(
                "キャッシュヒット率",
                session_summary['cache_hit_rate'],
                help="キャッシュの有効活用率"
            )
            st.metric(
                "評価数",
                session_summary['evaluations'],
                help="品質管理エージェントによる評価回数"
            )
        
        # エラーがある場合は目立つように表示
        if session_summary['errors'] > 0:
            st.error(f"⚠️ エラー発生: {session_summary['errors']}件")
    
    # API呼び出し詳細
    session_data = collector.get_session_data()
    if session_data and session_data.api_calls:
        with st.expander("🔌 API呼び出し詳細", expanded=False):
            for i, call in enumerate(session_data.api_calls, 1):
                st.markdown(f"**Call #{i}** - {call.agent_type or 'Generic'}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.text(f"⏱️ {call.response_time:.2f}s")
                with col2:
                    st.text(f"📝 {call.total_tokens} tokens")
                with col3:
                    st.text(f"🌡️ T={call.temperature}")
                with col4:
                    st.text(f"🔄 {'Stream' if call.stream else 'Sync'}")
                
                st.caption(f"📅 {call.timestamp}")
                st.markdown("---")
    
    # リファレンスデータ
    if session_data and session_data.references:
        with st.expander("📚 リファレンスデータ", expanded=False):
            for ref in session_data.references:
                st.markdown(f"**{ref.data_type}** - `{ref.source}`")
                if ref.description:
                    st.caption(ref.description)
                if ref.relevance_score is not None:
                    st.progress(ref.relevance_score)
                    st.caption(f"関連性: {ref.relevance_score * 100:.1f}%")
                st.markdown("---")
    
    # 評価情報
    if session_data and session_data.evaluations:
        with st.expander(f"⭐ 評価情報 ({len(session_data.evaluations)}件)", expanded=True):
            for i, eval_info in enumerate(session_data.evaluations, 1):
                st.markdown(f"**#{i} {eval_info.evaluation_type}**")
                
                # スコアを視覚化
                score_normalized = eval_info.score / 5.0 if eval_info.score <= 5 else eval_info.score / 100.0
                st.progress(score_normalized)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if eval_info.criteria:
                        st.caption(f"📊 {eval_info.criteria}")
                with col2:
                    # スコアの表示（100点満点 or 5点満点を自動判定）
                    if eval_info.score > 5:
                        st.metric("スコア", f"{eval_info.score:.0f}/100")
                    else:
                        st.metric("スコア", f"{eval_info.score:.1f}/5")
                
                if eval_info.details:
                    show_details = st.checkbox(
                        "詳細情報を表示",
                        key=f"eval_details_{i}",
                        value=False
                    )
                    if show_details:
                        # is_valid の表示
                        if "is_valid" in eval_info.details:
                            status = "✅ 合格" if eval_info.details["is_valid"] else "⚠️ 要改善"
                            st.markdown(f"**品質判定**: {status}")
                        
                        # issues の表示
                        if eval_info.details.get("issues"):
                            st.markdown("**⚠️ 問題点:**")
                            for issue in eval_info.details["issues"]:
                                st.markdown(f"- {issue}")
                        
                        # suggestions の表示
                        if eval_info.details.get("suggestions"):
                            st.markdown("**💡 改善提案:**")
                            for suggestion in eval_info.details["suggestions"]:
                                st.markdown(f"- {suggestion}")
                        
                        # その他の情報をJSON表示
                        st.json(eval_info.details)
                
                st.markdown("---")
    else:
        # デバッグ用：評価情報がない理由を表示
        if Settings.DEBUG_MODE:
            with st.expander("⭐ 評価情報（データなし）", expanded=False):
                if session_data:
                    st.info(f"現在のセッションID: {session_data.session_id}")
                    st.info(f"API呼び出し数: {len(session_data.api_calls)}")
                    st.info(f"評価データ数: {len(session_data.evaluations)}")
                else:
                    st.warning("セッションデータが存在しません")
    
    # キャッシュ操作
    if session_data and session_data.cache_operations:
        with st.expander("💾 キャッシュ操作", expanded=False):
            hits = len([c for c in session_data.cache_operations if c.action == "hit"])
            misses = len([c for c in session_data.cache_operations if c.action == "miss"])
            writes = len([c for c in session_data.cache_operations if c.action == "write"])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ ヒット", hits)
            with col2:
                st.metric("❌ ミス", misses)
            with col3:
                st.metric("💾 書込", writes)
            
            st.markdown("**操作履歴**")
            for cache_op in session_data.cache_operations:
                icon = "✅" if cache_op.action == "hit" else "❌" if cache_op.action == "miss" else "💾"
                st.text(f"{icon} {cache_op.cache_type} - {cache_op.action}")
    
    # エラー情報
    if session_data and session_data.errors:
        with st.expander("⚠️ エラー情報", expanded=True):
            for idx, error in enumerate(session_data.errors, 1):
                st.error(f"**{error.error_type}**: {error.message}")
                st.caption(f"発生時刻: {error.timestamp}")
                if error.traceback:
                    show_trace = st.checkbox(
                        "トレースバックを表示",
                        key=f"error_trace_{idx}",
                        value=False
                    )
                    if show_trace:
                        st.code(error.traceback, language="python")
    
    # JSONエクスポート
    with st.expander("📥 データエクスポート", expanded=False):
        if st.button("JSONとしてダウンロード"):
            from dataclasses import asdict
            json_data = json.dumps(asdict(session_data), ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 デバッグデータをダウンロード",
                data=json_data,
                file_name=f"debug_{session_data.session_id}.json",
                mime="application/json"
            )


def display_inline_debug_info(
    title: str,
    info: Dict[str, Any],
    icon: str = "🔍"
):
    """
    インラインでデバッグ情報を表示（特定の処理の詳細）
    
    Args:
        title: 表示タイトル
        info: 表示する情報
        icon: アイコン
    """
    if not Settings.DEBUG_MODE:
        return
    
    with st.expander(f"{icon} {title}", expanded=False):
        st.json(info)


def log_operation(operation_name: str, details: Optional[Dict[str, Any]] = None):
    """
    操作をログに記録し、DEBUG_MODE時は表示
    
    Args:
        operation_name: 操作名
        details: 詳細情報
    """
    if Settings.DEBUG_MODE:
        st.caption(f"🔧 {operation_name}")
        if details:
            with st.expander("詳細", expanded=False):
                st.json(details)

