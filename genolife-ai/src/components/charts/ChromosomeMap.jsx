/**
 * ChromosomeMap — 染色体全景图（方案 A）
 * =========================================
 * 线性染色体带 + 变异定位，展示全部变异在基因组中的分布。
 * 每条染色体一个横向色带，变异按位置标记，颜色区分临床意义。
 *
 * 交互：
 *   - hover 变异点 → 显示基因名/rsID/位置
 *   - 图例说明颜色含义
 *   - 点击变异可选中，配合外部详情展示
 */
import { useState, useMemo } from "react";

// 人类染色体 → 近似长度（Mb，GRCh38 近似值，用于比例定位）
const CHR_LENGTHS_MB = {
  1: 248, 2: 242, 3: 198, 4: 190, 5: 181, 6: 170, 7: 159, 8: 145,
  9: 138, 10: 133, 11: 135, 12: 133, 13: 114, 14: 107, 15: 102,
  16: 90, 17: 83, 18: 80, 19: 58, 20: 64, 21: 46, 22: 50,
  X: 156, Y: 57,
};

const SIGNIFICANCE_COLORS = {
  Pathogenic: "#dc2626",         // 红 — 致病
  Likely_pathogenic: "#f97316",  // 橙 — 可能致病
  Uncertain_significance: "#9ca3af", // 灰 — 意义不明
  VUS: "#9ca3af",
  Likely_benign: "#10b981",      // 绿 — 可能良性
  Benign: "#34d399",             // 绿 — 良性
};

const SIGNIFICANCE_LABELS = {
  Pathogenic: "致病",
  Likely_pathogenic: "可能致病",
  Uncertain_significance: "意义不明 (VUS)",
  VUS: "意义不明 (VUS)",
  Likely_benign: "可能良性",
  Benign: "良性",
};

const SIGNIFICANCE_ORDER = [
  "Pathogenic", "Likely_pathogenic", "Uncertain_significance", "Likely_benign", "Benign",
];

// 染色体展示顺序（常染色体 1-22 + X + Y）
const DISPLAY_CHROMOSOMES = [...Array.from({ length: 22 }, (_, i) => String(i + 1)), "X", "Y"];

function significanceColor(sig) {
  if (!sig) return SIGNIFICANCE_COLORS.Uncertain_significance;
  for (const [k, v] of Object.entries(SIGNIFICANCE_COLORS)) {
    if (sig.toLowerCase().includes(k.toLowerCase().replace("_", "")) || sig.toLowerCase() === k.toLowerCase()) {
      return v;
    }
  }
  return SIGNIFICANCE_COLORS.Uncertain_significance;
}

function significanceLabel(sig) {
  if (!sig) return "未分类";
  const norm = sig.toLowerCase().replace(/[_\s]/g, "");
  const map = {
    pathogenic: "致病", likelypathogenic: "可能致病",
    uncertainsignificance: "意义不明", vus: "意义不明",
    likelybenign: "可能良性", benign: "良性",
  };
  return map[norm] || sig;
}

export default function ChromosomeMap({ variants = [], height = 360 }) {
  const [hovered, setHovered] = useState(null);
  const [selected, setSelected] = useState(null);

  // 统计各临床意义的数量，用于图例
  const counts = useMemo(() => {
    const c = {};
    for (const v of variants) {
      const key = v.clinvar_significance || "Uncertain_significance";
      c[key] = (c[key] || 0) + 1;
    }
    return c;
  }, [variants]);

  // 染色体带宽与间距
  const margin = { top: 10, right: 30, bottom: 24, left: 8 };
  const bandHeight = 22;
  const gap = 7;
  // 宽度基于传入 height 的比例，至少 520px 保证可读性
  const usableWidth = Math.max(520, height * 1.6) - margin.left - margin.right;
  const totalBands = DISPLAY_CHROMOSOMES.length;
  const totalHeight = margin.top + margin.bottom + bandHeight * totalBands + gap * (totalBands - 1);

  return (
    <div className="w-full">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mb-3">
        {SIGNIFICANCE_ORDER.map((sig) => (
          <span key={"cmSig-" + sig} className="inline-flex items-center gap-1.5 text-[11px] text-text-tertiary">
            <span
              className="w-2.5 h-2.5 rounded-full"
              style={{ background: SIGNIFICANCE_COLORS[sig] }}
            />
            {SIGNIFICANCE_LABELS[sig] || sig}
            {counts[sig] > 0 && <span className="font-bold text-text-secondary">×{counts[sig]}</span>}
          </span>
        ))}
      </div>

      <div className="overflow-x-auto">
        <svg
          width="100%"
          viewBox={`0 0 ${usableWidth + margin.left + margin.right} ${totalHeight}`}
          style={{ minWidth: 520 }}
        >
          {DISPLAY_CHROMOSOMES.map((chr, i) => {
            const y = margin.top + i * (bandHeight + gap);
            const length = CHR_LENGTHS_MB[chr] || 150;
            const chrVariants = variants.filter(
              (v) => String(v.chromosome).replace("chr", "") === chr
            );
            const hasVariants = chrVariants.length > 0;

            return (
              <g key={chr}>
                {/* 染色体带 */}
                <rect
                  x={margin.left}
                  y={y}
                  width={usableWidth}
                  height={bandHeight}
                  rx={bandHeight / 2}
                  fill={hasVariants ? "#eef2ff" : "#f3f4f6"}
                  stroke={hasVariants ? "#c7d2fe" : "#e5e7eb"}
                  strokeWidth={1}
                />
                {/* 染色体标签 */}
                <text
                  x={margin.left + usableWidth + 10}
                  y={y + bandHeight / 2 + 4}
                  fontSize={10}
                  fill={hasVariants ? "#4338ca" : "#9ca3af"}
                  fontWeight={hasVariants ? 700 : 400}
                >
                  {chr}
                  {hasVariants && <tspan fill="#4338ca" fontWeight={700}>({chrVariants.length})</tspan>}
                </text>

                {/* 变异标记 */}
                {chrVariants.map((v, j) => {
                  const x = margin.left + (Math.min(v.position || 0, length * 1e6) / (length * 1e6)) * usableWidth;
                  const color = significanceColor(v.clinvar_significance);
                  const r = v.clinvar_significance && v.clinvar_significance.toLowerCase().includes("pathogenic") ? 6 : 4.5;
                  const isHover = hovered === `${chr}-${j}`;
                  const isSel = selected === `${chr}-${j}`;
                  return (
                    <g
                      key={j}
                      onMouseEnter={() => setHovered(`${chr}-${j}`)}
                      onMouseLeave={() => setHovered(null)}
                      onClick={() => setSelected(isSel ? null : `${chr}-${j}`)}
                      style={{ cursor: "pointer" }}
                    >
                      <circle
                        cx={x}
                        cy={y + bandHeight / 2}
                        r={isSel ? r + 3 : isHover ? r + 2 : r}
                        fill={color}
                        fillOpacity={isSel ? 1 : isHover ? 0.95 : 0.85}
                        stroke={isSel ? "#1f2937" : "white"}
                        strokeWidth={isSel ? 2 : 1}
                      />
                      {/* hover 提示 */}
                      {isHover && (
                        <g transform={`translate(${Math.min(x, usableWidth + margin.left - 120)}, ${y - 46})`}>
                          <rect
                            x={-6} y={-6} width={130} height={38} rx={8}
                            fill="#111827" fillOpacity={0.92}
                          />
                          <text x={0} y={6} fontSize={10} fill="white" fontWeight={700}>
                            {v.gene_name || v.rs_id || `${chr}:${v.position}`}
                          </text>
                          <text x={0} y={21} fontSize={9} fill="#c7d2fe">
                            {v.rs_id || ""} · {significanceLabel(v.clinvar_significance)}
                          </text>
                        </g>
                      )}
                      {isSel && (
                        <text
                          x={x}
                          y={y + bandHeight / 2 + 4}
                          fontSize={9}
                          fill="#1f2937"
                          textAnchor="middle"
                          fontWeight={700}
                        >
                          {v.gene_name || v.rs_id}
                        </text>
                      )}
                    </g>
                  );
                })}
              </g>
            );
          })}
        </svg>
      </div>

      <p className="mt-2 text-[11px] text-text-tertiary leading-relaxed">
        <strong>如何阅读：</strong>每条横带代表一条染色体，圆点标记您在报告中检测到的变异。
        颜色表示临床意义：<span style={{ color: "#dc2626" }}>红=致病</span>，
        <span style={{ color: "#9ca3af" }}>灰=意义不明</span>，
        <span style={{ color: "#10b981" }}>绿=良性</span>。
        圆点位置对应变异在染色体上的物理位置（距带左侧越远，位置越靠染色体的末端）。
        悬停查看详情，点击锁定标记。
      </p>
    </div>
  );
}
