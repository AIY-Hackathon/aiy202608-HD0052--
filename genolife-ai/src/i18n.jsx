/**
 * 语言上下文 — 中英双语切换
 * 管理全局语言状态，提供翻译函数 t(key)。
 */
import { createContext, useContext, useState, useCallback } from "react";

const LanguageContext = createContext(null);

export const translations = {
  en: {
    nav: { analysis: "Genetic Analysis", simulation: "Health Simulation", report: "Export Report" },
    common: { uploadFirst: "Please upload your genetic report to view analysis" },
  },
  zh: {
    nav: { analysis: "基因分析", simulation: "健康模拟", report: "报告导出" },
    common: { uploadFirst: "请先上传您的基因报告以查看分析" },
  },
};

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState("zh");

  const t = useCallback((section, key) => translations[lang]?.[section]?.[key] ?? key, [lang]);
  const toggleLang = useCallback(() => setLang((prev) => (prev === "zh" ? "en" : "zh")), []);

  return (
    <LanguageContext.Provider value={{ lang, setLang, toggleLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
