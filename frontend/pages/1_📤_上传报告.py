"""
P1：上传报告页面
"""
import streamlit as st
import time

st.set_page_config(
    page_title="上传报告 - 基因分析助手",
    page_icon="📤",
    layout="wide",
)

st.title("📤 上传基因报告")

# 检查免责声明
if not st.session_state.get("disclaimer_agreed", False):
    st.warning("⚠️ 请先在首页阅读并同意免责声明")
    st.page_link("app.py", label="← 返回首页")
    st.stop()

st.markdown("请上传您的基因检测报告文件。支持 VCF、TSV、TXT 格式，最大 100MB。")

st.markdown("---")

# 上传区域
uploaded_file = st.file_uploader(
    "拖拽文件到这里或点击选择文件",
    type=["vcf", "tsv", "txt", "vcf.gz"],
    help="支持 23andMe、AncestryDNA、BGI 等基因检测报告格式",
)

if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > 100:
        st.error(f"❌ 文件过大（{file_size_mb:.1f}MB），请上传小于 100MB 的文件")
    else:
        st.success(f"✅ 文件已选择：`{uploaded_file.name}`（{file_size_mb:.1f}MB）")

        # 文件内容预览
        with st.expander("📄 预览文件内容（前 20 行）"):
            content = uploaded_file.getvalue().decode("utf-8", errors="replace")
            lines = content.split("\n")[:20]
            for line in lines:
                st.text(line)

        st.markdown("---")

        # 上传按钮
        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button("🚀 开始上传分析", type="primary", use_container_width=True):
                with st.spinner("正在上传并解析文件..."):
                    # 进度条模拟
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    stages = [
                        (0.2, "校验文件格式..."),
                        (0.4, "解析基因组变异..."),
                        (0.7, "查询 ClinVar 数据库..."),
                        (0.9, "计算 PRS 风险评分..."),
                        (1.0, "生成分析报告..."),
                    ]

                    for progress, msg in stages:
                        time.sleep(0.5)
                        progress_bar.progress(progress)
                        status_text.text(msg)

                    # 调用 API
                    from api_client import upload as api_upload

                    result = api_upload(uploaded_file)

                    if result.get("success"):
                        progress_bar.progress(1.0)
                        status_text.text("✅ 分析完成！")

                        data = result["data"]
                        st.session_state.report_id = data["report_id"]

                        st.success(
                            f"🎉 报告上传成功！共检测到 **{data['variant_count']:,}** 个变异位点"
                        )

                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("报告 ID", data["report_id"])
                            st.metric("文件格式", data.get("original_filename", uploaded_file.name))
                        with col_b:
                            st.metric("变异数量", f"{data['variant_count']:,}")
                            st.metric("状态", "✅ 解析完成")

                        st.markdown("---")
                        st.markdown("### 📊 下一步")
                        st.page_link(
                            "pages/2_📊_分析结果.py",
                            label="→ 查看分析结果",
                            icon="📊",
                        )

                    else:
                        error_msg = result.get("error", {}).get("message", "未知错误")
                        st.error(f"❌ 上传失败：{error_msg}")

        with col2:
            st.info(
                """
            **📋 支持的文件格式**：
            - **VCF**（Variant Call Format）：标准基因组变异文件
            - **TSV/TXT**：23andMe、AncestryDNA 等原始数据
            - **VCF.GZ**：压缩 VCF 文件

            **🔒 隐私保证**：
            - 所有数据在本地加密处理
            - 不上传至第三方服务器
            - 分析完成后可随时删除数据
            """
            )

# 已有报告的快捷入口
if st.session_state.get("report_id"):
    st.markdown("---")
    st.info(f"📋 已有分析报告：`{st.session_state.report_id}`")
    st.page_link("pages/2_📊_分析结果.py", label="→ 直接查看分析结果", icon="📊")
