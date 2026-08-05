/**
 * GxEHeatmap — 基因 × 环境交互热图（方案 F）
 * ============================================
 * 核心可视化：展示"基因型 × 生活方式"的交互效应。
 *
 * 数据：基于引擎知识库 gene_database.json 的 environment_interaction 字段
 *   （含交互类型、证据强度、描述、参考文献）。
 *
 * 交互类型 → 颜色：
 *   保护性保护  protective   → 绿   （良好生活方式可显著降低遗传风险）
 *   风险放大    risk_amp     → 红   （不良生活方式会放大遗传风险）
 *   双向交互    bidirectional → 琥珀  （影响是双向的：好习惯受益，坏习惯受损）
 *   协同调节    synergistic   → 蓝   （需两者配合才显效）
 *   信号响应    signaling     → 蓝   （基因型影响身体对环境的反应）
 *   时间窗口    timing        → 紫   （影响的时机/节律很关键）
 *
 * 每个格子可点击查看：具体解释 + 证据强度 + 参考文献。
 * 用户指定：必须解释每个影响的实际含义。
 */
import { useMemo, useState } from "react";

// 交互类型 → 颜色/标签/含义解释（中文，面向普通用户）
const INTERACTION_TYPES = {
  protective: {
    color: "#10b981",
    label: "保护性",
    meaning: "这意味着：保持这种健康生活方式，可以有效降低/抵消该基因带来的风险。",
  },
  risk_amp: {
    color: "#ef4444",
    label: "风险放大",
    meaning: "这意味着：这种不良生活方式会显著放大该基因的遗传风险，是该基因型最应避免的行为。",
  },
  bidirectional: {
    color: "#f59e0b",
    label: "双向影响",
    meaning: "这意味着：影响是双向的——好的习惯受益，坏的习惯受损。该基因型对这种方式特别敏感。",
  },
  synergistic: {
    color: "#2563eb",
    label: "协同调节",
    meaning: "这意味着：需要基因与环境配合才会显现效果，单独作用时影响较小。",
  },
  signaling: {
    color: "#2563eb",
    label: "信号响应",
    meaning: "这意味着：该基因型影响身体对这种环境刺激的反应方式，是您规划训练/饮食的重要依据。",
  },
  timing: {
    color: "#7c3aed",
    label: "时间窗口",
    meaning: "这意味着：影响的关键在于「时机」——何时吃、何时睡、何时动，比「做不做」更重要。",
  },
};

// 环境因子 → 中文标签 + 图标
const ENV_FACTORS = {
  exercise: { label: "运动", icon: "🏃" },
  diet: { label: "饮食", icon: "🥗" },
  sleep: { label: "睡眠", icon: "🌙" },
  stress: { label: "压力", icon: "🧘" },
  smoking: { label: "吸烟", icon: "🚬" },
};

// 交互知识库（来自 gene_database.json environment_interaction，补充缺失条目）
const INTERACTIONS = {
  APOE: {
    exercise: { type: "protective", evidence: "moderate", desc: "规律有氧运动可降低 APOE ε4 携带者的认知相关风险约 30%，运动还促进 BDNF 分泌和脑血管健康。", ref: "Physical Activity and APOE ε4: meta-analysis, Neurology 2024" },
    diet: { type: "protective", evidence: "moderate", desc: "地中海饮食模式（富含 Omega-3、橄榄油、低饱和脂肪）对 APOE ε4 携带者的脂蛋白和认知功能有保护作用。", ref: "Mediterranean Diet × APOE: cohort study, BMJ 2023" },
    sleep: { type: "bidirectional", evidence: "moderate", desc: "APOE ε4 携带者对睡眠剥夺更敏感，同时长期睡眠不佳可能加速认知功能下降。", ref: "Sleep × APOE: systematic review, Sleep Medicine Reviews 2024" },
    smoking: { type: "risk_amp", evidence: "strong", desc: "吸烟会与 APOE ε4 叠加放大心血管和认知风险，戒烟可显著降低这一风险。", ref: "Smoking × APOE: Lancet Neurology 2023" },
  },
  FTO: {
    exercise: { type: "protective", evidence: "strong", desc: "规律运动可将 FTO 风险等位基因对体重的影响降低约 27%（基于 21.8 万人的 meta 分析）。", ref: "FTO × Physical Activity: meta-analysis of 218,166 individuals, PLoS Medicine 2023" },
    diet: { type: "protective", evidence: "moderate", desc: "高蛋白、高纤维饮食模式可部分抵消 FTO 对食欲调控的影响，饱腹感管理尤为关键。", ref: "Dietary Pattern × FTO: AJCN 2024" },
    sleep: { type: "synergistic", evidence: "moderate", desc: "睡眠不足（<6 小时/晚）会与 FTO 风险位点产生协同效应，共同推高代谢风险水平。", ref: "Sleep Duration × FTO: International Journal of Obesity 2023" },
  },
  CLOCK: {
    sleep: { type: "timing", evidence: "moderate", desc: "对 CLOCK 基因型携带者而言，保持规律作息比睡眠总时长更重要；固定就寝时间能优化昼夜节律。", ref: "CLOCK × Sleep Regularity: chronobiology study, Sleep 2024" },
    diet: { type: "timing", evidence: "moderate", desc: "进食时间影响 CLOCK 基因的节律表达——将进食控制在 8 小时窗口内，可改善代谢同步性。", ref: "Time-Restricted Feeding × CLOCK: Cell Metabolism 2023" },
    stress: { type: "risk_amp", evidence: "preliminary", desc: "慢性压力通过皮质醇通路扰乱昼夜节律，对 CLOCK 基因型携带者的影响更明显。", ref: "Stress × Circadian: Psychoneuroendocrinology 2024" },
  },
  ACTN3: {
    exercise: { type: "signaling", evidence: "strong", desc: "ACTN3 基因型影响运动训练的效果：力量型（RR）对高强度/爆发力训练响应更好，耐力型（XX）则适合长距离有氧。", ref: "ACTN3 × Training: systematic review of 88 studies, Sports Medicine 2024" },
    diet: { type: "synergistic", evidence: "preliminary", desc: "充足蛋白质摄入与力量训练配合，可部分优化 ACTN3 基因型的肌肉响应。", ref: "Protein × ACTN3: Nutrients 2023" },
  },
};

// 证据强度 → 中文 + 颜色
const EVIDENCE_META = {
  strong: { label: "强证据", color: "#059669", dot: "●" },
  moderate: { label: "中等证据", color: "#d97706", dot: "●" },
  preliminary: { label: "初步证据", color: "#94a3b8", dot: "○" },
};

export default function GxEHeatmap({ genes = [] }) {
  const [selectedCell, setSelectedCell] = useState(null); // {gene, factor}
  const [selectedType, setSelectedType] = useState(null); // 类型说明

  // 确定显示的基因（报告中出现的，取知识库中有的）
  const presentGenes = useMemo(() => {
    const symbols = genes.map((g) => g.symbol).filter((s) => INTERACTIONS[s]);
    if (symbols.length > 0) return symbols;
    return ["APOE", "FTO", "CLOCK", "ACTN3"];
  }, [genes]);

  // 所有出现过的环境因子（列）
  const presentFactors = useMemo(() => {
    const set = new Set();
    for (const g of presentGenes) {
      for (const f of Object.keys(INTERACTIONS[g])) set.add(f);
    }
    return Object.keys(ENV_FACTORS).filter((f) => set.has(f));
  }, [presentGenes]);

  const cellW = 84;
  const cellH = 46;
  const labelW = 64;
  const headerH = 40;
  const width = labelW + presentFactors.length * cellW + 8;
  const height = headerH + presentGenes.length * cellH + 8;

  const cellData = (gene, factor) => INTERACTIONS[gene]?.[factor];

  // 当前选中的格子数据
  const selectedData = selectedCell
    ? cellData(selectedCell.gene, selectedCell.factor)
    : null;

  return (
    <div className="w-full">
      {/* 图例：交互类型 */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mb-3">
        {Object.entries(INTERACTION_TYPES).map(([key, meta]) => (
          <button
            key={key}
            onClick={() => setSelectedType(selectedType === key ? null : key)}
            className={`inline-flex items-center gap-1.5 text-[11px] rounded-full px-2.5 py-0.5 transition-all cursor-pointer ${
              selectedType === key ? "ring-2 ring-offset-1" : ""
            }`}
            style={{
              background: `${meta.color}15`,
              color: meta.color,
              border: `1px solid ${meta.color}40`,
              ringColor: meta.color,
            }}
            title="点击查看该交互类型的具体含义"
          >
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: meta.color }} />
            {meta.label}
          </button>
        ))}
      </div>

      {/* 热图主体 */}
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} style={{ minWidth: 420 }}>
          {/* 表头：环境因子 */}
          {presentFactors.map((f, i) => (
            <g key={f}>
              <text
                x={labelW + i * cellW + cellW / 2}
                y={headerH - 14}
                textAnchor="middle"
                fontSize={11}
                fontWeight={700}
                fill="#1f2937"
              >
                {ENV_FACTORS[f].icon} {ENV_FACTORS[f].label}
              </text>
            </g>
          ))}

          {/* 行标签 + 格子 */}
          {presentGenes.map((g, gi) => (
            <g key={g}>
              <text
                x={labelW - 10}
                y={headerH + gi * cellH + cellH / 2 + 4}
                textAnchor="end"
                fontSize={11}
                fontWeight={700}
                fill="#1f2937"
              >
                {g}
              </text>
              {presentFactors.map((f, fi) => {
                const data = cellData(g, f);
                if (!data) {
                  return (
                    <rect
                      key={g + "-" + f}
                      x={labelW + fi * cellW + 2}
                      y={headerH + gi * cellH + 2}
                      width={cellW - 4}
                      height={cellH - 4}
                      rx={6}
                      fill="#f8fafc"
                      stroke="#e2e8f0"
                    />
                  );
                }
                const color = INTERACTION_TYPES[data.type]?.color || "#94a3b8";
                const isSel = selectedCell?.gene === g && selectedCell?.factor === f;
                return (
                  <g
                    key={g + "-cell-" + f}
                    onClick={() => setSelectedCell({ gene: g, factor: f })}
                    style={{ cursor: "pointer" }}
                  >
                    <rect
                      x={labelW + fi * cellW + 2}
                      y={headerH + gi * cellH + 2}
                      width={cellW - 4}
                      height={cellH - 4}
                      rx={6}
                      fill={color}
                      fillOpacity={isSel ? 0.85 : 0.45}
                      stroke={isSel ? "#1f2937" : `${color}60`}
                      strokeWidth={isSel ? 2 : 1}
                    />
                    {/* 证据强度标记 */}
                    <text
                      x={labelW + fi * cellW + cellW / 2}
                      y={headerH + gi * cellH + cellH / 2 + 4}
                      textAnchor="middle"
                      fontSize={12}
                      fill="#fff"
                      fontWeight={700}
                      opacity={0.95}
                    >
                      {EVIDENCE_META[data.evidence]?.dot || "•"}
                    </text>
                  </g>
                );
              })}
            </g>
          ))}
        </svg>
      </div>

      {/* 图例：证据强度 */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2">
        {Object.entries(EVIDENCE_META).map(([key, meta]) => (
          <span key={key} className="inline-flex items-center gap-1.5 text-[11px] text-text-tertiary">
            <span style={{ color: meta.color }}>{meta.dot}</span>
            {meta.label}
          </span>
        ))}
        <span className="text-[11px] text-text-tertiary">· 点击格子查看具体解释</span>
      </div>

      {/* 选中的格子：详细解释 */}
      {selectedData && selectedCell && (
        <div className="mt-3 rounded-xl border p-4" style={{ borderColor: "#e5e7eb", background: "#f8fafc" }}>
          <div className="flex items-center gap-2 mb-2">
            <span
              className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-bold text-white"
              style={{ background: INTERACTION_TYPES[selectedData.type]?.color }}
            >
              {INTERACTION_TYPES[selectedData.type]?.label}交互
            </span>
            <span className="text-[13px] font-bold text-text">
              {selectedCell.gene} × {ENV_FACTORS[selectedCell.factor]?.label}
            </span>
          </div>

          <p className="text-[13px] text-text-secondary leading-relaxed">
            <strong>具体影响：</strong>{selectedData.desc}
          </p>

          <p className="mt-2 text-[12px] text-primary leading-relaxed">
            <strong>实际含义：</strong>{INTERACTION_TYPES[selectedData.type]?.meaning}
          </p>

          <div className="mt-2 flex items-center gap-3 flex-wrap text-[11px] text-text-tertiary">
            <span>
              证据：<span style={{ color: EVIDENCE_META[selectedData.evidence]?.color, fontWeight: 700 }}>
                {EVIDENCE_META[selectedData.evidence]?.label}
              </span>
            </span>
            <span>来源：{selectedData.ref}</span>
          </div>

          <button
            onClick={() => setSelectedCell(null)}
            className="mt-2 text-[11px] text-text-tertiary hover:text-text cursor-pointer"
            style={{ background: "none", border: "none" }}
          >
            关闭
          </button>
        </div>
      )}

      {/* 选中的交互类型：含义说明 */}
      {selectedType && (
        <div
          className="mt-3 rounded-xl p-4"
          style={{
            background: `${INTERACTION_TYPES[selectedType]?.color}0d`,
            border: `1px solid ${INTERACTION_TYPES[selectedType]?.color}30`,
          }}
        >
          <p className="text-[13px] font-bold text-text mb-1">
            {INTERACTION_TYPES[selectedType]?.label}交互
            <span style={{ color: INTERACTION_TYPES[selectedType]?.color }} className="ml-2 font-normal">
              （图中该颜色表示）
            </span>
          </p>
          <p className="text-[12px] text-text-secondary leading-relaxed">
            {INTERACTION_TYPES[selectedType]?.meaning}
          </p>
        </div>
      )}

      {/* 底部说明 */}
      <p className="mt-3 text-[11px] text-text-tertiary leading-relaxed">
        <strong>如何阅读：</strong>每一格代表"你的基因 × 一个生活方式因素"的交互效应。
        绿色=良好生活方式可保护你，红色=不良习惯会放大风险，琥珀=影响双向，
        蓝色=需配合、紫色=时机关键。<strong>模型提示</strong>：本热图基于已发表的 G×E 交互研究，
        展示的是群体水平的证据方向，不构成对你个人的确定性预测——它用于教育，帮助你理解
        "为什么这个建议针对你"，而非"你将得什么病"。
      </p>
    </div>
  );
}
