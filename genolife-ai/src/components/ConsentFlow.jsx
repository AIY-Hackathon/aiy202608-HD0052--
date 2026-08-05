/**
 * ConsentFlow — 儿童基因数据双重知情同意流程
 * ====================================================
 * Step 1: 监护人身份确认 + 三项知情同意勾选
 * Step 2: 二次确认弹窗（禁止科研/AI训练/商业用途）
 *
 * 体现伦理价值：
 * - 儿童无法自主授权 → 监护人承担知情同意责任
 * - 双重确认防止"一键同意"的草率行为
 * - 明确告知数据用途边界
 */
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLanguage } from "../i18n";
import {
  Shield,
  CheckCircle2,
  AlertTriangle,
  Lock,
  UserCheck,
  FileText,
  ArrowRight,
  ArrowLeft,
  Baby,
} from "lucide-react";

export default function ConsentFlow({ onComplete, onCancel }) {
  const { t } = useLanguage();
  const [step, setStep] = useState(1); // 1 = consent checkboxes, 2 = confirmation dialog
  const [checks, setChecks] = useState({
    guardian: false,
    read: false,
    consent: false,
  });
  const [showValidation, setShowValidation] = useState(false);

  const allChecked = checks.guardian && checks.read && checks.consent;

  const toggleCheck = (key) => {
    setChecks((prev) => ({ ...prev, [key]: !prev[key] }));
    setShowValidation(false);
  };

  const handleProceed = () => {
    if (!allChecked) {
      setShowValidation(true);
      return;
    }
    setStep(2);
    setShowValidation(false);
  };

  const handleConfirm = () => {
    onComplete();
  };

  const handleBack = () => {
    if (step === 2) {
      setStep(1);
    } else {
      onCancel();
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[100] flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
      >
        {/* 柔和遮罩 */}
        <div
          className="absolute inset-0 bg-[#1E3A5F]/30 backdrop-blur-md"
          onClick={step === 1 ? onCancel : undefined}
        />

        {/* ================================================================
            STEP 1 — 知情同意勾选
           ================================================================ */}
        {step === 1 && (
          <motion.div
            className="relative bg-white rounded-3xl shadow-2xl border border-gray-100 max-w-lg w-full mx-4 overflow-hidden"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
          >
            {/* Header */}
            <div className="bg-gradient-to-br from-primary-light/60 to-white px-6 pt-8 pb-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Baby size={22} className="text-primary" />
                </div>
                <div>
                  <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em]">
                    GenoLife AI · Privacy Layer
                  </p>
                  <h2 className="font-display font-bold text-[18px] text-text leading-tight">
                    {t("privacy", "consentStep1Title")}
                  </h2>
                </div>
              </div>
              <p className="text-[13px] text-text-secondary leading-relaxed mt-2">
                {t("privacy", "consentSubtitle")}
              </p>
            </div>

            {/* 平台目的说明 */}
            <div className="px-6 py-4 space-y-2.5 bg-amber-50/60 border-y border-amber-100/60">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-start gap-2.5">
                  <div className="w-5 h-5 rounded-full bg-white border border-amber-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-[10px] font-bold text-amber-600">{i}</span>
                  </div>
                  <p className="text-[12px] text-text-secondary leading-relaxed">
                    {t("privacy", `consentPurpose${i}`)}
                  </p>
                </div>
              ))}
            </div>

            {/* 勾选区域 */}
            <div className="px-6 py-5 space-y-3.5">
              {[
                { key: "guardian", label: t("privacy", "consentLegalGuardian") },
                { key: "read", label: t("privacy", "consentReadUnderstand") },
                { key: "consent", label: t("privacy", "consentSingleUse") },
              ].map((item) => (
                <label
                  key={item.key}
                  className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all duration-200 border ${
                    checks[item.key]
                      ? "bg-accent-light/30 border-accent/30"
                      : "bg-gray-50 border-gray-100 hover:border-gray-200"
                  }`}
                  onClick={() => toggleCheck(item.key)}
                >
                  <div
                    className={`w-5 h-5 rounded-md border-2 flex items-center justify-center flex-shrink-0 transition-all ${
                      checks[item.key]
                        ? "bg-accent border-accent"
                        : "border-gray-300 bg-white"
                    }`}
                  >
                    {checks[item.key] && (
                      <CheckCircle2 size={14} className="text-white" />
                    )}
                  </div>
                  <span className="text-[13px] font-medium text-text">
                    {item.label}
                  </span>
                </label>
              ))}

              {showValidation && (
                <motion.p
                  className="flex items-center gap-1.5 text-[12px] text-risk-high"
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <AlertTriangle size={12} />
                  {t("privacy", "consentUnchecked")}
                </motion.p>
              )}
            </div>

            {/* 按钮 */}
            <div className="px-6 py-5 border-t border-gray-100 bg-gray-50/50">
              <button
                onClick={handleProceed}
                disabled={!allChecked}
                className={`w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full text-[14px] font-semibold transition-all cursor-pointer ${
                  allChecked
                    ? "bg-primary text-white hover:bg-primary-600 shadow-lg shadow-primary/20"
                    : "bg-gray-200 text-gray-400 cursor-not-allowed"
                }`}
                style={{ border: "none" }}
              >
                <UserCheck size={16} />
                {t("privacy", "consentProceed")}
                <ArrowRight size={14} />
              </button>
              <button
                onClick={onCancel}
                className="mt-3 w-full text-center text-[12px] text-text-tertiary hover:text-text-secondary cursor-pointer py-1"
                style={{ background: "none", border: "none" }}
              >
                {t("privacy", "consentBack")}
              </button>
            </div>
          </motion.div>
        )}

        {/* ================================================================
            STEP 2 — 二次确认弹窗
           ================================================================ */}
        {step === 2 && (
          <motion.div
            className="relative bg-white rounded-3xl shadow-2xl border border-gray-100 max-w-md w-full mx-4 overflow-hidden"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
          >
            {/* Header */}
            <div className="bg-gradient-to-br from-amber-50/80 to-white px-6 pt-8 pb-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
                  <Lock size={20} className="text-amber-600" />
                </div>
                <h2 className="font-display font-bold text-[18px] text-text leading-tight">
                  {t("privacy", "consentStep2Title")}
                </h2>
              </div>
              <p className="text-[13px] text-text-secondary leading-relaxed">
                {t("privacy", "consentStep2Content")}
              </p>
            </div>

            {/* 三项确认 */}
            <div className="px-6 py-4 space-y-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-3.5 rounded-xl bg-red-50/60 border border-red-100/60"
                >
                  <div className="w-7 h-7 rounded-full bg-white border border-red-200 flex items-center justify-center flex-shrink-0">
                    <Shield size={13} className="text-red-400" />
                  </div>
                  <p className="text-[13px] font-semibold text-text leading-snug">
                    {t("privacy", `consentStep2Item${i}`)}
                  </p>
                </div>
              ))}
            </div>

            {/* 按钮 */}
            <div className="px-6 py-5 border-t border-gray-100 bg-gray-50/50 flex flex-col gap-2.5">
              <button
                onClick={handleConfirm}
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full bg-accent text-white text-[14px] font-semibold hover:bg-accent/90 transition-colors shadow-lg shadow-accent/20 cursor-pointer"
                style={{ border: "none" }}
              >
                <FileText size={16} />
                {t("privacy", "consentConfirm")}
              </button>
              <button
                onClick={handleBack}
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full bg-white border border-gray-200 text-text-secondary text-[14px] font-semibold hover:bg-gray-50 transition-colors cursor-pointer"
              >
                <ArrowLeft size={14} />
                {t("privacy", "consentBack")}
              </button>
            </div>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
