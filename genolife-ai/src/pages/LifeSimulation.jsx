import { useState, useMemo, useCallback } from "react";
import { motion } from "framer-motion";
import HealthScoreRing from "../components/shared/HealthScoreRing";
import AnimatedNumber from "../components/shared/AnimatedNumber";
import SliderControl from "../components/shared/SliderControl";
import RecommendationCard from "../components/shared/RecommendationCard";
import RiskTrendLine from "../components/charts/RiskTrendLine";
import BeforeAfterBar from "../components/charts/BeforeAfterBar";
import {
  simulationDefaults,
  simulationFactors,
  calculateHealthScore,
  calculateRiskDimensions,
  generateTrendData,
  generateRecommendations,
} from "../data/mockData";

export default function LifeSimulation() {
  const [factors, setFactors] = useState(simulationDefaults);
  const [checkedRecs, setCheckedRecs] = useState(new Set());

  const healthScore = useMemo(() => calculateHealthScore(factors), [factors]);
  const optimizedFactors = { sleep: 8, exercise: 5, diet: 8, stress: 3 };
  const optimizedScore = useMemo(() => calculateHealthScore(optimizedFactors), []);

  const currentRisks = useMemo(() => calculateRiskDimensions(factors), [factors]);
  const optimizedRisks = useMemo(
    () => calculateRiskDimensions(optimizedFactors),
    []
  );

  const trendData = useMemo(() => generateTrendData(factors), [factors]);
  const recommendations = useMemo(() => generateRecommendations(factors), [factors]);

  const handleFactorChange = useCallback((key, value) => {
    setFactors((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleReset = () => setFactors(simulationDefaults);

  const toggleRec = (id) => {
    setCheckedRecs((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  // Score color
  const scoreColor =
    healthScore >= 85 ? "text-risk-low" :
    healthScore >= 70 ? "text-risk-moderate" :
    "text-risk-high";

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* ─────────────────────────────────────────────
          Hero: Live health score
         ───────────────────────────────────────────── */}
      <motion.section
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <p className="text-[13px] font-semibold text-text-tertiary uppercase tracking-[0.15em] mb-6">
          Life Simulation
        </p>
        <h2 className="font-display font-semibold text-2xl text-text mb-2">
          Your genes aren't your destiny
        </h2>
        <p className="text-[15px] text-text-secondary mb-8 max-w-lg mx-auto leading-relaxed">
          Adjust the lifestyle factors below and watch how your health projection changes in real time.
        </p>

        <div className="flex justify-center mb-6">
          <HealthScoreRing score={healthScore} size={220} strokeWidth={10} />
        </div>

        {/* Before / After comparison */}
        <div className="inline-flex items-center gap-8 bg-white rounded-2xl border border-gray-200/60 px-8 py-4 shadow-sm">
          <div className="text-center">
            <p className="text-[11px] text-text-tertiary uppercase tracking-wider mb-1">Current</p>
            <p className={`font-display font-bold text-3xl ${scoreColor}`}>
              <AnimatedNumber value={healthScore} duration={600} />
            </p>
          </div>
          <div className="w-px h-10 bg-gray-200" />
          <div className="text-center">
            <p className="text-[11px] text-text-tertiary uppercase tracking-wider mb-1">Potential</p>
            <p className="font-display font-bold text-3xl text-risk-low">
              {optimizedScore}
            </p>
          </div>
          <div className="w-px h-10 bg-gray-200" />
          <div className="text-center">
            <p className="text-[11px] text-text-tertiary uppercase tracking-wider mb-1">Upside</p>
            <p className="font-display font-bold text-3xl text-accent">
              +{optimizedScore - healthScore}
            </p>
          </div>
        </div>
      </motion.section>

      {/* ─────────────────────────────────────────────
          Two-column: Sliders + Charts
         ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-10 mb-16">
        {/* Left: Sliders */}
        <div className="bg-white rounded-2xl border border-gray-200/60 p-6 shadow-sm space-y-7 self-start">
          <div className="flex items-center justify-between">
            <h3 className="font-display font-semibold text-lg text-text">Your Lifestyle</h3>
            <button
              onClick={handleReset}
              className="text-[13px] text-text-tertiary hover:text-text transition-colors cursor-pointer"
              style={{ background: "none", border: "none" }}
            >
              Reset
            </button>
          </div>

          {simulationFactors.map((factor) => (
            <SliderControl
              key={factor.key}
              factor={factor}
              value={factors[factor.key]}
              onChange={handleFactorChange}
            />
          ))}
        </div>

        {/* Right: Charts */}
        <div className="space-y-8">
          {/* Trend line */}
          <motion.div
            className="bg-white rounded-2xl border border-gray-200/60 p-6 shadow-sm"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <h3 className="font-display font-semibold text-lg text-text mb-1">
              Health Risk Trajectory
            </h3>
            <p className="text-[13px] text-text-tertiary mb-4">
              Projected risk level over time — current vs optimized lifestyle
            </p>
            <RiskTrendLine data={trendData} height={280} />
          </motion.div>

          {/* Before/After bars */}
          <motion.div
            className="bg-white rounded-2xl border border-gray-200/60 p-6 shadow-sm"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <h3 className="font-display font-semibold text-lg text-text mb-1">
              Risk by Dimension: Now vs Optimized
            </h3>
            <p className="text-[13px] text-text-tertiary mb-4">
              Compare your current risk profile with your genetic potential
            </p>
            <BeforeAfterBar before={currentRisks} after={optimizedRisks} height={260} />
          </motion.div>
        </div>
      </div>

      {/* ─────────────────────────────────────────────
          Dynamic recommendations
         ───────────────────────────────────────────── */}
      <section>
        <p className="text-[13px] font-semibold text-text-tertiary uppercase tracking-[0.15em] mb-1">
          Personalized Actions
        </p>
        <h2 className="font-display font-semibold text-2xl text-text mb-6">
          What to focus on right now
        </h2>

        {recommendations.length === 0 ? (
          <div className="bg-accent-light rounded-2xl border border-accent/30 p-8 text-center">
            <p className="text-lg font-display font-semibold text-accent">
              🎉 Your lifestyle is already well-optimized for your genetics.
            </p>
            <p className="text-[15px] text-text-secondary mt-2">
              Keep maintaining your healthy habits. Your health trajectory looks strong.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((rec, i) => (
              <RecommendationCard
                key={rec.id}
                rec={rec}
                index={i}
                checked={checkedRecs.has(rec.id)}
                onToggle={toggleRec}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
