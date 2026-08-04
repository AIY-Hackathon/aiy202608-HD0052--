"""
风险可视化图表组件

提供：
- 染色体变异分布柱状图
- 风险概览指标卡片
- 风险评分雷达图
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_variant_distribution(variants: list[dict]):
    """染色体变异分布柱状图"""
    if not variants:
        return

    # 统计每条染色体的变异数量
    chrom_counts = {}
    for v in variants:
        chrom = str(v.get("chromosome", "?"))
        chrom_counts[chrom] = chrom_counts.get(chrom, 0) + 1

    # 排序（1-22, X, Y 自然排序）
    def _chrom_key(c):
        try:
            return int(c)
        except ValueError:
            return {"X": 23, "Y": 24}.get(c, 99)

    sorted_chroms = sorted(chrom_counts.keys(), key=_chrom_key)
    counts = [chrom_counts[c] for c in sorted_chroms]

    fig = px.bar(
        x=sorted_chroms,
        y=counts,
        labels={"x": "染色体", "y": "变异数量"},
        title="染色体变异分布",
        color_discrete_sequence=["#2563EB"],
    )
    fig.update_layout(
        showlegend=False,
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_risk_metrics(total_variants: int, pathogenic_count: int, overall_risk: float):
    """风险概览指标卡片"""
    col1, col2, col3 = st.columns(3)

    risk_level = "🟢 低风险" if overall_risk < 1.0 else ("🟡 中风险" if overall_risk < 2.0 else "🔴 高风险")

    col1.metric("总变异数", f"{total_variants:,}")
    col2.metric("致病性变异数", pathogenic_count, delta=None)
    col3.metric("综合风险评分", f"{overall_risk:.2f}", delta=risk_level, delta_color="off")


def render_risk_radar(risk_scores: dict[str, float]):
    """风险评分雷达图"""
    if not risk_scores:
        return

    categories = list(risk_scores.keys())
    values = list(risk_scores.values())

    # 中文标签映射
    label_map = {
        "cardio": "心血管",
        "diabetes": "2型糖尿病",
        "breast_cancer": "乳腺癌",
        "colorectal": "结直肠癌",
        "alzheimer": "阿尔茨海默",
        "obesity": "肥胖",
        "hypertension": "高血压",
    }
    labels = [label_map.get(c, c) for c in categories]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=labels,
            fill="toself",
            fillcolor="rgba(37, 99, 235, 0.2)",
            line=dict(color="#2563EB", width=2),
            name="风险评分",
        )
    )
    fig.update_layout(
        polar=dict(radial=dict(visible=True, range=[0, max(values) * 1.2])),
        showlegend=False,
        height=350,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
