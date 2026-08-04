import { useState } from "react";
import { motion } from "framer-motion";
import HealthScoreRing from "../components/shared/HealthScoreRing";
import GeneCard from "../components/shared/GeneCard";
import RiskBar from "../components/shared/RiskBar";
import AIBadge from "../components/shared/AIBadge";
import RiskRadar from "../components/charts/RiskRadar";
import { healthSummary, geneCards, riskDimensions } from "../data/mockData";
import { Activity, Dna, ShieldAlert } from "lucide-react";

export default function GeneMap() {
  const [expandedGene, setExpandedGene] = useState(null);

  const levelDot =
    healthSummary.level === "low" ? "bg-risk-low shadow-risk-low/40" :
    healthSummary.level === "moderate" ? "bg-risk-moderate shadow-risk-moderate/40" :
    "bg-risk-high shadow-risk-high/40";

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* ================================================================
          HERO — Health Score + AI Summary
         ================================================================ */}
      <motion.section
        className="text-center mb-24"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        {/* Section label */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-light/60 text-primary mb-8">
          <Dna size={14} />
          <span className="text-[12px] font-bold uppercase tracking-[0.12em]">Your Genetic Health Profile</span>
        </div>

        {/* Score ring */}
        <div className="flex justify-center mb-8">
          <HealthScoreRing
            score={healthSummary.score}
            size={240}
            strokeWidth={12}
            label="Health Score"
            subtitle="/100"
            showGlow
          />
        </div>

        {/* Summary text */}
        <div className="max-w-xl mx-auto">
          <div className="flex items-center justify-center gap-2.5 mb-4">
            <span className={`inline-block w-2.5 h-2.5 rounded-full shadow-lg ${levelDot}`} />
            <span className="text-[15px] font-semibold text-text">
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

      {/* ================================================================
          GENE CARDS — 2x2 grid
         ================================================================ */}
      <section className="mb-24">
        <div className="flex items-center gap-3 mb-8">
          <Activity size={17} className="text-accent" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
              Your Genetic Traits
            </p>
            <h2 className="font-display font-bold text-[26px] text-text tracking-tight mt-0.5">
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

      {/* ================================================================
          RISK PROFILE — Radar + Bars
         ================================================================ */}
      <section>
        <div className="flex items-center gap-3 mb-8">
          <ShieldAlert size={17} className="text-risk-moderate" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
              Risk Profile
            </p>
            <h2 className="font-display font-bold text-[26px] text-text tracking-tight mt-0.5">
              Your genetic risk across five dimensions
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          {/* Radar chart */}
          <div className="premium-card p-6">
            <RiskRadar data={riskDimensions} height={320} />
          </div>

          {/* Risk bars */}
          <div className="space-y-6">
            {riskDimensions.map((dim) => (
              <RiskBar
                key={dim.key}
                label={dim.label}
                score={dim.score}
                baseline={dim.baseline}
              />
            ))}
            <div className="pt-3">
              <p className="text-[12px] text-text-tertiary leading-relaxed bg-gray-50 rounded-xl p-3">
                Scores above <span className="font-semibold text-risk-moderate">70%</span> indicate elevated genetic influence.
                This does not guarantee any health outcome —{" "}
                <span className="font-semibold text-accent">lifestyle factors</span> play a major role.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
