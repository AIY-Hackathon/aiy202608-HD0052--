"""
P2：分析结果仪表板

展示变异列表、ClinVar 注释、风险评分
"""
import streamlit as st
from components.variant_table import render as render_variant_table
from components.risk_chart import (
    render_variant_distribution,
    render_risk_metrics,
    render_risk_radar,
)
from components.ai_badge import render as render_ai_badge

st.set_page_config(
    page_title="分析结果 - 基因分析助手",
    page_icon="📊",
    layout="wide",
)

st.title("📊 分析结果仪表板")

# 检查
if not st.session_state.get("disclaimer_agreed", False):
    st.warning("⚠️ 请先在首页阅读并同意免责声明")
    st.page_link("app.py", label="← 返回首页")
    st.stop()

if not st.session_state.get("report_id"):
    st.info("📤 请先上传基因报告文件")
    st.page_link("pages/1_📤_上传报告.py", label="→ 前往上传页面")
    st.stop()

report_id = st.session_state.report_id

# 获取分析数据
from api_client import get_analysis

with st.spinner("正在加载分析结果..."):
    result = get_analysis(report_id)

if not result.get("success"):
    st.error(f"❌ 获取分析结果失败：{result.get('error', {}).get('message', '未知错误')}")
    st.stop()

data = result["data"]
variants = data.get("variants", [])
risk_scores = data.get("risk_scores", {})
overall_risk = sum(risk_scores.values()) / len(risk_scores) if risk_scores else 0

# 统计
pathogenic_count = sum(
    1 for v in variants if "Pathogenic" in str(v.get("clinvar_significance", ""))
)

# ============================================================
# 顶部指标卡片
# ============================================================
st.markdown("### 📈 风险概览")
render_risk_metrics(len(variants), pathogenic_count, overall_risk)

st.markdown("---")

# ============================================================
# 双列布局：雷达图 + 柱状图
# ============================================================
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("#### 🎯 疾病风险评分")
    render_risk_radar(risk_scores)

with col_chart2:
    st.markdown("#### 🧬 染色体变异分布")
    render_variant_distribution(variants)

st.markdown("---")

# ============================================================
# 变异表格
# ============================================================
st.markdown("### 🔬 变异详情列表")
st.caption("按 CLNSIG 颜色编码：🔴 致病性 | 🟢 良性 | ⚪ 意义不明 | 🟡 解读冲突")

# 筛选器
with st.expander("🔍 筛选与搜索"):
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        significance_filter = st.multiselect(
            "临床意义",
            options=["Pathogenic", "Benign", "Uncertain significance", "Conflicting interpretations"],
            default=[],
        )

    with col_filter2:
        genes = sorted(set(v.get("gene_name", "") for v in variants if v.get("gene_name")))
        gene_filter = st.multiselect("基因", options=genes, default=[])

    with col_filter3:
        chrom_filter = st.multiselect(
            "染色体",
            options=sorted(set(str(v.get("chromosome", "")) for v in variants)),
            default=[],
        )

# 应用筛选
filtered_variants = variants
if significance_filter:
    filtered_variants = [
        v
        for v in filtered_variants
        if any(s in str(v.get("clinvar_significance", "")) for s in significance_filter)
    ]
if gene_filter:
    filtered_variants = [
        v for v in filtered_variants if v.get("gene_name") in gene_filter
    ]
if chrom_filter:
    filtered_variants = [
        v for v in filtered_variants if str(v.get("chromosome")) in chrom_filter
    ]

st.caption(f"共 {len(filtered_variants)} 条变异记录（总数：{len(variants)}）")
render_variant_table(filtered_variants)

st.markdown("---")

# ============================================================
# AI 解读（Mock）
# ============================================================
st.markdown("### 🤖 AI 辅助解读")

render_ai_badge(
    "解读",
    "本解读由 AI 模型生成，仅供参考，不构成临床诊断。请咨询具备资质的遗传咨询师或医生获取专业建议。",
)

st.markdown(
    """
根据上传的基因报告分析，该个体的基因风险档案显示：

**主要发现**：
- **BRCA1/BRCA2**：检测到致病性变异，乳腺癌和卵巢癌风险高于一般人群
- **CFTR**：携带致病变异（rs113993960），与囊性纤维化相关
- **APOE ε4**：携带一个 ε4 等位基因（rs429358），阿尔茨海默病风险轻度升高
- **MTHFR**：良性变异（rs1801133），无临床影响

**综合风险评估**：🟡 **中等风险**（综合评分：{:.2f}）

> ⚠️ 本解读由 AI 模型自动生成，仅供学习参考。请咨询具备资质的遗传咨询师或医生获取专业建议。
>
> 数据来源：ClinVar ID: SCV000123456, OMIM #219700
""".format(overall_risk)
)

st.markdown("---")

# 导航
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    st.page_link("pages/1_📤_上传报告.py", label="← 重新上传", icon="📤")
with col_nav2:
    st.page_link("pages/3_🧬_健康模拟.py", label="健康模拟 →", icon="🧬")
