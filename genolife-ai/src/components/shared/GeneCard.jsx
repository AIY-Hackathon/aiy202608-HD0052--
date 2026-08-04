import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

const riskColors = {
  advantage: "bg-accent-light border-accent/30",
  low: "bg-accent-light border-accent/30",
  moderate: "bg-amber-50 border-amber-200",
  elevated: "bg-orange-50 border-orange-200",
  high: "bg-red-50 border-red-200",
};

const riskLabels = {
  advantage: "Genetic Advantage",
  low: "Low Genetic Influence",
  moderate: "Moderate Genetic Influence",
  elevated: "Elevated Genetic Influence",
  high: "High Genetic Influence",
};

const riskDotColors = {
  advantage: "bg-accent",
  low: "bg-accent",
  moderate: "bg-risk-moderate",
  elevated: "bg-orange-500",
  high: "bg-risk-high",
};

/**
 * Gene insight card — shows gene symbol, what it means, expands for details.
 */
export default function GeneCard({ gene, index = 0, isExpanded, onToggle }) {
  const open = isExpanded;

  return (
    <motion.div
      className={`card-reveal rounded-2xl border p-6 cursor-pointer transition-shadow duration-200 hover:shadow-md ${
        riskColors[gene.riskLevel] || riskColors.moderate
      }`}
      style={{ animationDelay: `${index * 80}ms` }}
      onClick={onToggle}
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <span className="text-3xl">{gene.icon}</span>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className="font-mono text-sm font-semibold text-primary tracking-wide bg-primary-light/60 px-2 py-0.5 rounded-md">
                {gene.symbol}
              </span>
              <span className={`w-2 h-2 rounded-full ${riskDotColors[gene.riskLevel]}`} />
            </div>
            <h3 className="font-display font-semibold text-lg text-text leading-tight">
              {gene.name}
            </h3>
            <p className="text-sm text-text-secondary mt-0.5">{gene.category}</p>
          </div>
        </div>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-text-tertiary mt-1"
        >
          <ChevronDown size={20} />
        </motion.span>
      </div>

      {/* Summary (always visible) */}
      <p className="mt-4 text-[15px] text-text-secondary leading-relaxed">
        {gene.summary}
      </p>

      {/* Expandable detail */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="mt-5 pt-5 border-t border-gray-200/60 space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-text uppercase tracking-wider mb-2">
                  What this means
                </h4>
                <p className="text-[15px] text-text-secondary leading-relaxed">
                  {gene.interpretation}
                </p>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-text uppercase tracking-wider mb-2">
                  Recommended Actions
                </h4>
                <ul className="space-y-2">
                  {gene.recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start gap-2 text-[15px] text-text-secondary">
                      <span className="text-accent mt-0.5">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-ai-light text-ai text-xs font-medium">
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
