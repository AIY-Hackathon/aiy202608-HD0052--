/**
 * EthicsReference — 法规与科学依据展示页面
 * ============================================
 * 展示本平台的伦理设计所参考的国际和国内法规框架。
 *
 * 体现伦理价值：
 * - ICH E18：国际儿科基因组研究知情同意标准
 * - 中国《人类遗传资源管理条例》：国内法律依据
 * - 儿科基因检测伦理原则：儿童保护
 *
 * 注意：这是教育参考，不是法律咨询。
 */
import { motion } from "framer-motion";
import { useLanguage } from "../i18n";
import {
  BookOpen,
  Globe,
  Landmark,
  Heart,
  ExternalLink,
  Scale,
} from "lucide-react";

const frameworks = [
  {
    key: "ICHE",
    icon: Globe,
    color: "bg-blue-50 text-blue-600",
    borderColor: "border-l-blue-400",
  },
  {
    key: "China",
    icon: Landmark,
    color: "bg-red-50 text-red-600",
    borderColor: "border-l-red-400",
  },
  {
    key: "Pediatric",
    icon: Heart,
    color: "bg-purple-50 text-purple-600",
    borderColor: "border-l-purple-400",
  },
];

export default function EthicsReference() {
  const { t } = useLanguage();

  return (
    <div className="max-w-4xl mx-auto px-6 pt-28 pb-24">
      {/* ================================================================
          HERO
         ================================================================ */}
      <motion.section
        className="mb-12"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 rounded-xl bg-purple-100 flex items-center justify-center">
            <Scale size={20} className="text-purple-600" />
          </div>
          <div>
            <p className="text-[10px] font-bold text-text-tertiary uppercase tracking-[0.15em]">
              Ethics Framework
            </p>
            <h1 className="font-display font-bold text-[26px] sm:text-[30px] text-text tracking-tight leading-tight">
              {t("privacy", "referenceTitle")}
            </h1>
          </div>
        </div>
        <p className="text-[15px] text-text-secondary max-w-2xl leading-relaxed ml-12">
          {t("privacy", "referenceSubtitle")}
        </p>
      </motion.section>

      {/* ================================================================
          框架卡片
         ================================================================ */}
      <div className="space-y-5 mb-12">
        {frameworks.map((fw, i) => {
          const Icon = fw.icon;
          return (
            <motion.div
              key={fw.key}
              className={`premium-card p-6 sm:p-7 border-l-3 ${fw.borderColor}`}
              style={{ borderLeftWidth: 3 }}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.12 + i * 0.1, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              whileHover={{ y: -3 }}
            >
              <div className="flex items-start gap-4">
                {/* 图标 */}
                <div className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${fw.color}`}>
                  <Icon size={22} />
                </div>

                <div className="min-w-0">
                  {/* 标题 */}
                  <h3 className="font-display font-bold text-[17px] text-text mb-2">
                    {t("privacy", `reference${fw.key}Title`)}
                  </h3>
                  {/* 说明 */}
                  <p className="text-[13px] text-text-secondary leading-relaxed mb-3">
                    {t("privacy", `reference${fw.key}Desc`)}
                  </p>

                  {/* 标签 */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary-light text-[11px] font-semibold text-primary">
                      <BookOpen size={11} />
                      教育参考
                    </span>
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-gray-100 text-[11px] font-medium text-text-tertiary">
                      非法律咨询
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* ================================================================
          免责声明
         ================================================================ */}
      <motion.div
        className="premium-card p-5 sm:p-6 bg-amber-50/40 border border-amber-100/60"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
      >
        <div className="flex items-start gap-3">
          <div className="w-9 h-9 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
            <ExternalLink size={18} className="text-amber-600" />
          </div>
          <div>
            <p className="text-[12px] font-bold text-text mb-1">
              {t("privacy", "referenceDisclaimer")}
            </p>
            <p className="text-[12px] text-text-tertiary leading-relaxed">
              本页面引用的法规框架仅用于说明本平台的伦理设计依据，不构成法律意见。
              如需法律指导，请咨询具备资质的法律专业人士。
              基因检测和医疗决策应在专业医疗人员的指导下进行。
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
