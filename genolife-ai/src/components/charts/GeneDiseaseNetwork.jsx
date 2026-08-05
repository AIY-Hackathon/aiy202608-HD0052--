/**
 * GeneDiseaseNetwork — 基因-疾病关联网络图（方案 B）
 * =====================================================
 * 展示"哪些基因影响哪些疾病/健康维度"的关联网络。
 *
 * 布局：两层结构
 *   - 左侧：用户报告中检测到的基因节点
 *   - 右侧：基因影响的健康维度/疾病节点
 *   - 连线：基因 → 维度/疾病 的关联，线宽/颜色反映影响强度
 *
 * 数据：基于 prs_calculator 的 DIMENSION_GENE_MAP / DISEASE_GENE_MAP 知识映射。
 * 颜色：基因按风险等级着色，连线按影响强度着色。
 */
import { useMemo, useState } from "react";

// 基因 → 健康维度/疾病 映射（对齐后端 prs_calculator 知识库）
const GENE_LINKS = {
  APOE: [
    { target: "认知健康", type: "dimension", strength: 3 },
    { target: "阿尔茨海默", type: "disease", strength: 3 },
    { target: "心血管健康", type: "dimension", strength: 2 },
  ],
  FTO: [
    { target: "代谢健康", type: "dimension", strength: 3 },
    { target: "肥胖", type: "disease", strength: 2 },
    { target: "2型糖尿病", type: "disease", strength: 1 },
  ],
  CLOCK: [
    { target: "睡眠节律", type: "dimension", strength: 3 },
    { target: "代谢健康", type: "dimension", strength: 2 },
  ],
  ACTN3: [
    { target: "运动表现", type: "dimension", strength: 3 },
    { target: "力量代谢", type: "dimension", strength: 1 },
  ],
  LDLR: [
    { target: "心血管健康", type: "dimension", strength: 3 },
    { target: "家族性高胆固醇", type: "disease", strength: 3 },
  ],
  MC4R: [
    { target: "代谢健康", type: "dimension", strength: 3 },
    { target: "肥胖", type: "disease", strength: 3 },
  ],
  BRCA1: [
    { target: "乳腺癌", type: "disease", strength: 3 },
    { target: "卵巢癌", type: "disease", strength: 2 },
  ],
  BRCA2: [
    { target: "乳腺癌", type: "disease", strength: 3 },
    { target: "前列腺癌", type: "disease", strength: 2 },
  ],
  TOMM40: [
    { target: "认知健康", type: "dimension", strength: 2 },
    { target: "阿尔茨海默", type: "disease", strength: 2 },
  ],
  PER3: [
    { target: "睡眠节律", type: "dimension", strength: 2 },
  ],
  MSTN: [
    { target: "运动表现", type: "dimension", strength: 2 },
  ],
};

// 风险等级颜色（基因节点）
const RISK_COLORS = {
  elevated: "#dc2626",
  high: "#dc2626",
  moderate: "#f59e0b",
  low: "#10b981",
  advantage: "#2563eb",
};

// 节点类型颜色（右侧节点）
const TYPE_COLORS = {
  dimension: "#2563eb",   // 蓝色 — 健康维度
  disease: "#7c3aed",     // 紫色 — 疾病
};

const RISK_LABELS = {
  elevated: "风险升高",
  high: "高风险",
  moderate: "中等",
  low: "较低",
  advantage: "优势",
};

export default function GeneDiseaseNetwork({ genes = [] }) {
  const [hovered, setHovered] = useState(null); // {kind:'gene'|'target', id}

  // 收集出现的基因符号（支持对象数组 geneCards[] 或字符串数组）
  const presentGenes = useMemo(() => {
    if (genes.length === 0) return ["APOE", "FTO", "CLOCK", "ACTN3"];
    // 统一提取符号：对象有 symbol 字段，字符串直接用
    return genes.map((g) => (typeof g === "object" ? g.symbol : g)).filter(Boolean);
  }, [genes]);

  // 计算右侧所有目标节点及连线
  const { targets, edges } = useMemo(() => {
    const tSet = new Map();
    const eList = [];
    for (const g of presentGenes) {
      const links = GENE_LINKS[g] || [];
      for (const link of links) {
        if (!tSet.has(link.target)) {
          tSet.set(link.target, {
            name: link.target,
            type: link.type,
            strength: 0,
            genes: [],
          });
        }
        tSet.get(link.target).strength += link.strength;
        tSet.get(link.target).genes.push(g);
        eList.push({ gene: g, target: link.target, strength: link.strength, type: link.type });
      }
    }
    return {
      targets: Array.from(tSet.values()),
      edges: eList,
    };
  }, [presentGenes]);

  // 布局：左侧基因列 + 右侧目标列
  const width = 780;
  const height = Math.max(320, Math.max(presentGenes.length, targets.length) * 52 + 60);
  const leftX = 130;
  const rightX = 560;
  const geneY = (i) => 50 + i * (height - 100) / Math.max(1, presentGenes.length - 1);
  const targetY = (i) => 50 + i * (height - 100) / Math.max(1, targets.length - 1);

  // 基因风险等级（从外部传入的 gene 对象）
  const geneRisk = (symbol) => {
    const g = genes.find((x) => x.symbol === symbol);
    return g?.riskLevel || "moderate";
  };

  return (
    <div className="w-full">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mb-2">
        <span className="inline-flex items-center gap-1.5 text-[11px] text-text-tertiary">
          <span className="w-2.5 h-2.5 rounded-full" style={{ background: "#2563eb" }} />
          健康维度
        </span>
        <span className="inline-flex items-center gap-1.5 text-[11px] text-text-tertiary">
          <span className="w-2.5 h-2.5 rounded-full" style={{ background: "#7c3aed" }} />
          疾病风险
        </span>
        <span className="ml-auto text-[11px] text-text-tertiary">线越粗 = 关联越强</span>
      </div>

      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} style={{ minWidth: 560, maxHeight: 520 }}>
          {/* 连线 */}
          {edges.map((e, i) => {
            const gi = presentGenes.indexOf(e.gene);
            const ti = targets.findIndex((t) => t.name === e.target);
            if (gi < 0 || ti < 0) return null;
            const x1 = leftX, y1 = geneY(gi);
            const x2 = rightX, y2 = targetY(ti);
            const isHover = hovered?.kind === "gene" && hovered.id === e.gene
              || hovered?.kind === "target" && hovered.id === e.target;
            const strengthOpacity = 0.25 + e.strength * 0.2;
            return (
              <line
                key={i}
                x1={x1} y1={y1} x2={x2} y2={y2}
                stroke={isHover ? "#1f2937" : "#94a3b8"}
                strokeWidth={isHover ? 3 : 1 + e.strength * 1.2}
                strokeOpacity={isHover ? 0.9 : strengthOpacity}
              />
            );
          })}

          {/* 基因节点（左侧） */}
          {presentGenes.map((g, i) => {
            const risk = geneRisk(g);
            const color = RISK_COLORS[risk] || "#9ca3af";
            const isHover = hovered?.kind === "gene" && hovered.id === g;
            return (
              <g
                key={g}
                onMouseEnter={() => setHovered({ kind: "gene", id: g })}
                onMouseLeave={() => setHovered(null)}
                style={{ cursor: "pointer" }}
              >
                <circle cx={leftX} cy={geneY(i)} r={isHover ? 22 : 18} fill={color} fillOpacity={isHover ? 1 : 0.9} stroke="white" strokeWidth={2} />
                <text x={leftX} y={geneY(i) + 4} textAnchor="middle" fontSize={11} fontWeight={700} fill="white">
                  {g}
                </text>
                <text x={leftX} y={geneY(i) + 34} textAnchor="middle" fontSize={9} fill={color} fontWeight={600}>
                  {RISK_LABELS[risk] || risk}
                </text>
              </g>
            );
          })}

          {/* 目标节点（右侧） */}
          {targets.map((t, i) => {
            const color = TYPE_COLORS[t.type] || "#9ca3af";
            const isHover = hovered?.kind === "target" && hovered.id === t.name;
            return (
              <g
                key={t.name}
                onMouseEnter={() => setHovered({ kind: "target", id: t.name })}
                onMouseLeave={() => setHovered(null)}
                style={{ cursor: "pointer" }}
              >
                <rect
                  x={rightX - 60} y={targetY(i) - 12}
                  width={120} height={24} rx={12}
                  fill={isHover ? color : "white"}
                  fillOpacity={isHover ? 0.15 : 0.05}
                  stroke={color} strokeWidth={isHover ? 2 : 1.2}
                />
                <text x={rightX} y={targetY(i) + 4} textAnchor="middle" fontSize={11} fontWeight={600} fill={color}>
                  {t.name}
                </text>
              </g>
            );
          })}

          {/* hover 详情面板 */}
          {hovered && (
            <g>
              <rect
                x={width / 2 - 140} y={8} width={280} height={26} rx={10}
                fill="#111827" fillOpacity={0.92}
              />
              <text x={width / 2} y={25} textAnchor="middle" fontSize={11} fill="white" fontWeight={600}>
                {hovered.kind === "gene"
                  ? `${hovered.id} — 关联 ${GENE_LINKS[hovered.id]?.length || 0} 个健康维度/疾病`
                  : `${hovered.id} — 受 ${targets.find((t) => t.name === hovered.id)?.genes.join(", ") || ""} 影响`}
              </text>
            </g>
          )}
        </svg>
      </div>

      <p className="mt-2 text-[11px] text-text-tertiary leading-relaxed">
        <strong>如何阅读：</strong>左侧圆点是你的基因（颜色=风险等级），右侧是这些基因影响的健康维度（蓝）或疾病（紫）。
        连线表示"该基因与该健康维度/疾病存在已知关联"，线越粗表示关联越强。
        <span className="text-text-secondary"> 注意：关联≠因果，多数基因只贡献部分风险，生活方式和环境因素同等重要。</span>
      </p>
    </div>
  );
}
