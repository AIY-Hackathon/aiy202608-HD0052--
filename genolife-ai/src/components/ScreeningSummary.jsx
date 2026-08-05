import { motion } from "framer-motion";
import { ShieldCheck, FileText, Stethoscope, Info } from "lucide-react";

const SCREENED_CONDITIONS = [
  { name: "Phenylketonuria (PKU)", gene: "PAH" },
  { name: "G6PD Deficiency", gene: "G6PD" },
  { name: "Spinal Muscular Atrophy (SMA)", gene: "SMN1" },
  { name: "Congenital Hearing Loss", gene: "GJB2" },
  { name: "Congenital Adrenal Hyperplasia (CAH)", gene: "CYP21A2" },
  { name: "CHARGE Syndrome", gene: "CHD7" },
  { name: "Severe Combined Immunodeficiency (SCID)", gene: "Multiple" },
  { name: "Cystic Fibrosis (CF)", gene: "CFTR" },
  { name: "Thalassemia", gene: "HBB / HBA" },
];

/**
 * ScreeningSummary — 无匹配风险时的筛查总结页面
 * ==============================================
 * 当未在 9 种经典疾病中找到匹配时展示。
 * 不显示 "Healthy Baby"，只说明筛查范围内未发现显著发现。
 */
export default function ScreeningSummary() {
  return (
    <div className="max-w-4xl mx-auto px-6 pt-28 pb-24">
      {/* ── Header ── */}
      <motion.section
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-light/60 text-primary mb-8">
          <ShieldCheck size={14} />
          <span className="text-[12px] font-bold uppercase tracking-[0.12em]">
            Screening Summary
          </span>
        </div>
        <h2 className="font-display font-bold text-[28px] text-text mb-4 tracking-tight">
          未发现匹配疾病
        </h2>
        <p className="text-[13px] text-text-tertiary max-w-lg mx-auto leading-relaxed">
          未发现 GenoLife 当前覆盖的九类新生儿遗传筛查疾病相关明确变异。
        </p>
      </motion.section>

      {/* ── Result Card ── */}
      <motion.div
        className="premium-card p-8 mb-8 border border-primary/10"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5 }}
      >
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-primary-light/40 flex items-center justify-center flex-shrink-0">
            <FileText size={22} className="text-primary" />
          </div>
          <div>
            <h3 className="font-display font-bold text-[18px] text-text mb-3">
              Screening Result
            </h3>
            <p className="text-[14px] text-text-secondary leading-relaxed">
              In the 9 classical newborn genetic screening conditions focused on
              by GenoLife, no significant genetic findings were identified in
              your baby&apos;s report.
            </p>
          </div>
        </div>
      </motion.div>

      {/* ── What was screened ── */}
      <motion.div
        className="premium-card p-8 mb-8"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.5 }}
      >
        <h3 className="font-display font-bold text-[17px] text-text mb-4">
          What was screened
        </h3>
        <p className="text-[13px] text-text-secondary mb-6 leading-relaxed">
          The following 9 conditions were included in the current screening
          scope:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {SCREENED_CONDITIONS.map((c) => (
            <div
              key={c.name}
              className="flex items-center gap-3 px-4 py-3 rounded-xl bg-gray-50 border border-gray-100"
            >
              <span className="w-2 h-2 rounded-full bg-primary/40 flex-shrink-0" />
              <div>
                <p className="text-[13px] font-semibold text-text leading-tight">
                  {c.name}
                </p>
                <p className="text-[10px] text-text-tertiary uppercase tracking-[0.06em]">
                  {c.gene}
                </p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ── What this means ── */}
      <motion.div
        className="premium-card p-8 mb-8"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        <h3 className="font-display font-bold text-[17px] text-text mb-4">
          What this means
        </h3>
        <p className="text-[14px] text-text-secondary leading-relaxed">
          No clear genetic risk indicators were identified within the 9
          conditions screened by GenoLife. This is generally reassuring, and
          routine pediatric care remains the most important foundation for your
          baby&apos;s healthy development.
        </p>
      </motion.div>

      {/* ── Important limitation ── */}
      <motion.div
        className="premium-card p-8 mb-8 border border-amber-100 bg-amber-50/30"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25, duration: 0.5 }}
      >
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
            <Info size={18} className="text-amber-600" />
          </div>
          <div>
            <h3 className="font-display font-bold text-[17px] text-text mb-3">
              Important limitation
            </h3>
            <p className="text-[14px] text-text-secondary leading-relaxed">
              This result does not exclude all genetic conditions or future
              health risks. GenoLife screens a focused set of 9 classical
              conditions — many other genetic disorders are not included in this
              screening scope. Additionally, this screening does not replace
              standard newborn screening, regular pediatric check-ups, or
              professional medical evaluation.
            </p>
          </div>
        </div>
      </motion.div>

      {/* ── When to seek medical advice ── */}
      <motion.div
        className="premium-card p-8 mb-20"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.5 }}
      >
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-accent-light flex items-center justify-center flex-shrink-0">
            <Stethoscope size={18} className="text-accent" />
          </div>
          <div>
            <h3 className="font-display font-bold text-[17px] text-text mb-3">
              When to seek medical advice
            </h3>
            <p className="text-[14px] text-text-secondary leading-relaxed mb-4">
              Regardless of genetic screening results, consult your
              pediatrician if you notice:
            </p>
            <ul className="space-y-2.5">
              {[
                {
                  title: "Developmental concerns",
                  desc: "Delays in motor, language, or social milestones compared to expected developmental timelines.",
                },
                {
                  title: "Family history",
                  desc: "A known or suspected genetic condition in the family that was not detected in this screening.",
                },
                {
                  title: "Concerning symptoms",
                  desc: "Unexplained symptoms such as poor feeding, failure to thrive, recurrent infections, or unusual behavior.",
                },
              ].map((item) => (
                <li key={item.title} className="flex items-start gap-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent mt-2 flex-shrink-0" />
                  <div>
                    <p className="text-[13px] font-semibold text-text">
                      {item.title}
                    </p>
                    <p className="text-[12px] text-text-tertiary leading-relaxed">
                      {item.desc}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
