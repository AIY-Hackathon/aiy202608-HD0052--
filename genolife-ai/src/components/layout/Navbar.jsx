import { motion } from "framer-motion";
import { useLocation } from "./PageTransition";
import { useLanguage } from "../../i18n";
import { Home, Shield } from "lucide-react";

export default function Navbar() {
  const { currentPage, goTo, analysisResult } = useLocation();
  const { t, lang, toggleLang } = useLanguage();

  // 步骤 03 根据分析结果动态切换
  const step03 = analysisResult === "abnormal"
    ? { id: "genetic-assistance", label: "异常辅助", step: "03", icon: "🏥" }
    : { id: "healthy-growth", label: "健康成长", step: "03", icon: "🌱" };

  const links = [
    { id: "gene-map", labelKey: "analysis", step: "01", icon: "🧬" },
    { id: "action-map", labelKey: "actionMap", step: "02", icon: "🧭" },
    step03,
    { id: "report", labelKey: "report", step: "04", icon: "📋" },
  ];

  return (
    <nav className="glass-nav fixed top-0 inset-x-0 z-50">
      <div className="max-w-6xl mx-auto flex items-center justify-between px-6 h-16">
        {/* Logo */}
        <button
          onClick={() => goTo("home")}
          className="flex items-center gap-2.5 cursor-pointer"
          style={{ background: "none", border: "none" }}
        >
          <span className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-primary overflow-hidden shadow-lg shadow-primary/20">
            <span className="font-display text-white font-bold text-[15px]">G</span>
            <span className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />
          </span>
          <div className="flex flex-col leading-none">
            <span className="font-display font-bold text-[16px] text-text tracking-tight">
              GenoLife<span className="text-ai font-semibold">AI</span>
            </span>
            <span className="text-[10px] text-text-tertiary tracking-[0.12em] uppercase font-medium">
              Genetic Health
            </span>
          </div>
        </button>

        {/* Nav pills — numbered workflow + home */}
        <div className="flex items-center gap-1 bg-gray-100/60 rounded-full p-1">
          {/* 首页按钮 */}
          <button
            onClick={() => goTo("home")}
            style={{ border: "none", background: currentPage === "home" ? "white" : "none" }}
            className={`relative flex items-center gap-1.5 px-3 py-2 rounded-full transition-all duration-200 cursor-pointer ${
              currentPage === "home"
                ? "bg-white text-primary shadow-sm"
                : "text-text-tertiary hover:text-text"
            }`}
          >
            <Home size={14} />
            {currentPage === "home" && (
              <motion.span
                layoutId="nav-active-dot"
                className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-accent"
                transition={{ type: "spring", stiffness: 400, damping: 28 }}
              />
            )}
          </button>

          {links.map((link) => {
            const isActive = currentPage === link.id;
            const labelText = link.labelKey ? t("nav", link.labelKey) : link.label;
            return (
              <button
                key={link.id}
                onClick={() => goTo(link.id)}
                style={{ border: "none", background: isActive ? "white" : "none" }}
                className={`relative flex items-center gap-1.5 px-4 py-2 rounded-full transition-all duration-200 cursor-pointer ${
                  isActive
                    ? "bg-white text-primary shadow-sm"
                    : "text-text-tertiary hover:text-text"
                }`}
              >
                {/* Step number — always visible */}
                <span
                  className={`text-[11px] font-mono font-bold ${
                    isActive ? "text-accent" : "text-text-tertiary/60"
                  }`}
                >
                  {link.step}
                </span>
                {/* Label */}
                <span className="text-[12px] font-semibold">{labelText}</span>
                {/* Active indicator dot */}
                {isActive && (
                  <motion.span
                    layoutId="nav-active-dot"
                    className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-accent"
                    transition={{ type: "spring", stiffness: 400, damping: 28 }}
                  />
                )}
              </button>
            );
          })}
        </div>

        {/* 语言切换 */}
        <div className="flex items-center gap-1">
          {/* 隐私中心链接 */}
          <button
            onClick={() => goTo("privacy")}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-full text-[12px] font-semibold transition-colors cursor-pointer ${
              currentPage === "privacy"
                ? "bg-white text-accent shadow-sm"
                : "text-text-tertiary hover:text-text"
            }`}
            style={{ border: "none", background: currentPage === "privacy" ? "white" : "none" }}
          >
            <Shield size={14} />
            <span className="hidden sm:inline">{t("nav", "privacy")}</span>
          </button>

          <button
            onClick={toggleLang}
            className="flex items-center gap-1.5 px-3 py-2 rounded-full text-[12px] font-semibold text-text-secondary hover:text-text bg-gray-100/60 hover:bg-gray-200/60 cursor-pointer transition-colors"
            style={{ border: "none" }}
          >
            <span className="text-[14px]">{lang === "zh" ? "🌐" : "🌐"}</span>
            {lang === "zh" ? "EN" : "中文"}
          </button>
        </div>
      </div>
    </nav>
  );
}