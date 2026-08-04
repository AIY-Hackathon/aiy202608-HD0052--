"""
API 客户端 — 统一封装后端 API 调用

后端就绪后将 USE_MOCK 改为 False 即可切换为真实 API。
"""
import streamlit as st
from mock_data import (
    MOCK_UPLOAD_RESPONSE,
    MOCK_ANALYSIS_RESULT,
    MOCK_SIMULATION_RESULT,
    MOCK_RECOMMENDATIONS,
)

API_BASE = "http://localhost:8000/api"
USE_MOCK = True


def upload(file) -> dict:
    """上传基因报告文件"""
    if USE_MOCK:
        import time
        time.sleep(1.5)  # 模拟上传延迟
        return MOCK_UPLOAD_RESPONSE

    import requests
    r = requests.post(f"{API_BASE}/upload", files={"file": file})
    return r.json()


def get_analysis(report_id: str) -> dict:
    """获取分析结果"""
    if USE_MOCK:
        import time
        time.sleep(0.8)  # 模拟查询延迟
        return MOCK_ANALYSIS_RESULT

    import requests
    r = requests.get(f"{API_BASE}/analysis/{report_id}")
    return r.json()


def simulate(report_id: str, environmental_factors: dict) -> dict:
    """运行健康模拟"""
    if USE_MOCK:
        import time
        time.sleep(1.0)
        return MOCK_SIMULATION_RESULT

    import requests
    r = requests.post(
        f"{API_BASE}/simulate",
        json={"report_id": report_id, "environmental_factors": environmental_factors},
    )
    return r.json()


def get_recommendations(report_id: str, preferences: dict | None = None) -> dict:
    """获取个性化建议"""
    if USE_MOCK:
        import time
        time.sleep(0.6)
        return {
            "success": True,
            "data": {"recommendations": MOCK_RECOMMENDATIONS},
            "error": None,
        }

    import requests
    r = requests.post(
        f"{API_BASE}/recommendations",
        json={"report_id": report_id, "preferences": preferences or {}},
    )
    return r.json()


def export_report(report_id: str, format: str = "html") -> bytes | str:
    """导出报告"""
    if USE_MOCK:
        return "<html><body><h1>Mock 报告</h1><p>后端就绪后将生成真实报告。</p></body></html>"

    import requests
    r = requests.get(f"{API_BASE}/report/{report_id}/export", params={"format": format})
    return r.content if format == "pdf" else r.text
