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

// 儿科基因位点的人群频率（致病/风险等位基因携带率，%）
// 数据来源：gnomAD / 中国新生儿筛查数据 / 文献汇总（教育演示用近似值）
const POPULATION_FREQ = {
  PAH: {
    label: "PAH — 苯丙酮尿症(PKU)",
    variant: "中国发病率 ~1/11,000",
    populations: { 东亚: 1.8, 欧洲: 1.5, 非洲: 0.3, 南亚: 1.0 },
    note: "中国PKU发病率约1/11,000，北方高于南方。PAH致病变异携带率约1/50。",
  },
  G6PD: {
    label: "G6PD — G6PD缺乏症",
    variant: "中国南方携带率 ~5-10%",
    populations: { 东亚: 7.0, 欧洲: 0.5, 非洲: 15.0, 南亚: 8.0 },
    note: "全球约4亿人携带G6PD缺乏变异。中国南方（广东、广西、海南）发病率较高，约5-10%。",
  },
  SMN1: {
    label: "SMN1 — 脊髓性肌萎缩(SMA)",
    variant: "中国人群携带率 ~1/40-1/50",
    populations: { 东亚: 2.0, 欧洲: 2.5, 非洲: 1.5, 南亚: 2.0 },
    note: "SMN1缺失是中国人群最常见的严重遗传病携带之一，携带率约1/40-1/50。",
  },
  GJB2: {
    label: "GJB2 — 先天性听力损失",
    variant: "中国人群携带率 ~2-3%",
    populations: { 东亚: 2.5, 欧洲: 1.5, 非洲: 1.0, 南亚: 2.0 },
    note: "GJB2 c.235delC是中国人群最常见的致病变异，约占遗传性听力损失的50%。",
  },
  CFTR: {
    label: "CFTR — 囊性纤维化",
    variant: "亚洲人群发病率极低",
    populations: { 东亚: 0.05, 欧洲: 4.0, 非洲: 1.5, 南亚: 0.5 },
    note: "CF在东亚人群中极为罕见，但在欧美人群携带率高达1/25。",
  },
  HBB: {
    label: "HBB — 镰状细胞病/地中海贫血",
    variant: "中国南方携带率 ~3-8%",
    populations: { 东亚: 4.0, 欧洲: 0.5, 非洲: 25.0, 南亚: 8.0 },
    note: "中国南方（广东、广西）地中海贫血携带率约3-8%，非洲镰状细胞携带率高达25%。",
  },
  SCN1A: {
    label: "SCN1A — Dravet综合征",
    variant: "发病率 ~1/15,000-1/40,000",
    populations: { 东亚: 0.05, 欧洲: 0.05, 非洲: 0.05, 南亚: 0.05 },
    note: "Dravet综合征为罕见病，多为新生突变。SCN1A致病变异通常为杂合子。",
  },
  FMR1: {
    label: "FMR1 — 脆性X综合征",
    variant: "男性发病率 ~1/4,000-1/7,000",
    populations: { 东亚: 0.5, 欧洲: 1.0, 非洲: 0.8, 南亚: 0.6 },
    note: "脆性X综合征是最常见的遗传性智力障碍病因之一，前突变携带率约1/250-1/800。",
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
    return Object.keys(POPULATION_FREQ).slice(0, 6); // 兜底演示
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
