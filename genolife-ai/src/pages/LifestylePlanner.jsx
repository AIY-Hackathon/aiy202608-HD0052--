import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AIBadge from "../components/shared/AIBadge";
import { useLanguage } from "../i18n";
import { getRecommendations } from "../api/client";
import { thirtyDayPlan as mockPlan } from "../data/mockData";
import { ChevronDown, Target, Clock, Star, CheckCircle2, TrendingUp } from "lucide-react";

/* ── Skeleton placeholder ── */
function SkeletonBlock({ className = "" }) {
  return (
    <div className={`animate-pulse bg-gray-100 rounded-xl ${className}`} />
  );
}

export default function LifestylePlanner() {
  const { t } = useLanguage();
  const [checkedTasks, setCheckedTasks] = useState(new Set());
  const [expandedWeek, setExpandedWeek] = useState(0);

  // API 数据
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        const data = await getRecommendations();
        if (!cancelled && data?.thirtyDayPlan) {
          setPlan(data.thirtyDayPlan);
        }
      } catch {
        // 降级到 mock
        if (!cancelled) setPlan(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const thirtyDayPlan = plan || mockPlan;

  const toggleTask = (id) => {
    setCheckedTasks((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const totalTasks = thirtyDayPlan.weeks.reduce((s, w) => s + w.tasks.length, 0);
  const completedTasks = checkedTasks.size;
  const progressPct = Math.round((completedTasks / totalTasks) * 100);
  const estimatedScoreGain = Math.round(progressPct * 0.15);

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* ================================================================
          HERO — Goal
         ================================================================ */}
      <motion.section
        className="mb-20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-light/60 text-primary mb-8">
          <Target size={14} />
          <span className="text-[12px] font-bold uppercase tracking-[0.12em]">{t("simulation", "planTitle")}</span>
        </div>

        <h2 className="font-display font-bold text-[32px] text-text mb-2 tracking-tight">
          {t("simulation", "planSubtitle")}
        </h2>
        <p className="text-[15px] text-text-secondary mb-8 max-w-xl leading-relaxed">
          {t("simulation", "planDesc")}
        </p>

        {/* Goal card */}
        {loading ? (
          <SkeletonBlock className="inline-flex h-16 w-96 rounded-2xl" />
        ) : (
          <div className="premium-card inline-flex items-center gap-4 px-6 py-5">
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
      </motion.section>

      {/* ================================================================
          PROGRESS BAR
         ================================================================ */}
      <motion.section
        className="mb-16 premium-card p-6"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12 }}
      >
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
          {/* Tick marks */}
          {[25, 50, 75].map((pct) => (
            <div
              key={pct}
              className="absolute top-0 bottom-0 w-px bg-white/60"
              style={{ left: `${pct}%` }}
            />
          ))}
        </div>

        <div className="flex items-center gap-2 mt-4">
          <TrendingUp size={14} className="text-accent" />
          <p className="text-[12px] text-text-tertiary">
            {t("simulation", "estimatedImprovement")}{" "}
            <span className="font-bold text-accent">+{estimatedScoreGain}</span> {t("simulation", "points")}
          </p>
        </div>
      </motion.section>

      {/* ================================================================
          4-WEEK TIMELINE
         ================================================================ */}
      <section className="mb-20">
        <div className="flex items-center gap-3 mb-8">
          <Clock size={17} className="text-primary" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
              {t("simulation", "weeklyBreakdown")}
            </p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">
              {t("simulation", "weeklyBreakdownTitle")}
            </h2>
          </div>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <SkeletonBlock key={"lpSk" + i} className="h-20 rounded-2xl" />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {thirtyDayPlan.weeks.map((week, wi) => {
              const weekComplete = week.tasks.every((_, ti) => checkedTasks.has(`${wi}-${ti}`));
              const weekTaskIds = week.tasks.map((_, ti) => `${wi}-${ti}`);
              const weekProgress = weekTaskIds.filter((id) => checkedTasks.has(id)).length;

              // Map week index to i18n keys
              const weekKeys = ["foundation", "activation", "integration", "sustain"];
              const weekLabel = t("simulation", weekKeys[wi] || week.label);
              const weekTheme = t("simulation", weekKeys[wi] + "Desc" || week.theme);
              // Map task index to i18n task keys
              const taskKeys = weekKeys[wi] + "Tasks";
              const taskDescKeys = weekKeys[wi] + "TaskDescs";

              return (
                <motion.div
                  key={wi}
                  className={`premium-card overflow-hidden ${
                    weekComplete ? "ring-2 ring-accent/20 bg-accent-light/10" : ""
                  }`}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.18 + wi * 0.06 }}
                >
                  {/* Week header */}
                  <button
                    className="w-full flex items-center justify-between px-6 py-5 text-left cursor-pointer hover:bg-gray-50/50 transition-colors"
                    style={{ background: "none", border: "none" }}
                    onClick={() => setExpandedWeek(expandedWeek === wi ? -1 : wi)}
                  >
                    <div className="flex items-center gap-4">
                      {/* Week number badge */}
                      <div className={`w-11 h-11 rounded-2xl flex items-center justify-center font-display font-bold text-[15px] shadow-sm ${
                        weekComplete
                          ? "bg-accent text-white"
                          : "bg-primary-light text-primary"
                      }`}>
                        {weekComplete ? <CheckCircle2 size={18} /> : wi + 1}
                      </div>
                      <div>
                        <p className={`text-[13px] font-bold uppercase tracking-[0.08em] ${
                          weekComplete ? "text-accent" : "text-text-tertiary"
                        }`}>
                          {weekLabel}
                        </p>
                        <p className="text-[14px] text-text-secondary mt-0.5 font-medium">{weekTheme}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {/* Mini progress */}
                      <div className="hidden sm:flex items-center gap-1.5">
                        <span className="text-[11px] text-text-tertiary font-medium">
                          {weekProgress}/{week.tasks.length}
                        </span>
                        <div className="w-16 h-1.5 rounded-full bg-gray-100 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-accent transition-all duration-500"
                            style={{ width: `${(weekProgress / week.tasks.length) * 100}%` }}
                          />
                        </div>
                      </div>
                      <motion.span
                        animate={{ rotate: expandedWeek === wi ? 180 : 0 }}
                        transition={{ duration: 0.25 }}
                        className="text-text-tertiary"
                      >
                        <ChevronDown size={20} />
                      </motion.span>
                    </div>
                  </button>

                  {/* Week tasks */}
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
                            // Try to get i18n task name/desc, fallback to mock data
                            const i18nTaskName = t("simulation", taskKeys) && Array.isArray(t("simulation", taskKeys)) ? t("simulation", taskKeys)[ti] : null;
                            const i18nTaskDesc = t("simulation", taskDescKeys) && Array.isArray(t("simulation", taskDescKeys)) ? t("simulation", taskDescKeys)[ti] : null;
                            const taskTitle = i18nTaskName || task.title;
                            const taskDesc = i18nTaskDesc || task.desc;
                            return (
                              <motion.div
                                key={taskId}
                                className={`flex items-start gap-4 p-4 rounded-2xl transition-all duration-200 cursor-pointer ${
                                  done
                                    ? "bg-accent-light/30 border border-accent/20"
                                    : "hover:bg-gray-50 border border-transparent"
                                }`}
                                onClick={() => toggleTask(taskId)}
                                whileHover={{ scale: 1.01 }}
                              >
                                <button
                                  className={`mt-0.5 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 cursor-pointer ${
                                    done
                                      ? "bg-accent border-accent text-white shadow-lg shadow-accent/25"
                                      : "border-gray-200 hover:border-accent/50 bg-white"
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
                                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-lg ${
                                      done ? "bg-accent text-white" : "bg-gray-100 text-text-tertiary"
                                    }`}>
                                      {task.day}
                                    </span>
                                    <span className={`font-semibold text-[14px] ${
                                      done ? "text-accent" : "text-text"
                                    }`}>
                                      {taskTitle}
                                    </span>
                                  </div>
                                  <p className="text-[13px] text-text-secondary leading-relaxed">
                                    {taskDesc}
                                  </p>
                                </div>
                                {done && (
                                  <CheckCircle2 size={18} className="text-accent flex-shrink-0 mt-0.5" />
                                )}
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
      </section>

      {/* ================================================================
          DAILY ANCHORS
         ================================================================ */}
      <section>
        <div className="flex items-center gap-3 mb-8">
          <Star size={17} className="text-risk-moderate" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
              {t("simulation", "dailyAnchors")}
            </p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">
              {t("simulation", "dailyAnchorsTitle")}
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          {[
            { icon: Clock, title: t("simulation", "morningLightTitle"), desc: t("simulation", "morningLightDesc") },
            { icon: Target, title: t("simulation", "moveDailyTitle"), desc: t("simulation", "moveDailyDesc") },
            { icon: Star, title: t("simulation", "trackReflectTitle"), desc: t("simulation", "trackReflectDesc") },
          ].map((tip, i) => (
            <motion.div
              key={tip.title}
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
    </div>
  );
}