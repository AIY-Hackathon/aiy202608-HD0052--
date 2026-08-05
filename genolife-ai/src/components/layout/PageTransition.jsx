/**
 * Simple page transition context.
 * Manages current page state, reportId, uploaded status, and provides smooth page switching.
 */
import { createContext, useContext, useState, useCallback } from "react";

const LocationContext = createContext(null);

export function LocationProvider({ children }) {
  const [currentPage, setCurrentPage] = useState("home");
  const [reportId, setReportId] = useState(() => {
    try { return localStorage.getItem("genolife_active_report") || null; }
    catch { return null; }
  });
  // 是否已上传基因报告（控制页面数据展示：未上传时留空）
  // 从 localStorage 恢复，确保页面切换/刷新后评分正常显示
  const [uploaded, setUploaded] = useState(() => {
    try { return !!localStorage.getItem("genolife_active_report"); }
    catch { return false; }
  });
  // 分析结果分类：null=未分析, "normal"=正常, "abnormal"=异常
  // 分类标准：pathogenicCount > 0 或 healthScore < 60 → abnormal
  const [analysisResult, setAnalysisResult] = useState(null);

  const goTo = useCallback((page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  return (
    <LocationContext.Provider
      value={{ currentPage, goTo, reportId, setReportId, uploaded, setUploaded, analysisResult, setAnalysisResult }}
    >
      {children}
    </LocationContext.Provider>
  );
}

export function useLocation() {
  const ctx = useContext(LocationContext);
  if (!ctx) throw new Error("useLocation must be used within LocationProvider");
  return ctx;
}
