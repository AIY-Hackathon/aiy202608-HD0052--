/**
 * PopulationSelector — 人群感知选择器
 * ======================================
 * 展示祖先推断结果（辅助参考），并允许用户手动选择人群。
 * 选择后重新请求分析接口（带 population 参数），关键基因分析会随人群变化。
 *
 * 设计原则：
 *   - 祖先推断基于少量 SNP，置信度多为 low，仅作参考提示
 *   - 用户主动选择是权威输入（用户最了解自己的背景）
 *   - 每个选项标注在所选人群下会如何校准分析
 */
import { useState } from "react";
import { Globe, MapPin, ChevronDown, Check } from "lucide-react";

const POPULATIONS = [
  { id: "EAS", label: "东亚裔", region: "East Asian" },
  { id: "EUR", label: "欧洲裔", region: "European" },
  { id: "AFR", label: "非洲裔", region: "African" },
  { id: "SAS", label: "南亚裔", region: "South Asian" },
  { id: "LAT", label: "拉丁裔/混血", region: "Latino/Admixed" },
];

const CONFIDENCE_META = {
  high: { label: "较高置信度", color: "#059669" },
  moderate: { label: "中等置信度", color: "#d97706" },
  low: { label: "较低置信度", color: "#9ca3af" },
  none: { label: "无法推断", color: "#9ca3af" },
};

export default function PopulationSelector({
  ancestry = null,
  selectedPopulation = "",
  onSelect = () => {},
}) {
  const [open, setOpen] = useState(false);
  const [showDetail, setShowDetail] = useState(false);

  const inferred = ancestry?.inferred_population;
  const confMeta = CONFIDENCE_META[ancestry?.confidence] || CONFIDENCE_META.none;
  const selectedPop = POPULATIONS.find((p) => p.id === selectedPopulation);
  const activeLabel = selectedPop ? `${selectedPop.label} (${selectedPop.region})` : "请选择";

  // 推断概率（top3）
  const topProbs = (ancestry?.top3 || []).slice(0, 3);

  return (
    <div className="premium-card px-5 py-4 mb-6">
      {/* 头部 */}
      <div className="flex items-center gap-3 mb-3">
        <div className="w-9 h-9 rounded-xl bg-primary-light flex items-center justify-center flex-shrink-0">
          <Globe size={17} className="text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[13px] font-bold text-text">人群特点设置</p>
          <p className="text-[11px] text-text-tertiary">根据您的祖先背景校准关键基因分析</p>
        </div>
      </div>

      {/* 祖先推断提示 */}
      {inferred && (
        <div
          className="mb-3 px-3 py-2 rounded-xl text-[11px] leading-relaxed"
          style={{ background: `${confMeta.color}0d`, border: `1px solid ${confMeta.color}30` }}
        >
          <span className="inline-flex items-center gap-1.5 font-semibold" style={{ color: confMeta.color }}>
            <MapPin size={12} />
            数据参考：与 {ancestry.inferred_cn_name} 样本最相似（{confMeta.label}）
          </span>
          {confMeta.confidence === "low" || confMeta.confidence === "none" ? (
            <span className="block mt-1 text-text-tertiary">
              ⚠️ 推断基于少量位点，仅供参考。请结合自身认知确认。
            </span>
          ) : null}
        </div>
      )}

      {/* 下拉选择器 */}
      <div className="relative">
        <button
          onClick={() => setOpen(!open)}
          className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 text-[13px] font-semibold text-text hover:border-primary/40 transition-all cursor-pointer"
          style={{ border: "none", background: "none" }}
        >
          <span className="flex items-center gap-2">
            <MapPin size={14} className="text-primary" />
            {activeLabel}
          </span>
          <ChevronDown size={15} className={`text-text-tertiary transition-transform ${open ? "rotate-180" : ""}`} />
        </button>

        {open && (
          <div className="absolute z-30 mt-2 w-full rounded-xl bg-white border border-gray-100 shadow-xl overflow-hidden">
            {POPULATIONS.map((p) => {
              const isSel = selectedPopulation === p.id;
              return (
                <button
                  key={p.id}
                  onClick={() => {
                    onSelect(p.id);
                    setOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-4 py-3 text-[13px] transition-colors cursor-pointer ${
                    isSel ? "bg-primary-light/40 text-primary font-bold" : "hover:bg-gray-50 text-text"
                  }`}
                  style={{ background: isSel ? "rgba(37,99,235,0.08)" : "none", border: "none" }}
                >
                  <span>
                    {p.label}
                    <span className="block text-[10px] text-text-tertiary font-normal">{p.region}</span>
                  </span>
                  {isSel && <Check size={15} className="text-primary" />}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 推断概率详情 */}
      {topProbs.length > 0 && (
        <button
          onClick={() => setShowDetail(!showDetail)}
          className="mt-2 text-[11px] text-text-tertiary hover:text-text cursor-pointer"
          style={{ background: "none", border: "none" }}
        >
          {showDetail ? "收起" : "查看数据推断详情"}
        </button>
      )}
      {showDetail && topProbs.length > 0 && (
        <div className="mt-2 space-y-1.5">
          {topProbs.map((p) => (
            <div key={p.population} className="flex items-center gap-3">
              <span className="w-16 text-[11px] text-text-tertiary">{p.cn_name}</span>
              <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary/70"
                  style={{ width: `${p.probability * 100}%` }}
                />
              </div>
              <span className="w-10 text-right text-[11px] font-bold text-text-secondary">
                {Math.round(p.probability * 100)}%
              </span>
            </div>
          ))}
        </div>
      )}

      <p className="mt-3 text-[10px] text-text-tertiary leading-relaxed">
        选择人群后，系统将按该人群的等位基因频率重新校准关键基因的"稀有度"——
        在您人群中罕见的变异会更受关注，常见的则回归常态。此设置为教育用途，不影响医学诊断。
      </p>
    </div>
  );
}
