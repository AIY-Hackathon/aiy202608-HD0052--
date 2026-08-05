/**
 * AdvancedVisualizations — 高级基因可视化面板（方案 A/B/D/F 容器）
 * =================================================================
 * 将四种可视化组织为标签页，展示基因分析的不同视角：
 *   A. 染色体全景图   — 变异在基因组中的分布
 *   B. 基因-疾病网络   — 基因影响哪些健康维度/疾病
 *   D. 人群频率分布   — 我的基因型在人群中多常见
 *   F. 基因×环境交互  — 生活方式如何改变遗传风险（核心）
 */
import { useState } from "react";
import ChromosomeMap from "./charts/ChromosomeMap";
import GeneDiseaseNetwork from "./charts/GeneDiseaseNetwork";
import PopulationFrequency from "./charts/PopulationFrequency";
import GxEHeatmap from "./charts/GxEHeatmap";
import { Map, Network, BarChart3, Grid3x3 } from "lucide-react";

const TABS = [
  { id: "gxe", label: "基因×环境交互", icon: Grid3x3, desc: "生活方式如何改变遗传风险" },
  { id: "chromosome", label: "染色体全景", icon: Map, desc: "变异在基因组中的分布" },
  { id: "network", label: "基因-疾病网络", icon: Network, desc: "基因影响哪些健康维度" },
  { id: "population", label: "人群频率", icon: BarChart3, desc: "我的基因型有多常见" },
];

export default function AdvancedVisualizations({ genes = [], variants = [] }) {
  const [activeTab, setActiveTab] = useState("gxe");

  const active = TABS.find((t) => t.id === activeTab);

  return (
    <div className="mt-2">
      {/* 标签栏 */}
      <div className="flex flex-wrap gap-2 mb-5">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-[12px] font-semibold transition-all cursor-pointer ${
                isActive
                  ? "bg-primary text-white shadow-md shadow-primary/20"
                  : "bg-gray-100 text-text-tertiary hover:text-text hover:bg-gray-200"
              }`}
              style={{ border: "none" }}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* 当前标签说明 */}
      <p className="text-[11px] text-text-tertiary mb-4">
        <strong className="text-text-secondary">{active.label}：</strong>{active.desc}
      </p>

      {/* 内容区 */}
      <div className="premium-card p-5 sm:p-6">
        {activeTab === "gxe" && <GxEHeatmap genes={genes} />}
        {activeTab === "chromosome" && <ChromosomeMap variants={variants} />}
        {activeTab === "network" && <GeneDiseaseNetwork genes={genes} />}
        {activeTab === "population" && <PopulationFrequency genes={genes} />}
      </div>
    </div>
  );
}
