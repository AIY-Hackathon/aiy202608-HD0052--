import { motion } from "framer-motion";

const difficultyColors = {
  easy: "bg-green-50 text-green-700 border-green-200",
  moderate: "bg-amber-50 text-amber-700 border-amber-200",
  hard: "bg-red-50 text-red-700 border-red-200",
};

const difficultyLabels = {
  easy: "Easy",
  moderate: "Moderate",
  hard: "Challenging",
};

/**
 * Recommendation card for Lifestyle Planner & Simulation pages.
 */
export default function RecommendationCard({ rec, index = 0, onToggle, checked = false }) {
  return (
    <motion.div
      className={`card-reveal rounded-2xl border p-5 transition-all duration-200 hover:shadow-md cursor-pointer ${
        checked ? "border-accent/40 bg-accent-light/30" : "border-gray-200/60 bg-white"
      }`}
      style={{ animationDelay: `${index * 80}ms` }}
      whileHover={{ y: -3 }}
      onClick={() => onToggle?.(rec.id)}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <button
          className={`mt-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors cursor-pointer ${
            checked
              ? "bg-accent border-accent text-white"
              : "border-gray-300 hover:border-accent"
          }`}
          onClick={(e) => {
            e.stopPropagation();
            onToggle?.(rec.id);
          }}
        >
          {checked && (
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M2 6L5 9L10 3" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </button>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="text-lg">{rec.icon}</span>
            <h4 className="font-display font-semibold text-[16px] text-text">{rec.title}</h4>
          </div>
          <p className="text-[14px] text-text-secondary leading-relaxed mt-1">{rec.description}</p>

          <div className="flex items-center gap-3 mt-3 flex-wrap">
            <span
              className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${
                difficultyColors[rec.difficulty] || difficultyColors.moderate
              }`}
            >
              {difficultyLabels[rec.difficulty] || rec.difficulty}
            </span>
            <span className="text-[11px] text-text-tertiary">⏱ {rec.time}</span>
            <span className="text-[11px] text-text-tertiary">
              {"⭐".repeat(rec.impact)}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
