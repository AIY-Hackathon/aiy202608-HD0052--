import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import RecommendationCard from "../components/shared/RecommendationCard";
import AIBadge from "../components/shared/AIBadge";
import { thirtyDayPlan } from "../data/mockData";
import { ChevronDown, Target, Clock, Star } from "lucide-react";

export default function LifestylePlanner() {
  const [checkedTasks, setCheckedTasks] = useState(new Set());
  const [expandedWeek, setExpandedWeek] = useState(0);

  const toggleTask = (id) => {
    setCheckedTasks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const totalTasks = thirtyDayPlan.weeks.reduce((s, w) => s + w.tasks.length, 0);
  const completedTasks = checkedTasks.size;
  const progressPct = Math.round((completedTasks / totalTasks) * 100);
  const estimatedScoreGain = Math.round(progressPct * 0.15);

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* ─────────────────────────────────────────────
          Hero: Goal setting
         ───────────────────────────────────────────── */}
      <motion.section
        className="mb-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <p className="text-[13px] font-semibold text-text-tertiary uppercase tracking-[0.15em] mb-4">
          30-Day Health Plan
        </p>
        <h2 className="font-display font-semibold text-2xl text-text mb-2">
          Your personalized action plan
        </h2>
        <p className="text-[15px] text-text-secondary mb-6 max-w-xl leading-relaxed">
          A gene-informed 30-day program designed to work with your unique biology, not against it.
        </p>

        {/* Goal card */}
        <div className="inline-flex items-center gap-3 bg-white rounded-2xl border border-gray-200/60 px-6 py-4 shadow-sm">
          <Target size={18} className="text-accent" />
          <div>
            <p className="text-[11px] text-text-tertiary uppercase tracking-wider">Goal</p>
            <p className="text-[15px] font-medium text-text">{thirtyDayPlan.goal}</p>
          </div>
          <AIBadge />
        </div>
      </motion.section>

      {/* ─────────────────────────────────────────────
          Progress bar
         ───────────────────────────────────────────── */}
      <motion.section
        className="mb-14 bg-white rounded-2xl border border-gray-200/60 p-6 shadow-sm"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-display font-semibold text-lg text-text">Your Progress</h3>
          <span className="text-sm text-text-secondary font-medium">
            {completedTasks} / {totalTasks} tasks
          </span>
        </div>
        <div className="h-3 rounded-full bg-gray-100 overflow-hidden">
          <motion.div
            className="h-full rounded-full bg-accent"
            initial={{ width: 0 }}
            animate={{ width: `${progressPct}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </div>
        <p className="text-[13px] text-text-tertiary mt-3">
          Estimated health score improvement:{" "}
          <span className="font-semibold text-accent">+{estimatedScoreGain}</span> points
        </p>
      </motion.section>

      {/* ─────────────────────────────────────────────
          4-Week Timeline
         ───────────────────────────────────────────── */}
      <section className="mb-16">
        <p className="text-[13px] font-semibold text-text-tertiary uppercase tracking-[0.15em] mb-6">
          Weekly Breakdown
        </p>

        <div className="space-y-4">
          {thirtyDayPlan.weeks.map((week, wi) => (
            <motion.div
              key={wi}
              className="bg-white rounded-2xl border border-gray-200/60 shadow-sm overflow-hidden"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + wi * 0.08 }}
            >
              {/* Week header */}
              <button
                className="w-full flex items-center justify-between px-6 py-5 text-left hover:bg-gray-50/50 transition-colors cursor-pointer"
                style={{ background: "none", border: "none" }}
                onClick={() => setExpandedWeek(expandedWeek === wi ? -1 : wi)}
              >
                <div>
                  <p className="text-[13px] font-semibold text-text-tertiary uppercase tracking-[0.1em]">
                    {week.label}
                  </p>
                  <p className="text-[15px] text-text-secondary mt-0.5">{week.theme}</p>
                </div>
                <motion.span
                  animate={{ rotate: expandedWeek === wi ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="text-text-tertiary"
                >
                  <ChevronDown size={20} />
                </motion.span>
              </button>

              {/* Week tasks */}
              <AnimatePresence>
                {expandedWeek === wi && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="px-6 pb-5 space-y-3 border-t border-gray-100 pt-4">
                      {week.tasks.map((task, ti) => {
                        const taskId = `${wi}-${ti}`;
                        const done = checkedTasks.has(taskId);
                        return (
                          <div
                            key={taskId}
                            className={`flex items-start gap-4 p-4 rounded-xl transition-colors cursor-pointer ${
                              done ? "bg-accent-light/30" : "hover:bg-gray-50"
                            }`}
                            onClick={() => toggleTask(taskId)}
                          >
                            <button
                              className={`mt-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors cursor-pointer ${
                                done
                                  ? "bg-accent border-accent text-white"
                                  : "border-gray-300 hover:border-accent"
                              }`}
                            >
                              {done && (
                                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                                  <path
                                    d="M2 6L5 9L10 3"
                                    stroke="white"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                  />
                                </svg>
                              )}
                            </button>
                            <div>
                              <div className="flex items-center gap-2 mb-0.5">
                                <span className="text-[11px] font-semibold text-text-tertiary bg-gray-100 px-2 py-0.5 rounded-md">
                                  {task.day}
                                </span>
                                <span className="font-medium text-[15px] text-text">
                                  {task.title}
                                </span>
                              </div>
                              <p className="text-[14px] text-text-secondary leading-relaxed mt-1">
                                {task.desc}
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ─────────────────────────────────────────────
          Quick tips
         ───────────────────────────────────────────── */}
      <section>
        <p className="text-[13px] font-semibold text-text-tertiary uppercase tracking-[0.15em] mb-6">
          Daily Anchors
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { icon: Clock, title: "Morning light", desc: "10 min of outdoor light within 30 min of waking — helps reset your CLOCK gene rhythm." },
            { icon: Target, title: "Move daily", desc: "At least 30 min of movement. Your ACTN3 genotype responds well to short bursts of intensity." },
            { icon: Star, title: "Track & reflect", desc: "A quick evening journal entry builds self-awareness and reinforces positive changes." },
          ].map((tip, i) => (
            <motion.div
              key={i}
              className="bg-white rounded-2xl border border-gray-200/60 p-6 shadow-sm"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
            >
              <tip.icon size={20} className="text-primary mb-3" />
              <h4 className="font-display font-semibold text-[16px] text-text mb-1.5">{tip.title}</h4>
              <p className="text-[14px] text-text-secondary leading-relaxed">{tip.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
