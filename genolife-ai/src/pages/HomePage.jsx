/**
 * Landing 首页 — GenoLife AI
 * =================================
 * UX 参考 HumanLongevity：暗色全屏 hero、极简文案、惯性滚动、内容全在首屏以下
 * 设计词条：科学感 · 克制 · 呼吸 · 信任
 */
import { useEffect, useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { useLocation } from "../components/layout/PageTransition";
import { useLanguage } from "../i18n";
import {
  Dna,
  Activity,
  FileText,
  ArrowRight,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

// ── Lenis 平滑滚动 ──
let lenis = null;

function initLenis() {
  // 只在首次调用时初始化
  if (lenis) return lenis;
  if (typeof window === "undefined") return null;
  const Lenis = window.__LenisClass;
  if (!Lenis) return null;
  lenis = new Lenis({ duration: 1.2, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
  function raf(time) {
    lenis?.raf(time);
    requestAnimationFrame(raf);
  }
  requestAnimationFrame(raf);
  return lenis;
}

function destroyLenis() {
  lenis?.destroy();
  lenis = null;
}

// ── How it works ──
const FEATURES_META = [
  { target: "gene-map" },
  { target: "simulation" },
  { target: "report" },
];

export default function HomePage() {
  const { goTo } = useLocation();
  const { t } = useLanguage();
  const heroRef = useRef(null);
  const { scrollY } = useScroll();
  const heroOpacity = useTransform(scrollY, [0, 400], [1, 0.3]);
  const heroScale = useTransform(scrollY, [0, 400], [1, 0.96]);

  // ── 初始化 Lenis ──
  useEffect(() => {
    // 动态 import lenis 避免 SSR 问题
    import("lenis").then((mod) => {
      const LenisClass = mod.default;
      window.__LenisClass = LenisClass;
      initLenis();
    }).catch(() => {});
    return () => destroyLenis();
  }, []);

  const stats = [
    { value: "30+", label: t("home", "geneticMarkers") },
    { value: "5D", label: t("home", "riskDimensions") },
    { value: "G×E", label: t("home", "interactionModel") },
  ];

  const features = [
    {
      icon: <Dna size={24} />,
      title: t("home", "feature1Title"),
      desc: t("home", "feature1Desc"),
      target: "gene-map",
    },
    {
      icon: <Activity size={24} />,
      title: t("home", "feature2Title"),
      desc: t("home", "feature2Desc"),
      target: "simulation",
    },
    {
      icon: <FileText size={24} />,
      title: t("home", "feature3Title"),
      desc: t("home", "feature3Desc"),
      target: "report",
    },
  ];

  return (
    <div className="flex flex-col">
      {/* ================================================================
          HERO — 全屏，暗色，极简
          ================================================================ */}
      <motion.section
        ref={heroRef}
        style={{ opacity: heroOpacity, scale: heroScale }}
        className="relative min-h-screen flex flex-col justify-center items-start px-6 lg:px-16"
      >
        {/* 深色渐变背景 */}
        <div className="absolute inset-0" style={{ background: "linear-gradient(160deg, #060A12 0%, #0C1525 40%, #111D30 100%)" }} />

        {/* 微弱的径向光晕 */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] rounded-full opacity-[0.04]" style={{ background: "radial-gradient(circle, #2A4A3E 0%, transparent 70%)", transform: "translate(20%, -20%)" }} />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] rounded-full opacity-[0.03]" style={{ background: "radial-gradient(circle, #3A3028 0%, transparent 70%)", transform: "translate(-15%, 15%)" }} />

        <div className="relative z-10 max-w-4xl">
          {/* 小标签 — 克制 */}
          <motion.p
            className="text-white/40 text-[11px] font-bold tracking-[0.22em] uppercase mb-8"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          >
            {t("home", "badge")}
          </motion.p>

          {/* 主标题 — 大字、极少词 */}
          <motion.h1
            className="font-display font-bold text-[44px] sm:text-[58px] lg:text-[72px] text-white leading-[1.04] tracking-tight mb-6"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          >
            {t("home", "headline1")}<br />
            <span style={{ background: "linear-gradient(135deg, #7EB8AE 0%, #5C9A90 60%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              {t("home", "headlineGradient")}
            </span>
          </motion.h1>

          {/* 副标题 — 一行 */}

          {/* CTA + stats row */}
          <motion.div
            className="flex flex-col sm:flex-row items-start sm:items-center gap-5"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.42, duration: 0.5 }}
          >
            <button
              onClick={() => goTo("gene-map")}
              className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-full text-white/90 text-[15px] font-semibold cursor-pointer transition-all duration-300 hover:bg-white/12 bg-white/8 border border-white/10"
            >
              {t("home", "cta")}
              <ArrowRight size={17} />
            </button>

            {/* 数据点 — 用竖线分隔 */}
            <div className="flex items-center gap-5 text-white/30">
              {stats.map((s, i) => (
                <div key={s.label} className="flex items-center gap-2.5">
                  {i > 0 && <span className="w-px h-8 bg-white/8" />}
                  <div>
                    <p className="text-[18px] font-bold text-white/80 leading-none mb-0.5">{s.value}</p>
                    <p className="text-[10px] tracking-[0.1em] uppercase">{s.label}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* 底部滚动指示 — 暗示往下看 */}
        <motion.div
          className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/15"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        >
          <span className="text-[10px] font-medium tracking-[0.14em] uppercase">{t("home", "howItWorks")}</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9" /></svg>
        </motion.div>
      </motion.section>

      {/* ================================================================
          HOW IT WORKS — 首屏以下才看到
          ================================================================ */}
      <section className="py-28 lg:py-36 px-6 lg:px-16 max-w-6xl mx-auto w-full">
        <div className="text-center mb-16">
          <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.2em] mb-4">{t("home", "howItWorks")}</p>
          <h2 className="font-display font-bold text-[28px] sm:text-[34px] text-text tracking-tight leading-tight">
            {t("home", "threeSteps")}
            <span className="text-text-secondary font-normal"> {t("home", "noFluff")}</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((f, i) => (
            <motion.article
              key={f.target}
              className="group relative premium-card px-7 py-8 cursor-pointer"
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ delay: i * 0.1, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
              whileHover={{ y: -6 }}
              onClick={() => goTo(f.target)}
            >
              {/* 序号 */}
              <span className="text-[10px] font-mono font-bold text-text/12 block mb-6">0{i + 1}</span>
              {/* 图标 */}
              <div className="w-12 h-12 rounded-2xl bg-primary-light flex items-center justify-center mb-5 group-hover:bg-primary/8 transition-colors">
                <span className="text-primary group-hover:text-primary-600 transition-colors">{f.icon}</span>
              </div>
              {/* 文案 */}
              <h3 className="font-display font-bold text-[17px] text-text mb-2.5">{f.title}</h3>
              <p className="text-[13px] text-text-secondary leading-relaxed">{f.desc}</p>

              {/* hover 动作 */}
              <div className="inline-flex items-center gap-1.5 mt-5 text-[12px] font-semibold text-accent opacity-0 group-hover:opacity-100 transition-all duration-200 translate-x-0 group-hover:translate-x-1">
                <span>{t("home", "explore")}</span>
                <TrendingUp size={13} />
              </div>
            </motion.article>
          ))}
        </div>

        {/* trust line */}
        <motion.p
          className="mt-20 text-center text-[13px] text-text-tertiary max-w-xl mx-auto leading-relaxed"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-1.5 mr-2"><ShieldCheck size={13} className="text-accent" /></span>
          {t("home", "trustLine")} <span className="font-medium text-text-secondary">{t("home", "privacyFirst")}</span>
        </motion.p>
      </section>
    </div>
  );
}
