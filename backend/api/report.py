"""
GET /api/report/{report_id}/export — 报告导出
==============================================
从数据库读取分析结果，生成 HTML/PDF 报告。

自包含实现（不依赖外部引擎文件）：
  1. 从数据库读取报告及其变异
  2. 调用 prs_calculator 科学分析（关键基因/维度/建议）
  3. 生成 HTML 报告（含免责声明水印）
  4. 可选 PDF 导出（reportlab）

关联需求：R8.1 / R8.2 / R8.4 / R8.6
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, Response

from backend.services import prs_calculator as engine

router = APIRouter(prefix="/api", tags=["report"])


def _load_report_data(report_id: str):
    """从数据库加载报告及其变异。"""
    from backend.database import SessionLocal
    from backend.models import GeneticReport, GeneticVariant
    from sqlalchemy import select

    async def _query():
        async with SessionLocal() as session:
            report = await session.get(GeneticReport, report_id)
            if not report:
                return None, []
            result = await session.execute(
                select(GeneticVariant).where(GeneticVariant.report_id == report_id)
            )
            variants = result.scalars().all()
            return report, variants

    return asyncio.run(_query())


def _variants_to_dicts(variants) -> list[dict]:
    """ORM 变异对象 → 字典。"""
    return [
        {
            "chromosome": v.chromosome,
            "position": v.position,
            "gene_name": v.gene_name,
            "clinvar_significance": v.clinvar_significance,
            "odds_ratio": v.odds_ratio,
            "risk_score": v.risk_score,
            "rs_id": v.rs_id,
        }
        for v in variants
    ]


def _generate_html(report_id: str, filename: str, variants: list[dict]) -> str:
    """生成 HTML 报告（自包含）。"""
    # 科学分析
    scientific = engine.generate_scientific_analysis(variants)
    key_genes = scientific.get("key_genes", [])
    dims = engine.calculate_dimension_scores(variants)
    recs = engine.generate_recommendations({})
    plan = engine.generate_thirty_day_plan()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # 基因卡片行
    gene_rows = ""
    for g in key_genes:
        risk_color = "red" if g["risk_level"] in ("elevated", "high") else (
            "orange" if g["risk_level"] == "moderate" else "green")
        gene_rows += f"""
        <div style="background:#f8fafc;border-radius:12px;padding:16px;margin-bottom:12px;border-left:4px solid {risk_color};">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <strong style="font-size:15px;color:#1a1a2e;">{g['symbol']}</strong>
            <span style="font-size:11px;font-weight:700;color:{risk_color};text-transform:uppercase;">{g['risk_level']}</span>
          </div>
          <p style="font-size:12px;color:#4b5563;margin:6px 0 0;line-height:1.6;">{g.get('function','')}</p>
          <p style="font-size:11px;color:#6b7280;margin:4px 0 0;">人群影响：{g.get('population_impact','')}</p>
        </div>"""

    # 维度行
    dim_rows = ""
    for d in dims:
        bar_color = "#dc2626" if d["score"] >= 70 else ("#d97706" if d["score"] >= 55 else "#059669")
        dim_rows += f"""
        <div style="margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;font-size:12px;color:#4b5563;margin-bottom:4px;">
            <span>{d['label']}</span><span>{d['score']}</span>
          </div>
          <div style="background:#e5e7eb;border-radius:4px;height:8px;">
            <div style="background:{bar_color};width:{min(d['score'],100)}%;height:8px;border-radius:4px;"></div>
          </div>
        </div>"""

    # 建议列表
    rec_items = "".join(
        f"<li style='font-size:13px;color:#4b5563;margin-bottom:8px;'>{r.get('title','')}</li>"
        for r in recs[:5]
    ) or "<li style='font-size:13px;color:#6b7280;'>暂无建议</li>"

    # 30 天计划
    plan_weeks = "".join(
        f"<div style='margin-bottom:8px;'><strong style='font-size:13px;color:#1a1a2e;'>{w.get('label','')}</strong>"
        f"<span style='font-size:12px;color:#6b7280;'> — {w.get('theme','')}</span></div>"
        for w in plan.get("weeks", [])[:2]
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>基因健康分析报告 — GenoLife AI</title>
<style>
  body {{ font-family: -apple-system, "Segoe UI", "Noto Sans SC", sans-serif; line-height:1.6; color:#1a1a2e; background:#f5f5f7; max-width:900px; margin:0 auto; padding:24px; }}
  body::after {{ content:"⚠ 非临床诊断用途 | 仅供学习参考 | 不替代专业医疗建议"; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%) rotate(-30deg); font-size:48px; color:rgba(0,0,0,0.03); white-space:nowrap; pointer-events:none; z-index:9999; }}
  .section {{ background:white; border-radius:12px; padding:24px; margin-bottom:20px; box-shadow:0 1px 3px rgba(0,0,0,0.08); page-break-inside:avoid; }}
  .title {{ font-size:20px; font-weight:700; color:#2563eb; margin-bottom:16px; padding-bottom:8px; border-bottom:2px solid #e5e7eb; }}
  .cover {{ text-align:center; padding:40px 24px; background:linear-gradient(135deg,#2563eb,#1d4ed8); color:white; border-radius:12px; margin-bottom:20px; }}
  .cover h1 {{ font-size:28px; margin:0 0 8px; }}
  .cover p {{ opacity:0.85; font-size:14px; margin:0; }}
</style>
</head>
<body>
  <div class="cover">
    <h1>🧬 基因健康分析报告</h1>
    <p>GenoLife AI · {filename}</p>
    <p style="margin-top:12px;font-size:11px;opacity:0.6;">报告编号 {report_id} · 生成于 {now}</p>
  </div>

  <div class="section">
    <div class="title">📊 分析概览</div>
    <div style="display:flex;gap:16px;flex-wrap:wrap;">
      <div style="flex:1;min-width:120px;text-align:center;background:#eff6ff;border-radius:10px;padding:16px;">
        <p style="font-size:28px;font-weight:800;color:#1e3a5f;margin:0;">{scientific.get('polygenic_score',0)}</p>
        <p style="font-size:11px;color:#6b7280;">多基因评分</p>
      </div>
      <div style="flex:1;min-width:120px;text-align:center;background:#f0fdf4;border-radius:10px;padding:16px;">
        <p style="font-size:28px;font-weight:800;color:#059669;margin:0;">{scientific.get('genetic_load','中')}</p>
        <p style="font-size:11px;color:#6b7280;">遗传负荷</p>
      </div>
      <div style="flex:1;min-width:120px;text-align:center;background:#faf5ff;border-radius:10px;padding:16px;">
        <p style="font-size:28px;font-weight:800;color:#7c3aed;margin:0;">{len(key_genes)}</p>
        <p style="font-size:11px;color:#6b7280;">关键基因</p>
      </div>
    </div>
    <p style="font-size:14px;color:#4b5563;margin:16px 0 0;padding:12px;background:#f9fafb;border-radius:8px;">
      {scientific.get('summary','')}
    </p>
  </div>

  <div class="section">
    <div class="title">🧬 关键基因分析</div>
    {gene_rows or "<p style='font-size:13px;color:#6b7280;'>未识别到显著关键基因。</p>"}
  </div>

  <div class="section">
    <div class="title">📈 健康维度评分</div>
    {dim_rows}
  </div>

  <div class="section">
    <div class="title">💡 个性化建议</div>
    <ul style="padding-left:20px;">{rec_items}</ul>
  </div>

  <div class="section">
    <div class="title">📅 30 天健康计划</div>
    {plan_weeks}
  </div>

  <div style="text-align:center;font-size:11px;color:#9ca3af;padding:16px;">
    GenoLife AI © 2026 · 教育研究用途 · 报告生成于 {now}
  </div>
</body>
</html>"""


@router.get("/report/{report_id}/export", response_class=Response)
def export_report(
    report_id: str,
    format: str = Query("html", pattern="^(html|pdf)$"),
):
    """导出基因健康报告（HTML 或 PDF）。"""
    report, variants = _load_report_data(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"报告 {report_id} 不存在")

    variant_dicts = _variants_to_dicts(variants)

    try:
        html = _generate_html(report_id, report.original_filename, variant_dicts)

        if format == "html":
            return HTMLResponse(
                content=html,
                headers={"Content-Disposition": f'inline; filename="genolife-report-{report_id}.html"'},
            )

        # PDF：用 reportlab 从 HTML 生成
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from io import BytesIO

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        # 提取纯文本（简化：去 HTML 标签）
        import re
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        story.append(Paragraph(f"基因健康分析报告 — {report.original_filename}", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(text[:4000], styles["BodyText"]))
        doc.build(story)
        pdf_bytes = buf.getvalue()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="genolife-report-{report_id}.pdf"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {e}")
