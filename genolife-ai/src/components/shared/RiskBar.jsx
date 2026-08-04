import { motion } from "framer-motion";

/**
 * Premium risk bar with animated fill and label.
 */
export default function RiskBar({ label, score, baseline = 50, showScore = true }) {
  const barColor =
    score > 70 ? "from-orange-400 to-risk-high" :
    score > 50 ? "from-amber-300 to-risk-moderate" :
    "from-accent to-emerald-400";

  const shadowColor =
    score > 70 ? "rgba(220,91,81,.25)" :
    score > 50 ? "rgba(232,166,64,.25)" :
    "rgba(13,148,136,.25)";

  return (
    <div className="flex items-center gap-4">
      <span className="w-28 text-[13px] font-semibold text-text-secondary">{label}</span>
      <div className="flex-1 relative">
        <div className="h-2.5 rounded-full bg-gray-100 overflow-hidden">
          <motion.div
            className={`h-full rounded-full bg-gradient-to-r ${barColor}`}
            initial={{ width: 0 }}
            animate={{ width: `${score}%` }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1], delay: 0.1 }}
            style={{ boxShadow: `0 0 8px ${shadowColor}` }}
          />
        </div>
        {/* Baseline marker */}
        <div
          className="absolute top-1/2 -translate-y-1/2 w-px h-4 bg-gray-300"
          style={{ left: `${baseline}%` }}
        />
      </div>
      {showScore && (
        <span className="w-11 text-right text-[13px] font-bold text-text tabular-nums">
          {score}%
        </span>
      )}
    </div>
  );
}
