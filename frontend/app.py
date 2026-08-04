"""
基因分析助手 — 主入口
"""
import streamlit as st

st.set_page_config(
    page_title="基因分析助手",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 免责声明同意状态
if "disclaimer_agreed" not in st.session_state:
    st.session_state.disclaimer_agreed = False

# 报告 ID（上传后获得）
if "report_id" not in st.session_state:
    st.session_state.report_id = None

# 已保存的场景列表
if "saved_scenarios" not in st.session_state:
    st.session_state.saved_scenarios = []

# 建议进度跟踪
if "recommendation_progress" not in st.session_state:
    st.session_state.recommendation_progress = {}

# ============================================================
# 主页面
# ============================================================

st.title("🧬 基因分析助手")
st.caption("Gene Analysis Assistant — 教育研究型基因数据可视化工具")

st.markdown("---")

# 免责声明横幅
from components.disclaimer import render_disclaimer

if not st.session_state.disclaimer_agreed:
    render_disclaimer()
    st.stop()

# 侧边栏导航
st.sidebar.title("📋 导航")
st.sidebar.markdown("---")

pages = {
    "📤 上传报告": "pages/1_📤_上传报告.py",
    "📊 分析结果": "pages/2_📊_分析结果.py",
    # Day 2 添加：
    # "🧬 健康模拟": "pages/3_🧬_健康模拟.py",
    # "💡 生活建议": "pages/4_💡_生活建议.py",
    # "📄 报告导出": "pages/5_📄_报告导出.py",
}

st.sidebar.markdown("### 功能页面")
for label, path in pages.items():
    st.sidebar.page_link(path, label=label)

st.sidebar.markdown("---")
if st.session_state.report_id:
    st.sidebar.info(f"📋 当前报告：`{st.session_state.report_id}`")
else:
    st.sidebar.warning("⚠️ 尚未上传报告")

# 欢迎页
st.markdown("""
### 👋 欢迎使用基因分析助手

本平台为**教育研究型项目**，提供以下功能：

| 功能 | 说明 |
|------|------|
| 📤 **上传报告** | 上传您的基因检测报告文件（VCF/TSV 格式） |
| 📊 **分析结果** | 查看变异列表、ClinVar 注释、综合风险评估 |
| 🧬 **健康模拟** | 调整环境因素，模拟基因-环境交互对健康的影响 |
| 💡 **生活建议** | 基于基因风险档案的个性化生活方式建议 |
| 📄 **报告导出** | 导出 PDF / HTML 格式的综合分析报告 |

---
**⚠️ 请从左上方侧边栏选择"📤 上传报告"开始。**
""")
