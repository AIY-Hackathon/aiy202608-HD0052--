/**
 * Landing 首页 — GenoLife AI
 * =================================
 * 高端基因健康分析平台定位。
 * 设计词条：简洁 · 克制 · 专业 · 信任
 */
import { useEffect, useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { useLocation } from "../components/layout/PageTransition";
import { useLanguage } from "../i18n";
import { ArrowRight, ShieldCheck, TrendingUp } from "lucide-react";

// ── Lenis 平滑滚动 ──
let lenis = null;

function initLenis() {
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

export default function HomePage() {
  const { goTo } = useLocation();
  const { t } = useLanguage();
  const heroRef = useRef(null);
  const { scrollY } = useScroll();
  const heroOpacity = useTransform(scrollY, [0, 400], [1, 0.35]);
  const heroScale = useTransform(scrollY, [0, 400], [1, 0.97]);

  // ── 初始化 Lenis ──
  useEffect(() => {
    import("lenis").then((mod) => {
      window.__LenisClass = mod.default;
      initLenis();
    }).catch(() => {});
    return () => destroyLenis();
  }, []);

  const features = [
    {
      icon: null,
      title: t("home", "feature1Title"),
      desc: t("home", "feature1Desc"),
      target: "gene-map",
    },
    {
      icon: null,
      title: t("home", "feature2Title"),
      desc: t("home", "feature2Desc"),
      target: "simulation",
    },
    {
      icon: null,
      title: t("home", "feature3Title"),
      desc: t("home", "feature3Desc"),
      target: "report",
    },
  ];

  return (
    <div className="flex flex-col">
      {/* ================================================================
          HERO — 暗色全屏，品牌核心信息，极简克制
          ================================================================ */}
      <motion.section
        ref={heroRef}
        style={{ opacity: heroOpacity, scale: heroScale }}
        className="relative min-h-screen flex flex-col justify-center items-start px-6 lg:px-16"
      >
        {/* 深色渐变背景 */}
        <div className="absolute inset-0" style={{ background: "linear-gradient(160deg, #060A12 0%, #0C1525 40%, #111D30 100%)" }} />

        {/* 微弱径向光晕 */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] rounded-full opacity-[0.04]" style={{ background: "radial-gradient(circle, #2A4A3E 0%, transparent 70%)", transform: "translate(20%, -20%)" }} />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] rounded-full opacity-[0.03]" style={{ background: "radial-gradient(circle, #3A3028 0%, transparent 70%)", transform: "translate(-15%, 15%)" }} />

        <div className="relative z-10 max-w-4xl w-full">
          {/* 品牌标签 */}
          <motion.p
            className="text-white/30 text-[11px] font-bold tracking-[0.22em] uppercase mb-10"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          >
            {t("home", "badge")}
          </motion.p>

          {/* 主标题 — 大字、两行、强视觉中心 */}
          <motion.h1
            className="font-display font-bold text-[44px] sm:text-[58px] lg:text-[72px] text-white leading-[1.04] tracking-tight mb-8"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          >
            {t("home", "headline1")}<br />
            <span style={{ background: "linear-gradient(135deg, #7EB8AE 0%, #5C9A90 60%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              {t("home", "headlineGradient")}
            </span>
          </motion.h1>

          {/* 副标题 — 一行简短解释 */}
          <motion.p
            className="text-white/45 text-[15px] sm:text-[16px] max-w-[520px] leading-relaxed mb-12"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.28, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          >
            {t("home", "heroSubtitle")}
          </motion.p>

          {/* CTA 按钮 — 核心行动 */}
          <motion.div
            className="mb-16"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.42, duration: 0.5 }}
          >
            <button
              onClick={() => goTo("gene-map")}
              className="inline-flex items-center gap-2.5 px-7 py-4 rounded-full text-[15px] font-semibold cursor-pointer transition-all duration-300"
              style={{
                background: "linear-gradient(135deg, #7EB8AE 0%, #5C9A90 100%)",
                color: "#060A12",
                border: "none",
              }}
            >
              {t("home", "cta")}
              <ArrowRight size={17} />
            </button>
          </motion.div>

          {/* 微弱数据展示 — 第三视觉层级 */}
          <motion.div
            className="flex items-center gap-5 text-white/20"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.58, duration: 0.5 }}
          >
            <span className="w-px h-4 bg-white/8" />
            <span className="text-[12px] font-medium tracking-[0.1em] uppercase">{t("common", "disclaimer")}</span>
          </motion.div>
        </div>

        {/* 底部滚动指示 */}
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
          HOW IT WORKS — 首屏以下
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
              <span className="text-[10px] font-mono font-bold text-text/12 block mb-6">0{i + 1}</span>
              <div className="w-12 h-12 rounded-2xl bg-primary-light flex items-center justify-center mb-5 group-hover:bg-primary/8 transition-colors">
                <span className="text-primary group-hover:text-primary-600 transition-colors">{f.icon}</span>
              </div>
              <h3 className="font-display font-bold text-[17px] text-text mb-2.5">{f.title}</h3>
              <p className="text-[13px] text-text-secondary leading-relaxed">{f.desc}</p>
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
