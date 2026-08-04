import { useState } from "react";
import { motion } from "framer-motion";
import HealthScoreRing from "../components/shared/HealthScoreRing";
import GeneCard from "../components/shared/GeneCard";
import RiskBar from "../components/shared/RiskBar";
import AIBadge from "../components/shared/AIBadge";
import RiskRadar from "../components/charts/RiskRadar";
import { healthSummary, geneCards, riskDimensions } from "../data/mockData";

export default function GeneMap() {
  const [expandedGene, setExpandedGene] = useState(null);

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* ─────────────────────────────────────────────
          Hero: Health Score + AI Summary
         ───────────────────────────────────────────── */}
      <motion.section
        className="text-center mb-20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <p className="text-[13px] font-semibold text-text-tertiary uppercase tracking-[0.15em] mb-6">
          Your Genetic Health Profile
        </p>

        <div className="flex justify-center mb-8">
          <HealthScoreRing score={healthSummary.score} size={220} strokeWidth={10} />
        </div>

        <div className="max-w-xl mx-auto">
          <div className="flex items-center justify-center gap-2 mb-3">
            <span
              className={`inline-block w-2.5 h-2.5 rounded-full ${
                healthSummary.level === "low" ? "bg-risk-low" :
                healthSummary.level === "moderate" ? "bg-risk-moderate" :
                "bg-risk-high"
              }`}
            />
            <span className="text-[15px] font-semibold text-text tracking-wide">
              {healthSummary.levelLabel}
            </span>
          </div>
          <p className="text-[15px] text-text-secondary leading-relaxed">
            {healthSummary.aiSummary}
          </p>
          <div className="mt-4">
            <AIBadge text="AI-generated summary" />
          </div>
        </div>
      </motion.section>

      {/* ─────────────────────────────────────────────
          Gene Cards (2x2 grid)
         ───────────────────────────────────────────── */}
      <section className="mb-20">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-[13px] font-semibold text-text-tertiary uppercase tracking-[0.15em]">
              Your Genetic Traits
            </p>
            <h2 className="font-display font-semibold text-2xl text-text mt-1">
              What your genes say about you
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {geneCards.map((gene, i) => (
            <GeneCard
              key={gene.id}
              gene={gene}
              index={i}
              isExpanded={expandedGene === gene.id}
              onToggle={() =>
                setExpandedGene(expandedGene === gene.id ? null : gene.id)
              }
            />
          ))}
        </div>
      </section>

      {/* ─────────────────────────────────────────────
          Risk Radar + Risk Bars
         ───────────────────────────────────────────── */}
      <section>
        <p className="text-[13px] font-semibold text-text-tertiary uppercase tracking-[0.15em] mb-1">
          Risk Profile
        </p>
        <h2 className="font-display font-semibold text-2xl text-text mb-8">
          Your genetic risk across five dimensions
        </h2>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          {/* Radar */}
          <div className="bg-white rounded-2xl border border-gray-200/60 p-6 shadow-sm">
            <RiskRadar data={riskDimensions} height={300} />
          </div>

          {/* Bars */}
          <div className="space-y-5">
            {riskDimensions.map((dim) => (
              <RiskBar
                key={dim.key}
                label={dim.label}
                score={dim.score}
                baseline={dim.baseline}
              />
            ))}
            <p className="text-[13px] text-text-tertiary pt-2">
              Scores above 70% indicate elevated genetic influence. This does not
              guarantee any health outcome — lifestyle factors play a major role.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
