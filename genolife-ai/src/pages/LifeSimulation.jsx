import { useState, useCallback, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import HealthScoreRing from "../components/shared/HealthScoreRing";
import AnimatedNumber from "../components/shared/AnimatedNumber";
import SliderControl from "../components/shared/SliderControl";
import RecommendationCard from "../components/shared/RecommendationCard";
import AIBadge from "../components/shared/AIBadge";
import RiskTrendLine from "../components/charts/RiskTrendLine";
import BeforeAfterBar from "../components/charts/BeforeAfterBar";
import { simulate, getRecommendations } from "../api/client";
import { useLocation } from "../components/layout/PageTransition";
import { useLanguage } from "../i18n";
import {
  simulationDefaults,
  simulationFactors,
  calculateHealthScore,
  calculateRiskDimensions,
  generateTrendData,
  generateRecommendations,
  thirtyDayPlan as mockPlan,
} from "../data/mockData";
import {
  Sliders,
  TrendingUp,
  Zap,
  RotateCcw,
  Target,
  Clock,
  Star,
  CheckCircle2,
  ChevronDown,
} from "lucide-react";

export default function LifeSimulation() {
  const { uploaded } = useLocation();
  const { t } = useLanguage();
  const [factors, setFactors] = useState(simulationDefaults);
  const [checkedRecs, setCheckedRecs] = useState(new Set());

  // API 状态
  const [apiResult, setApiResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  // 防抖 timer
  const debounceRef = useRef(null);

  // ── 30 天计划状态 ──
  const [checkedTasks, setCheckedTasks] = useState(new Set());
  const [expandedWeek, setExpandedWeek] = useState(0);
  const [plan, setPlan] = useState(null);
  const [planLoading, setPlanLoading] = useState(true);

  // 初始加载 + 每次 factors 变化后防抖请求
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    let cancelled = false;
    debounceRef.current = setTimeout(async () => {
      setSimLoading(true);
      try {
        const result = await simulate(factors);
        if (!cancelled) setApiResult(result);
      } catch {
        if (!cancelled) setApiResult(null);
      } finally {
        if (!cancelled) setSimLoading(false);
      }
    }, 300);

    return () => { cancelled = true; };
  }, [factors]);

  // 加载 30 天计划
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setPlanLoading(true);
        const data = await getRecommendations();
        if (!cancelled && data?.thirtyDayPlan) {
          setPlan(data.thirtyDayPlan);
        }
      } catch {
        if (!cancelled) setPlan(null);
      } finally {
        if (!cancelled) setPlanLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  // 有 API 结果则用 API，没上传则锁住显示 "--"
  const healthScore = uploaded ? (apiResult?.healthScore ?? null) : null;
  const optimizedScore = uploaded ? (apiResult?.optimizedScore ?? null) : null;
  const currentRisks = uploaded ? (apiResult?.riskDimensions ?? []) : [];
  const optimizedFactors = { sleep: 8, exercise: 5, diet: 8, stress: 3 };
  const optimizedRisks = uploaded ? (apiResult?.riskDimensions ? calculateRiskDimensions(optimizedFactors) : []) : [];
  const trendData = uploaded ? (apiResult?.trendData ?? []) : [];
  const recommendations = uploaded ? (apiResult?.recommendations ?? []) : [];

  const handleFactorChange = useCallback((key, value) => {
    setFactors((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleReset = () => setFactors(simulationDefaults);
  const thirtyDayPlan = plan || mockPlan;

  const toggleRec = (id) => {
    setCheckedRecs((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleTask = (id) => {
    setCheckedTasks((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const scoreColor = !uploaded || healthScore == null ? "text-text-tertiary" :
    healthScore >= 85 ? "text-risk-low" :
    healthScore >= 70 ? "text-risk-moderate" :
    "text-risk-high";

  // 30 天计划统计数据
  const totalTasks = thirtyDayPlan.weeks.reduce((s, w) => s + w.tasks.length, 0);
  const completedTasks = checkedTasks.size;
  const progressPct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
  const estimatedScoreGain = Math.round(progressPct * 0.15);

  /* ── Skeleton placeholder ── */
  function SkeletonBlock({ className = "" }) {
    return <div className={`animate-pulse bg-gray-100 rounded-xl ${className}`} />;
  }

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
          <span className="text-[12px] font-bold uppercase tracking-[0.12em]">{t("simulation", "badge")}</span>
        </div>

        <h2 className="font-display font-bold text-[32px] text-text mb-3 tracking-tight">
          {t("simulation", "title")}
        </h2>
        <p className="text-[15px] text-text-secondary mb-10 max-w-md mx-auto leading-relaxed">
          {t("simulation", "subtitle")}
        </p>

        <div className="flex justify-center mb-8">
          <HealthScoreRing
            score={healthScore ?? "--"}
            size={220}
            strokeWidth={10}
            label={simLoading ? t("simulation", "calculating") : uploaded ? t("simulation", "currentScore") : t("simulation", "uploadToUnlock")}
            subtitle={uploaded ? "/100" : ""}
            showGlow={uploaded}
          />
        </div>

        {/* Before / After comparison */}
        <motion.div
          className="inline-flex items-center gap-10 premium-card px-10 py-5"
          layout
        >
          <div className="text-center">
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-1">{t("simulation", "current")}</p>
            <p className={`font-display font-bold text-[36px] tracking-tight leading-none ${uploaded ? scoreColor : "text-text-tertiary"}`}>
              {uploaded ? <AnimatedNumber value={healthScore} duration={500} /> : "--"}
            </p>
          </div>

          <div className="flex flex-col items-center gap-1">
            <div className="w-px h-10 bg-gray-200" />
            <TrendingUp size={16} className="text-accent" />
            <div className="w-px h-10 bg-gray-200" />
          </div>

          <div className="text-center">
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-1">{t("simulation", "potential")}</p>
            <p className="font-display font-bold text-[36px] tracking-tight leading-none text-risk-low">
              {uploaded ? optimizedScore : "--"}
            </p>
          </div>

          <div className="flex flex-col items-center gap-1">
            <div className="w-px h-10 bg-gray-200" />
            <Zap size={16} className="text-ai" />
            <div className="w-px h-10 bg-gray-200" />
          </div>

          <div className="text-center">
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-1">{t("simulation", "upside")}</p>
            <p className="font-display font-bold text-[36px] tracking-tight leading-none text-accent">
              {uploaded && healthScore && optimizedScore ? `+${optimizedScore - healthScore}` : "--"}
            </p>
          </div>
        </motion.div>
      </motion.section>

      {/* ================================================================
          DATA AREA — 仅在已上传后显示
         ================================================================ */}
      {uploaded ? (
      <>
      {/* ================================================================
          TWO-COLUMN: Sliders + Charts
         ================================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-10 mb-20">
        {/* LEFT: Sliders */}
        <div className="premium-card p-6 space-y-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-primary-light flex items-center justify-center">
                <Sliders size={15} className="text-primary" />
              </div>
              <h3 className="font-display font-bold text-[17px] text-text">{t("simulation", "yourLifestyle")}</h3>
            </div>
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 text-[12px] font-semibold text-text-tertiary hover:text-text transition-colors px-3 py-1.5 rounded-full hover:bg-gray-100 cursor-pointer"
              style={{ background: "none", border: "none" }}
            >
              <RotateCcw size={12} />
              {t("simulation", "reset")}
            </button>
          </div>

          {simulationFactors.map((factor) => (
            <SliderControl
              key={factor.key}
              factor={factor}
              value={factors[factor.key]}
              label={t("simulation", `slider_${factor.key}_label`)}
              description={t("simulation", `slider_${factor.key}_desc`)}
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
                {t("simulation", "healthTrajectory")}
              </h3>
            </div>
            <p className="text-[12px] text-text-tertiary mb-5">
              {t("simulation", "projectedRisk")}
            </p>
            <RiskTrendLine data={trendData} height={280} />
            <p className="mt-3 text-[11px] text-text-tertiary leading-relaxed bg-blue-50/40 border border-blue-100/60 rounded-xl px-3 py-2.5">
              {t("simulation", "trajectoryHint")}
            </p>
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
                {t("simulation", "riskByDimension")}
              </h3>
            </div>
            <p className="text-[12px] text-text-tertiary mb-5">
              {t("simulation", "riskByDimensionDesc")}
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
              {t("simulation", "personalizedActions")}
            </p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">
              {t("simulation", "whatToFocus")}
            </h2>
          </div>
        </div>

        {recommendations.length === 0 ? (
          <div className="premium-card p-10 text-center bg-accent-light/20 border-accent/20">
            <div className="text-4xl mb-4">🎉</div>
            <p className="font-display font-bold text-xl text-accent">
              {t("simulation", "optimizedWell")}
            </p>
            <p className="text-[14px] text-text-secondary mt-2">
              {t("simulation", "keepHabits")}
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

      {/* ================================================================
          30-DAY HEALTH PLAN
         ================================================================ */}
      <section className="mt-20">
        <div className="flex items-center gap-3 mb-6">
          <Target size={17} className="text-accent" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
              {t("simulation", "planTitle")}
            </p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">
              {t("simulation", "planSubtitle")}
            </h2>
          </div>
        </div>

        {/* Goal */}
        {planLoading ? (
          <SkeletonBlock className="h-16 w-96 rounded-2xl mb-6" />
        ) : (
          <div className="premium-card inline-flex items-center gap-4 px-6 py-5 mb-6">
            <div className="w-10 h-10 rounded-xl bg-accent-light flex items-center justify-center">
              <Target size={20} className="text-accent" />
            </div>
            <div>
              <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em]">{t("simulation", "primaryGoal")}</p>
              <p className="text-[15px] font-semibold text-text leading-snug">{thirtyDayPlan.goal}</p>
            </div>
            <AIBadge />
          </div>
        )}

        {/* Progress bar */}
        <div className="premium-card p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-accent-light flex items-center justify-center">
                <CheckCircle2 size={16} className="text-accent" />
              </div>
              <h3 className="font-display font-bold text-[17px] text-text">{t("simulation", "yourProgress")}</h3>
            </div>
            <span className="text-[13px] font-semibold text-text-secondary tabular-nums">
              {completedTasks} / {totalTasks} {t("simulation", "tasks")}
            </span>
          </div>
          <div className="h-3 rounded-full bg-gray-100 overflow-hidden relative">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-accent to-emerald-400"
              initial={{ width: 0 }}
              animate={{ width: `${progressPct}%` }}
              transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
            />
            {[25, 50, 75].map((pct) => (
              <div key={pct} className="absolute top-0 bottom-0 w-px bg-white/60" style={{ left: `${pct}%` }} />
            ))}
          </div>
          <div className="flex items-center gap-2 mt-4">
            <TrendingUp size={14} className="text-accent" />
            <p className="text-[12px] text-text-tertiary">
              {t("simulation", "estimatedImprovement")}{" "}
              <span className="font-bold text-accent">+{estimatedScoreGain}</span> {t("simulation", "points")}
            </p>
          </div>
        </div>

        {/* 4-week timeline */}
        {planLoading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => <SkeletonBlock key={i} className="h-20 rounded-2xl" />)}
          </div>
        ) : (
          <div className="space-y-4 mb-20">
            {thirtyDayPlan.weeks.map((week, wi) => {
              const weekTaskIds = week.tasks.map((_, ti) => `${wi}-${ti}`);
              const weekProgress = weekTaskIds.filter((id) => checkedTasks.has(id)).length;
              const weekComplete = week.tasks.every((_, ti) => checkedTasks.has(`${wi}-${ti}`));
              const weekKeys = ["foundation", "activation", "integration", "sustain"];
              const weekLabel = t("simulation", weekKeys[wi] || week.label);
              const weekTheme = t("simulation", weekKeys[wi] + "Desc" || week.theme);

              return (
                <motion.div
                  key={wi}
                  className={`premium-card overflow-hidden ${weekComplete ? "ring-2 ring-accent/20 bg-accent-light/10" : ""}`}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.18 + wi * 0.06 }}
                >
                  <button
                    className="w-full flex items-center justify-between px-6 py-5 text-left cursor-pointer hover:bg-gray-50/50 transition-colors"
                    style={{ background: "none", border: "none" }}
                    onClick={() => setExpandedWeek(expandedWeek === wi ? -1 : wi)}
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-11 h-11 rounded-2xl flex items-center justify-center font-display font-bold text-[15px] shadow-sm ${
                        weekComplete ? "bg-accent text-white" : "bg-primary-light text-primary"
                      }`}>
                        {weekComplete ? <CheckCircle2 size={18} /> : wi + 1}
                      </div>
                      <div>
                        <p className={`text-[13px] font-bold uppercase tracking-[0.08em] ${weekComplete ? "text-accent" : "text-text-tertiary"}`}>
                          {weekLabel}
                        </p>
                        <p className="text-[14px] text-text-secondary mt-0.5 font-medium">{weekTheme}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="hidden sm:flex items-center gap-1.5">
                        <span className="text-[11px] text-text-tertiary font-medium">{weekProgress}/{week.tasks.length}</span>
                        <div className="w-16 h-1.5 rounded-full bg-gray-100 overflow-hidden">
                          <div className="h-full rounded-full bg-accent transition-all duration-500" style={{ width: `${(weekProgress / week.tasks.length) * 100}%` }} />
                        </div>
                      </div>
                      <motion.span animate={{ rotate: expandedWeek === wi ? 180 : 0 }} transition={{ duration: 0.25 }} className="text-text-tertiary">
                        <ChevronDown size={20} />
                      </motion.span>
                    </div>
                  </button>
                  <AnimatePresence>
                    {expandedWeek === wi && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                        className="overflow-hidden"
                      >
                        <div className="px-6 pb-5 space-y-3 border-t border-gray-100 pt-4">
                          {week.tasks.map((task, ti) => {
                            const taskId = `${wi}-${ti}`;
                            const done = checkedTasks.has(taskId);
                            return (
                              <motion.div
                                key={taskId}
                                className={`flex items-start gap-4 p-4 rounded-2xl transition-all duration-200 cursor-pointer ${
                                  done ? "bg-accent-light/30 border border-accent/20" : "hover:bg-gray-50 border border-transparent"
                                }`}
                                onClick={() => toggleTask(taskId)}
                                whileHover={{ scale: 1.01 }}
                              >
                                <button
                                  className={`mt-0.5 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 cursor-pointer ${
                                    done ? "bg-accent border-accent text-white shadow-lg shadow-accent/25" : "border-gray-200 hover:border-accent/50 bg-white"
                                  }`}
                                >
                                  {done && (
                                    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                                      <path d="M2.5 6.5L5.5 9.5L10.5 3.5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                    </svg>
                                  )}
                                </button>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-lg ${done ? "bg-accent text-white" : "bg-gray-100 text-text-tertiary"}`}>
                                      {task.day}
                                    </span>
                                    <span className={`font-semibold text-[14px] ${done ? "text-accent" : "text-text"}`}>
                                      {task.title}
                                    </span>
                                  </div>
                                  <p className="text-[13px] text-text-secondary leading-relaxed">{task.desc}</p>
                                </div>
                                {done && <CheckCircle2 size={18} className="text-accent flex-shrink-0 mt-0.5" />}
                              </motion.div>
                            );
                          })}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* Daily anchors */}
        <div className="flex items-center gap-3 mb-8">
          <Star size={17} className="text-risk-moderate" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">{t("simulation", "dailyAnchors")}</p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">{t("simulation", "dailyAnchorsTitle")}</h2>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          {[
            { icon: Clock, title: t("simulation", "morningLightTitle"), desc: t("simulation", "morningLightDesc") },
            { icon: Target, title: t("simulation", "moveDailyTitle"), desc: t("simulation", "moveDailyDesc") },
            { icon: Star, title: t("simulation", "trackReflectTitle"), desc: t("simulation", "trackReflectDesc") },
          ].map((tip, i) => (
            <motion.div
              key={i}
              className="premium-card p-6"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45 + i * 0.08 }}
              whileHover={{ y: -6 }}
            >
              <div className="w-10 h-10 rounded-xl bg-primary-light flex items-center justify-center mb-4">
                <tip.icon size={20} className="text-primary" />
              </div>
              <h4 className="font-display font-bold text-[16px] text-text mb-2">{tip.title}</h4>
              <p className="text-[13px] text-text-secondary leading-relaxed">{tip.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
      </>
      ) : (
        /* 未上传时：显示引导占位 */
        <motion.section
          className="mb-14 text-center py-20"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-6">
            <TrendingUp size={26} className="text-text-tertiary" />
          </div>
          <h2 className="font-display font-bold text-[20px] text-text mb-2">
            {t("simulation", "uploadFirst")}
          </h2>
          <p className="text-[14px] text-text-tertiary max-w-md mx-auto leading-relaxed">
            {t("common", "uploadFirst")}
          </p>
        </motion.section>
      )}
    </div>
  );
}
