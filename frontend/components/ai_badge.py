"""
AI 内容标注标签组件

用法：
    from components.ai_badge import ai_badge
    ai_badge("解读", "本解读由 AI 模型生成，仅供参考，不构成临床诊断。")
"""

import streamlit as st

BADGE_STYLES = {
    "解读": {"emoji": "🤖", "label": "AI 辅助解读", "color": "#D97706", "bg": "#FFFBEB"},
    "建议": {"emoji": "📋", "label": "AI 生成建议", "color": "#2563EB", "bg": "#EFF6FF"},
    "风险": {"emoji": "⚠️", "label": "统计估算", "color": "#DC2626", "bg": "#FEF2F2"},
    "教育": {"emoji": "📖", "label": "学习资料", "color": "#059669", "bg": "#ECFDF5"},
}


def render(badge_type: str, disclaimer_text: str = ""):
    """渲染 AI 标注标签"""
    style = BADGE_STYLES.get(badge_type, BADGE_STYLES["解读"])

    st.markdown(
        f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        color: {style['color']};
        background: {style['bg']};
        border: 1px solid {style['color']}30;
        margin: 8px 0;
    ">
        {style['emoji']} {style['label']}
    </div>
    """,
        unsafe_allow_html=True,
    )

    if disclaimer_text:
        st.caption(f"⚠️ {disclaimer_text}")
