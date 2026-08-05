import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLocation } from "./layout/PageTransition";
import { getAnalysis } from "../api/client";
import geneticActionKnowledge from "../data/geneticActionKnowledge";
import ScreeningSummary from "./ScreeningSummary";
import {
  ShieldCheck,
  Dna,
  ChevronDown,
  ChevronRight,
  Star,
  Clock,
  MessageCircle,
  ExternalLink,
} from "lucide-react";

/* ───────────────────────────────────────────────
   Attention Level Badge
   ─────────────────────────────────────────────── */
function AttentionBadge({ level }) {
  const map = {
    high: {
      label: "High Clinical Attention",
      cn: "高临床关注度",
      bg: "bg-red-50",
      text: "text-red-600",
      dot: "bg-red-400",
    },
    moderate: {
      label: "Moderate Clinical Attention",
      cn: "中等临床关注度",
      bg: "bg-amber-50",
      text: "text-amber-600",
      dot: "bg-amber-400",
    },
  };
  const s = map[level] || map.moderate;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold ${s.bg} ${s.text}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {s.cn}
    </span>
  );
}

/* ───────────────────────────────────────────────
   Evidence Level Badge
   ─────────────────────────────────────────────── */
function EvidenceBadge({ level }) {
  const isHigh = level === "High";
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-[0.06em] ${
        isHigh
          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
          : "bg-blue-50 text-blue-700 border border-blue-200"
      }`}
    >
      <Star size={10} className={isHigh ? "text-emerald-500" : "text-blue-500"} />
      {level} Evidence
    </span>
  );
}

/* ───────────────────────────────────────────────
   Expandable Card
   ─────────────────────────────────────────────── */
function ExpandableCard({ area, index }) {
  const [open, setOpen] = useState(index === 0);
  return (
    <motion.div
      className="premium-card overflow-hidden"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05 * index, duration: 0.4 }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-4 px-6 py-5 text-left cursor-pointer hover:bg-gray-50/50 transition-colors"
        style={{ background: "none", border: "none" }}
      >
        <span className="text-2xl flex-shrink-0">{area.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <h4 className="font-display font-bold text-[15px] text-text">
              {area.title}
            </h4>
            <EvidenceBadge level={area.evidenceLevel} />
          </div>
          <p className="text-[12px] text-text-tertiary">{area.shortTitle}</p>
        </div>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-text-tertiary flex-shrink-0"
        >
          <ChevronDown size={18} />
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-5 pt-1 border-t border-gray-100">
              <p className="text-[13px] text-text-secondary leading-relaxed mb-3">
                {area.explanation}
              </p>
              {area.evidenceSource && (
                <p className="text-[10px] text-text-tertiary">
                  Source: {area.evidenceSource}
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ───────────────────────────────────────────────
   Match Diseases from geneCards

   筛选规则：
     1. 只匹配 clinvarSignificance 非 benign/likely_benign 的基因
        （纯良性基因不触发疾病匹配，避免健康 sample 被错误显示）
     2. 收集所有匹配疾病，不截断为单个
     3. 去重：同一 disease 只出现一次
   ─────────────────────────────────────────────── */
function matchDiseases(geneCards) {
  if (!geneCards || geneCards.length === 0) return [];

  const BENIGN_SIGS = new Set(["benign", "likely_benign"]);

  // 过滤：只保留有显著意义的基因
  const significantGenes = geneCards.filter((gene) => {
    const sig = (gene.clinvarSignificance || gene.clinvar_significance || "").toLowerCase();
    if (!sig) return false;
    if (BENIGN_SIGS.has(sig)) return false;
    return true;
  });

  if (significantGenes.length === 0) return [];

  const seenDiseases = new Set();
  const results = [];

  for (const gene of significantGenes) {
    const symbol = (gene.symbol || "").trim().toLowerCase();
    const name = (gene.name || "").trim().toLowerCase();

    for (const entry of geneticActionKnowledge) {
      if (seenDiseases.has(entry.disease)) continue;

      const searchTokens = [
        ...entry.genes.map((g) => g.toLowerCase()),
        ...(entry.aliases || []).map((a) => a.toLowerCase()),
      ];

      const matched =
        searchTokens.includes(symbol) ||
        searchTokens.includes(name) ||
        searchTokens.some((a) => name.includes(a)) ||
        searchTokens.some((a) => symbol.includes(a));

      if (matched) {
        seenDiseases.add(entry.disease);
        results.push({ entry, gene });
        break; // same gene → one knowledge entry per gene
      }
    }
  }

  return results;
}

/* ───────────────────────────────────────────────
   GeneticActionMap — 主页面
   ─────────────────────────────────────────────── */
export default function GeneticActionMap() {
  const { reportId, uploaded } = useLocation();
  const [matchedDiseases, setMatchedDiseases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checked, setChecked] = useState({});
  const allChecked =
    matchedDiseases.length > 0 &&
    matchedDiseases.every((md) =>
      md.entry.doctorQuestions.every((_, i) => checked[`${md.entry.disease}_${i}`])
    );

  // 页面加载时匹配
  useEffect(() => {
    if (!uploaded || !reportId) {
      setLoading(false);
      return;
    }
    getAnalysis(reportId)
      .then((data) => {
        const genes = data?.profile?.geneCards || [];
        const results = matchDiseases(genes);
        setMatchedDiseases(results);
      })
      .catch(() => setMatchedDiseases([]))
      .finally(() => setLoading(false));
  }, [reportId, uploaded]);

  if (!uploaded) {
    return (
      <div className="max-w-4xl mx-auto px-6 pt-28 pb-24 text-center">
        <div className="premium-card p-16">
          <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-6">
            <Dna size={28} className="text-text-tertiary" />
          </div>
          <h2 className="font-display font-bold text-[20px] text-text mb-3">
            Genetic Action Map
          </h2>
          <p className="text-[14px] text-text-tertiary max-w-md mx-auto leading-relaxed">
            Upload your baby&apos;s genetic report in Step 01 to view
            personalized action guidance based on screening results.
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-6 pt-28 pb-24">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse bg-gray-100 rounded-2xl h-24 mb-4" />
        ))}
      </div>
    );
  }

  if (matchedDiseases.length === 0) {
    return <ScreeningSummary />;
  }

  /* ── 有匹配疾病 → 渲染完整 6 Section ── */
  return (
    <div className="max-w-4xl mx-auto px-6 pt-28 pb-24">
      {/* ============================================
          SECTION 1 — Screening Scope Banner
          ============================================ */}
      <motion.div
        className="premium-card p-5 mb-10 border border-primary/10 bg-primary-light/10 flex items-start gap-3"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <ShieldCheck size={18} className="text-primary flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-[12px] font-semibold text-primary mb-0.5">
            Screening Scope Notice
          </p>
          <p className="text-[12px] text-text-secondary leading-relaxed">
            GenoLife currently focuses on{" "}
            <strong>9 classical newborn genetic screening conditions</strong>.
            This screening panel does not cover all genetic disorders. A
            negative result on one condition does not exclude risks for others.
          </p>
        </div>
      </motion.div>

      {/* ============================================
          SECTION 2 — Genetic Findings (multi-disease)
          ============================================ */}
      <motion.section
        className="mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-light/60 text-primary mb-6">
          <Dna size={14} />
          <span className="text-[12px] font-bold uppercase tracking-[0.12em]">
            Genetic Findings
          </span>
        </div>

        {matchedDiseases.map((md, idx) => {
          const matchedDisease = md.entry;
          const matchedGene = md.gene;
          return (
            <motion.div
              key={matchedDisease.disease}
              className="premium-card p-8 border border-primary/10 mb-4 last:mb-0"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 * idx, duration: 0.4 }}
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-2xl bg-primary-light/40 flex items-center justify-center flex-shrink-0">
                  <Dna size={22} className="text-primary" />
                </div>
                <div className="flex-1">
                  <p className="text-[11px] font-bold text-text-tertiary uppercase tracking-[0.1em] mb-2">
                    检测到相关遗传变异
                  </p>
                  <h1 className="font-display font-bold text-[22px] text-text mb-2 tracking-tight">
                    {matchedDisease.disease}
                    {matchedDisease.shortName && matchedDisease.shortName !== matchedDisease.disease && (
                      <span className="text-text-tertiary text-[16px] ml-2">
                        ({matchedDisease.shortName})
                      </span>
                    )}
                  </h1>
                  <div className="flex flex-wrap items-center gap-3 mt-3">
                    <span className="text-[13px] text-text-secondary">
                      相关基因:{" "}
                      <strong className="text-text font-mono">
                        {matchedGene.symbol}
                      </strong>
                    </span>
                    <AttentionBadge level={matchedDisease.attentionLevel} />
                    <span className="text-[12px] text-text-tertiary px-2 py-0.5 rounded-md bg-gray-100">
                      {matchedDisease.category}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}

        <p className="mt-4 text-[12px] text-text-tertiary leading-relaxed">
          {matchedDiseases.length > 1
            ? `以上 ${matchedDiseases.length} 个遗传变异需要进一步医学评估。请与儿科专科医生讨论确认性检测和管理方案。`
            : "以上遗传变异需要进一步医学评估。请与儿科专科医生讨论确认性检测和管理方案。"}
        </p>
      </motion.section>

      {/* ============================================
          SECTION 3 — Understanding The Findings (per disease)
          ============================================ */}
      <motion.section
        className="mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5 }}
      >
        <h2 className="font-display font-bold text-[20px] text-text mb-5 tracking-tight">
          Understanding the {matchedDiseases.length > 1 ? "Findings" : "Finding"}
        </h2>

        {matchedDiseases.map((md, idx) => {
          const matchedDisease = md.entry;
          const matchedGene = md.gene;
          return (
            <motion.div
              key={`mechanism-${matchedDisease.disease}`}
              className="premium-card p-8 mb-4 last:mb-0"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + idx * 0.05, duration: 0.4 }}
            >
              <h3 className="font-display font-bold text-[16px] text-text mb-2">
                {matchedDisease.disease}
              </h3>

              <div className="flex flex-col items-center gap-4 mb-6">
                <div className="flex items-center gap-3 text-[13px]">
                  <span className="px-4 py-2 rounded-xl bg-primary-light/30 text-primary font-bold font-mono">
                    {matchedGene.symbol}
                  </span>
                  <ChevronRight size={16} className="text-text-tertiary" />
                  <span className="px-4 py-2 rounded-xl bg-gray-50 text-text-secondary text-center max-w-[260px] leading-snug">
                    {matchedDisease.mechanism.length > 140
                      ? matchedDisease.mechanism.slice(0, 140) + "…"
                      : matchedDisease.mechanism}
                  </span>
                </div>
              </div>

              <p className="text-[14px] text-text-secondary leading-relaxed">
                {matchedDisease.mechanism}
              </p>
            </motion.div>
          );
        })}
      </motion.section>

      {/* ============================================
          SECTION 4 — Management Pathways (per disease)
          ============================================ */}
      <motion.section
        className="mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.5 }}
      >
        <h2 className="font-display font-bold text-[20px] text-text mb-2 tracking-tight">
          Management {matchedDiseases.length > 1 ? "Pathways" : "Pathway"}
        </h2>
        <p className="text-[13px] text-text-tertiary mb-6 leading-relaxed">
          Each management area below is based on published clinical guidelines.
          Click to learn more.
        </p>

        {matchedDiseases.map((md, idx) => {
          const matchedDisease = md.entry;
          return (
            <motion.div
              key={`mgmt-${matchedDisease.disease}`}
              className="mb-6 last:mb-0"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + idx * 0.05, duration: 0.4 }}
            >
              <h3 className="font-display font-bold text-[14px] text-text mb-3 ml-1">
                {matchedDisease.disease}
              </h3>
              <div className="space-y-3.5">
                {matchedDisease.managementAreas.map((area, i) => (
                  <ExpandableCard key={`${matchedDisease.disease}-${area.title}`} area={area} index={i} />
                ))}
              </div>
            </motion.div>
          );
        })}
      </motion.section>

      {/* ============================================
          SECTION 5 — Early Life Timeline
          ============================================ */}
      <motion.section
        className="mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <h2 className="font-display font-bold text-[20px] text-text mb-2 tracking-tight">
          Early Life Timeline
        </h2>
        <p className="text-[13px] text-text-tertiary mb-6 leading-relaxed">
          Key focus areas at different stages of early life. This timeline is
          for educational guidance and does not predict disease progression.
        </p>

        {matchedDiseases.map((md, idx) => {
          const matchedDisease = md.entry;
          return (
            <motion.div
              key={`timeline-${matchedDisease.disease}`}
              className="mb-10 last:mb-0"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + idx * 0.05, duration: 0.4 }}
            >
              <h3 className="font-display font-bold text-[14px] text-text mb-4 ml-1">
                {matchedDisease.disease}
              </h3>
              <div className="relative">
                <div className="absolute left-[23px] top-0 bottom-0 w-px bg-gray-200" />
                <div className="space-y-0">
                  {matchedDisease.timeline.map((t) => (
                    <div key={`${matchedDisease.disease}-${t.stage}`} className="relative flex items-start gap-6 pb-8 last:pb-0">
                      <div className="relative z-10 flex-shrink-0">
                        <div className="w-12 h-12 rounded-full bg-white border-2 border-primary/30 flex items-center justify-center shadow-sm">
                          <Clock size={18} className="text-primary" />
                        </div>
                      </div>
                      <div className="flex-1 pt-1.5">
                        <h4 className="font-display font-bold text-[15px] text-text mb-1.5">
                          {t.stage}
                        </h4>
                        <p className="text-[13px] text-text-secondary leading-relaxed">
                          {t.focus}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          );
        })}
      </motion.section>

      {/* ============================================
          SECTION 6 — Doctor Discussion Guide (per disease)
          ============================================ */}
      <motion.section
        className="mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25, duration: 0.5 }}
      >
        {matchedDiseases.map((md, idx) => {
          const matchedDisease = md.entry;
          return (
            <motion.div
              key={`doctor-${matchedDisease.disease}`}
              className="premium-card p-8 mb-5 last:mb-0 border border-accent/20 bg-accent-light/5"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 + idx * 0.05, duration: 0.5 }}
            >
              <div className="flex items-start gap-4 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-accent-light flex items-center justify-center flex-shrink-0">
                  <MessageCircle size={22} className="text-accent" />
                </div>
                <div>
                  <h2 className="font-display font-bold text-[18px] text-text mb-1 tracking-tight">
                    {matchedDisease.disease} — Discussion Guide
                  </h2>
                  <p className="text-[13px] text-text-tertiary leading-relaxed">
                    Questions you may find helpful to discuss with your healthcare
                    provider. These are not a script — adapt them to your specific
                    situation.
                  </p>
                </div>
              </div>

              <ul className="space-y-2.5">
                {matchedDisease.doctorQuestions.map((q, i) => (
                  <motion.li
                    key={i}
                    className="flex items-start gap-3"
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + i * 0.04 }}
                  >
                    <span className="w-6 h-6 rounded-lg bg-accent-light/60 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-[11px] font-bold text-accent">
                        {i + 1}
                      </span>
                    </span>
                    <label className="flex items-center gap-3 text-[14px] text-text-secondary leading-relaxed cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={!!checked[`${matchedDisease.disease}_${i}`]}
                        onChange={() =>
                          setChecked((prev) => ({
                            ...prev,
                            [`${matchedDisease.disease}_${i}`]: !prev[`${matchedDisease.disease}_${i}`],
                          }))
                        }
                        className="w-4 h-4 rounded border-gray-300 text-accent focus:ring-accent accent-accent cursor-pointer"
                      />
                      {q}
                    </label>
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          );
        })}

        {allChecked && (
          <motion.p
            className="mt-5 text-[12px] text-accent font-semibold text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            All questions checked — you&apos;re well prepared for your next
            healthcare visit.
          </motion.p>
        )}
      </motion.section>

      {/* ============================================
           Parent Messages
           ============================================ */}
      {matchedDiseases.filter(md => md.entry.parentMessage).length > 0 && (
        matchedDiseases
          .filter(md => md.entry.parentMessage)
          .map((md, idx) => (
            <motion.div
              key={`parent-${md.entry.disease}`}
              className="premium-card p-8 bg-gradient-to-r from-primary-light/5 to-accent-light/5 border border-primary/10 mb-4 last:mb-0"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 + idx * 0.05, duration: 0.5 }}
            >
              <h3 className="font-display font-bold text-[14px] text-text mb-2">
                {md.entry.disease}
              </h3>
              <p className="text-[14px] text-text-secondary leading-relaxed">
                {md.entry.parentMessage}
              </p>
            </motion.div>
          ))
      )}

      {/* ── Disclaimer ── */}
      <motion.p
        className="text-center text-[11px] text-text-tertiary mt-12 leading-relaxed"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        The information provided is for educational reference only and does not
        constitute medical diagnosis or treatment advice. Please consult
        qualified healthcare professionals for clinical evaluation and
        management.
      </motion.p>
    </div>
  );
}
