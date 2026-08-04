"""
FDA 免责声明横幅组件
"""
import streamlit as st


def render_disclaimer():
    """显示 FDA 免责声明横幅，需要用户点击同意后进入"""

    st.markdown(
        """
    <style>
    .disclaimer-box {
        border: 2px solid #F59E0B;
        border-radius: 12px;
        padding: 24px;
        background: #FFFBEB;
        margin: 20px 0;
    }
    .disclaimer-box h3 {
        color: #D97706;
        margin-top: 0;
    }
    .disclaimer-box ul {
        color: #92400E;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="disclaimer-box">
        <h3>⚠️ 重要免责声明</h3>
        <p><strong>本平台为教育研究型项目，不构成医疗器械，不提供临床诊断。</strong></p>
        <ul>
            <li>所有 AI 生成的基因解读仅供学习参考</li>
            <li>不得将本平台信息作为医疗决策依据</li>
            <li>如有健康疑虑，请咨询具备资质的医疗专业人员</li>
            <li>本平台不向医疗机构或保险公司提供数据</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        if st.button("✅ 同意并继续", type="primary", use_container_width=True):
            st.session_state.disclaimer_agreed = True
            st.rerun()

    with col2:
        if st.button("📖 了解更多", use_container_width=True):
            with st.expander("📖 关于本平台", expanded=True):
                st.markdown(
                    """
                **本产品定位**

                基因分析助手（Gene Analysis Assistant）是一个教育研究型基因数据可视化工具。

                **参考标准**
                - ACMG/AMP 变异解读指南（2015 版）
                - FDA PCCP 最终指南（2024.12）
                - FDA AI 生命周期指南草案（2025.1）

                **数据来源**
                - ClinVar（NCBI 公共数据库）
                - OMIM（约翰霍普金斯大学）
                - PharmGKB（Stanford/NIH）
                - 1000 Genomes（IGSR / CNGBdb 镜像）
                """
                )
