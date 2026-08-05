# =============================================================================
# engine/report_generator.py — 报告生成模块
# =============================================================================
#
# 支持格式：
#   - HTML：单文件自包含，内联 CSS/JS（可在浏览器直接打开）
#   - PDF：使用 reportlab（需要安装，当前为基础实现）
#
# 报告结构（对齐 requirements.md §4.8）：
#   1. 封面（用户信息、报告时间）
#   2. 基因档案摘要
#   3. 健康维度评估
#   4. G×E 模拟结果（轨迹图）
#   5. 个性化建议清单
#   6. 免责声明页（含水印）
#
# 设计约束：
#   - 每页包含 "非临床诊断用途" 水印
#   - 明确标注生成日期
#   - AI 生成内容透明标注
# =============================================================================
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── 模板目录 ──
_TEMPLATE_DIR = Path(__file__).parent / "templates"


# =============================================================================
# 1. 主入口
# =============================================================================

def generate_html(
    report_data: dict[str, Any],
) -> str:
    """生成 HTML 报告字符串 —— 协作接口（对齐 design.md §7.3）。

    参数:
        report_data: {
            "user": {...},
            "genetic_profile": {...},
            "simulation_result": {...},
            "recommendations": [...],
            "ai_interpretation": {...},
            "report_id": str,
            "generated_at": str,
        }

    返回: 完整的 HTML 文档字符串
    """
    now = _now_iso()

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>基因健康分析报告 — GenoLife AI</title>
<style>
  /* ===== 基础重置 ===== */
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
    line-height: 1.6; color: #1a1a2e; background: #f5f5f7;
    max-width: 900px; margin: 0 auto; padding: 20px;
  }}
  /* ===== 水印（所有页面） ===== */
  body::after {{
    content: "⚠ 非临床诊断用途 | 仅供学习参考 | 不替代专业医疗建议";
    position: fixed; top: 50%; left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 48px; color: rgba(0,0,0,0.03); white-space: nowrap;
    pointer-events: none; z-index: 9999;
  }}
  /* ===== 区块样式 ===== */
  .report-container {{ position: relative; z-index: 1; }}
  .section {{
    background: white; border-radius: 12px; padding: 32px;
    margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    page-break-inside: avoid;
  }}
  .section-title {{
    font-size: 20px; font-weight: 700; color: #2563eb;
    margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #e5e7eb;
    display: flex; align-items: center; gap: 8px;
  }}
  .section-title .icon {{ font-size: 24px; }}
  /* ===== 封面 ===== */
  .cover {{
    text-align: center; padding: 60px 32px;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white; border-radius: 12px; margin-bottom: 24px;
  }}
  .cover h1 {{ font-size: 32px; font-weight: 800; margin-bottom: 12px; }}
  .cover .subtitle {{ font-size: 16px; opacity: 0.9; }}
  .cover .meta {{ font-size: 14px; opacity: 0.7; margin-top: 24px; }}
  /* ===== 评分卡片 ===== */
  .score-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }}
  .score-card {{
    background: #f9fafb; border-radius: 8px; padding: 16px; text-align: center;
    border-left: 4px solid #2563eb;
  }}
  .score-card.high {{ border-left-color: #ef4444; }}
  .score-card.low {{ border-left-color: #10b981; }}
  .score-card .score-value {{ font-size: 28px; font-weight: 800; color: #111827; }}
  .score-card .score-label {{ font-size: 13px; color: #6b7280; margin-top: 4px; }}
  .score-card .score-level {{ font-size: 12px; margin-top: 4px; }}
  /* ===== 轨迹表格 ===== */
  .trajectory-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
  .trajectory-table th, .trajectory-table td {{
    padding: 10px 16px; text-align: center; border-bottom: 1px solid #e5e7eb;
  }}
  .trajectory-table th {{ background: #f9fafb; font-weight: 600; font-size: 13px; color: #6b7280; }}
  .trajectory-table td {{ font-size: 15px; }}
  /* ===== 建议列表 ===== */
  .rec-list {{ list-style: none; }}
  .rec-item {{
    display: flex; gap: 12px; padding: 16px; border-radius: 8px;
    margin-bottom: 12px; background: #f9fafb;
  }}
  .rec-item .rec-icon {{ font-size: 28px; flex-shrink: 0; }}
  .rec-item .rec-content {{ flex: 1; }}
  .rec-item .rec-title {{ font-weight: 600; margin-bottom: 4px; }}
  .rec-item .rec-desc {{ font-size: 14px; color: #4b5563; }}
  .rec-item .rec-meta {{ font-size: 12px; color: #9ca3af; margin-top: 6px; }}
  .difficulty-badge {{
    display: inline-block; padding: 2px 8px; border-radius: 12px;
    font-size: 11px; font-weight: 600;
  }}
  .difficulty-easy {{ background: #d1fae5; color: #065f46; }}
  .difficulty-moderate {{ background: #fef3c7; color: #92400e; }}
  .difficulty-hard {{ background: #fee2e2; color: #991b1b; }}
  /* ===== 免责声明 ===== */
  .disclaimer {{
    background: #fef3c7; border: 1px solid #fcd34d; border-radius: 8px;
    padding: 20px; font-size: 13px; color: #92400e;
  }}
  .disclaimer h3 {{ font-size: 16px; margin-bottom: 8px; }}
  .ai-badge {{
    display: inline-block; background: #dbeafe; color: #1e40af;
    padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;
  }}
  /* ===== 打印样式 ===== */
  @media print {{
    body {{ background: white; padding: 0; max-width: none; }}
    .section {{ box-shadow: none; border: 1px solid #e5e7eb; }}
    body::after {{ font-size: 36px; }}
  }}
</style>
</head>
<body>
<div class="report-container">

  <!-- ════ 封面 ════ -->
  <div class="cover">
    <h1>🧬 基因健康分析报告</h1>
    <div class="subtitle">GenoLife AI — Gene × Environment Health Report</div>
    <div class="meta">
      报告编号：{report_data.get("report_id", "N/A")}<br>
      生成时间：{now}<br>
      分析引擎版本：v1.0.0
    </div>
  </div>

  <!-- ════ 第1部分：基因档案摘要 ════ -->
  <div class="section">
    <div class="section-title"><span class="icon">📋</span> 基因档案摘要</div>
    {_render_genetic_profile(report_data.get("genetic_profile", {}))}
    <div class="ai-badge">🤖 AI 辅助分析</div>
  </div>

  <!-- ════ 第2部分：健康评分概览 ════ -->
  <div class="section">
    <div class="section-title"><span class="icon">📊</span> 健康评分概览</div>
    {_render_score_overview(report_data)}
    <div class="ai-badge" style="background:#fef3c7;color:#92400e;">⚠️ 统计估算 — 非临床诊断</div>
  </div>

  <!-- ════ 第3部分：健康轨迹 ════ -->
  <div class="section">
    <div class="section-title"><span class="icon">📈</span> G×E 健康轨迹预测</div>
    {_render_trajectory(report_data.get("simulation_result", {}))}
    <p style="font-size:12px;color:#9ca3af;margin-top:12px;">
      * 轨迹为基于群体统计模型的趋势估计，不代表个体确定性预测。
      置信区间随预测时间增长而扩大。
    </p>
    <div class="ai-badge" style="background:#fef3c7;color:#92400e;">⚠️ 统计估算 — 含置信区间</div>
  </div>

  <!-- ════ 第4部分：维度评分 ════ -->
  <div class="section">
    <div class="section-title"><span class="icon">🎯</span> 健康维度评分</div>
    {_render_dimension_scores(report_data.get("simulation_result", {}))}
  </div>

  <!-- ════ 第5部分：个性化建议 ════ -->
  <div class="section">
    <div class="section-title"><span class="icon">💡</span> 个性化生活方式建议</div>
    {_render_recommendations(report_data.get("recommendations", []))}
    <div class="ai-badge" style="background:#d1fae5;color:#065f46;">📋 AI 生成建议</div>
  </div>

  <!-- ════ 第6部分：AI 解读 ════ -->
  <div class="section">
    <div class="section-title"><span class="icon">🔬</span> AI 科学解读</div>
    {_render_ai_interpretation(report_data.get("ai_interpretation", {}))}
    <div class="ai-badge">🤖 AI 辅助解读</div>
  </div>

  <!-- ════ 免责声明 ════ -->
  <div class="section disclaimer">
    {_render_disclaimer()}
  </div>

</div>
</body>
</html>"""


def generate_pdf(report_data: dict[str, Any]) -> bytes:
    """生成 PDF 报告字节流 —— 协作接口。

    当前为基础实现（使用 reportlab）。
    如需完整 PDF，请安装 reportlab 并在 requirements.txt 中取消注释。
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

        from io import BytesIO

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        # 中文字体支持（需要系统中文字体）
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            # 尝试注册系统自带中文字体
            import platform
            if platform.system() == "Darwin":
                font_paths = [
                    "/System/Library/Fonts/PingFang.ttc",
                    "/System/Library/Fonts/STHeiti Light.ttc",
                ]
            else:
                font_paths = []
            for fp in font_paths:
                if Path(fp).exists():
                    pdfmetrics.registerFont(TTFont("ChineseFont", fp))
                    styles["Normal"].fontName = "ChineseFont"
                    break
        except Exception:
            pass  # 回退到默认字体

        story = []

        # 标题
        story.append(Paragraph("基因健康分析报告 — GenoLife AI", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"生成时间：{_now_iso()}", styles["Normal"]))
        story.append(Spacer(1, 24))

        # 免责声明
        story.append(Paragraph("⚠ 非临床诊断用途 | 仅供学习参考 | 不替代专业医疗建议", styles["Normal"]))
        story.append(Spacer(1, 12))

        # 简易内容
        sim = report_data.get("simulation_result", {})
        story.append(Paragraph(f"健康基线评分：{sim.get('baseline_score', 'N/A')}", styles["Normal"]))

        recs = report_data.get("recommendations", [])
        story.append(Paragraph(f"个性化建议：{len(recs)} 条", styles["Normal"]))

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        # reportlab 未安装时返回 HTML 转 PDF 的方案不可用
        # 返回说明性字节流
        msg = (
            "PDF 生成需要 reportlab 库。\n"
            "请在 requirements.txt 中取消注释 reportlab。\n"
            "当前请使用 HTML 格式导出报告。\n"
        )
        return msg.encode("utf-8")


# =============================================================================
# 2. 各部分渲染函数
# =============================================================================

def _render_genetic_profile(profile: dict) -> str:
    """渲染基因档案摘要。"""
    if not profile:
        return "<p>暂无基因数据</p>"

    genes = []
    for gene, risk in profile.items():
        if isinstance(risk, (int, float)):
            risk_text = "风险相关" if risk > 0.5 else "保护型或中等"
            genes.append(f"<tr><td><strong>{gene}</strong></td><td>{risk:.1f}</td><td>{risk_text}</td></tr>")

    return f"""<table class="trajectory-table">
      <tr><th>基因</th><th>风险值 (0-1)</th><th>分类</th></tr>
      {"".join(genes) if genes else '<tr><td colspan="3">暂无数据</td></tr>'}
    </table>"""


def _render_score_overview(data: dict) -> str:
    """渲染健康评分概览。"""
    sim = data.get("simulation_result", {})
    baseline = sim.get("baseline_score", 72)
    gene_eff = sim.get("gene_effect_total", 0)
    env_eff = sim.get("environment_effect_total", 0)
    inter_eff = sim.get("interaction_effect_total", 0)

    level = "健康优势" if baseline >= 85 else "中等偏上" if baseline >= 70 else "中等" if baseline >= 55 else "需关注"

    return f"""<div class="score-grid">
      <div class="score-card {_score_card_class(baseline)}">
        <div class="score-value">{baseline}</div>
        <div class="score-label">综合健康评分 / 100</div>
        <div class="score-level">{level}</div>
      </div>
      <div class="score-card">
        <div class="score-value">{gene_eff:+.1f}</div>
        <div class="score-label">基因贡献</div>
      </div>
      <div class="score-card">
        <div class="score-value">{env_eff:+.1f}</div>
        <div class="score-label">环境贡献</div>
      </div>
      <div class="score-card">
        <div class="score-value">{inter_eff:+.1f}</div>
        <div class="score-label">G×E 交互贡献</div>
      </div>
    </div>"""


def _render_trajectory(sim: dict) -> str:
    """渲染健康轨迹表格。"""
    trajectory = sim.get("trajectory", [])
    if not trajectory:
        return "<p>暂无轨迹数据</p>"

    rows = []
    for t in trajectory:
        rows.append(
            f"<tr><td>{t['year']} 年</td>"
            f"<td><strong>{t['score']}</strong></td>"
            f"<td>{t.get('level', '-')}</td>"
            f"<td>[{t.get('confidence', [0,0])[0]}, {t.get('confidence', [0,0])[1]}]</td></tr>"
        )

    return f"""<table class="trajectory-table">
      <tr><th>时间节点</th><th>预测评分</th><th>健康等级</th><th>置信区间</th></tr>
      {"".join(rows)}
    </table>"""


def _render_dimension_scores(sim: dict) -> str:
    """渲染健康维度评分。"""
    dims = sim.get("dimension_scores", {})
    if not dims:
        return "<p>暂无维度数据</p>"

    cards = []
    for key, dim in dims.items():
        if isinstance(dim, dict):
            cards.append(
                f'<div class="score-card {_score_card_class(dim.get("score", 50))}">'
                f'<div style="font-size:24px">{dim.get("icon", "")}</div>'
                f'<div class="score-value">{dim.get("score", "-")}</div>'
                f'<div class="score-label">{dim.get("label", key)}</div>'
                f'<div class="score-level">{dim.get("level", "")}</div>'
                f"</div>"
            )

    return f'<div class="score-grid">{"".join(cards)}</div>'


def _render_recommendations(recs: list) -> str:
    """渲染建议列表。"""
    if not recs:
        return "<p>暂无建议</p>"

    items = []
    for r in recs:
        priority = r.get("priority", 0)
        stars = "⭐" * r.get("impact", 3)
        diff = r.get("difficulty", "moderate")
        evidence = r.get("evidence_level", "moderate")
        items.append(
            f'<li class="rec-item">'
            f'<div class="rec-icon">{r.get("icon", "🎯")}</div>'
            f'<div class="rec-content">'
            f'<div class="rec-title">{r.get("title", "")}</div>'
            f'<div class="rec-desc">{r.get("description", "")}</div>'
            f'<div class="rec-meta">'
            f'优先级: {priority} | {stars} | 证据: {evidence} | '
            f'<span class="difficulty-badge difficulty-{diff}">{diff}</span> | '
            f'⏱ {r.get("time", "")}'
            f'</div>'
            f'</div>'
            f'</li>'
        )

    return f'<ul class="rec-list">{"".join(items)}</ul>'


def _render_ai_interpretation(interp: dict) -> str:
    """渲染 AI 解读。"""
    if not interp:
        return "<p>暂无 AI 解读</p>"

    scientific = interp.get("scientific_summary", "")
    simple = interp.get("simple_explanation", "")
    evidence = interp.get("evidence", "")

    return f"""
    <div style="margin-bottom:16px;">
      <h4 style="color:#2563eb;">🔬 科学概述</h4>
      <p>{scientific}</p>
    </div>
    <div style="margin-bottom:16px;">
      <h4 style="color:#10b981;">💬 通俗解释</h4>
      <p>{simple}</p>
    </div>
    <div>
      <h4 style="color:#6b7280;">📚 支撑证据</h4>
      <p style="font-size:13px;color:#6b7280;">{evidence}</p>
    </div>
    """


def _render_disclaimer() -> str:
    """渲染免责声明。"""
    return f"""
    <h3>⚠️ 重要免责声明</h3>
    <p><strong>本报告由 GenoLife AI v1.0 自动生成</strong></p>
    <p>生成日期：{_now_iso()}</p>
    <p>⚠️ 非临床诊断用途 | 仅供学习参考 | 不替代专业医疗建议</p>
    <p>AI 模型版本：v1.0-mock | 数据库版本：Gene Database 2026-08</p>
    <hr style="margin:12px 0;border-color:#fcd34d;">
    <ul style="margin-left:20px;">
      <li>本产品为教育研究型项目，<strong>不构成医疗器械</strong></li>
      <li>所有 AI 生成的基因解读仅供学习参考</li>
      <li>不得将本平台信息作为医疗决策依据</li>
      <li>如有健康疑虑，请咨询具备资质的医疗专业人员</li>
      <li>基因风险评分仅为统计估算，个体结果可能存在较大差异</li>
      <li>当前基因参考数据主要基于东亚和欧洲人群研究</li>
    </ul>
    """


# =============================================================================
# 3. 便捷函数 — 一键生成完整报告数据
# =============================================================================

def build_report_data(
    report_id: str,
    genetic_profile: dict[str, float],
    environment: dict[str, float],
    simulation_result: dict[str, Any],
    recommendations: list[dict],
    ai_interpretation: dict | None = None,
) -> dict[str, Any]:
    """组装完整的报告数据字典。"""
    return {
        "report_id": report_id,
        "genetic_profile": genetic_profile,
        "environment": environment,
        "simulation_result": simulation_result,
        "recommendations": recommendations,
        "ai_interpretation": ai_interpretation or {},
        "generated_at": _now_iso(),
    }


# =============================================================================
# 4. 工具函数
# =============================================================================

def _score_card_class(score: int) -> str:
    """根据评分返回 CSS 类。"""
    if score >= 85:
        return "low"
    elif score <= 40:
        return "high"
    return ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# =============================================================================
# 5. 独立运行示例
# =============================================================================

if __name__ == "__main__":
    from engine.gxe_model import simulate_health_trajectory
    from engine.recommendation_engine import generate_from_simulation
    from engine.ai_interpreter import interpret_simulation_result

    print("=" * 70)
    print("报告生成器 — 测试示例")
    print("=" * 70)

    genetic = {"APOE": 0.7, "FTO": 0.5, "CLOCK": 0.3, "ACTN3": 0.4}
    env = {"exercise": 5, "sleep": 6, "diet": 5, "stress": 5, "smoking": 2}

    sim = simulate_health_trajectory(genetic, env)
    recs = generate_from_simulation(sim, genetic)
    interpretation = interpret_simulation_result(sim, genetic, env)

    report_data = build_report_data(
        report_id="rpt_demo_001",
        genetic_profile=genetic,
        environment=env,
        simulation_result=sim,
        recommendations=recs,
        ai_interpretation=interpretation,
    )

    html = generate_html(report_data)

    # 保存到文件
    out_path = Path(__file__).parent.parent / "output" / "demo_report.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"\n✅ HTML 报告已生成: {out_path}")
    print(f"   文件大小: {len(html):,} 字节")

    # PDF 测试
    pdf = generate_pdf(report_data)
    print(f"   PDF 状态: {'生成成功' if len(pdf) > 200 else '基础文本模式（需安装 reportlab）'}")

    print(f"\n{'=' * 70}")
    print("✅ 报告生成器测试完成")
    print(f"{'=' * 70}")
