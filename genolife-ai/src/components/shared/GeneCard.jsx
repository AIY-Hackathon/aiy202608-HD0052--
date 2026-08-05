import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Shield, Sparkles, Box } from "lucide-react";

const riskStyles = {
  advantage: {
    bg: "bg-accent-light/50 border-accent/20",
    dot: "bg-accent",
    label: "Genetic Advantage",
    labelColor: "text-accent",
  },
  low: {
    bg: "bg-accent-light/40 border-accent/15",
    dot: "bg-accent",
    label: "Low Genetic Influence",
    labelColor: "text-accent",
  },
  moderate: {
    bg: "bg-amber-50/70 border-amber-100",
    dot: "bg-risk-moderate",
    label: "Moderate Genetic Influence",
    labelColor: "text-risk-moderate",
  },
  elevated: {
    bg: "bg-orange-50/70 border-orange-100",
    dot: "bg-orange-500",
    label: "Elevated Genetic Influence",
    labelColor: "text-orange-500",
  },
  high: {
    bg: "bg-red-50/70 border-red-100",
    dot: "bg-risk-high",
    label: "High Genetic Influence",
    labelColor: "text-risk-high",
  },
};

export default function GeneCard({ gene, index = 0, isExpanded, onToggle, onView3D }) {
  const style = riskStyles[gene.riskLevel] || riskStyles.moderate;

  return (
    <motion.div
      className={`card-reveal premium-card p-6 cursor-pointer overflow-hidden group ${
        isExpanded ? "ring-2 ring-primary/10" : ""
      }`}
      style={{ animationDelay: `${index * 80}ms` }}
      onClick={onToggle}
      whileHover={{ y: -6 }}
      transition={{ type: "spring", stiffness: 280, damping: 24 }}
    >
      {/* Card background accent */}
      <div className={`absolute top-0 right-0 w-32 h-32 rounded-bl-full opacity-[0.04] pointer-events-none ${style.dot}`} />

      {/* Header */}
      <div className="relative flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          {/* Gene icon */}
          <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-2xl shadow-sm ${
            isExpanded ? style.bg : "bg-gray-50"
          }`}>
            {gene.icon}
          </div>

          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className="font-mono text-[12px] font-bold text-primary/70 tracking-wide bg-primary-light/40 px-2 py-0.5 rounded-md">
                {gene.symbol}
              </span>
              <span className={`w-2 h-2 rounded-full ${style.dot} shadow-sm`} />
            </div>
            <h3 className="font-display font-semibold text-[17px] text-text leading-tight">
              {gene.name}
            </h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={`text-[11px] font-semibold ${style.labelColor} uppercase tracking-wider`}>
                {style.label}
              </span>
            </div>
          </div>
        </div>

        <motion.span
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.25 }}
          className="text-text-tertiary mt-2 opacity-50 group-hover:opacity-100 transition-opacity"
        >
          <ChevronDown size={18} />
        </motion.span>
      </div>

      {/* 3D 结构按钮 */}
      {onView3D && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onView3D(gene);
          }}
          className="relative mt-4 w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-primary/5 hover:bg-primary/10 text-primary text-[13px] font-semibold transition-all duration-200 cursor-pointer group"
          style={{ border: "1px dashed rgba(30,58,95,0.2)" }}
        >
          <Box size={14} className="group-hover:scale-110 transition-transform" />
          View 3D Structure
        </button>
      )}

      {/* Summary */}
      <div className="relative mt-5">
        <div className="absolute left-0 top-0 bottom-0 w-0.5 rounded-full bg-primary/8" />
        <p className="pl-4 text-[14px] text-text-secondary leading-relaxed">
          {gene.summary}
        </p>
      </div>

      {/* Expandable detail */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden relative"
          >
            <div className="mt-6 pt-6 border-t border-gray-100 space-y-5">
              {/* What this means */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles size={15} className="text-ai" />
                  <h4 className="text-[12px] font-bold text-text uppercase tracking-[0.1em]">
                    What This Means
                  </h4>
                </div>
                <p className="text-[14px] text-text-secondary leading-relaxed bg-gray-50/50 rounded-xl p-4">
                  {gene.interpretation}
                </p>
              </div>

              {/* Actions */}
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Shield size={15} className="text-accent" />
                  <h4 className="text-[12px] font-bold text-text uppercase tracking-[0.1em]">
                    Recommended Actions
                  </h4>
                </div>
                <ul className="space-y-2">
                  {gene.recommendations.map((rec, i) => (
                    <li
                      key={rec.slice(0, 30) + "-" + i}
                      className="flex items-start gap-3 text-[14px] text-text-secondary bg-white rounded-xl p-3 border border-gray-100"
                    >
                      <span className="flex-shrink-0 w-5 h-5 rounded-full bg-accent-light text-accent flex items-center justify-center text-[10px] font-bold mt-0.5">
                        {i + 1}
                      </span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>

              {/* AI badge */}
              <div className="flex items-center gap-2 pt-1">
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-ai-light text-ai text-[11px] font-semibold">
                  🤖 AI-generated interpretation
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
