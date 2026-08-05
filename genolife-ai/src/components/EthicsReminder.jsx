/**
 * EthicsReminder — 伦理风险提醒条
 * ==================================
 * 根据分析结果类型（正常/异常），在分析页面底部显示不同的伦理提醒。
 *
 * 体现伦理价值：
 * - 正常结果 ≠ 不会生病（防止过度依赖基因检测）
 * - 异常结果 ≠ AI诊断（防止误解AI功能）
 * - 始终引导用户咨询专业医疗人员
 */
import { motion } from "framer-motion";
import { useLanguage } from "../i18n";
import { Info, Stethoscope } from "lucide-react";

/**
 * @param {"normal" | "abnormal"} resultType — 分析结果分类
 */
export default function EthicsReminder({ resultType = "normal" }) {
  const { t } = useLanguage();

  const isNormal = resultType === "normal";

  return (
    <motion.section
      className="mb-16"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7, duration: 0.5 }}
    >
      <div
        className={`premium-card px-6 py-5 sm:px-7 sm:py-6 border-l-3 ${
          isNormal
            ? "bg-accent-light/15 border-l-accent"
            : "bg-amber-50/40 border-l-amber-400"
        }`}
        style={{ borderLeftWidth: 3 }}
      >
        <div className="flex items-start gap-3.5">
          {/* 图标 */}
          <div
            className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
              isNormal ? "bg-accent/10" : "bg-amber-100"
            }`}
          >
            {isNormal ? (
              <Info size={20} className="text-accent" />
            ) : (
              <Stethoscope size={20} className="text-amber-600" />
            )}
          </div>

          {/* 内容 */}
          <div className="min-w-0">
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.12em] mb-1">
              {t("privacy", isNormal ? "ethicsNormalTitle" : "ethicsAbnormalTitle")}
            </p>
            <p className="text-[13px] text-text-secondary leading-relaxed">
              {t(
                "privacy",
                isNormal ? "ethicsNormalContent" : "ethicsAbnormalContent"
              )}
            </p>
          </div>
        </div>

        {/* 底部警示线 */}
        <div
          className={`mt-4 pt-3 border-t ${
            isNormal ? "border-accent/15" : "border-amber-200/60"
          }`}
        >
          <p className="text-[11px] text-text-tertiary leading-relaxed flex items-start gap-1.5">
            <Info size={12} className="shrink-0 mt-0.5" />
            <span>
              {isNormal
                ? "这份分析仅反映基因层面的倾向性，不代表未来的健康状况。建议与儿科医生讨论宝宝的常规发育里程碑。"
                : "这份分析不是临床诊断。AI 检测到的潜在遗传异常需要在临床环境中由合格的遗传咨询师或医生进行验证和解释。"}
            </span>
          </p>
        </div>
      </div>
    </motion.section>
  );
}
