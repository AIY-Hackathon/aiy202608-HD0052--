import { useState } from "react";
import { motion } from "framer-motion";
import HealthScoreRing from "../components/shared/HealthScoreRing";
import GeneCard from "../components/shared/GeneCard";
import RiskBar from "../components/shared/RiskBar";
import RiskRadar from "../components/charts/RiskRadar";
import { useLocation } from "../components/layout/PageTransition";
import { healthSummary, geneCards, riskDimensions, geneticProfile, riskSummaryCards } from "../data/mockData";
import { Dna, ShieldAlert, ArrowRight } from "lucide-react";

/* ── Trait chip for the genetic profile section ── */
function TraitCard({ trait, index = 0 }) {
  return (
    <motion.div
      className="premium-card px-5 py-4 flex items-center gap-4"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 + index * 0.08, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -3 }}
    >
      <span className="text-2xl flex-shrink-0">{trait.icon}</span>
      <div className="min-w-0">
        <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
          {trait.label}
        </p>
        <p className="text-[14px] font-semibold text-text leading-snug">{trait.trait}</p>
        <p className="text-[12px] text-text-tertiary truncate">{trait.detail}</p>
      </div>
    </motion.div>
  );
}

/* ── Risk summary card ── */
function RiskSummaryCard({ card, index = 0 }) {
  return (
    <motion.div
      className={`premium-card px-6 py-5 border-l-3 ${card.bg} ${card.border}`}
      style={{ borderLeftWidth: 3, borderLeftColor: "var(--tw-border-color, currentColor)" }}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.45 + index * 0.07, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -3 }}
    >
      <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em] mb-1">
        {card.label}
      </p>
      <p className={`text-[13px] font-bold ${card.levelColor} mb-2`}>{card.level}</p>
      <p className="text-[12px] text-text-secondary leading-relaxed">{card.desc}</p>
    </motion.div>
  );
}

export default function GeneMap() {
  const { goTo } = useLocation();
  const [expandedGene, setExpandedGene] = useState(null);

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* ================================================================
          1. HERO — Product Identity
          "Who are we and what does this report tell you?"
         ================================================================ */}
      <motion.section
        className="mb-16"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
          {/* Left: brand + tagline */}
          <div>
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.18em] mb-3">
              GenoLife AI
            </p>
            <h1 className="font-display font-bold text-[26px] sm:text-[30px] text-text tracking-tight leading-tight mb-2">
              AI Genetic Health Report
            </h1>
            <p className="text-[15px] text-text-secondary max-w-md leading-relaxed">
              Your genes reveal tendencies. <span className="text-text-tertiary">Your choices shape outcomes.</span>
            </p>
          </div>

          {/* Right: report metadata */}
          <div className="flex items-center gap-4 text-[11px] text-text-tertiary">
            <div className="text-right">
              <p className="font-mono text-text-secondary font-semibold">#GNO-2026-0042</p>
              <p>Generated Aug 2026</p>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-right">
              <p className="text-text-secondary font-semibold">Alex</p>
              <p>Age 30 · Male</p>
            </div>
          </div>
        </div>
      </motion.section>

      {/* ================================================================
          2. PERSONAL GENETIC PROFILE
          "What are your genetic tendencies?"
         ================================================================ */}
      <section className="mb-14">
        <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-4">
          Genetic Profile
        </p>

        {/* 4 trait cards in a horizontal row on desktop, 2x2 on mobile */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
          {geneticProfile.map((trait, i) => (
            <TraitCard key={trait.key} trait={trait} index={i} />
          ))}
        </div>
      </section>

      {/* ================================================================
          3. HEALTH INDEX
          The score + what it's calculated from
         ================================================================ */}
      <section className="mb-14">
        <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-4">
          Health Index
        </p>

        <div className="flex flex-col lg:flex-row items-center gap-8 lg:gap-12">
          {/* Score ring */}
          <motion.div
            className="flex-shrink-0"
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          >
            <HealthScoreRing
              score={healthSummary.score}
              size={210}
              strokeWidth={11}
              label="Genetic Health Index"
              subtitle="/100"
              showGlow
            />
          </motion.div>

          {/* Methodology — right side on desktop, below on mobile */}
          <div className="flex-1 max-w-xs lg:max-w-none mx-auto lg:mx-0">
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em] mb-4 text-center lg:text-left">
              Calculated from
            </p>

            <div className="flex lg:flex-col items-center lg:items-stretch justify-center gap-2 lg:gap-3 flex-wrap lg:flex-nowrap">
              {[
                { label: "Genetic variants", desc: "4 key genes analyzed", color: "border-l-primary" },
                { label: "Family history", desc: "3-generation health background", color: "border-l-accent" },
                { label: "Lifestyle factors", desc: "Sleep, diet, exercise, stress", color: "border-l-risk-moderate" },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  className="premium-card px-4 py-3 border-l-3 flex-1 lg:flex-none"
                  style={{ borderLeftWidth: 3, borderLeftColor: i === 0 ? "var(--color-primary)" : i === 1 ? "var(--color-accent)" : "var(--color-risk-moderate)" }}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.35 + i * 0.08, duration: 0.4 }}
                >
                  <p className="text-[13px] font-semibold text-text">{item.label}</p>
                  <p className="text-[11px] text-text-tertiary">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ================================================================
          4. KEY RISK SUMMARY
          3 cards — one sentence each
         ================================================================ */}
      <section className="mb-16">
        <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-4">
          Key Findings
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {riskSummaryCards.map((card, i) => (
            <RiskSummaryCard key={card.key} card={card} index={i} />
          ))}
        </div>
      </section>

      {/* ================================================================
          5. NEXT STEP — CTA to Simulation
         ================================================================ */}
      <motion.section
        className="mb-24"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <div className="premium-card px-6 py-6 sm:px-8 sm:py-7 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r from-white to-primary-light/20">
          <div>
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em] mb-1">
              Explore your health journey
            </p>
            <p className="text-[15px] font-semibold text-text leading-snug">
              See how lifestyle changes affect your genetic risk profile.
            </p>
          </div>
          <button
            onClick={() => goTo("simulation")}
            className="flex-shrink-0 inline-flex items-center gap-2 px-5 py-3 rounded-full bg-primary text-white text-[14px] font-semibold hover:bg-primary-600 transition-colors shadow-lg shadow-primary/20 cursor-pointer"
            style={{ border: "none" }}
          >
            Simulate Lifestyle Impact
            <ArrowRight size={16} />
          </button>
        </div>
      </motion.section>

      {/* ================================================================
          6. GENE CARDS — 2x2 grid (detailed view for those who scroll)
         ================================================================ */}
      <section className="mb-24">
        <div className="flex items-center gap-3 mb-8">
          <Dna size={17} className="text-accent" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
              Detailed Gene Analysis
            </p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">
              Dive deeper into your genetic traits
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
          7. RISK PROFILE — Radar + Bars
         ================================================================ */}
      <section>
        <div className="flex items-center gap-3 mb-8">
          <ShieldAlert size={17} className="text-risk-moderate" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
              Risk Profile
            </p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">
              Five dimensions of genetic influence
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
          <div className="premium-card p-6">
            <RiskRadar data={riskDimensions} height={320} />
          </div>

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
