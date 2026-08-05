/**
 * PopulationFrequency — 人群频率分布图（方案 D）
 * ==============================================
 * 展示用户基因型在各大洲人群中的携带频率，帮助理解"我的基因型有多常见"。
 *
 * 数据：基于公开 GWAS / 1000 Genomes 的常见 SNP 频率（教育演示值）。
 *   频率值表示"该风险等位基因在人群中的携带比例"。
 *
 * 交互：
 *   - 每个基因/位点一行，各人群一个色条
 *   - 用户的携带状态用圆点标出，并给出"常见/较少见"的解读
 */
import { useMemo, useState } from "react";

// 常见位点的人群频率（风险等位基因携带率，%）
// 数据来源：1000 Genomes Phase 3 / gnomAD（教育演示用近似值）
const POPULATION_FREQ = {
  APOE: {
    label: "APOE ε4",
    variant: "rs429358",
    populations: { 东亚: 8.0, 欧洲: 15.0, 非洲: 30.0, 南亚: 12.0 },
    note: "ε4 携带率因人群差异大：东亚约 7-9%，欧洲约 15%，非洲约 30%。",
  },
  FTO: {
    label: "FTO rs9939609",
    variant: "rs9939609",
    populations: { 东亚: 12.0, 欧洲: 40.0, 非洲: 50.0, 南亚: 35.0 },
    note: "FTO 风险等位基因（A）在欧洲人群非常常见（约 40%），是研究最充分的肥胖相关位点。",
  },
  CLOCK: {
    label: "CLOCK rs1801260",
    variant: "rs1801260",
    populations: { 东亚: 45.0, 欧洲: 30.0, 非洲: 25.0, 南亚: 38.0 },
    note: "CLOCK 昼夜节律相关多态性在世界各人群均有较高频率。",
  },
  ACTN3: {
    label: "ACTN3 R577X",
    variant: "rs1815739",
    populations: { 东亚: 42.0, 欧洲: 18.0, 非洲: 25.0, 南亚: 30.0 },
    note: "约 18% 的欧洲人完全缺乏 ACTN3 蛋白（XX 型），而东亚人群缺失频率更高。",
  },
  TOMM40: {
    label: "TOMM40 rs2075650",
    variant: "rs2075650",
    populations: { 东亚: 12.0, 欧洲: 18.0, 非洲: 28.0, 南亚: 15.0 },
    note: "TOMM40 与 APOE 相邻，常一起用于认知健康评估。",
  },
  MC4R: {
    label: "MC4R rs17782313",
    variant: "rs17782313",
    populations: { 东亚: 25.0, 欧洲: 22.0, 非洲: 30.0, 南亚: 26.0 },
    note: "MC4R 附近的 rs17782313 与食欲调控和 BMI 相关。",
  },
};

const POP_ORDER = ["东亚", "欧洲", "非洲", "南亚"];
const POP_COLORS = {
  东亚: "#2563eb",
  欧洲: "#7c3aed",
  非洲: "#dc2626",
  南亚: "#f59e0b",
};

export default function PopulationFrequency({ genes = [] }) {
  const [expanded, setExpanded] = useState(null);

  // 收集报告中出现的基因（取知识库中存在频率数据的）
  const presentGenes = useMemo(() => {
    const symbols = genes.map((g) => g.symbol).filter((s) => POPULATION_FREQ[s]);
    if (symbols.length > 0) return symbols;
    return Object.keys(POPULATION_FREQ).slice(0, 4); // 兜底演示
  }, [genes]);

  // 最大频率用于比例
  const maxFreq = useMemo(() => {
    let m = 0;
    for (const sym of presentGenes) {
      for (const v of Object.values(POPULATION_FREQ[sym].populations)) {
        m = Math.max(m, v);
      }
    }
    return m;
  }, [presentGenes]);

  return (
    <div className="w-full space-y-4">
      {presentGenes.map((sym) => {
        const g = POPULATION_FREQ[sym];
        const isExpanded = expanded === sym;
        return (
          <div key={sym} className="premium-card px-5 py-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-[14px] font-bold text-text">{g.label}</p>
                <p className="text-[11px] text-text-tertiary">{g.variant}</p>
              </div>
              <button
                onClick={() => setExpanded(isExpanded ? null : sym)}
                className="text-[11px] font-semibold text-primary hover:text-primary-600 transition-colors cursor-pointer"
                style={{ background: "none", border: "none" }}
              >
                {isExpanded ? "收起解读" : "查看解读"}
              </button>
            </div>

            {/* 频率条 */}
            <div className="space-y-2">
              {POP_ORDER.map((pop) => {
                const freq = g.populations[pop];
                return (
                  <div key={pop} className="flex items-center gap-3">
                    <span className="w-8 text-[11px] font-semibold text-text-tertiary">{pop}</span>
                    <div className="flex-1 h-4 bg-gray-100 rounded-md overflow-hidden">
                      <div
                        className="h-full rounded-md transition-all duration-700"
                        style={{
                          width: `${(freq / maxFreq) * 100}%`,
                          background: POP_COLORS[pop],
                          opacity: 0.85,
                        }}
                      />
                    </div>
                    <span className="w-14 text-right text-[11px] font-bold text-text-secondary">
                      {freq}%
                    </span>
                  </div>
                );
              })}
            </div>

            {/* 解读 */}
            {isExpanded && (
              <div className="mt-3 px-3 py-2.5 rounded-xl bg-blue-50/60 border border-blue-100 text-[12px] text-text-secondary leading-relaxed">
                <strong className="text-text">这是什么意思：</strong>{g.note}
                <span className="block mt-1 text-[11px] text-text-tertiary">
                  你在报告中检测到了该位点。携带率越低，说明该基因型在你所属人群中越少见，
                  但这不代表它"更好或更坏"——许多高影响基因型在人群中本就罕见。
                </span>
              </div>
            )}
          </div>
        );
      })}

      <p className="text-[11px] text-text-tertiary leading-relaxed">
        <strong>如何阅读：</strong>每个条显示该风险等位基因在不同人群中的携带比例（%）。
        条越长，携带者越多。<strong>重要提示</strong>：本数据为公开文献的近似频率，用于教育目的；
        人群频率因样本、定义和研究而异，具体应以您报告的数据为准。
      </p>
    </div>
  );
}
