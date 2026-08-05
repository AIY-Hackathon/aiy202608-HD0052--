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

// 环境因子 → 中文标签 + 图标（婴儿版）
const ENV_FACTORS = {
  nutrition_type: { label: "喂养方式", icon: "🍼" },
  sleep_quality: { label: "睡眠质量", icon: "😴" },
  development_stimulation: { label: "发育刺激", icon: "🧸" },
  medical_adherence: { label: "医疗依从", icon: "🏥" },
  environmental_safety: { label: "环境安全", icon: "🏠" },
};

// 交互知识库（儿科版：基于 gene_database.json 的 environment_interaction 字段）
const INTERACTIONS = {
  PAH: {
    nutrition_type: { type: "protective", evidence: "strong", desc: "严格的苯丙氨酸限制饮食可完全预防 PKU 导致的神经系统损伤。早期饮食管理与预后直接相关。", ref: "PKU饮食管理指南, 中华儿科杂志 2023" },
    medical_adherence: { type: "protective", evidence: "strong", desc: "定期监测血苯丙氨酸水平并依从特殊配方饮食，是PAH缺乏症管理的核心。", ref: "PAH deficiency management, Genetics in Medicine 2024" },
  },
  G6PD: {
    nutrition_type: { type: "risk_amp", evidence: "strong", desc: "接触蚕豆（蚕豆病）可诱发G6PD缺乏症患儿的急性溶血性贫血，严格避免是关键。", ref: "G6PD deficiency: dietary triggers, Lancet Haematology 2023" },
    medical_adherence: { type: "protective", evidence: "strong", desc: "告知医生G6PD缺乏情况，避免磺胺类、阿司匹林等氧化性药物，可完全预防药物性溶血。", ref: "G6PD drug safety, WHO guidelines 2023" },
    environmental_safety: { type: "risk_amp", evidence: "moderate", desc: "樟脑丸（萘）等氧化性化学物质接触可诱发溶血，注意居家环境安全。", ref: "G6PD environmental triggers, Pediatric Research 2024" },
  },
  SMN1: {
    medical_adherence: { type: "protective", evidence: "strong", desc: "症状前治疗（基因治疗/药物干预）与症状后治疗的预后差异巨大。新生儿筛查+早期干预是关键。", ref: "SMA newborn screening outcomes, NEJM 2024" },
    development_stimulation: { type: "protective", evidence: "moderate", desc: "早期康复训练和发育刺激可显著改善SMA患儿的运动功能保留。", ref: "Early intervention in SMA, Pediatric Neurology 2023" },
  },
  GJB2: {
    development_stimulation: { type: "protective", evidence: "strong", desc: "早期听力筛查（<1月龄）+早期干预（<6月龄）+语言康复训练，可使GJB2相关听力损失患儿语言发育接近正常。", ref: "Early hearing intervention outcomes, Pediatrics 2024" },
    medical_adherence: { type: "protective", evidence: "moderate", desc: "定期听力学随访和助听器/人工耳蜗的及时适配是GJB2听力损失管理的关键。", ref: "Cochlear implant in GJB2, Otology & Neurotology 2023" },
  },
  CFTR: {
    medical_adherence: { type: "protective", evidence: "strong", desc: "CFTR调节剂治疗+定期肺功能监测+营养支持，可显著改善囊性纤维化患儿的预后。", ref: "CFTR modulator therapy, NEJM 2023" },
    nutrition_type: { type: "protective", evidence: "moderate", desc: "高热量、高蛋白饮食+胰酶替代治疗，对CFTR相关胰腺功能不全的患儿至关重要。", ref: "Nutrition in CF, J Cystic Fibrosis 2024" },
  },
  HBB: {
    medical_adherence: { type: "protective", evidence: "strong", desc: "镰状细胞病/地中海贫血患儿的定期输血、羟基脲治疗和感染预防，显著降低并发症风险。", ref: "Sickle cell management, Blood 2024" },
    environmental_safety: { type: "risk_amp", evidence: "moderate", desc: "镰状细胞病患儿对低温、高海拔、脱水等环境因素极为敏感，需要注意防护。", ref: "Environmental triggers in SCD, American Journal of Hematology 2023" },
  },
  SCN1A: {
    development_stimulation: { type: "protective", evidence: "moderate", desc: "Dravet综合征患儿通过避免发热诱因+早期发育康复，可减少癫痫持续状态并改善发育结局。", ref: "Dravet syndrome management, Epilepsia 2024" },
    medical_adherence: { type: "protective", evidence: "strong", desc: "规范的抗癫痫药物治疗和发热管理，是SCN1A相关癫痫管理的基石。", ref: "SCN1A epilepsy guidelines, Neurology 2023" },
  },
  FMR1: {
    development_stimulation: { type: "protective", evidence: "strong", desc: "脆性X综合征患儿通过早期行为干预、言语治疗和特殊教育支持，可显著改善社交沟通和适应能力。", ref: "Early intervention in Fragile X, J Developmental Pediatrics 2024" },
    sleep_quality: { type: "bidirectional", evidence: "moderate", desc: "FMR1前突变/全突变患儿常伴睡眠障碍，改善睡眠质量可提升白天的学习和行为表现。", ref: "Sleep in Fragile X syndrome, Sleep Medicine 2023" },
  },
  IL2RG: {
    medical_adherence: { type: "protective", evidence: "strong", desc: "SCID（严重联合免疫缺陷）患儿的早期诊断+造血干细胞移植/基因治疗是挽救生命的关键。感染预防至关重要。", ref: "SCID newborn screening and treatment, Blood 2024" },
    environmental_safety: { type: "risk_amp", evidence: "strong", desc: "SCID患儿对环境病原体极度敏感，需要严格隔离和感染控制。", ref: "Infection prevention in SCID, J Clinical Immunology 2023" },
  },
  CYP21A2: {
    medical_adherence: { type: "protective", evidence: "strong", desc: "先天性肾上腺皮质增生症(CAH)的糖皮质激素/盐皮质激素替代治疗，需终身依从以预防肾上腺危象。", ref: "CAH management guidelines, Endocrine Reviews 2024" },
    nutrition_type: { type: "protective", evidence: "moderate", desc: "CAH患儿的钠补充和电解质平衡管理，对预防失盐型危象至关重要。", ref: "Salt-wasting CAH management, JCEM 2023" },
  },
  TSC1: {
    medical_adherence: { type: "protective", evidence: "moderate", desc: "结节性硬化症患儿的mTOR抑制剂治疗和定期影像学监测，可延缓肿瘤生长。", ref: "TSC management, Pediatric Neurology 2024" },
    development_stimulation: { type: "protective", evidence: "moderate", desc: "TSC常伴自闭症和癫痫，早期发育干预和行为治疗显著改善长期预后。", ref: "TSC-associated ASD, Neurology 2023" },
  },
  NF1: {
    medical_adherence: { type: "protective", evidence: "moderate", desc: "NF1患儿的定期眼科、骨科和神经科随访，以及MEK抑制剂治疗，是疾病管理的基石。", ref: "NF1 management guidelines, Genetics in Medicine 2023" },
    development_stimulation: { type: "protective", evidence: "moderate", desc: "NF1常伴学习障碍和ADHD，教育支持和认知训练可改善学业表现。", ref: "Cognitive outcomes in NF1, Developmental Medicine 2024" },
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
    return ["PAH", "G6PD", "SMN1", "GJB2", "CFTR", "HBB", "SCN1A", "FMR1"];
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
            key={"interKey-" + key}
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
            <g key={"hdr-" + f}>
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
            <g key={"row-" + g}>
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
          <span key={"evKey-" + key} className="inline-flex items-center gap-1.5 text-[11px] text-text-tertiary">
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
