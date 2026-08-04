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
import { Sliders, TrendingUp, Zap, RotateCcw } from "lucide-react";

export default function LifeSimulation() {
  const [factors, setFactors] = useState(simulationDefaults);
  const [checkedRecs, setCheckedRecs] = useState(new Set());

  const healthScore = useMemo(() => calculateHealthScore(factors), [factors]);
  const optimizedFactors = { sleep: 8, exercise: 5, diet: 8, stress: 3 };
  const optimizedScore = useMemo(() => calculateHealthScore(optimizedFactors), []);

  const currentRisks = useMemo(() => calculateRiskDimensions(factors), [factors]);
  const optimizedRisks = useMemo(() => calculateRiskDimensions(optimizedFactors), []);
  const trendData = useMemo(() => generateTrendData(factors), [factors]);
  const recommendations = useMemo(() => generateRecommendations(factors), [factors]);

  const handleFactorChange = useCallback((key, value) => {
    setFactors((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleReset = () => setFactors(simulationDefaults);
  const toggleRec = (id) => {
    setCheckedRecs((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const scoreColor =
    healthScore >= 85 ? "text-risk-low" :
    healthScore >= 70 ? "text-risk-moderate" :
    "text-risk-high";

  const upside = optimizedScore - healthScore;

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* ================================================================
          HERO — Live health score + Before/After
         ================================================================ */}
      <motion.section
        className="text-center mb-20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-light/60 text-primary mb-8">
          <Sliders size={14} />
          <span className="text-[12px] font-bold uppercase tracking-[0.12em]">Life Simulation</span>
        </div>

        <h2 className="font-display font-bold text-[32px] text-text mb-3 tracking-tight">
          Your genes aren't your destiny
        </h2>
        <p className="text-[15px] text-text-secondary mb-10 max-w-md mx-auto leading-relaxed">
          Adjust the lifestyle factors below and watch how your health projection changes — in real time.
        </p>

        <div className="flex justify-center mb-8">
          <HealthScoreRing
            score={healthScore}
            size={220}
            strokeWidth={10}
            label="Current Score"
            subtitle={`/100`}
            showGlow
          />
        </div>

        {/* Before / After comparison */}
        <motion.div
          className="inline-flex items-center gap-10 premium-card px-10 py-5"
          layout
        >
          <div className="text-center">
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-1">Current</p>
            <p className={`font-display font-bold text-[36px] tracking-tight leading-none ${scoreColor}`}>
              <AnimatedNumber value={healthScore} duration={500} />
            </p>
          </div>

          <div className="flex flex-col items-center gap-1">
            <div className="w-px h-10 bg-gray-200" />
            <TrendingUp size={16} className="text-accent" />
            <div className="w-px h-10 bg-gray-200" />
          </div>

          <div className="text-center">
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-1">Potential</p>
            <p className="font-display font-bold text-[36px] tracking-tight leading-none text-risk-low">
              {optimizedScore}
            </p>
          </div>

          <div className="flex flex-col items-center gap-1">
            <div className="w-px h-10 bg-gray-200" />
            <Zap size={16} className="text-ai" />
            <div className="w-px h-10 bg-gray-200" />
          </div>

          <div className="text-center">
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-1">Upside</p>
            <p className="font-display font-bold text-[36px] tracking-tight leading-none text-accent">
              +{upside}
            </p>
          </div>
        </motion.div>
      </motion.section>

      {/* ================================================================
          TWO-COLUMN: Sliders + Charts
         ================================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-10 mb-20">
        {/* LEFT: Sliders */}
        <div className="premium-card p-6 space-y-8 self-start sticky top-24">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-primary-light flex items-center justify-center">
                <Sliders size={15} className="text-primary" />
              </div>
              <h3 className="font-display font-bold text-[17px] text-text">Your Lifestyle</h3>
            </div>
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 text-[12px] font-semibold text-text-tertiary hover:text-text transition-colors px-3 py-1.5 rounded-full hover:bg-gray-100 cursor-pointer"
              style={{ background: "none", border: "none" }}
            >
              <RotateCcw size={12} />
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

        {/* RIGHT: Charts */}
        <div className="space-y-8">
          {/* Trend line */}
          <motion.div
            className="premium-card p-6"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.12 }}
          >
            <div className="flex items-center gap-2.5 mb-1">
              <TrendingUp size={16} className="text-primary" />
              <h3 className="font-display font-bold text-[16px] text-text">
                Health Risk Trajectory
              </h3>
            </div>
            <p className="text-[12px] text-text-tertiary mb-5">
              Projected risk level over time — current vs optimized lifestyle
            </p>
            <RiskTrendLine data={trendData} height={280} />
          </motion.div>

          {/* Before / After bars */}
          <motion.div
            className="premium-card p-6"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center gap-2.5 mb-1">
              <Zap size={16} className="text-accent" />
              <h3 className="font-display font-bold text-[16px] text-text">
                Risk by Dimension
              </h3>
            </div>
            <p className="text-[12px] text-text-tertiary mb-5">
              Current risk profile vs your genetic potential with an optimized lifestyle
            </p>
            <BeforeAfterBar before={currentRisks} after={optimizedRisks} height={260} />
          </motion.div>
        </div>
      </div>

      {/* ================================================================
          DYNAMIC RECOMMENDATIONS
         ================================================================ */}
      <section>
        <div className="flex items-center gap-3 mb-6">
          <Zap size={17} className="text-ai" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
              Personalized Actions
            </p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">
              What to focus on right now
            </h2>
          </div>
        </div>

        {recommendations.length === 0 ? (
          <div className="premium-card p-10 text-center bg-accent-light/20 border-accent/20">
            <div className="text-4xl mb-4">🎉</div>
            <p className="font-display font-bold text-xl text-accent">
              Your lifestyle is well-optimized
            </p>
            <p className="text-[14px] text-text-secondary mt-2">
              Keep maintaining your healthy habits. Your health trajectory looks excellent.
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
