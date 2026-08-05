/**
 * 模块一：基因档案分析（Genetic Analysis）
 * 包含：VCF 上传 + 基因档案 + 健康指数 + 关键发现 + 基因卡片 + 风险雷达 + 变异表格
 */
import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import HealthScoreRing from "../components/shared/HealthScoreRing";
import GeneCard from "../components/shared/GeneCard";
import RiskBar from "../components/shared/RiskBar";
import RiskRadar from "../components/charts/RiskRadar";
import Gene3DViewer from "../components/Gene3DViewer";
import AdvancedVisualizations from "../components/AdvancedVisualizations";
import PopulationSelector from "../components/PopulationSelector";
import { useLocation } from "../components/layout/PageTransition";
import { useLanguage } from "../i18n";
import { getProfile, uploadReport, getAnalysis } from "../api/client";
import {
  Dna,
  ShieldAlert,
  Upload,
  FileText,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Search,
  TrendingUp,
  Trash2,
  ChevronDown,
  CheckCircle,
} from "lucide-react";

const ALLOWED_EXTS = [".vcf", ".vcf.gz", ".tsv", ".txt"];
const MAX_SIZE = 100 * 1024 * 1024;

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/* ── Trait chip ── */
function TraitCard({ trait, index = 0 }) {
  return (
    <motion.div
      className="premium-card px-5 py-4 flex items-center gap-4"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 + index * 0.08, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -3 }}
    >
      <span className="text-2xl flex-shrink-0">{trait.icon}</span>
      <div className="min-w-0">
        <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em]">{trait.label}</p>
        <p className="text-[14px] font-semibold text-text leading-snug">{trait.trait}</p>
        <p className="text-[12px] text-text-tertiary truncate">{trait.detail}</p>
      </div>
    </motion.div>
  );
}

/* ── Risk summary card ── */
function RiskSummaryCard({ card, index = 0 }) {
  return (
    <motion.div
      className={`premium-card px-6 py-5 border-l-3 ${card.bg} ${card.border}`}
      style={{ borderLeftWidth: 3 }}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.45 + index * 0.07, duration: 0.5 }}
      whileHover={{ y: -3 }}
    >
      <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em] mb-1">{card.label}</p>
      <p className={`text-[13px] font-bold ${card.levelColor} mb-2`}>{card.level}</p>
      <p className="text-[12px] text-text-secondary leading-relaxed">{card.desc}</p>
    </motion.div>
  );
}

/* ── Skeleton ── */
function SkeletonBlock({ className = "" }) {
  return <div className={`animate-pulse bg-gray-100 rounded-xl ${className}`} />;
}

/* ── ClinVar badge ── */
function ClinvarBadge({ significance, reviewStatus }) {
  const config = {
    Pathogenic: { bg: "bg-red-50", text: "text-red-600", icon: AlertTriangle },
    Likely_pathogenic: { bg: "bg-orange-50", text: "text-orange-600", icon: AlertTriangle },
    Uncertain_significance: { bg: "bg-gray-50", text: "text-gray-500", icon: HelpCircle },
    VUS: { bg: "bg-gray-50", text: "text-gray-500", icon: HelpCircle },
    Likely_benign: { bg: "bg-emerald-50", text: "text-emerald-600", icon: CheckCircle2 },
    Benign: { bg: "bg-emerald-50", text: "text-emerald-600", icon: CheckCircle2 },
    Conflicting: { bg: "bg-amber-50", text: "text-amber-600", icon: AlertTriangle },
  };
  const c = config[significance] || config.Uncertain_significance;
  const Icon = c.icon;
  const label = (significance || "VUS").replace(/_/g, " ");
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[11px] font-bold ${c.bg} ${c.text}`}>
      <Icon size={12} />
      {label}
      {reviewStatus && (
        <span className="text-[10px] opacity-70 ml-0.5">{"⭐".repeat(Math.min(reviewStatus, 4))}</span>
      )}
    </span>
  );
}

function MiniRiskBar({ score }) {
  const clamped = Math.max(0, Math.min(100, (score || 0) * 100));
  const color = clamped > 70 ? "bg-risk-high" : clamped > 40 ? "bg-risk-moderate" : "bg-risk-low";
  return (
    <div className="w-16 h-1.5 rounded-full bg-gray-100 overflow-hidden">
      <div className={`h-full rounded-full ${color} transition-all duration-500`} style={{ width: `${clamped}%` }} />
    </div>
  );
}

export default function GeneMap() {
  const { goTo, setReportId, uploaded, setUploaded } = useLocation();
  const { t } = useLanguage();
  const fileInputRef = useRef(null);
  const [expandedGene, setExpandedGene] = useState(null);

  // ── 上传状态 ──
  const [file, setFile] = useState(null);
  const [dragover, setDragover] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("idle"); // idle | uploading | done | error
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState("");
  const [uploadResult, setUploadResult] = useState(null);

  // ── 报告列表管理（localStorage 持久化） ──
  const [reportHistory, setReportHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("genolife_reports") || "[]");
    } catch { return []; }
  });
  const [activeReportId, setActiveReportId] = useState(() => {
    try {
      return localStorage.getItem("genolife_active_report") || null;
    } catch { return null; }
  });
  const [showReportList, setShowReportList] = useState(false);

  const persistReports = useCallback((reports, activeId) => {
    setReportHistory(reports);
    localStorage.setItem("genolife_reports", JSON.stringify(reports));
    if (activeId !== undefined) {
      setActiveReportId(activeId);
      localStorage.setItem("genolife_active_report", activeId || "");
    }
  }, []);

  const switchReport = useCallback((reportId) => {
    setActiveReportId(reportId);
    localStorage.setItem("genolife_active_report", reportId);
    setReportId(reportId);
    setUploaded(true);
    setShowReportList(false);
    // 触发重新加载数据
    setUploadResult({ report_id: reportId });
  }, [setReportId, setUploaded]);

  const deleteReport = useCallback((reportId, e) => {
    e.stopPropagation();
    const updated = reportHistory.filter(r => r.reportId !== reportId);
    persistReports(updated, updated.length > 0 ? updated[0].reportId : null);
    if (updated.length === 0) {
      setUploaded(false);
      setReportId(null);
      setUploadResult(null);
      setAnalysisData(null);
      setUploadStatus("idle");
      setFile(null);
    } else if (activeReportId === reportId) {
      // 如果删除的是当前活跃报告，切换到第一个
      switchReport(updated[0].reportId);
    }
  }, [reportHistory, activeReportId, persistReports, setUploaded, setReportId, switchReport]);

  // ── 档案数据 ──
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  // ── 真实 variants（上传后从 /api/analysis/:id 加载）
  const [analysisData, setAnalysisData] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  // ── 3D 基因可视化状态 ──
  const [view3DGene, setView3DGene] = useState(null);

  // ── 变异表格过滤 ──
  const [searchQuery, setSearchQuery] = useState("");
  const [filterSig, setFilterSig] = useState("all");

  // ── 人群特点（祖先推断参考 + 用户手动选择）──
  const [selectedPopulation, setSelectedPopulation] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        const data = await getProfile();
        if (!cancelled) setProfileData(data);
      } catch {
        // 降级到 mock
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  // 上传完成后加载真实 variants
  useEffect(() => {
    if (!uploadResult?.report_id) return;
    let cancelled = false;
    async function loadAnalysis() {
      try {
        setAnalysisLoading(true);
        const data = await getAnalysis(uploadResult.report_id, { population: selectedPopulation });
        if (!cancelled) setAnalysisData(data);
      } catch {
        // fallback
      } finally {
        if (!cancelled) setAnalysisLoading(false);
      }
    }
    loadAnalysis();
    return () => { cancelled = true; };
  }, [uploadResult?.report_id, selectedPopulation]);

  // ── 数据源：优先用当前报告的 analysisData.profile（随切换刷新），
  //    无 analysisData 时用 profileData（GET /api/profile，组件 mount 时加载一次）
  const activeProfile = analysisData?.profile || profileData;
  const summary = activeProfile?.summary || null;
  const genes = activeProfile?.geneCards || [];
  const risks = activeProfile?.riskDimensions || [];

  // 基因档案 traits（从后端 geneCards 动态生成）
  const profileTraits = genes.slice(0, 4).map((g) => ({
    key: g.id,
    icon: g.icon || "🧬",
    label: g.category?.toUpperCase() || g.symbol?.toUpperCase(),
    trait: g.name || g.symbol,
    detail: g.summary || g.interpretation?.slice(0, 80) + "…",
  }));

  // Key findings（从基因卡片动态生成）
  const findings = genes.slice(0, 3).map((g) => {
    const levelMap = { elevated: "Elevated Risk", moderate: "Moderate Risk", low: "Optimization Opportunity", advantage: "Genetic Advantage" };
    const levelColorMap = { elevated: "text-risk-high", moderate: "text-risk-moderate", low: "text-accent", advantage: "text-accent" };
    const bgMap = { elevated: "bg-red-50/60", moderate: "bg-amber-50/60", low: "bg-accent-light/60", advantage: "bg-accent-light/60" };
    const borderMap = { elevated: "border-red-100", moderate: "border-amber-100", low: "border-accent/20", advantage: "border-accent/20" };
    return {
      key: g.id,
      label: g.category || g.name,
      level: levelMap[g.riskLevel] || "Moderate Risk",
      levelColor: levelColorMap[g.riskLevel] || "text-risk-moderate",
      bg: bgMap[g.riskLevel] || "bg-amber-50/60",
      border: borderMap[g.riskLevel] || "border-amber-100",
      desc: g.summary || g.interpretation?.slice(0, 100) + "…",
    };
  });

  // ── 变异表格数据 ──
  const variants = analysisData?.variants || [];
  const pathogenicCount = variants.filter((v) => v.clinvar_significance?.includes("Pathogenic")).length;
  const benignCount = variants.filter((v) => v.clinvar_significance === "Benign" || v.clinvar_significance === "Likely_benign").length;
  const vusCount = variants.filter((v) => v.clinvar_significance === "Uncertain_significance" || !v.clinvar_significance).length;

  const filteredVariants = variants.filter((v) => {
    if (filterSig !== "all") {
      if (filterSig === "VUS" && v.clinvar_significance !== "Uncertain_significance") return false;
      if (filterSig === "Pathogenic" && !v.clinvar_significance?.includes("Pathogenic")) return false;
      if (filterSig === "Benign" && v.clinvar_significance !== "Benign" && v.clinvar_significance !== "Likely_benign") return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const haystack = [v.gene_name, v.rs_id, v.clinvar_significance, v.chromosome].filter(Boolean).join(" ").toLowerCase();
      if (!haystack.includes(q)) return false;
    }
    return true;
  });

  // ── 文件校验 ──
  const validateFile = useCallback((f) => {
    const ext = "." + f.name.split(".").pop()?.toLowerCase();
    const fullExt = f.name.endsWith(".vcf.gz") ? ".vcf.gz" : ext;
    if (!ALLOWED_EXTS.includes(fullExt)) return `不支持 "${fullExt}" 格式，仅支持 ${ALLOWED_EXTS.join(", ")}`;
    if (f.size > MAX_SIZE) return `文件过大 (${formatSize(f.size)})，最大支持 100MB`;
    return null;
  }, []);

  // ── 拖拽 ──
  const handleDragOver = (e) => { e.preventDefault(); setDragover(true); };
  const handleDragLeave = (e) => { e.preventDefault(); setDragover(false); };
  const handleDrop = (e) => {
    e.preventDefault();
    setDragover(false);
    const f = e.dataTransfer.files[0];
    if (!f) return;
    const err = validateFile(f);
    if (err) { setUploadStatus("error"); setUploadError(err); setFile(null); return; }
    setFile(f);
    setUploadStatus("idle");
    setUploadError("");
  };
  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    const err = validateFile(f);
    if (err) { setUploadStatus("error"); setUploadError(err); setFile(null); return; }
    setFile(f);
    setUploadStatus("idle");
    setUploadError("");
  };

  // ── 上传 ──
  const handleUpload = async () => {
    if (!file) return;
    setUploadStatus("uploading");
    setUploadProgress(0);
    setUploadError("");
    const interval = setInterval(() => {
      setUploadProgress((prev) => (prev >= 90 ? prev : prev + Math.random() * 20));
    }, 300);
    try {
      const result = await uploadReport(file);
      clearInterval(interval);
      setUploadProgress(100);
      setUploadResult(result);
      setUploadStatus("done");
      setUploaded(true);
      // 传递 report_id 给 Report 页
      if (result.report_id) setReportId(result.report_id);
      // 添加到报告历史
      const newEntry = {
        reportId: result.report_id,
        filename: file.name,
        variantCount: result.variant_count,
        createdAt: new Date().toISOString(),
      };
      const updated = [newEntry, ...reportHistory.filter(r => r.reportId !== result.report_id)];
      persistReports(updated, result.report_id);
    } catch (err) {
      clearInterval(interval);
      setUploadStatus("error");
      setUploadProgress(0);
      setUploadError(err.message || "上传失败，请重试");
    }
  };
  const handleUploadReset = () => {
    setFile(null);
    setUploadStatus("idle");
    setUploadProgress(0);
    setUploadError("");
    setUploadResult(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* ================================================================
          HERO
         ================================================================ */}
      <motion.section
        className="mb-10"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
          <div>
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.18em] mb-3">{t("geneMap", "heroBadge")}</p>
            <h1 className="font-display font-bold text-[26px] sm:text-[30px] text-text tracking-tight leading-tight mb-2">
              {t("geneMap", "heroTitle")}
            </h1>
            <p className="text-[15px] text-text-secondary max-w-md leading-relaxed">
              {t("geneMap", "heroDesc")} <span className="text-text-tertiary">{t("geneMap", "heroDescDim")}</span>
            </p>
          </div>
          <div className="flex items-center gap-4 text-[11px] text-text-tertiary">
            <div className="text-right">
              <p className="font-mono text-text-secondary font-semibold">#GNO-2026-0001</p>
              <p>Generated Aug 2026</p>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-right">
              <p className="text-text-secondary font-semibold">Alex</p>
              <p>Age 30 · Male</p>
            </div>
          </div>
        </div>

        {/* ── 报告列表管理 ── */}
        {reportHistory.length > 0 && (
          <div className="mt-4 relative">
            <button
              onClick={() => setShowReportList(!showReportList)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-gray-200 text-[13px] font-semibold text-text hover:border-primary/30 transition-colors cursor-pointer"
              style={{ background: "white" }}
            >
              <FileText size={14} className="text-primary" />
              {t("geneMap", "myReports")}: {reportHistory.length} {t("geneMap", "reportsCount")}
              <ChevronDown size={14} className={`transition-transform ${showReportList ? "rotate-180" : ""}`} />
            </button>
            {activeReportId && (
              <span className="ml-3 text-[12px] text-text-tertiary">
                {t("geneMap", "activeReport")}: <span className="font-mono text-accent font-semibold">{activeReportId}</span>
              </span>
            )}
            {showReportList && (
              <div className="absolute top-full mt-2 left-0 w-80 bg-white rounded-xl border border-gray-200 shadow-xl z-40 overflow-hidden">
                <div className="max-h-60 overflow-y-auto">
                  {reportHistory.map((r) => (
                    <div
                      key={r.reportId}
                      onClick={() => switchReport(r.reportId)}
                      className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors cursor-pointer border-b border-gray-100 last:border-0 ${activeReportId === r.reportId ? "bg-primary-light/30" : ""}`}
                      style={{ background: activeReportId === r.reportId ? "var(--color-primary-light, #eef2ff)" : "none" }}
                    >
                      {activeReportId === r.reportId ? (
                        <CheckCircle size={16} className="text-accent flex-shrink-0" />
                      ) : (
                        <FileText size={16} className="text-text-tertiary flex-shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-[13px] font-semibold text-text truncate">{r.filename}</p>
                        <p className="text-[11px] text-text-tertiary">
                          {r.variantCount || "?"} variants · {new Date(r.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => deleteReport(r.reportId, e)}
                        className="p-1.5 rounded-lg hover:bg-red-50 text-text-tertiary hover:text-red-500 transition-colors cursor-pointer flex-shrink-0"
                        style={{ border: "none", background: "none" }}
                        title={t("geneMap", "deleteReport")}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </motion.section>

      {/* ================================================================
          UPLOAD ZONE — 可折叠
         ================================================================ */}
      {uploadStatus !== "done" && (
        <motion.section
          className="mb-12"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08 }}
        >
          <div
            className={`relative rounded-2xl border-2 border-dashed p-8 text-center transition-all duration-200 cursor-pointer ${
              dragover
                ? "border-primary bg-primary-light/40 scale-[1.01]"
                : file
                  ? "border-accent bg-accent-light/20"
                  : "border-gray-200 hover:border-gray-300 bg-white"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !file && fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".vcf,.vcf.gz,.tsv,.txt"
              onChange={handleFileChange}
              className="hidden"
            />
            {!file ? (
              <div className="flex flex-col items-center gap-3">
                <motion.div
                  className="w-14 h-14 rounded-2xl bg-primary-light flex items-center justify-center"
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                >
                  <Dna size={28} className="text-primary" />
                </motion.div>
                <div>
                  <p className="font-display font-bold text-[16px] text-text mb-1">
                    {t("geneMap", "uploadTitle")}
                  </p>
                  <p className="text-[12px] text-text-tertiary">
                    {t("geneMap", "uploadHint")} <span className="text-primary font-semibold underline underline-offset-2">{t("geneMap", "uploadBrowse")}</span>
                  </p>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-text-tertiary font-medium">
                  <span className="px-2 py-0.5 rounded-full bg-gray-100">.vcf</span>
                  <span className="px-2 py-0.5 rounded-full bg-gray-100">.vcf.gz</span>
                  <span className="px-2 py-0.5 rounded-full bg-gray-100">.tsv</span>
                  <span>{t("geneMap", "uploadMaxSize")}</span>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <div className="w-14 h-14 rounded-2xl bg-accent-light flex items-center justify-center">
                  <FileText size={24} className="text-accent" />
                </div>
                <div>
                  <p className="font-display font-bold text-[16px] text-text mb-1">{file.name}</p>
                  <p className="text-[12px] text-text-tertiary">{formatSize(file.size)}</p>
                </div>
                {uploadStatus === "uploading" && (
                  <div className="w-full max-w-xs">
                    <div className="h-2 rounded-full bg-gray-100 overflow-hidden mb-1.5">
                      <motion.div
                        className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(uploadProgress, 100)}%` }}
                      />
                    </div>
                    <p className="text-[11px] text-text-tertiary">{t("geneMap", "uploadParsing")}</p>
                  </div>
                )}
                {uploadStatus === "error" && (
                  <div className="flex items-center gap-2 text-risk-high">
                    <AlertTriangle size={14} />
                    <p className="text-[12px] font-medium">{uploadError}</p>
                  </div>
                )}
                {uploadStatus !== "uploading" && (
                  <div className="flex items-center gap-3 mt-1">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleUploadReset(); }}
                      className="px-3 py-2 rounded-full text-[12px] font-semibold text-text-tertiary hover:text-text hover:bg-gray-100 transition-colors cursor-pointer"
                      style={{ background: "none", border: "none" }}
                    >
                      {t("geneMap", "uploadChangeFile")}
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleUpload(); }}
                      className="inline-flex items-center gap-1.5 px-5 py-2 rounded-full bg-primary text-white text-[13px] font-semibold hover:bg-primary-600 transition-colors shadow-lg shadow-primary/20 cursor-pointer"
                      style={{ border: "none" }}
                    >
                      <Upload size={14} />
                      {t("geneMap", "uploadStart")}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.section>
      )}

      {/* ================================================================
          UPLOAD SUCCESS BANNER
         ================================================================ */}
      {uploadStatus === "done" && uploadResult && (
        <motion.div
          className="premium-card px-6 py-4 mb-12 flex items-center gap-4 bg-accent-light/20 border-accent/20"
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <CheckCircle2 size={20} className="text-accent flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-[13px] font-semibold text-text">
              {uploadResult.original_filename} — {uploadResult.variant_count} {t("geneMap", "variantsProcessed")}
            </p>
            <p className="text-[11px] text-text-tertiary">{t("geneMap", "reportId")} {uploadResult.report_id}</p>
          </div>
          <button
            onClick={handleUploadReset}
            className="text-[11px] font-semibold text-text-tertiary hover:text-text cursor-pointer flex-shrink-0"
            style={{ background: "none", border: "none" }}
          >
            {t("geneMap", "reupload")}
          </button>
        </motion.div>
      )}

      {/* ================================================================
          DATA AREA — 仅在已上传后显示
         ================================================================ */}
      {uploaded ? (
      <>
      {/* ================================================================
          GENETIC PROFILE
         ================================================================ */}
      <section className="mb-14">
        <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-4">{t("geneMap", "sectionGeneticProfile")}</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
          {profileTraits.map((trait, i) => (
            <TraitCard key={trait.key} trait={trait} index={i} />
          ))}
        </div>
      </section>

      {/* ================================================================
          HEALTH INDEX + Variant Stats
         ================================================================ */}
      <div className="flex flex-col lg:flex-row items-center gap-8 mb-14">
        {/* Score ring */}
        <div className="flex-shrink-0">
          {loading ? (
            <SkeletonBlock className="w-[210px] h-[210px] rounded-full" />
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.92 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            >
              <HealthScoreRing score={summary?.score ?? null} size={210} strokeWidth={11} label={summary ? t("geneMap", "geneticHealthIndex") : t("common", "uploadToUnlock")} subtitle={summary ? "/100" : ""} showGlow={!!summary} />
            </motion.div>
          )}
        </div>

        {/* Right: methodology + stats */}
        <div className="flex-1 max-w-xs lg:max-w-none mx-auto lg:mx-0 space-y-5">
          <div>
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em] mb-3 text-center lg:text-left">{t("geneMap", "calculatedFrom")}</p>
            <div className="flex lg:flex-col items-center lg:items-stretch justify-center gap-2 lg:gap-3 flex-wrap lg:flex-nowrap">
              {[
                { label: t("geneMap", "methodologyGenetic"), desc: t("geneMap", "methodologyGeneticDesc") },
                { label: t("geneMap", "methodologyFamily"), desc: t("geneMap", "methodologyFamilyDesc") },
                { label: t("geneMap", "methodologyLifestyle"), desc: t("geneMap", "methodologyLifestyleDesc") },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  className="premium-card px-4 py-3 flex-1 lg:flex-none"
                  style={{ borderLeft: `3px solid ${[i === 0 ? "var(--color-primary)" : i === 1 ? "var(--color-accent)" : "var(--color-risk-moderate)"][i] || "var(--color-primary)"}` }}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.35 + i * 0.08, duration: 0.4 }}
                >
                  <p className="text-[13px] font-semibold text-text">{item.label}</p>
                  <p className="text-[11px] text-text-tertiary">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>

          {/* variant count chips */}
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center gap-1.5 bg-red-50 px-3 py-1.5 rounded-full">
              <AlertTriangle size={12} className="text-red-500" />
              <span className="text-[12px] font-bold text-red-600">{pathogenicCount}</span>
              <span className="text-[10px] text-red-400">{t("geneMap", "chipPathogenic")}</span>
            </div>
            <div className="flex items-center gap-1.5 bg-gray-50 px-3 py-1.5 rounded-full">
              <HelpCircle size={12} className="text-gray-400" />
              <span className="text-[12px] font-bold text-gray-500">{vusCount}</span>
              <span className="text-[10px] text-gray-400">{t("geneMap", "chipVUS")}</span>
            </div>
            <div className="flex items-center gap-1.5 bg-emerald-50 px-3 py-1.5 rounded-full">
              <CheckCircle2 size={12} className="text-emerald-500" />
              <span className="text-[12px] font-bold text-emerald-600">{benignCount}</span>
              <span className="text-[10px] text-emerald-400">{t("geneMap", "chipBenign")}</span>
            </div>
          </div>
        </div>
      </div>

      {/* ================================================================
          POPULATION SELECTOR — 人群特点（祖先参考 + 用户选择）
         ================================================================ */}
      <section className="mb-14">
        <PopulationSelector
          ancestry={analysisData?.ancestry || null}
          selectedPopulation={selectedPopulation}
          onSelect={setSelectedPopulation}
        />
      </section>

      {/* ================================================================
          KEY FINDINGS
         ================================================================ */}
      <section className="mb-16">
        <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em] mb-4">{t("geneMap", "sectionKeyFindings")}</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {findings.map((card, i) => (
            <RiskSummaryCard key={card.key} card={card} index={i} />
          ))}
        </div>
      </section>

      {/* ================================================================
          GENE CARDS
         ================================================================ */}
      <section className="mb-16">
        <div className="flex items-center gap-3 mb-8">
          <Dna size={17} className="text-accent" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">{t("geneMap", "sectionDetailedGene")}</p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">{t("geneMap", "sectionDiveDeeper")}</h2>
          </div>
        </div>
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {[1, 2, 3, 4].map((i) => <SkeletonBlock key={i} className="h-48 rounded-2xl" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {genes.length > 0 ? (
              genes.map((gene, i) => (
                <GeneCard
                  key={gene.id}
                  gene={gene}
                  index={i}
                  isExpanded={expandedGene === gene.id}
                  onToggle={() => setExpandedGene(expandedGene === gene.id ? null : gene.id)}
                  onView3D={setView3DGene}
                />
              ))
            ) : (
              <div className="col-span-full premium-card p-12 text-center text-text-tertiary">
                <Dna size={28} className="mx-auto mb-3 opacity-30" />
                <p className="text-[14px] font-semibold">{t("geneMap", "noGeneData")}</p>
                <p className="text-[12px] mt-1">{t("geneMap", "noGeneDataDesc")}</p>
              </div>
            )}
          </div>
        )}
      </section>

      {/* ================================================================
          VARIANT TABLE
         ================================================================ */}
      <section className="mb-16">
        <div className="flex items-center gap-3 mb-6">
          <FileText size={17} className="text-primary" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">{t("geneMap", "variantDetails")}</p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">{t("geneMap", "variantDetailsTitle")}</h2>
          </div>
        </div>

        {/* 科普：如何阅读 */}
        <div className="premium-card px-5 py-4 mb-4 bg-blue-50/40 border border-blue-100/60">
          <p className="text-[12px] font-bold text-primary mb-2.5 flex items-center gap-1.5">
            <HelpCircle size={13} />
            {t("geneMap", "variantHowToRead")}
          </p>
          <p className="text-[11px] text-text-tertiary mb-3">{t("geneMap", "variantHowToReadDesc")}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2">
            {[
              { k: "variantChrPos", key2: "colChrPos" },
              { k: "variantRsid", key2: "colRsid" },
              { k: "variantGene", key2: "colGene" },
              { k: "variantRefAlt", key2: "colRefAlt" },
              { k: "variantClinvar", key2: "colClinvar" },
              { k: "variantRisk", key2: "colRisk" },
            ].map(({ k, key2 }) => (
              <div key={k} className="flex items-start gap-2">
                <span className="shrink-0 px-1.5 py-0.5 rounded-md bg-white text-[10px] font-bold text-text-secondary border border-gray-200 mt-0.5">
                  {t("geneMap", k)}
                </span>
                <p className="text-[11px] text-text-secondary leading-relaxed">{t("geneMap", key2)}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-4">
          <div className="relative flex-1 max-w-xs">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" />
            <input
              type="text"
              placeholder={t("geneMap", "variantSearch")}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-white border border-gray-200 text-[13px] text-text placeholder:text-text-tertiary/70 focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/10 transition-all"
            />
          </div>
          <div className="flex items-center gap-1.5">
            {["all", "Pathogenic", "Benign", "VUS"].map((f) => (
              <button
                key={f}
                onClick={() => setFilterSig(f)}
                className={`px-3 py-1.5 rounded-full text-[12px] font-semibold transition-all cursor-pointer ${filterSig === f ? "bg-primary text-white shadow-sm" : "bg-gray-100 text-text-tertiary hover:text-text hover:bg-gray-200"}`}
                style={{ border: "none" }}
              >
                {f === "all" ? t("geneMap", "variantAll") : f}
              </button>
            ))}
          </div>
        </div>

        <div className="premium-card overflow-hidden">
          {analysisLoading ? (
            <div className="p-12 text-center">
              <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin mx-auto mb-3" />
              <p className="text-[13px] text-text-tertiary">{t("geneMap", "loadingVariants")}</p>
            </div>
          ) : variants.length === 0 ? (
            <div className="p-12 text-center text-text-tertiary">
              <FileText size={28} className="mx-auto mb-3 opacity-30" />
              <p className="text-[14px] font-semibold">{t("geneMap", "noVariantData")}</p>
              <p className="text-[12px] mt-1">{t("geneMap", "noVariantDataDesc")}</p>
            </div>
          ) : (
          <>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50/50">
                  <th className="px-5 py-3 text-[10px] font-bold text-text-tertiary uppercase tracking-[0.1em]">#</th>
                  <th className="px-5 py-3 text-[10px] font-bold text-text-tertiary uppercase tracking-[0.1em]">{t("geneMap", "variantChrPos")}</th>
                  <th className="px-5 py-3 text-[10px] font-bold text-text-tertiary uppercase tracking-[0.1em]">{t("geneMap", "variantRsid")}</th>
                  <th className="px-5 py-3 text-[10px] font-bold text-text-tertiary uppercase tracking-[0.1em]">{t("geneMap", "variantGene")}</th>
                  <th className="px-5 py-3 text-[10px] font-bold text-text-tertiary uppercase tracking-[0.1em]">{t("geneMap", "variantRefAlt")}</th>
                  <th className="px-5 py-3 text-[10px] font-bold text-text-tertiary uppercase tracking-[0.1em]">{t("geneMap", "variantClinvar")}</th>
                  <th className="px-5 py-3 text-[10px] font-bold text-text-tertiary uppercase tracking-[0.1em]">{t("geneMap", "variantRisk")}</th>
                </tr>
              </thead>
              <tbody>
                {filteredVariants.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-5 py-12 text-center text-[13px] text-text-tertiary">{t("geneMap", "variantNoResults")}</td>
                  </tr>
                ) : (
                  filteredVariants.slice(0, 100).map((v, i) => (
                    <tr key={v.id || i} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                      <td className="px-5 py-3 text-[12px] text-text-tertiary font-mono">{i + 1}</td>
                      <td className="px-5 py-3 text-[13px] font-semibold text-text font-mono">{v.chromosome}:{v.position.toLocaleString()}</td>
                      <td className="px-5 py-3 text-[12px] text-accent font-mono">{v.rs_id || "—"}</td>
                      <td className="px-5 py-3 text-[13px] font-semibold text-text">{v.gene_name || "—"}</td>
                      <td className="px-5 py-3 text-[12px] text-text-secondary font-mono">{v.reference} → {v.alternative}</td>
                      <td className="px-5 py-3"><ClinvarBadge significance={v.clinvar_significance} reviewStatus={v.clinvar_review_status} /></td>
                      <td className="px-5 py-3"><MiniRiskBar score={v.risk_score} /></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {filteredVariants.length > 100 && (
            <div className="px-5 py-3 bg-gray-50/50 border-t border-gray-100 text-center text-[12px] text-text-tertiary">
              {t("geneMap", "variantShowingN").replace("{total}", filteredVariants.length)}
            </div>
          )}
          </>
          )}
        </div>

        {/* 科普：ClinVar 标签图例 */}
        <div className="premium-card px-5 py-4 mt-4">
          <p className="text-[12px] font-bold text-text mb-3 flex items-center gap-1.5">
            <HelpCircle size={13} className="text-primary" />
            {t("geneMap", "clinvarLegend")}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-2.5">
            {[
              { sig: "Pathogenic", color: "text-red-600 bg-red-50", label: "clinvarPathogenic" },
              { sig: "Likely_pathogenic", color: "text-orange-600 bg-orange-50", label: "clinvarLikelyPathogenic" },
              { sig: "Uncertain_significance", color: "text-gray-500 bg-gray-50", label: "clinvarVus" },
              { sig: "Likely_benign", color: "text-emerald-600 bg-emerald-50", label: "clinvarLikelyBenign" },
              { sig: "Benign", color: "text-emerald-600 bg-emerald-50", label: "clinvarBenign" },
            ].map(({ sig, color, label }) => (
              <div key={sig} className="flex items-start gap-2">
                <span className={`shrink-0 px-2 py-0.5 rounded-md text-[10px] font-bold ${color} mt-0.5`}>
                  {sig.replace(/_/g, " ")}
                </span>
                <p className="text-[11px] text-text-secondary leading-relaxed">{t("geneMap", label)}</p>
              </div>
            ))}
          </div>
          <p className="mt-3 text-[11px] text-text-tertiary leading-relaxed flex items-start gap-1.5">
            <ShieldAlert size={13} className="shrink-0 mt-0.5 text-risk-moderate" />
            {t("geneMap", "clinvarDisclaimer")}
          </p>
        </div>
      </section>

      {/* ================================================================
          RISK PROFILE — Radar + Bars
         ================================================================ */}
      <section className="mb-16">
        <div className="flex items-center gap-3 mb-8">
          <ShieldAlert size={17} className="text-risk-moderate" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">{t("geneMap", "sectionRiskProfile")}</p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">{t("geneMap", "sectionFiveDimensions")}</h2>
          </div>
        </div>
        {loading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <SkeletonBlock className="h-[320px] rounded-2xl" />
            <div className="space-y-6">{[1, 2, 3, 4, 5].map((i) => <SkeletonBlock key={i} className="h-14 rounded-xl" />)}</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div className="premium-card p-6"><RiskRadar data={risks} height={320} /></div>
            <div className="space-y-6">
              {risks.map((dim) => <RiskBar key={dim.key} label={dim.label} score={dim.score} baseline={dim.baseline} />)}
              <div className="pt-3">
                <p className="text-[12px] text-text-tertiary leading-relaxed bg-gray-50 rounded-xl p-3">
                  {t("geneMap", "riskExplanation")
                    .replace("{threshold}", t("geneMap", "riskExplanationThreshold"))
                    .replace("{lifestyle}", t("geneMap", "riskExplanationLifestyle"))}
                </p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* ================================================================
          ADVANCED VISUALIZATIONS — 基因可视化方案 A/B/D/F
         ================================================================ */}
      <section className="mb-16">
        <div className="flex items-center gap-3 mb-8">
          <ShieldAlert size={17} className="text-primary" />
          <div>
            <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">Advanced Visualizations</p>
            <h2 className="font-display font-bold text-[24px] text-text tracking-tight mt-0.5">Explore your genome from four angles</h2>
          </div>
        </div>
        <AdvancedVisualizations genes={genes} variants={variants} />
      </section>

      {/* ================================================================
          CTA to Simulation
         ================================================================ */}
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <div className="premium-card px-6 py-6 sm:px-8 sm:py-7 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-gradient-to-r from-white to-primary-light/20">
          <div>
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em] mb-1">{t("geneMap", "ctaExploreTitle")}</p>
            <p className="text-[15px] font-semibold text-text leading-snug">
              {t("geneMap", "ctaExploreDesc")}
            </p>
          </div>
          <button
            onClick={() => goTo("simulation")}
            className="flex-shrink-0 inline-flex items-center gap-2 px-5 py-3 rounded-full bg-primary text-white text-[14px] font-semibold hover:bg-primary-600 transition-colors shadow-lg shadow-primary/20 cursor-pointer"
            style={{ border: "none" }}
          >
            {t("geneMap", "ctaSimulate")}
            <TrendingUp size={16} />
          </button>
        </div>
      </motion.section>
      </>
      ) : (
        /* 未上传时：显示引导占位，数据区留空 */
        <motion.section
          className="mb-14 text-center py-20"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-6">
            <Upload size={26} className="text-text-tertiary" />
          </div>
          <h2 className="font-display font-bold text-[20px] text-text mb-2">
            {t("common", "uploadFirst")}
          </h2>
          <p className="text-[14px] text-text-tertiary max-w-md mx-auto leading-relaxed">
            {t("geneMap", "subtitle")}
          </p>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="mt-8 inline-flex items-center gap-2 px-6 py-3 rounded-full bg-primary text-white text-[14px] font-semibold hover:bg-primary-600 transition-colors shadow-lg shadow-primary/20 cursor-pointer"
            style={{ border: "none" }}
          >
            <Upload size={16} />
            {t("geneMap", "uploadReport")}
          </button>
        </motion.section>
      )}

      {/* 3D 基因可视化模态框 */}
      <AnimatePresence>
        {view3DGene && (
          <Gene3DViewer
            gene={view3DGene}
            onClose={() => setView3DGene(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}