/**
 * PrivacyCenter — 儿童基因数据伦理中心
 * ==========================================
 * 模块：
 * 1. [NEW] 双重监护人授权 (Guardian Consent)
 * 2. [KEPT] 数据生命周期管理 (Timeline + 倒计时 + 手动删除)
 * 3. [NEW] AI 安全边界 (AI Safety Boundary)
 * 4. [KEPT] 数据使用政策 (允许 vs 禁止)
 * 5. [NEW] 伦理框架 (Ethical Framework)
 *
 * 页面顺序：Hero → Guardian Consent → Data Lifecycle → AI Safety → Usage Policy → Ethical Framework
 */
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLocation } from "../components/layout/PageTransition";
import { useLanguage } from "../i18n";
import {
  Clock,
  Trash2,
  Shield,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Database,
  Upload,
  Zap,
  BarChart3,
  Timer,
  Lock,
  UsersRound,
  Bot,
  Scale,
  Baby,
  ChevronRight,
  ArrowDown,
} from "lucide-react";

// 删除倒计时常量
const RETENTION_DAYS = 7;

function calculateRemainingDays(createdAt) {
  if (!createdAt) return null;
  const created = new Date(createdAt).getTime();
  const expires = created + RETENTION_DAYS * 24 * 60 * 60 * 1000;
  const remaining = Math.max(0, Math.ceil((expires - Date.now()) / (24 * 60 * 60 * 1000)));
  return remaining;
}

export default function PrivacyCenter() {
  const { uploaded, reportId } = useLocation();
  const { t } = useLanguage();

  // 从 localStorage 读取报告创建时间
  const [reportMeta, setReportMeta] = useState(null);
  const [remainingDays, setRemainingDays] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleted, setDeleted] = useState(false);
  // [NEW] 监护人授权弹窗
  const [showConsentModal, setShowConsentModal] = useState(false);

  useEffect(() => {
    try {
      const reports = JSON.parse(localStorage.getItem("genolife_reports") || "[]");
      if (reports.length > 0) {
        setReportMeta(reports[0]);
        const days = calculateRemainingDays(reports[0].createdAt);
        setRemainingDays(days);
      }
    } catch {
      // ignore
    }
  }, [uploaded, reportId]);

  const handleDelete = () => {
    localStorage.removeItem("genolife_reports");
    localStorage.removeItem("genolife_active_report");
    setDeleted(true);
    setReportMeta(null);
    setRemainingDays(null);
    setShowDeleteModal(false);
  };

  // ── 数据生命周期步骤 ──
  const lifecycleSteps = [
    { key: "uploaded", icon: Upload, active: !!reportMeta || deleted, done: !!reportMeta || deleted },
    { key: "processing", icon: Zap, active: !!reportMeta, done: !!reportMeta },
    { key: "analyzed", icon: BarChart3, active: uploaded && !deleted, done: uploaded && !deleted },
    { key: "deletion", icon: Timer, active: deleted, done: deleted },
  ];

  // ── 数据使用政策 ──
  const allowedItems = [
    { label: t("privacy", "usageAllowed1"), icon: CheckCircle2, color: "text-accent" },
    { label: t("privacy", "usageAllowed2"), icon: CheckCircle2, color: "text-accent" },
  ];

  const prohibitedItems = [
    { label: t("privacy", "usageProhibited1"), icon: XCircle, color: "text-red-400" },
    { label: t("privacy", "usageProhibited2"), icon: XCircle, color: "text-red-400" },
    { label: t("privacy", "usageProhibited3"), icon: XCircle, color: "text-red-400" },
    { label: t("privacy", "usageProhibited4"), icon: XCircle, color: "text-red-400" },
  ];

  // ── [NEW] AI 安全边界 ──
  const aiAllowed = [
    t("privacy", "aiAllow1"),
    t("privacy", "aiAllow2"),
    t("privacy", "aiAllow3"),
    t("privacy", "aiAllow4"),
  ];
  const aiProhibited = [
    t("privacy", "aiProhibit1"),
    t("privacy", "aiProhibit2"),
    t("privacy", "aiProhibit3"),
    t("privacy", "aiProhibit4"),
  ];

  // ── [NEW] 监护人不包含项 ──
  const consentExclusions = [
    t("privacy", "guardianModalNot1"),
    t("privacy", "guardianModalNot2"),
    t("privacy", "guardianModalNot3"),
    t("privacy", "guardianModalNot4"),
  ];

  return (
    <div className="max-w-5xl mx-auto px-6 pt-28 pb-24">
      {/* ================================================================
          HERO — 升级为"儿童基因数据伦理中心"
         ================================================================ */}
      <motion.section
        className="mb-12"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center shadow-sm">
            <Baby size={22} className="text-primary" />
          </div>
          <div>
            <p className="text-[10px] font-bold text-accent uppercase tracking-[0.15em]">
              {t("privacy", "ethicsCenterBadge")}
            </p>
            <h1 className="font-display font-bold text-[26px] sm:text-[30px] text-text tracking-tight leading-tight">
              {t("privacy", "lifecycleTitle")}
            </h1>
          </div>
        </div>
        <p className="text-[15px] text-text-secondary max-w-2xl leading-relaxed ml-[52px]">
          {t("privacy", "pageSubtitle")}
        </p>
      </motion.section>

      {/* ================================================================
          [NEW] 模块1 — Guardian Consent 监护人授权
         ================================================================ */}
      <section className="mb-10">
        <motion.div
          className="premium-card p-6 sm:p-7 border-l-3 border-l-accent"
          style={{ borderLeftWidth: 3 }}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08, duration: 0.5 }}
        >
          {/* Header */}
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <UsersRound size={20} className="text-blue-600" />
            </div>
            <div>
              <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
                Guardian Authorization
              </p>
              <h2 className="font-display font-bold text-[20px] text-text tracking-tight">
                {t("privacy", "guardianTitle")}
              </h2>
            </div>
          </div>

          {/* 说明 */}
          <p className="text-[13px] text-text-secondary leading-relaxed mb-5 bg-accent-light/20 rounded-xl p-4 flex items-start gap-2.5">
            <Shield size={16} className="text-accent flex-shrink-0 mt-0.5" />
            {t("privacy", "guardianSubtitle")}
          </p>

          {/* 两个授权状态 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
            <div className="flex items-center gap-3 p-4 rounded-xl bg-emerald-50/70 border border-emerald-100">
              <div className="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 size={18} className="text-emerald-600" />
              </div>
              <div className="min-w-0">
                <p className="text-[13px] font-semibold text-text leading-snug">
                  {t("privacy", "guardianIdentityLabel")}
                </p>
                <p className="text-[11px] text-emerald-600 font-medium flex items-center gap-1 mt-0.5">
                  <span className="text-[16px] leading-none">✓</span>
                  {t("privacy", "guardianConfirmed")}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-4 rounded-xl bg-emerald-50/70 border border-emerald-100">
              <div className="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                <CheckCircle2 size={18} className="text-emerald-600" />
              </div>
              <div className="min-w-0">
                <p className="text-[13px] font-semibold text-text leading-snug">
                  {t("privacy", "guardianInformedLabel")}
                </p>
                <p className="text-[11px] text-emerald-600 font-medium flex items-center gap-1 mt-0.5">
                  <span className="text-[16px] leading-none">✓</span>
                  {t("privacy", "guardianAccepted")}
                </p>
              </div>
            </div>
          </div>

          {/* Review 按钮 */}
          <button
            onClick={() => setShowConsentModal(true)}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-primary text-white text-[13px] font-semibold hover:bg-primary-600 transition-colors shadow-md shadow-primary/15 cursor-pointer"
            style={{ border: "none" }}
          >
            <UsersRound size={15} />
            {t("privacy", "guardianReviewBtn")}
            <ChevronRight size={14} />
          </button>
        </motion.div>
      </section>

      {/* ================================================================
          [KEPT] 模块2 — Data Lifecycle (原始 + 增强)
         ================================================================ */}
      <section className="mb-10">
        <motion.div
          className="premium-card p-6 sm:p-8"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.14, duration: 0.5 }}
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Clock size={20} className="text-primary" />
            </div>
            <div>
              <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
                {t("privacy", "lifecycleTitle")}
              </p>
              <h2 className="font-display font-bold text-[20px] text-text tracking-tight">
                {t("privacy", "lifecycleSubtitle")}
              </h2>
            </div>
          </div>

          {/* ── 步骤 Timeline ── */}
          <div className="relative">
            <div className="absolute top-5 left-5 right-5 sm:left-8 sm:right-8 h-0.5 bg-gray-100" />
            <div className="relative grid grid-cols-2 sm:grid-cols-4 gap-4">
              {lifecycleSteps.map((step) => {
                const Icon = step.icon;
                const isDone = step.done;
                const isActive = step.active;
                return (
                  <div key={step.key} className="flex flex-col items-center text-center">
                    <div
                      className={`relative z-10 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ${
                        isDone
                          ? "bg-accent text-white shadow-lg shadow-accent/20"
                          : isActive
                            ? "bg-primary text-white shadow-lg shadow-primary/20"
                            : "bg-gray-100 text-text-tertiary"
                      }`}
                    >
                      <Icon size={18} />
                    </div>
                    <p
                      className={`mt-2.5 text-[11px] font-semibold ${
                        isDone ? "text-accent" : isActive ? "text-primary" : "text-text-tertiary"
                      }`}
                    >
                      {t("privacy", `lifecycle${step.key.charAt(0).toUpperCase() + step.key.slice(1)}`)}
                    </p>
                    {isDone && <CheckCircle2 size={12} className="text-accent mt-1" />}
                  </div>
                );
              })}
            </div>
          </div>

          {/* ── 自动删除倒计时/状态 ── */}
          <div className="mt-8 pt-6 border-t border-gray-100">
            {deleted ? (
              <div className="flex items-center gap-3 p-4 rounded-xl bg-red-50/60 border border-red-100">
                <CheckCircle2 size={20} className="text-red-400" />
                <p className="text-[14px] font-semibold text-text">
                  {t("privacy", "lifecycleDeleted")}
                </p>
              </div>
            ) : uploaded && reportMeta ? (
              <div className="space-y-4">
                {/* [ENHANCED] Original VCF File 信息卡片 */}
                <div className="p-4 rounded-xl bg-primary-light/30 border border-primary/10 space-y-3">
                  <div className="flex items-center gap-3">
                    <Database size={18} className="text-primary" />
                    <div>
                      <p className="text-[13px] font-semibold text-text">
                        {reportMeta.filename || "genetic_report"}
                      </p>
                      <p className="text-[11px] text-text-tertiary">
                        {t("privacy", "lifecycleDaysRemaining").replace("{days}", remainingDays)}
                      </p>
                    </div>
                  </div>
                  {/* [NEW] Status + Retention */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <div className="flex items-center gap-2 text-[11px] text-text-secondary bg-white/60 rounded-lg px-3 py-2">
                      <span className="text-[10px] font-bold text-text-tertiary uppercase">Status:</span>
                      <span className="font-semibold text-amber-600">{t("privacy", "lifecycleVcfStatus")}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-text-secondary bg-white/60 rounded-lg px-3 py-2">
                      <span className="text-[10px] font-bold text-text-tertiary uppercase">Period:</span>
                      <span className="font-semibold">{t("privacy", "lifecycleVcfPeriod")}</span>
                    </div>
                  </div>
                </div>

                {/* [NEW] Day 0-7 mini timeline */}
                <div className="flex items-center gap-0 py-2 px-1">
                  {[t("privacy", "lifecycleDay0"), t("privacy", "lifecycleDay1to6"), t("privacy", "lifecycleDay7")].map((label, i) => (
                    <div key={i} className="flex-1 flex items-center">
                      <div className="flex flex-col items-center text-center gap-1.5 flex-1">
                        <div
                          className={`w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold ${
                            i === 0
                              ? "bg-primary text-white"
                              : i === 2
                                ? "bg-risk-high/10 text-risk-high border border-risk-high/20"
                                : "bg-gray-100 text-text-tertiary"
                          }`}
                        >
                          {i === 0 ? "0" : i === 1 ? "1-6" : "7"}
                        </div>
                        <p className="text-[10px] text-text-tertiary leading-tight max-w-[80px]">{label}</p>
                      </div>
                      {i < 2 && (
                        <ArrowDown size={12} className="text-gray-300 flex-shrink-0 -mt-4" />
                      )}
                    </div>
                  ))}
                </div>

                {/* 进度条 */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[12px] text-text-secondary flex items-center gap-1.5">
                      <Timer size={13} />
                      {t("privacy", "lifecycleAutoDelete").replace("{days}", RETENTION_DAYS)}
                    </span>
                    <span className="text-[12px] font-bold text-primary font-mono">
                      {remainingDays}/{RETENTION_DAYS} days
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${
                        remainingDays <= 1 ? "bg-risk-high" : remainingDays <= 3 ? "bg-risk-moderate" : "bg-accent"
                      }`}
                      initial={{ width: 0 }}
                      animate={{ width: `${((RETENTION_DAYS - remainingDays) / RETENTION_DAYS) * 100}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                    />
                  </div>
                </div>

                {/* Delete now 按钮 */}
                <button
                  onClick={() => setShowDeleteModal(true)}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-full bg-red-50 text-red-600 text-[13px] font-semibold hover:bg-red-100 transition-colors cursor-pointer"
                  style={{ border: "none" }}
                >
                  <Trash2 size={14} />
                  {t("privacy", "lifecycleDeleteNow")}
                </button>

                {/* [NEW] VCF note */}
                <p className="text-[11px] text-text-tertiary leading-relaxed flex items-start gap-1.5">
                  <Shield size={12} className="shrink-0 mt-0.5" />
                  {t("privacy", "lifecycleVcfNote")}
                </p>
              </div>
            ) : (
              <div className="text-center py-6">
                <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
                  <Upload size={20} className="text-text-tertiary" />
                </div>
                <p className="text-[13px] text-text-tertiary">
                  上传基因报告后，数据生命周期管理将自动激活。
                </p>
              </div>
            )}

            {/* 说明 */}
            {!reportMeta && (
              <p className="mt-4 text-[11px] text-text-tertiary leading-relaxed flex items-start gap-1.5">
                <Shield size={12} className="shrink-0 mt-0.5" />
                {t("privacy", "lifecycleDeletionNote")}
              </p>
            )}
          </div>
        </motion.div>
      </section>

      {/* ================================================================
          [NEW] 模块3 — AI Safety Boundary
         ================================================================ */}
      <section className="mb-10">
        <motion.div
          className="premium-card p-6 sm:p-7"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center">
              <Bot size={20} className="text-purple-600" />
            </div>
            <div>
              <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
                AI Safety
              </p>
              <h2 className="font-display font-bold text-[20px] text-text tracking-tight">
                {t("privacy", "aiSafetyTitle")}
              </h2>
            </div>
          </div>

          {/* 核心承诺 */}
          <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-purple-50/60 to-accent-light/20 border border-purple-100/50 flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
              <Shield size={18} className="text-purple-600" />
            </div>
            <p className="text-[14px] font-semibold text-text leading-relaxed">
              {t("privacy", "aiSafetySubtitle")}
            </p>
          </div>

          {/* ALLOW / PROHIBITED 双卡片 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* ALLOW */}
            <div className="rounded-xl bg-accent-light/15 border border-accent/15 p-5">
              <h3 className="text-[10px] font-bold text-accent uppercase tracking-[0.15em] mb-3 flex items-center gap-1.5">
                <CheckCircle2 size={14} />
                {t("privacy", "aiAllowTitle")}
              </h3>
              <div className="space-y-2.5">
                {aiAllowed.map((item) => (
                  <div key={item} className="flex items-center gap-2.5">
                    <CheckCircle2 size={13} className="text-accent flex-shrink-0" />
                    <span className="text-[12px] text-text">{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* PROHIBITED */}
            <div className="rounded-xl bg-red-50/40 border border-red-100/50 p-5">
              <h3 className="text-[10px] font-bold text-red-500 uppercase tracking-[0.15em] mb-3 flex items-center gap-1.5">
                <XCircle size={14} />
                {t("privacy", "aiProhibitTitle")}
              </h3>
              <div className="space-y-2.5">
                {aiProhibited.map((item) => (
                  <div key={item} className="flex items-center gap-2.5">
                    <XCircle size={13} className="text-red-400 flex-shrink-0" />
                    <span className="text-[12px] text-text">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ================================================================
          [KEPT] 模块4 — Data Usage Policy
         ================================================================ */}
      <section className="mb-10">
        <motion.div
          className="premium-card p-6 sm:p-7"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.26, duration: 0.5 }}
        >
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Lock size={20} className="text-primary" />
            </div>
            <div>
              <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
                {t("privacy", "usageTitle")}
              </p>
              <h2 className="font-display font-bold text-[20px] text-text tracking-tight">
                {t("privacy", "usageSubtitle")}
              </h2>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* 允许 */}
            <div className="rounded-xl border-t-3 border-t-accent p-5 bg-accent-light/10" style={{ borderTopWidth: 3 }}>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
                  <CheckCircle2 size={16} className="text-accent" />
                </div>
                <h3 className="font-display font-bold text-[15px] text-text">
                  {t("privacy", "usageAllowed")}
                </h3>
              </div>
              <div className="space-y-2.5">
                {allowedItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.label} className="flex items-center gap-3 p-3 rounded-xl bg-white/70">
                      <Icon size={16} className={item.color} />
                      <span className="text-[13px] font-medium text-text">{item.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* 禁止 */}
            <div className="rounded-xl border-t-3 border-t-red-400 p-5 bg-red-50/30" style={{ borderTopWidth: 3 }}>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center">
                  <XCircle size={16} className="text-red-400" />
                </div>
                <h3 className="font-display font-bold text-[15px] text-text">
                  {t("privacy", "usageProhibited")}
                </h3>
              </div>
              <div className="space-y-2.5">
                {prohibitedItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.label} className="flex items-center gap-3 p-3 rounded-xl bg-white/70">
                      <Icon size={16} className={item.color} />
                      <span className="text-[13px] font-medium text-text">{item.label}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* 承诺 */}
          <div className="mt-5 px-5 py-4 rounded-xl bg-primary-light/20 flex items-start gap-3">
            <Shield size={18} className="text-primary flex-shrink-0 mt-0.5" />
            <p className="text-[13px] text-text-secondary leading-relaxed">
              {t("privacy", "usageCommitment")}
            </p>
          </div>
        </motion.div>
      </section>

      {/* ================================================================
          [NEW] 模块5 — Ethical Framework 伦理框架
         ================================================================ */}
      <section className="mb-10">
        <motion.div
          className="premium-card p-6 sm:p-7"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.32, duration: 0.5 }}
        >
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center">
              <Scale size={20} className="text-amber-600" />
            </div>
            <div>
              <p className="text-[12px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
                {t("privacy", "referenceTitle")}
              </p>
              <h2 className="font-display font-bold text-[20px] text-text tracking-tight">
                {t("privacy", "ethicsFrameworkTitle")}
              </h2>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Card 1: ICH E18 */}
            <div className="rounded-xl bg-blue-50/60 border border-blue-100 p-5 flex flex-col gap-3">
              <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Scale size={18} className="text-blue-600" />
              </div>
              <h4 className="font-display font-bold text-[14px] text-text leading-snug">
                {t("privacy", "referenceICHETitle")}
              </h4>
              <p className="text-[12px] text-text-secondary leading-relaxed flex-1">
                {t("privacy", "referenceICHEDesc")}
              </p>
            </div>

            {/* Card 2: Chinese Regulation */}
            <div className="rounded-xl bg-red-50/50 border border-red-100 p-5 flex flex-col gap-3">
              <div className="w-9 h-9 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
                <Scale size={18} className="text-red-500" />
              </div>
              <h4 className="font-display font-bold text-[14px] text-text leading-snug">
                {t("privacy", "referenceChinaTitle")}
              </h4>
              <p className="text-[12px] text-text-secondary leading-relaxed flex-1">
                {t("privacy", "referenceChinaDesc")}
              </p>
            </div>

            {/* Card 3: Medical Disclaimer */}
            <div className="rounded-xl bg-amber-50/60 border border-amber-100 p-5 flex flex-col gap-3">
              <div className="w-9 h-9 rounded-lg bg-amber-100 flex items-center justify-center flex-shrink-0">
                <AlertTriangle size={18} className="text-amber-600" />
              </div>
              <h4 className="font-display font-bold text-[14px] text-text leading-snug">
                {t("privacy", "ethicsMedDisclaimer")}
              </h4>
              <p className="text-[12px] text-text-secondary leading-relaxed flex-1">
                {t("privacy", "ethicsMedDisclaimerDesc")}
              </p>
            </div>
          </div>

          {/* 免责声明 */}
          <p className="mt-4 text-[11px] text-text-tertiary leading-relaxed flex items-start gap-1.5">
            <Shield size={12} className="shrink-0 mt-0.5" />
            {t("privacy", "referenceDisclaimer")}
          </p>
        </motion.div>
      </section>

      {/* ================================================================
          [NEW] Guardian Consent Modal — 授权详情弹窗
         ================================================================ */}
      <AnimatePresence>
        {showConsentModal && (
          <motion.div
            className="fixed inset-0 z-[100] flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div
              className="absolute inset-0 bg-black/30 backdrop-blur-sm"
              onClick={() => setShowConsentModal(false)}
            />
            <motion.div
              className="relative bg-white rounded-2xl shadow-2xl border border-gray-100 max-w-md w-full p-6"
              initial={{ scale: 0.95, y: 10 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 10 }}
            >
              <div className="flex items-center gap-3 mb-5">
                <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                  <UsersRound size={20} className="text-blue-600" />
                </div>
                <h3 className="font-display font-bold text-[18px] text-text">
                  {t("privacy", "guardianModalTitle")}
                </h3>
              </div>

              {/* Purpose */}
              <div className="mb-4">
                <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em] mb-2">
                  {t("privacy", "guardianModalPurpose")}
                </p>
                <div className="p-3 rounded-xl bg-accent-light/20 border border-accent/15">
                  <p className="text-[13px] font-medium text-text">
                    {t("privacy", "guardianModalPurposeDesc")}
                  </p>
                </div>
              </div>

              {/* Not included */}
              <div className="mb-5">
                <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em] mb-2">
                  {t("privacy", "guardianModalNot")}
                </p>
                <div className="space-y-2">
                  {consentExclusions.map((item) => (
                    <div key={item} className="flex items-center gap-2.5 p-2.5 rounded-lg bg-red-50/60">
                      <XCircle size={14} className="text-red-400 flex-shrink-0" />
                      <span className="text-[12px] text-text">{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={() => setShowConsentModal(false)}
                className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-full bg-primary text-white text-[14px] font-semibold hover:bg-primary-600 transition-colors cursor-pointer"
                style={{ border: "none" }}
              >
                <CheckCircle2 size={16} />
                I Understand
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ================================================================
          [KEPT] 删除确认 Modal
         ================================================================ */}
      <AnimatePresence>
        {showDeleteModal && (
          <motion.div
            className="fixed inset-0 z-[100] flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div
              className="absolute inset-0 bg-black/30 backdrop-blur-sm"
              onClick={() => setShowDeleteModal(false)}
            />
            <motion.div
              className="relative bg-white rounded-2xl shadow-2xl border border-gray-100 max-w-md w-full p-6"
              initial={{ scale: 0.95, y: 10 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 10 }}
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
                  <AlertTriangle size={20} className="text-risk-high" />
                </div>
                <h3 className="font-display font-bold text-[18px] text-text">
                  {t("privacy", "lifecycleDeleteConfirmTitle")}
                </h3>
              </div>
              <p className="text-[13px] text-text-secondary leading-relaxed mb-6">
                {t("privacy", "lifecycleDeleteConfirmContent")}
              </p>
              <div className="flex flex-col gap-2.5">
                <button
                  onClick={handleDelete}
                  className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-full bg-risk-high text-white text-[14px] font-semibold hover:bg-red-600 transition-colors cursor-pointer"
                  style={{ border: "none" }}
                >
                  <Trash2 size={16} />
                  {t("privacy", "lifecycleDeleteConfirm")}
                </button>
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-full bg-gray-100 text-text-secondary text-[14px] font-semibold hover:bg-gray-200 transition-colors cursor-pointer"
                  style={{ border: "none" }}
                >
                  {t("privacy", "lifecycleDeleteCancel")}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
