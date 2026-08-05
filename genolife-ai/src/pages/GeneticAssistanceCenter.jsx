/**
 * GeneticAssistanceCenter — 03-2 基因异常辅助中心（异常结果）
 * ===========================================================
 * 当发现致病变异（pathogenicCount > 0）或健康评分 < 60 时显示。
 * 提供基因特异性推荐、专科资源指引和家长心理支持。
 */
import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { useLocation } from "../components/layout/PageTransition";
import { getAnalysis } from "../api/client";
import {
  ShieldAlert, Hospital, Stethoscope, Phone, Heart,
  FileText, ExternalLink, ChevronRight, AlertTriangle,
  Activity, Users, BookOpen, Bot, Send, Sparkles, Loader2,
  CheckCircle2,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { API_BASE } from "../api/client";

/* ── 基因 → 专科推荐映射 ── */
const GENE_SPECIALTY_MAP = {
  PAH:    { specialty: "遗传代谢科 / 儿科内分泌科", desc: "苯丙氨酸羟化酶缺乏，需新生儿筛查随访和饮食管理。", urgency: "高" },
  G6PD:   { specialty: "儿科血液科 / 儿科保健科", desc: "G6PD 缺乏症——避免诱因即可正常生活。需告知所有接诊医生。", urgency: "中" },
  CYP21A2:{ specialty: "儿科内分泌科", desc: "先天性肾上腺皮质增生——激素替代治疗和应激管理至关重要。", urgency: "高" },
  SMN1:   { specialty: "儿科神经科 / 遗传咨询", desc: "脊髓性肌萎缩——治疗窗口极为紧迫，症状前干预效果最佳。", urgency: "极高" },
  GJB2:   { specialty: "耳鼻喉科 / 听力中心", desc: "先天性听力损失——早期听力辅助和语言康复可达到接近正常的语言发育。", urgency: "高" },
  SLC26A4:{ specialty: "耳鼻喉科 / 听力中心", desc: "大前庭导水管综合征——避免头部外伤，定期听力监测。", urgency: "中" },
  CHD7:   { specialty: "多学科综合门诊", desc: "CHARGE综合征——涉及心脏、听力、眼科、喂养多系统评估管理。", urgency: "高" },
  IL2RG:  { specialty: "儿科免疫科 / 骨髓移植中心", desc: "SCID-X1——3.5月龄前造血干细胞移植生存率>95%，严格感染防护。", urgency: "极高" },
  BTK:    { specialty: "儿科免疫科", desc: "XLA——免疫球蛋白替代治疗和感染预防是管理核心。", urgency: "高" },
  RAG1:   { specialty: "儿科免疫科 / 骨髓移植中心", desc: "RAG1 相关 SCID/Omenn 综合征——需免疫重建治疗。", urgency: "极高" },
  CFTR:   { specialty: "儿科呼吸科 / 儿科消化科", desc: "囊性纤维化——营养支持、呼吸道管理和 CFTR 调节剂综合治疗。", urgency: "高" },
  HBB:    { specialty: "儿科血液科", desc: "镰状细胞病/地中海贫血——预防性抗生素、疫苗接种和定期血液科随访。", urgency: "中" },
  FBN1:   { specialty: "儿科心脏科 / 临床遗传科", desc: "马凡综合征——定期心血管影像监测和β阻滞剂治疗。", urgency: "高" },
  MYH7:   { specialty: "儿科心脏科", desc: "肥厚型心肌病——定期心脏超声、心电图和专科随访。", urgency: "高" },
  SCN1A:  { specialty: "儿科神经科", desc: "Dravet综合征——避免钠通道阻滞剂，发热管理和个体化抗癫痫方案。", urgency: "高" },
  MECP2:  { specialty: "儿科神经科 / 发育行为儿科", desc: "Rett综合征——多学科康复和支持性治疗。", urgency: "高" },
  FMR1:   { specialty: "发育行为儿科 / 儿科神经科", desc: "脆性X综合征——早期发育干预和行为治疗。", urgency: "中" },
  TSC1:   { specialty: "儿科神经科 / 儿科肾脏科", desc: "结节性硬化症——mTOR抑制剂靶向治疗 + 多器官监测。", urgency: "高" },
  NF1:    { specialty: "儿科神经科 / 临床遗传科", desc: "神经纤维瘤病1型——定期体检和影像学监测。", urgency: "中" },
  DHCR7:  { specialty: "遗传代谢科 / 儿科内分泌科", desc: "Smith-Lemli-Opitz综合征——胆固醇补充和多学科支持。", urgency: "高" },
  ACADM:  { specialty: "遗传代谢科", desc: "MCAD缺乏症——避免禁食、紧急葡萄糖输注方案。", urgency: "高" },
  SLC2A1: { specialty: "儿科神经科 / 营养科", desc: "GLUT1缺乏综合征——生酮饮食是有效的治疗选择。", urgency: "高" },
  COL1A1: { specialty: "儿科骨科 / 临床遗传科", desc: "成骨不全症——多学科骨骼健康管理和康复。", urgency: "中" },
  USH2A:  { specialty: "耳鼻喉科 / 眼科 / 听力中心", desc: "Usher综合征——听力辅助 + 定期视网膜监测。", urgency: "中" },
  RB1:    { specialty: "儿科眼科 / 肿瘤科", desc: "视网膜母细胞瘤——定期眼底筛查，早期发现可保留视力和生命。", urgency: "极高" },
};

/* ── 心理支持资源 ── */
const SUPPORT_RESOURCES = [
  { title: "遗传咨询", desc: "与遗传咨询师详细解读宝宝的基因报告，了解遗传模式和家庭再发风险。", icon: Users },
  { title: "家长互助社群", desc: "加入相关疾病的患儿家长互助组织，分享照护经验和情感支持。", icon: Heart },
  { title: "心理支持热线", desc: "面对基因异常诊断，家长的心理调适同样重要。寻求专业心理支持是勇气的体现。", icon: Phone },
];

export default function GeneticAssistanceCenter() {
  const { uploaded, reportId } = useLocation();
  const [analysisData, setAnalysisData] = useState(null);
  const [selectedGene, setSelectedGene] = useState(null);

  // AI 问答助手状态
  const [aiMessages, setAiMessages] = useState([]);
  const [aiInput, setAiInput] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const aiMessagesEndRef = useRef(null);

  useEffect(() => {
    if (!reportId) return;
    let cancelled = false;
    async function load() {
      try {
        const data = await getAnalysis(reportId);
        if (!cancelled) setAnalysisData(data);
      } catch { /* fallback */ }
    }
    load();
    return () => { cancelled = true; };
  }, [reportId]);

  useEffect(() => {
    aiMessagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [aiMessages, aiLoading]);

  const sendAiMessage = async () => {
    const text = aiInput.trim();
    if (!text || aiLoading) return;
    const userMsg = { role: "user", content: text };
    setAiMessages((prev) => [...prev, userMsg]);
    setAiInput("");
    setAiLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: aiMessages.slice(-6),
        }),
      });
      const body = await resp.json();
      if (body.success) {
        setAiMessages((prev) => [...prev, { role: "assistant", content: body.data.answer }]);
      } else {
        setAiMessages((prev) => [...prev, { role: "assistant", content: `⚠️ ${body.error?.message || "AI 服务暂时不可用"}` }]);
      }
    } catch {
      setAiMessages((prev) => [...prev, { role: "assistant", content: "⚠️ 无法连接 AI 服务，请确认后端已启动。" }]);
    } finally {
      setAiLoading(false);
    }
  };

  const variants = analysisData?.variants || [];
  const pathogenicVariants = variants.filter((v) =>
    v.clinvar_significance?.includes("Pathogenic")
  );
  const affectedGenes = [...new Set(pathogenicVariants.map((v) => v.gene_name))];
  const hasAbnormal = affectedGenes.length > 0;

  if (!uploaded) {
    return (
      <div className="max-w-6xl mx-auto px-6 pt-28 pb-24 text-center">
        <ShieldAlert size={48} className="mx-auto mb-4 text-gray-300" />
        <p className="text-[15px] text-text-secondary">请先上传宝宝的基因报告</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* Hero — 根据是否有异常显示不同内容 */}
      <motion.section
        className="mb-16 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {hasAbnormal ? (
          <>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-100 text-amber-700 mb-6">
              <AlertTriangle size={14} />
              <span className="text-[12px] font-bold uppercase tracking-[0.12em]">基因筛查发现关注位点</span>
            </div>
            <h1 className="font-display font-bold text-[36px] text-text mb-3 tracking-tight">
              基因异常<span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-500 to-orange-600"> 辅助中心</span>
            </h1>
            <p className="text-[15px] text-text-secondary max-w-2xl mx-auto leading-relaxed">
              宝宝的基因筛查发现了需要关注的变异。请放心，许多遗传风险在早期干预和科学管理下
              可以显著改善预后。以下是为您整理的个性化辅助信息。
            </p>
          </>
        ) : (
          <>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-green-100 text-green-700 mb-6">
              <CheckCircle2 size={14} />
              <span className="text-[12px] font-bold uppercase tracking-[0.12em]">基因筛查未发现致病变异</span>
            </div>
            <h1 className="font-display font-bold text-[36px] text-text mb-3 tracking-tight">
              基因<span className="text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-primary"> 辅助中心</span>
            </h1>
            <p className="text-[15px] text-text-secondary max-w-2xl mx-auto leading-relaxed">
              宝宝的基因筛查结果整体良好，未发现明确致病变异。以下是育儿知识问答助手，如有任何关于基因、遗传或婴幼儿照护的疑问，可以随时提问。
            </p>
          </>
        )}
      </motion.section>

      {/* 核心提示 — 根据状态显示不同颜色 */}
      <motion.div
        className={`premium-card p-5 mb-12 border-l-4 flex items-start gap-4 ${
          hasAbnormal ? "border-l-amber-400 bg-amber-50/50" : "border-l-green-400 bg-green-50/50"
        }`}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {hasAbnormal ? (
          <>
            <ShieldAlert size={20} className="text-amber-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-[14px] font-bold text-text mb-1">重要提示</p>
              <p className="text-[13px] text-text-secondary leading-relaxed">
                本页面提供的信息仅供教育参考<b>而非医学诊断</b>。
                基因变异 ≠ 一定会患病——许多致病变异的临床表现受多种因素影响。
                请务必带宝宝到正规医疗机构，由专科医生进行<b>临床评估和确诊</b>。
              </p>
            </div>
          </>
        ) : (
          <>
            <CheckCircle2 size={20} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-[14px] font-bold text-text mb-1">健康提示</p>
              <p className="text-[13px] text-text-secondary leading-relaxed">
                宝宝的基因筛查<b>未发现明确致病变异</b>，遗传风险处于正常人群范围。
                本报告为教育性基因筛查，<b>不能替代</b>国家规定的新生儿疾病筛查和常规儿科体检。
                请继续保持科学的喂养方式和定期儿科随访。
              </p>
            </div>
          </>
        )}
      </motion.div>

      {/* 基因特异性推荐 */}
      <motion.section
        className="mb-16"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-8 h-8 rounded-xl bg-amber-100 flex items-center justify-center">
            <Activity size={16} className="text-amber-600" />
          </div>
          <div>
            <h2 className="font-display font-bold text-[22px] text-text">基因特异性管理建议</h2>
            <p className="text-[12px] text-text-tertiary">基于宝宝检测到的基因变异，针对性推荐就医方向</p>
          </div>
        </div>

        {affectedGenes.length === 0 ? (
          <div className="premium-card p-8 text-center">
            <FileText size={32} className="mx-auto mb-3 text-gray-300" />
            <p className="text-[14px] text-text-secondary">未检测到明确致病变异，但健康评分提示需要关注。</p>
            <p className="text-[13px] text-text-tertiary mt-1">建议定期儿科随访，关注宝宝的生长发育轨迹。</p>
          </div>
        ) : (
          <div className="space-y-4">
            {affectedGenes.map((gene) => {
              const info = GENE_SPECIALTY_MAP[gene] || { specialty: "临床遗传科 / 遗传咨询", desc: "请咨询遗传专科医生获取个体化评估。", urgency: "中" };
              const isExpanded = selectedGene === gene;
              return (
                <motion.div
                  key={gene}
                  className="premium-card overflow-hidden"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <button
                    onClick={() => setSelectedGene(isExpanded ? null : gene)}
                    className="w-full flex items-center justify-between px-6 py-5 text-left cursor-pointer hover:bg-gray-50/50 transition-colors"
                    style={{ background: "none", border: "none" }}
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-[18px] font-display font-bold ${
                        info.urgency === "极高" ? "bg-red-100 text-red-600" :
                        info.urgency === "高" ? "bg-amber-100 text-amber-600" :
                        "bg-blue-100 text-blue-600"
                      }`}>
                        {gene.slice(0, 2)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="text-[15px] font-bold text-text">{gene}</p>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            info.urgency === "极高" ? "bg-red-100 text-red-600" :
                            info.urgency === "高" ? "bg-amber-100 text-amber-600" :
                            "bg-blue-100 text-blue-600"
                          }`}>
                            紧急度：{info.urgency}
                          </span>
                        </div>
                        <p className="text-[13px] text-text-secondary mt-0.5">{info.desc}</p>
                      </div>
                    </div>
                    <ChevronRight
                      size={18}
                      className={`text-text-tertiary transition-transform ${isExpanded ? "rotate-90" : ""}`}
                    />
                  </button>

                  {isExpanded && (
                    <div className="px-6 pb-5 border-t border-gray-100 pt-4 space-y-3">
                      <div className="flex items-start gap-3 p-4 rounded-xl bg-blue-50/60 border border-blue-100">
                        <Stethoscope size={18} className="text-blue-600 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="text-[13px] font-bold text-text mb-1">推荐就诊科室</p>
                          <p className="text-[14px] text-blue-700 font-semibold">{info.specialty}</p>
                        </div>
                      </div>
                      <div className="p-4 rounded-xl bg-gray-50">
                        <p className="text-[12px] font-bold text-text-tertiary mb-2">就诊前准备</p>
                        <ul className="space-y-1.5">
                          <li className="flex items-start gap-2 text-[13px] text-text-secondary">
                            <ChevronRight size={12} className="text-primary mt-0.5 flex-shrink-0" />
                            携带完整的基因检测报告和新生儿筛查结果
                          </li>
                          <li className="flex items-start gap-2 text-[13px] text-text-secondary">
                            <ChevronRight size={12} className="text-primary mt-0.5 flex-shrink-0" />
                            整理宝宝的症状、喂养和发育情况记录
                          </li>
                          <li className="flex items-start gap-2 text-[13px] text-text-secondary">
                            <ChevronRight size={12} className="text-primary mt-0.5 flex-shrink-0" />
                            准备家族史信息（三代内的遗传病和健康情况）
                          </li>
                          <li className="flex items-start gap-2 text-[13px] text-text-secondary">
                            <ChevronRight size={12} className="text-primary mt-0.5 flex-shrink-0" />
                            列出您最关心的问题，确保就诊时不遗漏
                          </li>
                        </ul>
                      </div>
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        )}
      </motion.section>

      {/* 支持资源 */}
      <motion.section
        className="mb-16"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3 className="font-display font-bold text-[18px] text-text mb-5">支持与资源</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {SUPPORT_RESOURCES.map((res) => (
            <motion.div
              key={res.title}
              className="premium-card p-5"
              whileHover={{ y: -3 }}
            >
              <div className="w-9 h-9 rounded-xl bg-primary-light flex items-center justify-center mb-3">
                <res.icon size={17} className="text-primary" />
              </div>
              <h4 className="font-bold text-[14px] text-text mb-2">{res.title}</h4>
              <p className="text-[12px] text-text-secondary leading-relaxed">{res.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* ================================================================
          AI 育儿知识问答助手（内嵌版）
         ================================================================ */}
      <motion.section
        className="mb-16"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
      >
        <div className="premium-card overflow-hidden">
          {/* 助手头部 */}
          <div className="px-6 py-4 bg-gradient-to-r from-primary to-primary-600 text-white flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center">
                <Sparkles size={18} />
              </div>
              <div>
                <h3 className="text-[15px] font-bold">AI 育儿知识问答助手</h3>
                <p className="text-[11px] opacity-80">由 DeepSeek 提供支持 · 解答基因科普和育儿疑问</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-[11px] text-white/60">
              <Bot size={16} />
              DeepSeek AI
            </div>
          </div>

          {/* 消息区 */}
          <div className="h-[360px] overflow-y-auto px-5 py-4 space-y-3 bg-gray-50/50">
            {aiMessages.length === 0 && (
              <div className="text-center py-10">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-primary-light/60 mb-4">
                  <Bot size={28} className="text-primary" />
                </div>
                <p className="text-[14px] font-semibold text-text mb-1">育儿知识，随时提问</p>
                <p className="text-[12px] text-text-tertiary mb-5 max-w-xs mx-auto leading-relaxed">
                  关于宝宝的基因报告、遗传风险、喂养照护有任何疑问，都可以问我
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {[
                    "基因筛查结果异常怎么办？",
                    "什么是基因×环境交互？",
                    "如何科学喂养新生儿？",
                    "宝宝发育里程碑有哪些？",
                  ].map((q) => (
                    <button
                      key={q}
                      onClick={() => { setAiInput(q); }}
                      className="px-3 py-1.5 rounded-full bg-white border border-gray-200 text-[11px] text-text-secondary hover:border-primary/40 hover:text-primary cursor-pointer transition-all"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {aiMessages.map((m, i) => (
              <div
                key={`aimsg-${i}-${m.role}`}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] px-3.5 py-2.5 rounded-2xl text-[13px] leading-relaxed ${
                    m.role === "user"
                      ? "bg-primary text-white rounded-br-sm"
                      : "bg-white text-text-secondary border border-gray-100 rounded-bl-sm shadow-sm"
                  }`}
                >
                  {m.role === "user" ? (
                    m.content
                  ) : (
                    <ReactMarkdown
                      className="ai-markdown"
                      components={{
                        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                        strong: ({ children }) => <strong className="font-bold text-text">{children}</strong>,
                        ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
                        li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                        h1: ({ children }) => <p className="font-bold text-text text-[14px] mb-1">{children}</p>,
                        h2: ({ children }) => <p className="font-bold text-text text-[14px] mb-1">{children}</p>,
                        h3: ({ children }) => <p className="font-bold text-text text-[13px] mb-1">{children}</p>,
                        code: ({ children }) => (
                          <code className="px-1 py-0.5 rounded bg-gray-100 text-[11px] font-mono text-primary">{children}</code>
                        ),
                        blockquote: ({ children }) => (
                          <blockquote className="border-l-2 border-primary/30 pl-2 my-1.5 text-text-tertiary">{children}</blockquote>
                        ),
                        a: ({ href, children }) => (
                          <a href={href} target="_blank" rel="noreferrer" className="text-primary underline underline-offset-2">{children}</a>
                        ),
                      }}
                    >
                      {m.content}
                    </ReactMarkdown>
                  )}
                </div>
              </div>
            ))}

            {aiLoading && (
              <div className="flex justify-start">
                <div className="px-3.5 py-2.5 rounded-2xl bg-white border border-gray-100 shadow-sm flex items-center gap-2">
                  <Loader2 size={14} className="animate-spin text-primary" />
                  <span className="text-[12px] text-text-tertiary">AI 思考中...</span>
                </div>
              </div>
            )}
            <div ref={aiMessagesEndRef} />
          </div>

          {/* 输入区 */}
          <div className="px-5 py-3 border-t border-gray-100 bg-white">
            <div className="flex items-center gap-2 bg-gray-50 rounded-2xl px-3 py-2">
              <input
                value={aiInput}
                onChange={(e) => setAiInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendAiMessage()}
                placeholder="输入育儿或基因问题..."
                className="flex-1 bg-transparent text-[13px] text-text outline-none placeholder:text-text-tertiary/70"
              />
              <button
                onClick={sendAiMessage}
                disabled={aiLoading || !aiInput.trim()}
                className="w-8 h-8 rounded-xl bg-primary text-white flex items-center justify-center disabled:opacity-40 cursor-pointer transition-all"
                style={{ border: "none" }}
                aria-label="发送"
              >
                <Send size={14} />
              </button>
            </div>
            <p className="mt-1.5 text-[9px] text-gray-400 text-center">
              ⚠️ 回答仅供学习参考，不构成医疗建议
            </p>
          </div>
        </div>
      </motion.section>

      {/* 家长须知 */}
      <motion.section
        className="premium-card p-6 bg-gradient-to-r from-amber-50/50 to-transparent"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex items-center gap-3 mb-4">
          <BookOpen size={18} className="text-amber-600" />
          <h3 className="font-display font-bold text-[17px] text-text">家长须知</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-[13px] text-text-secondary leading-relaxed">
              <strong className="text-text">1. 基因≠命运。</strong>许多遗传病在早期干预下预后显著改善。您不是独自面对——有专业的医疗团队和家长社群在您身边。
            </p>
            <p className="text-[13px] text-text-secondary leading-relaxed">
              <strong className="text-text">2. 知识就是力量。</strong>了解宝宝的具体情况，主动参与照护决策。科学的管理方案每天都在进步。
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-[13px] text-text-secondary leading-relaxed">
              <strong className="text-text">3. 照顾好自己。</strong>家长的心理状态直接影响照护质量。寻求心理支持不是软弱——是为了更好地支持宝宝。
            </p>
            <p className="text-[13px] text-text-secondary leading-relaxed">
              <strong className="text-text">4. 保持希望。</strong>基因治疗、靶向药物和精准医学正在以前所未有的速度发展。许多曾经的"不治之症"今天已经有了有效的管理方案。
            </p>
          </div>
        </div>
      </motion.section>

      <p className="mt-16 text-center text-[11px] text-text-tertiary">
        ⚠️ 本页面信息仅供教育参考，不构成医疗诊断或治疗建议。请务必咨询专业医疗机构。
      </p>
    </div>
  );
}
