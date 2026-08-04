import { motion } from "framer-motion";
import { Clock, Star } from "lucide-react";

const difficultyMeta = {
  easy: { bg: "bg-green-50 border-green-100", text: "text-green-700", label: "Easy" },
  moderate: { bg: "bg-amber-50 border-amber-100", text: "text-amber-700", label: "Moderate" },
  hard: { bg: "bg-red-50 border-red-100", text: "text-red-700", label: "Challenging" },
};

export default function RecommendationCard({ rec, index = 0, onToggle, checked = false }) {
  const diff = difficultyMeta[rec.difficulty] || difficultyMeta.moderate;

  return (
    <motion.div
      className={`card-reveal premium-card p-5 cursor-pointer transition-all duration-200 ${
        checked ? "ring-2 ring-accent/30 bg-accent-light/20" : ""
      }`}
      style={{ animationDelay: `${index * 70}ms` }}
      whileHover={{ y: -4 }}
      onClick={() => onToggle?.(rec.id)}
    >
      <div className="flex items-start gap-4">
        {/* Check circle */}
        <button
          className={`mt-1 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 cursor-pointer ${
            checked
              ? "bg-accent border-accent text-white shadow-lg shadow-accent/25"
              : "border-gray-200 hover:border-accent/50 bg-white"
          }`}
          onClick={(e) => {
            e.stopPropagation();
            onToggle?.(rec.id);
          }}
        >
          {checked && (
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path d="M2.5 6.5L5.5 9.5L10.5 3.5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </button>

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-2.5 mb-2">
            <div className="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center text-base shadow-sm">
              {rec.icon}
            </div>
            <h4 className="font-display font-semibold text-[15px] text-text leading-snug">
              {rec.title}
            </h4>
          </div>

          {/* Description */}
          <p className="text-[13px] text-text-secondary leading-relaxed mb-3">
            {rec.description}
          </p>

          {/* Meta chips */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${diff.bg} ${diff.text}`}>
              {diff.label}
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] text-text-tertiary font-medium">
              <Clock size={11} /> {rec.time}
            </span>
            <span className="inline-flex items-center gap-0.5 text-[13px]">
              {Array.from({ length: rec.impact }).map((_, i) => (
                <Star key={i} size={10} className="fill-risk-moderate text-risk-moderate" />
              ))}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
