"""
变异信息表格组件

展示变异列表：染色体、位置、基因、临床意义、风险评分
支持 CLNSIG 颜色编码和 ClinVar 星级评审图标
"""
import streamlit as st
import pandas as pd


def render(variants: list[dict]):
    """渲染变异信息表格"""
    if not variants:
        st.info("暂无变异数据")
        return

    df = pd.DataFrame(variants)

    # 确保必要列存在
    required_cols = [
        "chromosome",
        "position",
        "gene_name",
        "clinvar_significance",
        "clinvar_review_status",
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = "-"

    # CLNSIG 颜色映射
    def _color_clnsig(val):
        if "Pathogenic" in str(val):
            return "background-color: #FEE2E2; color: #991B1B"
        elif "Benign" in str(val):
            return "background-color: #D1FAE5; color: #065F46"
        elif "VUS" in str(val) or "Uncertain" in str(val):
            return "background-color: #F3F4F6; color: #374151"
        elif "Conflicting" in str(val):
            return "background-color: #FEF3C7; color: #92400E"
        return ""

    # 星级评审图标映射
    def _format_review_status(val):
        star_map = {
            "practice_guideline": "⭐⭐⭐⭐",
            "reviewed_by_expert_panel": "⭐⭐⭐",
            "criteria_provided": "⭐⭐",
            "single_submitter": "⭐",
            "no_assertion": "-",
        }
        stars = star_map.get(str(val).lower(), str(val))
        return stars

    # 显示列
    display_cols = {
        "gene_name": "基因",
        "chromosome": "染色体",
        "position": "位置",
        "clinvar_significance": "临床意义",
        "clinvar_review_status": "评审状态",
    }

    # 构造显示 DataFrame
    display_df = pd.DataFrame()
    for col_key, col_name in display_cols.items():
        if col_key in df.columns:
            display_df[col_name] = df[col_key]

    # 评审状态转星级
    if "评审状态" in display_df.columns:
        display_df["评审状态"] = display_df["评审状态"].apply(_format_review_status)

    # 应用颜色
    styled = display_df.style.map(
        _color_clnsig, subset=["临床意义"] if "临床意义" in display_df.columns else []
    )

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "位置": st.column_config.NumberColumn(format="%d"),
        },
    )

    # 展开详情
    with st.expander("🔍 点击展开变异详细信息"):
        for i, v in enumerate(variants[:20]):  # 最多显示前 20 条详情
            with st.container():
                cols = st.columns([1, 1, 1, 1])
                cols[0].metric("染色体", v.get("chromosome", "-"))
                cols[1].metric("位置", v.get("position", "-"))
                cols[2].metric("基因", v.get("gene_name", "-"))
                cols[3].metric("风险评分", f"{v.get('risk_score', 0):.3f}")

                st.caption(
                    f"rsID: {v.get('rs_id', '-')} | "
                    f"人群频率: {v.get('population_frequency', '-')}"
                )
                st.divider()
