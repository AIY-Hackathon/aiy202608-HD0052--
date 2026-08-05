import { motion } from "framer-motion";

/**
 * 分类选择控件 — 用于非连续型环境因素（如喂养方式）。
 * 三选一按钮组，选中项高亮显示。
 */
export default function CategoricalControl({ factor, value, onChange, label }) {
  const displayLabel = label || factor.label;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2.5">
        <div className="w-9 h-9 rounded-xl bg-gray-50 flex items-center justify-center text-lg shadow-sm">
          {factor.icon}
        </div>
        <span className="text-[14px] font-semibold text-text">{displayLabel}</span>
      </div>

      <div className="grid grid-cols-3 gap-2">
        {factor.options.map((opt) => {
          const selected = value === opt.value;
          return (
            <motion.button
              key={opt.value}
              onClick={() => onChange(factor.key, opt.value)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              className={`flex flex-col items-center gap-1 px-3 py-3 rounded-2xl text-center cursor-pointer transition-colors ${
                selected
                  ? "bg-primary text-white shadow-md"
                  : "bg-gray-50 text-text-secondary hover:bg-gray-100 border border-gray-100"
              }`}
              style={{ border: selected ? "2px solid transparent" : "1px solid #e5e7eb" }}
            >
              <span className={`text-[13px] font-bold ${selected ? "text-white" : "text-text"}`}>
                {opt.label}
              </span>
              <span className={`text-[10px] leading-tight ${selected ? "text-white/80" : "text-text-tertiary"}`}>
                {opt.desc}
              </span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
