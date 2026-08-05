import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLocation } from "../components/layout/PageTransition";
import { useLanguage } from "../i18n";
import { FileDown, FileText, CheckCircle2, Eye, Download, ShieldAlert, FileCheck, AlignLeft, Copy, Check } from "lucide-react";
import { exportReport, getProfile, exportTextReport } from "../api/client";
import DOMPurify from "dompurify";
import ReactMarkdown from "react-markdown";

export default function ReportPage() {
  const { reportId, uploaded } = useLocation();
  const { t } = useLanguage();
  const [selectedSections, setSelectedSections] = useState(new Set(["summary", "variants", "risk", "recommendations"]));
  const [format, setFormat] = useState("text");
  const [generating, setGenerating] = useState(false);
  const [previewHtml, setPreviewHtml] = useState(null);
  const [previewMd, setPreviewMd] = useState(null);
  const [apiError, setApiError] = useState("");
  const [copied, setCopied] = useState(false);

  const SECTIONS = [
    { id: "summary", key: "sectionSummary", keyDesc: "sectionSummaryDesc", icon: FileText },
    { id: "variants", key: "sectionVariants", keyDesc: "sectionVariantsDesc", icon: FileCheck },
    { id: "risk", key: "sectionRisk", keyDesc: "sectionRiskDesc", icon: ShieldAlert },
    { id: "recommendations", key: "sectionRecommendations", keyDesc: "sectionRecommendationsDesc", icon: CheckCircle2 },
  ];

  const FORMATS = [
    { id: "text", key: "optTextLabel", keyDesc: "optTextDesc", icon: AlignLeft },
    { id: "html", key: "optHtmlLabel", keyDesc: "optHtmlDesc", icon: Eye },
    { id: "pdf", key: "optPdfLabel", keyDesc: "optPdfDesc", icon: Download },
  ];

  const allSelected = selectedSections.size === SECTIONS.length;

  // 加载基因档案（用于传给后端）
  const [geneticProfile, setGeneticProfile] = useState(null);
  useEffect(() => {
    let cancelled = false;
    getProfile()
      .then((data) => { if (!cancelled) setGeneticProfile(data); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  const toggleSection = (id) => {
    setSelectedSections((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleAll = () => {
    if (allSelected) {
      setSelectedSections(new Set());
    } else {
      setSelectedSections(new Set(SECTIONS.map((s) => s.id)));
    }
  };

  // ── 生成报告（调用后端真实 API）──
  const handleGenerate = async () => {
    setGenerating(true);
    setApiError("");
    setCopied(false);
    try {
      if (format === "text") {
        const result = await exportTextReport(reportId);
        setPreviewMd(result.data);
        setPreviewHtml(null);
        return;
      }
      if (format === "html") {
        const result = await exportReport(reportId || undefined, {
          selectedSections: Array.from(selectedSections),
          format: "html",
        });
        setPreviewHtml(result.data);
        setPreviewMd(null);
        return;
      }
      if (format === "pdf") {
        // PDF 需要后端 WeasyPrint 支持，先尝试获取
        const result = await exportReport(reportId || undefined, {
          selectedSections: Array.from(selectedSections),
          format: "pdf",
        });
        const blob = result.data instanceof Blob
          ? result.data
          : new Blob([result.data], { type: "application/pdf" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = result.filename || `genolife-report-${reportId || "demo"}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
        setPreviewHtml(null);
        setPreviewMd(null);
      }
    } catch (err) {
      setApiError(err.message || "报告生成失败");
      setPreviewHtml(null);
      setPreviewMd(null);
    } finally {
      setGenerating(false);
    }
  };

  // ── 下载 ──
  const handleDownload = () => {
    if (previewMd) {
      const blob = new Blob([previewMd], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `genolife-report-${reportId || "demo"}.md`;
      a.click();
      URL.revokeObjectURL(url);
      return;
    }
    if (previewHtml) {
      const blob = new Blob([previewHtml], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `genolife-report-${reportId || "demo"}.html`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  // ── 复制 Markdown ──
  const handleCopy = async () => {
    if (!previewMd) return;
    try {
      await navigator.clipboard.writeText(previewMd);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 pt-28 pb-24">
      {/* ================================================================
          HERO
         ================================================================ */}
      <motion.section
        className="mb-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-light/60 text-primary mb-8">
          <FileDown size={14} />
          <span className="text-[12px] font-bold uppercase tracking-[0.12em]">{t("report", "stepBadge")}</span>
        </div>

        <h1 className="font-display font-bold text-[32px] text-text mb-2 tracking-tight">
          {t("report", "heroTitle")}
        </h1>
        <p className="text-[15px] text-text-secondary max-w-md leading-relaxed">
          {t("report", "heroDesc")}
        </p>
      </motion.section>

      {/* ================================================================
          DATA AREA — 仅在已上传后显示
         ================================================================ */}
      {uploaded ? (
      <>
      {/* ================================================================
          SECTION SELECTION
         ================================================================ */}
      <section className="mb-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display font-bold text-[17px] text-text">{t("report", "reportSections")}</h2>
          <button
            onClick={toggleAll}
            className="text-[13px] font-semibold text-primary hover:text-primary-600 transition-colors cursor-pointer"
            style={{ background: "none", border: "none" }}
          >
            {allSelected ? t("report", "deselectAll") : t("report", "selectAll")}
          </button>
        </div>

        <div className="space-y-3">
          {SECTIONS.map((section, i) => {
            const selected = selectedSections.has(section.id);
            const Icon = section.icon;
            return (
              <motion.div
                key={section.id}
                className={`premium-card px-5 py-4 flex items-center gap-4 cursor-pointer transition-all duration-200 ${
                  selected ? "ring-2 ring-primary/20 bg-primary-light/5" : "opacity-70 hover:opacity-100"
                }`}
                onClick={() => toggleSection(section.id)}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.08 + i * 0.05 }}
              >
                <div
                  className={`w-6 h-6 rounded-md border-2 flex items-center justify-center flex-shrink-0 transition-all ${
                    selected ? "bg-primary border-primary" : "border-gray-200 bg-white"
                  }`}
                >
                  {selected && (
                    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                      <path d="M2.5 6.5L5.5 9.5L10.5 3.5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  )}
                </div>
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  selected ? "bg-primary-light" : "bg-gray-100"
                }`}>
                  <Icon size={18} className={selected ? "text-primary" : "text-text-tertiary"} />
                </div>
                <div>
                  <p className="text-[14px] font-semibold text-text">{t("report", section.key)}</p>
                  <p className="text-[12px] text-text-tertiary">{t("report", section.keyDesc)}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* ================================================================
          FORMAT SELECTION
         ================================================================ */}
      <section className="mb-10">
        <h2 className="font-display font-bold text-[17px] text-text mb-4">{t("report", "formatLabel")}</h2>
        <div className="flex items-center gap-3">
          {FORMATS.map((opt) => {
            const active = format === opt.id;
            const Icon = opt.icon;
            return (
              <button
                key={opt.id}
                onClick={() => { setFormat(opt.id); setPreviewHtml(null); }}
                className={`flex-1 premium-card px-5 py-4 flex items-center gap-4 transition-all duration-200 cursor-pointer ${
                  active ? "ring-2 ring-primary/30 bg-primary-light/5" : "hover:bg-gray-50"
                }`}
                style={{ border: active ? undefined : "1px solid rgba(0,0,0,0.06)" }}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  active ? "bg-primary-light" : "bg-gray-100"
                }`}>
                  <Icon size={18} className={active ? "text-primary" : "text-text-tertiary"} />
                </div>
                <div className="text-left">
                  <p className="text-[14px] font-semibold text-text">{t("report", opt.key)}</p>
                  <p className="text-[12px] text-text-tertiary">{t("report", opt.keyDesc)}</p>
                </div>
                <div className={`ml-auto w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                  active ? "border-primary" : "border-gray-200"
                }`}>
                  {active && <div className="w-2.5 h-2.5 rounded-full bg-primary" />}
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* ================================================================
          GENERATE BUTTON
         ================================================================ */}
      <div className="mb-10">
        <button
          onClick={handleGenerate}
          disabled={selectedSections.size === 0 || generating}
          className={`w-full flex items-center justify-center gap-3 px-6 py-4 rounded-2xl text-[15px] font-bold transition-all cursor-pointer ${
            selectedSections.size === 0 || generating
              ? "bg-gray-100 text-text-tertiary cursor-not-allowed"
              : "bg-primary text-white hover:bg-primary-600 shadow-xl shadow-primary/20"
          }`}
          style={{ border: "none" }}
        >
          {generating ? (
            <>
              <div className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              {t("report", "generatingReport")}
            </>
          ) : format === "text" ? (
            <>
              <AlignLeft size={18} />
              {t("report", "generateText")}
            </>
          ) : format === "html" ? (
            <>
              <Eye size={18} />
              {t("report", "generatePreview")}
            </>
          ) : (
            <>
              <Download size={18} />
              {t("report", "generatePdf")}
            </>
          )}
        </button>

        {/* API error */}
        {apiError && (
          <div className="mt-3 flex items-center gap-2 text-[13px] text-risk-high bg-red-50 rounded-xl px-4 py-3">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {apiError}
          </div>
        )}
      </div>

      {/* ================================================================
          PREVIEW
         ================================================================ */}
      {(previewHtml || previewMd) && (
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-10"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-bold text-[18px] text-text">{t("report", "previewTitle")}</h2>
            <div className="flex items-center gap-3">
              {previewMd && (
                <button
                  onClick={handleCopy}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-[13px] font-semibold text-text-secondary hover:text-text bg-gray-100 hover:bg-gray-200 transition-colors cursor-pointer"
                  style={{ border: "none" }}
                >
                  {copied ? <Check size={14} className="text-accent" /> : <Copy size={14} />}
                  {copied ? t("report", "copied") || "已复制" : t("report", "copyMarkdown") || "复制 Markdown"}
                </button>
              )}
              {previewHtml && (
                <button
                  onClick={() => window.print()}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-[13px] font-semibold text-text-secondary hover:text-text bg-gray-100 hover:bg-gray-200 transition-colors cursor-pointer"
                  style={{ border: "none" }}
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="6 9 6 2 18 2 18 9" /><path d="M6 12H4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-4a2 2 0 0 0-2-2h-2" /><rect x="6" y="14" width="12" height="8" />
                  </svg>
                  {t("report", "print")}
                </button>
              )}
              <button
                onClick={handleDownload}
                className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-primary text-white text-[13px] font-semibold hover:bg-primary-600 transition-colors shadow-lg shadow-primary/20 cursor-pointer"
                style={{ border: "none" }}
              >
                <Download size={14} />
                {previewMd ? t("report", "downloadText") : t("report", "downloadHtml")}
              </button>
            </div>
          </div>

          <div className="premium-card p-8 bg-white overflow-auto max-h-[600px] shadow-inner">
            {previewMd ? (
              <div className="prose prose-sm max-w-none text-[14px] leading-relaxed text-text-secondary">
                <ReactMarkdown>{previewMd}</ReactMarkdown>
              </div>
            ) : (
              <div
                className="prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(previewHtml) }}
              />
            )}
          </div>
        </motion.section>
      )}
      </>
      ) : (
        /* 未上传时：显示引导占位 */
        <motion.section
          className="mb-14 text-center py-20"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-6">
            <FileDown size={26} className="text-text-tertiary" />
          </div>
          <h2 className="font-display font-bold text-[20px] text-text mb-2">
            {t("report", "uploadFirst")}
          </h2>
          <p className="text-[14px] text-text-tertiary max-w-md mx-auto leading-relaxed">
            {t("common", "uploadFirst")}
          </p>
        </motion.section>
      )}
    </div>
  );
}