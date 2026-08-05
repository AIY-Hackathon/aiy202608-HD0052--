/**
 * Simple page transition context.
 * Manages current page state, reportId, uploaded status, and provides smooth page switching.
 */
import { createContext, useContext, useState, useCallback } from "react";

const LocationContext = createContext(null);

export function LocationProvider({ children }) {
  const [currentPage, setCurrentPage] = useState("home");
  const [reportId, setReportId] = useState(null);
  // 是否已上传基因报告（控制页面数据展示：未上传时留空）
  const [uploaded, setUploaded] = useState(false);

  const goTo = useCallback((page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  return (
    <LocationContext.Provider
      value={{ currentPage, goTo, reportId, setReportId, uploaded, setUploaded }}
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
