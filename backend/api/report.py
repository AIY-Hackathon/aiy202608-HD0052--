"""
GET /api/report/{report_id}/export — 报告导出
==============================================
从数据库读取分析结果，生成高端 HTML/PDF 健康报告。

使用 WeasyPrint 渲染 PDF，确保视觉效果与 HTML 一致。
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone
from math import cos, sin

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


# ── 视觉常量 ──
COLORS = {
    "bg": "#ffffff",
    "text": "#1a1a2e",
    "textSecondary": "#4b5563",
    "textTertiary": "#9ca3af",
    "accent": "#0d9488",
    "accentLight": "#f0fdfa",
    "primary": "#1e3a5f",
    "primaryLight": "#eff6ff",
    "gold": "#b8860b",
    "goldLight": "#fefce8",
    "riskLow": "#059669",
    "riskModerate": "#d97706",
    "riskHigh": "#dc2626",
    "border": "#e5e7eb",
    "surface": "#f8fafc",
}

GENE_CARD_META = {
    "PAH": {"name": "苯丙氨酸羟化酶 (Phenylalanine Hydroxylase)", "category": "代谢与内分泌", "icon": "⚡"},
    "G6PD": {"name": "葡萄糖-6-磷酸脱氢酶 (G6PD)", "category": "心血管与血液", "icon": "🩸"},
    "CYP21A2": {"name": "21-羟化酶 (21-Hydroxylase)", "category": "代谢与内分泌", "icon": "⚡"},
    "SMN1": {"name": "运动神经元存活蛋白1 (SMN1)", "category": "神经发育", "icon": "🧠"},
    "GJB2": {"name": "间隙连接蛋白β2 (Connexin 26)", "category": "感官与结构", "icon": "👂"},
    "SLC26A4": {"name": "Pendrin 阴离子转运蛋白", "category": "感官与结构", "icon": "👂"},
    "CHD7": {"name": "染色质解旋酶DNA结合蛋白7", "category": "心血管与血液", "icon": "❤️"},
    "IL2RG": {"name": "白细胞介素-2受体γ链", "category": "免疫与感染", "icon": "🛡️"},
    "BTK": {"name": "布鲁顿酪氨酸激酶", "category": "免疫与感染", "icon": "🛡️"},
    "RAG1": {"name": "重组激活基因1", "category": "免疫与感染", "icon": "🛡️"},
    "CFTR": {"name": "囊性纤维化跨膜传导调节因子", "category": "代谢与内分泌", "icon": "🫁"},
    "HBB": {"name": "血红蛋白β亚基", "category": "心血管与血液", "icon": "🩸"},
    "FBN1": {"name": "原纤蛋白-1 (Fibrillin-1)", "category": "心血管与血液", "icon": "❤️"},
    "MYH7": {"name": "肌球蛋白重链7", "category": "心血管与血液", "icon": "❤️"},
    "SCN1A": {"name": "电压门控钠通道α亚基1", "category": "神经发育", "icon": "🧠"},
    "MECP2": {"name": "甲基CpG结合蛋白2", "category": "神经发育", "icon": "🧠"},
    "FMR1": {"name": "脆性X智力低下蛋白 (FMRP)", "category": "神经发育", "icon": "🧠"},
    "TSC1": {"name": "错构瘤蛋白 (Hamartin)", "category": "神经发育", "icon": "🧠"},
    "NF1": {"name": "神经纤维瘤蛋白 (Neurofibromin)", "category": "神经发育", "icon": "🧠"},
    "DHCR7": {"name": "7-脱氢胆固醇还原酶", "category": "代谢与内分泌", "icon": "⚡"},
    "ACADM": {"name": "中链酰基辅酶A脱氢酶", "category": "代谢与内分泌", "icon": "⚡"},
    "SLC2A1": {"name": "葡萄糖转运蛋白1 (GLUT1)", "category": "神经发育", "icon": "🧠"},
    "COL1A1": {"name": "I型胶原α1链", "category": "感官与结构", "icon": "🦴"},
    "USH2A": {"name": "Usherin 蛋白", "category": "感官与结构", "icon": "👂"},
    "RB1": {"name": "视网膜母细胞瘤蛋白 (pRb)", "category": "感官与结构", "icon": "👁️"},
}

RISK_LABELS = {
    "elevated": ("Elevated Risk", COLORS["riskHigh"]),
    "high": ("High Risk", COLORS["riskHigh"]),
    "moderate": ("Moderate", COLORS["riskModerate"]),
    "low": ("Favorable", COLORS["riskLow"]),
}


def _gene_interpretation(g: dict) -> str:
    """为单个基因生成文字性解读。"""
    symbol = g.get("symbol", "")
    risk = g.get("risk_level", "moderate")
    function = g.get("function", "")
    lifestyle = g.get("lifestyle", "")
    population = g.get("population_impact", "")

    if risk in ("elevated", "high"):
        risk_text = "该基因携带临床显著变异，遗传风险相对升高。"
    elif risk == "moderate":
        risk_text = "该基因存在中等程度的遗传影响，属于常见人群范围。"
    else:
        risk_text = "该基因未发现显著风险变异，遗传影响较低。"

    lifestyle_text = f"可调节建议：{lifestyle}" if lifestyle else ""
    return f"{function} {risk_text} {population}。{lifestyle_text}"


def _health_score_ring_svg(score: float, size: int = 160) -> str:
    """生成环形健康评分 SVG。"""
    r = (size - 12) / 2
    circumference = r * 2 * 3.14159
    offset = circumference * (1 - score / 100)

    if score >= 85:
        color = COLORS["riskLow"]
    elif score >= 70:
        color = COLORS["riskModerate"]
    else:
        color = COLORS["riskHigh"]

    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
      <circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="#e5e7eb" stroke-width="10"/>
      <circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="{color}" stroke-width="10"
              stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
              stroke-linecap="round" transform="rotate(-90 {size/2} {size/2})"/>
      <text x="{size/2}" y="{size/2 - 10}" text-anchor="middle" font-family="-apple-system,sans-serif"
            font-size="32" font-weight="800" fill="{color}">{int(score)}</text>
      <text x="{size/2}" y="{size/2 + 16}" text-anchor="middle" font-family="-apple-system,sans-serif"
            font-size="11" fill="#9ca3af">/100</text>
    </svg>"""


def _dimension_bar(label: str, score: float, color: str) -> str:
    """生成维度评分条。"""
    return f"""
    <div style="margin-bottom:14px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="font-size:12px;font-weight:600;color:#1a1a2e;">{label}</span>
        <span style="font-size:12px;font-weight:700;color:{color};">{int(score)}</span>
      </div>
      <div style="background:#e5e7eb;border-radius:5px;height:8px;">
        <div style="background:{color};width:{min(score,100)}%;height:8px;border-radius:5px;"></div>
      </div>
    </div>"""


def _gene_card(g: dict) -> str:
    """生成单个基因卡片。"""
    meta = GENE_CARD_META.get(g["symbol"], {
        "name": g["symbol"],
        "category": "Unknown",
        "variant": "—",
        "icon": "🧬",
    })
    risk_level = g.get("risk_level", "moderate")
    risk_label, risk_color = RISK_LABELS.get(risk_level, ("Moderate", COLORS["riskModerate"]))

    return f"""
    <div style="background:#f8fafc;border-radius:16px;padding:24px;margin-bottom:16px;
                border-left:5px solid {risk_color};page-break-inside:avoid;">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px;">
        <div>
          <div style="font-size:20px;margin-bottom:4px;">{meta['icon']}</div>
          <strong style="font-size:17px;color:#1a1a2e;display:block;">{g['symbol']}</strong>
          <span style="font-size:13px;color:#6b7280;">{meta['name']}</span>
        </div>
        <span style="font-size:11px;font-weight:700;color:{risk_color};text-transform:uppercase;
                     background:{risk_color}15;padding:4px 12px;border-radius:20px;">
          {risk_label}
        </span>
      </div>
      <div style="background:white;border-radius:10px;padding:14px;margin-top:12px;">
        <div style="display:flex;gap:32px;flex-wrap:wrap;">
          <div>
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;">Category</span>
            <p style="font-size:13px;color:#1a1a2e;margin:4px 0 0;">{meta['category']}</p>
          </div>
          <div>
            <span style="font-size:10px;font-weight:700;color:#9ca3af;text-transform:uppercase;">Variant</span>
            <p style="font-size:13px;font-family:monospace;color:#1a1a2e;margin:4px 0 0;">{meta['variant']}</p>
          </div>
        </div>
        <p style="font-size:12px;color:#4b5563;margin:12px 0 0;line-height:1.6;">
          {g.get('function','')}
        </p>
        <p style="font-size:11px;color:#6b7280;margin:6px 0 0;">
          {g.get('population_impact','')}
        </p>
      </div>
    </div>"""


def _radar_chart_svg(dimensions: list[dict]) -> str:
    """生成雷达图（SVG）。"""
    if len(dimensions) < 3:
        return ""

    cx, cy, r = 140, 140, 100
    n = len(dimensions)
    angles = [(2 * 3.14159 * i / n) - 3.14159 / 2 for i in range(n)]

    # 数据多边形
    radar_pts = " ".join(
        f"{cx + r * (dimensions[i].get('score', 50) / 100) * cos(angles[i])},{cy + r * (dimensions[i].get('score', 50) / 100) * sin(angles[i])}"
        for i in range(n)
    )

    # 背景网格
    grid_pts = ""
    for level in [0.25, 0.5, 0.75, 1.0]:
        level_pts = " ".join(
            f"{cx + r * level * cos(a)},{cy + r * level * sin(a)}" for a in angles
        )
        grid_pts += f'<polygon points="{level_pts}" fill="none" stroke="#e5e7eb" stroke-width="0.5"/>'

    # 轴线
    axis_lines = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{cx + r * cos(a)}" y2="{cy + r * sin(a)}" stroke="#e5e7eb" stroke-width="0.5"/>'
        for a in angles
    )

    # 标签
    labels = "".join(
        f'<text x="{cx + (r + 18) * cos(a)}" y="{cy + (r + 18) * sin(a) + 4}" text-anchor="middle" '
        f'font-family="-apple-system,sans-serif" font-size="10" fill="#4b5563">{dimensions[i]["label"][:4]}</text>'
        for i, a in enumerate(angles)
    )

    return f"""
    <svg width="280" height="280" viewBox="0 0 280 280" xmlns="http://www.w3.org/2000/svg">
      {grid_pts}
      {axis_lines}
      <polygon points="{radar_pts}" fill="{COLORS['accent']}30" stroke="{COLORS['accent']}" stroke-width="2" stroke-linejoin="round"/>
      {labels}
    </svg>"""


def _generate_html(report_id: str, filename: str, variants: list[dict]) -> str:
    """生成高端品牌 HTML 报告。"""
    scientific = engine.generate_scientific_analysis(variants)
    key_genes = scientific.get("key_genes", [])
    dims = engine.calculate_dimension_scores(variants)
    recs = engine.generate_recommendations({})

    now = datetime.now(timezone.utc).strftime("%B %d, %Y")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── Health Score ──
    health_score = scientific.get("polygenic_score", 72)
    if isinstance(health_score, str):
        try:
            health_score = float(health_score)
        except ValueError:
            health_score = 72
    score_svg = _health_score_ring_svg(min(max(health_score, 0), 100))

    # ── 基因卡片 ──
    gene_cards = "".join(_gene_card(g) for g in key_genes) or (
        '<p style="font-size:13px;color:#6b7280;text-align:center;padding:32px;">No significant key genes identified in this report.</p>'
    )

    # ── 维度评分 ──
    dim_bars = "".join(
        _dimension_bar(
            d["label"],
            d["score"],
            COLORS["riskLow"] if d["score"] < 55 else (COLORS["riskModerate"] if d["score"] < 70 else COLORS["riskHigh"]),
        )
        for d in dims
    ) or '<p style="font-size:13px;color:#6b7280;">No dimension data available.</p>'

    # ── 健康概览卡片 ──
    def _overview_card(label: str, score, color: str, desc: str) -> str:
        return f"""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:14px;padding:20px;
                    text-align:center;page-break-inside:avoid;">
          <p style="font-size:26px;font-weight:800;color:{color};margin:0 0 4px;">{score}</p>
          <p style="font-size:11px;font-weight:700;color:#1a1a2e;text-transform:uppercase;letter-spacing:0.08em;margin:0;">{label}</p>
          <p style="font-size:11px;color:#6b7280;margin:6px 0 0;line-height:1.4;">{desc}</p>
        </div>"""

    overview_cards = ""
    for d in dims[:4]:
        score_val = d["score"]
        if score_val < 55:
            color = COLORS["riskLow"]
            desc = "Favorable"
        elif score_val < 70:
            color = COLORS["riskModerate"]
            desc = "Moderate tendency"
        else:
            color = COLORS["riskHigh"]
            desc = "Needs attention"
        overview_cards += _overview_card(d["label"], int(score_val), color, desc)

    # ── 建议 ──
    rec_items = "".join(
        f"""
        <div style="display:flex;align-items:flex-start;gap:14px;padding:16px 0;border-bottom:1px solid #f1f5f9;">
          <div style="width:28px;height:28px;border-radius:50%;background:{COLORS['accentLight']};
                      color:{COLORS['accent']};display:flex;align-items:center;justify-content:center;
                      font-weight:700;font-size:13px;flex-shrink:0;">{i+1}</div>
          <div>
            <p style="font-size:14px;font-weight:600;color:#1a1a2e;margin:0 0 4px;">{r.get('title','')}</p>
            <p style="font-size:12px;color:#6b7280;margin:0;line-height:1.5;">{r.get('description','')}</p>
          </div>
        </div>"""
        for i, r in enumerate(recs[:3])
    ) or '<p style="font-size:13px;color:#6b7280;">No recommendations available.</p>'

    # ── 雷达图 ──
    radar_svg = _radar_chart_svg(dims[:5]) if len(dims) >= 3 else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Genetic Health Report — GenoLife AI</title>
<style>
  @page {{
    size: A4;
    margin: 40px 48px;
    @top-center {{
      content: "GenoLife AI — Personal Genetic Health Report";
      font-family: -apple-system, "Segoe UI", sans-serif;
      font-size: 8px;
      color: #9ca3af;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }}
    @bottom-center {{
      content: "Page " counter(page);
      font-family: -apple-system, "Segoe UI", sans-serif;
      font-size: 8px;
      color: #9ca3af;
    }}
  }}
  @page :first {{
    @top-center {{ content: none; }}
    margin-top: 0;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, "Segoe UI", "Helvetica Neue", sans-serif;
    line-height: 1.6;
    color: #1a1a2e;
    background: #ffffff;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  /* ── Cover Page ── */
  .cover {{
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: linear-gradient(170deg, #060A12 0%, #0C1525 50%, #111D30 100%);
    color: white;
    padding: 60px;
    page-break-after: always;
  }}
  .cover-logo {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
    margin-bottom: 64px;
  }}
  .cover-title {{
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin-bottom: 16px;
  }}
  .cover-title span {{
    background: linear-gradient(135deg, #7EB8AE, #5C9A90);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  .cover-subtitle {{
    font-size: 14px;
    color: rgba(255,255,255,0.45);
    max-width: 380px;
    line-height: 1.6;
    margin-bottom: 48px;
  }}
  .cover-meta {{
    font-size: 12px;
    color: rgba(255,255,255,0.3);
    line-height: 1.8;
  }}
  .cover-score {{
    margin: 40px 0;
  }}
  .cover-tagline {{
    font-size: 12px;
    color: rgba(255,255,255,0.25);
    font-style: italic;
    margin-top: 48px;
  }}

  /* ── Section ── */
  .section {{
    padding: 40px 0;
    page-break-inside: avoid;
  }}
  .section-title {{
    font-size: 20px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 8px;
    letter-spacing: -0.01em;
  }}
  .section-subtitle {{
    font-size: 13px;
    color: #9ca3af;
    margin-bottom: 28px;
    font-weight: 400;
  }}
  .section-divider {{
    width: 40px;
    height: 3px;
    border-radius: 2px;
    background: #0d9488;
    margin-bottom: 28px;
  }}

  /* ── Overview Grid ── */
  .overview-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-bottom: 28px;
  }}

  /* ── Footer ── */
  .report-footer {{
    margin-top: 60px;
    padding: 24px 0;
    border-top: 1px solid #e5e7eb;
    text-align: center;
    font-size: 10px;
    color: #9ca3af;
    line-height: 1.8;
  }}

  /* ── Watermark ── */
  body::after {{
    content: "Educational Research Tool — Not a Medical Device";
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-25deg);
    font-size: 52px;
    color: rgba(0,0,0,0.015);
    white-space: nowrap;
    pointer-events: none;
    z-index: 9999;
  }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <p class="cover-logo">GenoLife AI</p>
  <h1 class="cover-title">
    Personal <span>Genetic Health</span><br>Report
  </h1>
  <p class="cover-subtitle">
    AI-powered genetic analysis — understand your biology and make informed health decisions.
  </p>

  <div class="cover-score">
    {score_svg}
  </div>

  <div class="cover-meta">
    <p>Prepared for <strong style="color:rgba(255,255,255,0.6);">Sample User</strong></p>
    <p>{filename} &middot; {now}</p>
    <p style="font-size:10px;margin-top:4px;">Report ID: {report_id}</p>
  </div>

  <p class="cover-tagline">Your genes reveal tendencies. Your choices shape outcomes.</p>
</div>

<!-- HEALTH OVERVIEW -->
<div class="section">
  <h2 class="section-title">Health Overview</h2>
  <p class="section-subtitle">Your genetic profile across key health dimensions</p>
  <div class="section-divider"></div>

  <div class="overview-grid">
    {overview_cards}
  </div>
</div>

<!-- GENE INSIGHTS -->
<div class="section">
  <h2 class="section-title">Gene Insights</h2>
  <p class="section-subtitle">Key genetic variants identified in your analysis</p>
  <div class="section-divider"></div>

  {gene_cards}
</div>

<!-- HEALTH DIMENSION PROFILE -->
<div class="section">
  <h2 class="section-title">Health Dimension Profile</h2>
  <p class="section-subtitle">Score breakdown across health categories</p>
  <div class="section-divider"></div>

  <div style="display:flex;gap:40px;flex-wrap:wrap;align-items:center;">
    <div style="flex:1;min-width:280px;">
      {dim_bars}
    </div>
    {f'<div style="flex-shrink:0;">{radar_svg}</div>' if radar_svg else ''}
  </div>

  <p style="font-size:11px;color:#9ca3af;margin-top:20px;font-style:italic;">
    These scores reflect genetic tendencies, not clinical diagnoses. Lifestyle choices significantly influence health outcomes.
  </p>
</div>

<!-- PERSONALIZED RECOMMENDATIONS -->
<div class="section">
  <h2 class="section-title">Personalized Recommendations</h2>
  <p class="section-subtitle">Top actions based on your genetic profile</p>
  <div class="section-divider"></div>

  {rec_items}
</div>

<!-- FOOTER -->
<div class="report-footer">
  <p><strong>GenoLife AI</strong> &middot; Personal Genetic Health Report</p>
  <p>Generated {now_iso} &middot; Educational research tool — not a medical device</p>
  <p>This report does not diagnose, treat, or predict any health condition.</p>
</div>

</body>
</html>"""


def _generate_markdown(report_id: str, filename: str, variants: list[dict]) -> str:
    """生成可读的 Markdown 基因报告（儿科版）。"""
    scientific = engine.generate_scientific_analysis(variants)
    key_genes = scientific.get("key_genes", [])
    dims = engine.calculate_dimension_scores(variants)
    recs = engine.generate_recommendations({})

    now = datetime.now(timezone.utc).strftime("%Y年%m月%d日 %H:%M UTC")

    # ── 统计 ──
    pathogenic = [v for v in variants if "Pathogenic" in (v.get("clinvar_significance") or "")]
    vus = [v for v in variants if "Uncertain" in (v.get("clinvar_significance") or "")]
    benign = [v for v in variants if "Benign" in (v.get("clinvar_significance") or "")]

    lines = [
        f"# 🧬 GenoLife AI — 新生儿基因风险评估报告",
        "",
        f"**报告编号**：`{report_id}`  ",
        f"**原始文件**：{filename}  ",
        f"**生成时间**：{now}  ",
        f"**分析变异数**：{len(variants)} 个",
        "",
        "---",
        "",
        "> ⚠️ **重要免责声明**：本报告为教育科研用途，不构成临床诊断。",
        "> 基因检测结果仅供参考，任何医疗决策请咨询专业儿科医生或遗传咨询师。",
        "> 本报告不替代新生儿疾病筛查、常规体检和专业医疗建议。",
        "",
        "---",
        "",
        "## 一、检测概览",
        "",
    ]

    # 健康评分
    health_score = scientific.get("polygenic_score", 72)
    if isinstance(health_score, str):
        try:
            health_score = float(health_score)
        except ValueError:
            health_score = 72
    health_score = min(max(health_score, 0), 100)

    if health_score >= 80:
        level_str = "低风险 (Low Risk)"
        level_desc = "宝宝的基因筛查结果整体良好，未发现显著致病变异。建议保持常规儿童保健随访。"
    elif health_score >= 60:
        level_str = "中等关注 (Moderate)"
        level_desc = "宝宝的基因筛查提示部分遗传风险需要关注，建议针对性地进行专科随访和早期干预。"
    else:
        level_str = "需重点关注 (Elevated)"
        level_desc = "宝宝的基因筛查发现较多致病变异，强烈建议尽快咨询儿科遗传专科医生，制定个性化的随访和干预计划。"

    lines.extend([
        f"| 项目 | 结果 |",
        f"|------|------|",
        f"| **综合健康评分** | {int(health_score)} / 100 |",
        f"| **风险等级** | {level_str} |",
        f"| **致病性变异** | {len(pathogenic)} 个 |",
        f"| **意义不明确变异 (VUS)** | {len(vus)} 个 |",
        f"| **良性/可能良性变异** | {len(benign)} 个 |",
        "",
        f"> {level_desc}",
        "",
        scientific.get("summary", ""),
        "",
    ])

    # ── 二、关键基因 ──
    lines.extend([
        "---",
        "",
        "## 二、关键基因分析",
        "",
    ])

    if not key_genes:
        lines.append("本次分析未识别到显著关键基因变异。")
        lines.append("")
    else:
        for g in key_genes:
            symbol = g.get("symbol", "")
            meta = GENE_CARD_META.get(symbol, {"name": symbol, "category": "未知", "icon": "🧬"})
            risk = g.get("risk_level", "moderate")

            risk_cn = {"elevated": "⚠️ 高风险", "high": "⚠️ 高风险", "moderate": "• 中等关注", "low": "✅ 低风险"}.get(risk, "• 中等关注")

            lines.extend([
                f"### {meta.get('icon','🧬')} {symbol} — {meta.get('name', '')}",
                f"- **风险等级**：{risk_cn}  ",
                f"- **健康维度**：{meta.get('category', '')}  ",
                f"- **功能**：{g.get('function', '')}  ",
                f"- **人群影响**：{g.get('population_impact', '')}  ",
                f"- **可调节因素**：{g.get('lifestyle', '')}  ",
                f"- **解读**：{_gene_interpretation(g)}",
                "",
            ])

    # ── 三、健康维度评分 ──
    lines.extend([
        "---",
        "",
        "## 三、五大健康维度评分",
        "",
        "| 维度 | 评分 | 解读 |",
        "|------|------|------|",
    ])
    for d in dims:
        score = d.get("score", 50)
        if score >= 70:
            interpret = "⚠️ 需重点关注"
        elif score >= 50:
            interpret = "• 中等关注"
        else:
            interpret = "✅ 相对良好"
        lines.append(f"| **{d.get('label', '')}** | {int(score)} / 100 | {interpret} |")
    lines.append("")

    lines.extend([
        "**维度说明**：",
        "- **代谢与内分泌**：涉及氨基酸代谢、糖代谢、脂质代谢及内分泌激素合成相关基因",
        "- **心血管与血液**：涉及心肌结构、血管发育、血红蛋白及凝血功能相关基因",
        "- **神经发育**：涉及神经元功能、突触传递、脑发育及神经保护相关基因",
        "- **免疫与感染**：涉及免疫细胞发育、抗体生成及感染防御相关基因",
        "- **感官与结构**：涉及听力、视力、骨骼发育及结缔组织结构相关基因",
        "",
    ])

    # ── 四、变异详情 ──
    lines.extend([
        "---",
        "",
        "## 四、变异详情",
        "",
    ])

    if pathogenic:
        lines.append("### ⚠️ 致病性/可能致病性变异")
        lines.append("")
        lines.append("| 基因 | 位置 | rsID | ClinVar 意义 |")
        lines.append("|------|------|------|-------------|")
        for v in pathogenic[:20]:
            lines.append(f"| **{v.get('gene_name','—')}** | {v.get('chromosome','')}:{v.get('position','')} | {v.get('rs_id','—')} | {v.get('clinvar_significance','')} |")
        lines.append("")

    if vus:
        lines.append("### VUS (意义不明确变异)")
        lines.append("")
        lines.append("| 基因 | 位置 | rsID |")
        lines.append("|------|------|------|")
        for v in vus[:10]:
            lines.append(f"| **{v.get('gene_name','—')}** | {v.get('chromosome','')}:{v.get('position','')} | {v.get('rs_id','—')} |")
        lines.append("")

    # ── 五、个性化建议 ──
    lines.extend([
        "---",
        "",
        "## 五、个性化照护建议",
        "",
    ])
    if recs:
        for i, r in enumerate(recs[:8]):
            lines.append(f"{i+1}. **{r.get('title', '')}** — {r.get('description', '')}")
        lines.append("")
    else:
        lines.append("暂无针对性的个性化建议。建议保持常规儿童保健随访。")
        lines.append("")

    # ── 六、家长须知 ──
    lines.extend([
        "---",
        "",
        "## 六、家长须知",
        "",
        "1. **基因不是命运**：基因检测结果反映的是"倾向"和"风险"，而非确定性的命运。",
        "   科学的早期照护、定期随访和良好的成长环境可以对孩子的健康发展产生深远影响。",
        "2. **G×E 交互**：基因（Gene）× 环境（Environment）交互是当代医学的核心认知。",
        "   即使携带致病变异，通过优化喂养方式、睡眠质量、发育刺激等环境因素，也可以显著改善预后。",
        "3. **定期随访**：请按照儿科医生的建议进行定期生长发育评估和必要的专科随访。",
        "4. **新生儿筛查**：本报告不能替代国家规定的新生儿疾病筛查（如 PKU、先天性甲低等）。",
        "5. **遗传咨询**：如有疑问，建议咨询有资质的遗传咨询师或儿科遗传专科医生。",
        "",
    ])

    # ── 尾部 ──
    lines.extend([
        "---",
        "",
        f"*本报告由 GenoLife AI 自动生成 · {now}*  ",
        "*GenoLife AI 是面向非医疗消费者的新生儿基因风险科普平台，不属于医疗器械。*  ",
        "*基因检测结果仅供学习参考，不构成医疗建议。*",
    ])

    return "\n".join(lines)


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

        # PDF：优先 WeasyPrint（视觉与 HTML 一致），缺失时降级 reportlab（纯 Python）
        pdf_bytes = None
        try:
            try:
                from weasyprint import HTML
                pdf_bytes = HTML(string=html).write_pdf()
            except Exception as e:
                print(f"[report] WeasyPrint 不可用（{type(e).__name__}: {e}），降级 reportlab")
                pdf_bytes = _pdf_with_reportlab(html, report.original_filename)
        except Exception as e:
            print(f"[report] PDF 生成失败: {e}")
            raise HTTPException(status_code=500, detail=f"PDF 生成失败: {e}")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="genolife-report-{report_id}.pdf"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {e}")


def _pdf_with_reportlab(html: str, filename: str) -> bytes:
    """用 reportlab 从 HTML 提取文本生成 PDF（无需系统库，跨平台可用）。

    注册系统中文字体解决中文乱码：
      - 优先微软雅黑 (msyh.ttc, 子字体 0) / 黑体 (simhei.ttf)
      - 其次中易宋体 (simsun.ttc)
      - 均不可用时回退 Helvetica（此时中文可能乱码，但保证不崩溃）
    """
    import os
    import re
    from io import BytesIO

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    # ── 注册中文字体 ──
    font_dir = "C:/Windows/Fonts"
    cn_font = None
    candidates = [
        ("GenoLifeCN", os.path.join(font_dir, "msyh.ttc"), 0),   # 微软雅黑
        ("GenoLifeCN", os.path.join(font_dir, "simhei.ttf"), None),  # 黑体
        ("GenoLifeCN", os.path.join(font_dir, "simsun.ttc"), 0),  # 宋体
        ("GenoLifeCN", os.path.join(font_dir, "Deng.ttf"), None),  # 等线
    ]
    registered = False
    for name, path, subfont in candidates:
        try:
            if os.path.exists(path):
                if subfont is not None:
                    pdfmetrics.registerFont(TTFont(name, path, subfontIndex=subfont))
                else:
                    pdfmetrics.registerFont(TTFont(name, path))
                registered = True
                cn_font = name
                break
        except Exception:
            continue
    if not registered:
        cn_font = "Helvetica"

    # 提取纯文本 + 保留换行
    text = re.sub(r"<br\s*/?>", "\n", html)
    text = re.sub(r"</(div|p|h\d|li)>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=50, bottomMargin=50)

    title_style = ParagraphStyle("title", fontName=cn_font, fontSize=18, leading=24, alignment=1, spaceAfter=12)
    body_style = ParagraphStyle("body", fontName=cn_font, fontSize=9.5, leading=14, spaceAfter=6)

    story = []
    story.append(Paragraph(f"GenoLife AI 基因健康报告 — {filename}", title_style))
    story.append(Spacer(1, 10))

    # 分段（最多 80 段避免超长）
    for para in text.split("\n\n")[:80]:
        clean = para.strip()
        if clean:
            story.append(Paragraph(clean[:1200], body_style))

    doc.build(story)
    return buf.getvalue()


@router.get("/report/{report_id}/text", response_class=HTMLResponse)
def text_report(report_id: str):
    """生成文字性基因报告（Markdown 格式）。"""
    report, variants = _load_report_data(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"报告 {report_id} 不存在")

    variant_dicts = _variants_to_dicts(variants)
    try:
        md = _generate_markdown(report_id, report.original_filename, variant_dicts)
        return HTMLResponse(
            content=md,
            headers={"Content-Disposition": f'inline; filename="genolife-report-{report_id}.md"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文字报告生成失败: {e}")
