/**
 * HealthyGrowthCenter — 03-1 健康成长中心（正常结果）
 * ====================================================
 * 当宝宝的基因筛查未发现明确致病变异且健康评分 ≥ 60 时显示。
 * 集成 DeepSeek AI 育儿问答 + 预设模板 + 常规健康管理建议。
 */
import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLocation } from "../components/layout/PageTransition";
import AIBadge from "../components/shared/AIBadge";
import { API_BASE } from "../api/client";
import {
  Sparkles, Send, Loader2, Heart, Baby, Moon, Apple, Brain,
  Syringe, BookOpen, MessageCircle, ChevronRight, CheckCircle2,
} from "lucide-react";

const FAQ_CATEGORIES = [
  {
    icon: Apple, key: "feeding", label: "喂养与营养",
    questions: [
      "母乳喂养对宝宝有哪些基因层面的好处？",
      "如何判断宝宝是否吃饱了？",
      "配方奶喂养的宝宝需要注意什么？",
    ],
  },
  {
    icon: Moon, key: "sleep", label: "睡眠与作息",
    questions: [
      "新生儿每天需要睡多久才算正常？",
      "如何帮宝宝建立昼夜节律？",
      "什么样的睡眠环境对宝宝最安全？",
    ],
  },
  {
    icon: Brain, key: "development", label: "发育与早教",
    questions: [
      "0-3个月的宝宝有哪些发育里程碑？",
      "如何通过亲子互动促进宝宝大脑发育？",
      "基因筛查结果正常，还需要关注什么发育红旗信号？",
    ],
  },
  {
    icon: Syringe, key: "vaccine", label: "疫苗与体检",
    questions: [
      "宝宝需要打哪些疫苗？时间表是怎样的？",
      "接种疫苗前后家长需要注意什么？",
      "基因筛查结果正常，是否意味着不需要额外检查？",
    ],
  },
];

const PRESET_QUESTIONS = [
  "宝宝的基因筛查结果全部正常，我应该如何规划日常照护？",
  "如何在家为宝宝提供丰富的感官刺激？",
  "基因正常是否意味着宝宝以后一定健康？",
];

export default function HealthyGrowthCenter() {
  const { uploaded, reportId } = useLocation();

  // AI Chat
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (text) => {
    const msg = text || input.trim();
    if (!msg || loading) return;

    const userMsg = { role: "user", content: msg };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const resp = await fetch(`${API_BASE}/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          history: messages.slice(-6),
        }),
      });
      const body = await resp.json();
      if (body.success) {
        setMessages((prev) => [...prev, { role: "assistant", content: body.data.answer }]);
      } else {
        // FAQ 降级回答
        fallbackAnswer(msg);
      }
    } catch {
      fallbackAnswer(msg);
    } finally {
      setLoading(false);
    }
  };

  const fallbackAnswer = (question) => {
    const answers = {
      default: "感谢您的提问！宝宝的基因筛查结果显示正常，这是一个好消息。基因正常意味着目前没有发现已知的致病变异，但宝宝的健康发展依然需要科学的日常照护——包括均衡喂养、充足睡眠、丰富的感官刺激和定期儿科体检。\n\n⚠️ 以上内容仅供学习参考，不构成医疗建议。",
    };
    setMessages((prev) => [...prev, { role: "assistant", content: answers.default }]);
  };

  if (!uploaded) {
    return (
      <div className="max-w-6xl mx-auto px-6 pt-28 pb-24 text-center">
        <Heart size={48} className="mx-auto mb-4 text-gray-300" />
        <p className="text-[15px] text-text-secondary">请先上传宝宝的基因报告</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 pt-28 pb-24">
      {/* Hero */}
      <motion.section
        className="mb-16 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-green-100 text-green-700 mb-6">
          <CheckCircle2 size={14} />
          <span className="text-[12px] font-bold uppercase tracking-[0.12em]">基因筛查结果正常</span>
        </div>
        <h1 className="font-display font-bold text-[36px] text-text mb-3 tracking-tight">
          宝宝的
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-emerald-600"> 健康成长中心</span>
        </h1>
        <p className="text-[15px] text-text-secondary max-w-xl mx-auto leading-relaxed">
          基因筛查未发现明确致病变异，这是一个令人安心的好消息。
          在这里，您可以获得科学育儿知识和 AI 智能问答支持。
        </p>
      </motion.section>

      {/* 核心信息卡片 */}
      <motion.section
        className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-16"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {[
          { icon: Heart, title: "基因筛查正常", desc: "您的宝宝在本次检测的 25 个核心基因中未发现明确致病变异，这意味着遗传风险处于普通人群水平。", color: "bg-green-50 text-green-600" },
          { icon: Baby, title: "科学照护为重", desc: "基因只是起点——科学的喂养、睡眠、发育刺激和定期体检对宝宝的健康成长有更深远的正面影响。", color: "bg-blue-50 text-blue-600" },
          { icon: BookOpen, title: "持续学习", desc: "了解婴儿发育里程碑和育儿知识，帮助您在宝宝的成长过程中做出明智的健康决策。", color: "bg-amber-50 text-amber-600" },
        ].map((card, i) => (
          <motion.div
            key={card.title}
            className="premium-card p-6"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.07 }}
            whileHover={{ y: -4 }}
          >
            <div className={`w-10 h-10 rounded-xl ${card.color} flex items-center justify-center mb-4`}>
              <card.icon size={20} />
            </div>
            <h3 className="font-display font-bold text-[16px] text-text mb-2">{card.title}</h3>
            <p className="text-[13px] text-text-secondary leading-relaxed">{card.desc}</p>
          </motion.div>
        ))}
      </motion.section>

      {/* AI 育儿问答 */}
      <motion.section
        className="mb-16"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-8 h-8 rounded-xl bg-primary-light flex items-center justify-center">
            <Sparkles size={16} className="text-primary" />
          </div>
          <div>
            <h2 className="font-display font-bold text-[22px] text-text">AI 育儿问答</h2>
            <p className="text-[12px] text-text-tertiary">向 AI 助手提问宝宝喂养、睡眠、发育和健康相关问题</p>
          </div>
          <AIBadge />
        </div>

        {/* 聊天区域 */}
        <div className="premium-card overflow-hidden mb-6">
          {!showChat ? (
            /* 初始状态 — 预设问题 */
            <div className="p-8 text-center">
              <MessageCircle size={40} className="mx-auto mb-4 text-gray-300" />
              <p className="text-[15px] font-semibold text-text mb-2">有任何育儿问题吗？</p>
              <p className="text-[13px] text-text-tertiary mb-6">点击下方问题开始对话，或直接输入您的疑问</p>
              <div className="flex flex-wrap justify-center gap-3 mb-6">
                {PRESET_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => { setShowChat(true); setTimeout(() => sendMessage(q), 100); }}
                    className="px-4 py-2.5 rounded-full bg-primary-light/60 text-[13px] text-primary font-medium hover:bg-primary-light cursor-pointer transition-colors"
                    style={{ border: "none" }}
                  >
                    {q}
                  </button>
                ))}
              </div>
              <button
                onClick={() => { setShowChat(true); setTimeout(() => inputRef.current?.focus(), 100); }}
                className="px-5 py-2.5 rounded-full bg-primary text-white text-[13px] font-semibold cursor-pointer hover:bg-primary-600 transition-colors"
                style={{ border: "none" }}
              >
                直接提问
              </button>
            </div>
          ) : (
            /* 对话界面 */
            <>
              <div className="h-[360px] overflow-y-auto px-5 py-4 space-y-3 bg-gray-50/50">
                {messages.map((m, i) => (
                  <div key={`msg-${i}`} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-[13px] leading-relaxed ${
                      m.role === "user"
                        ? "bg-primary text-white rounded-br-sm"
                        : "bg-white text-text-secondary border border-gray-100 rounded-bl-sm shadow-sm"
                    }`}>
                      <div className="whitespace-pre-wrap">{m.content}</div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="px-4 py-2.5 rounded-2xl bg-white border border-gray-100 shadow-sm flex items-center gap-2">
                      <Loader2 size={14} className="animate-spin text-primary" />
                      <span className="text-[12px] text-text-tertiary">AI 思考中...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
              <div className="px-4 py-3 border-t border-gray-100">
                <div className="flex items-center gap-2 bg-gray-50 rounded-2xl px-3 py-2">
                  <input
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                    placeholder="输入育儿问题..."
                    className="flex-1 bg-transparent text-[13px] text-text outline-none placeholder:text-text-tertiary/70"
                  />
                  <button
                    onClick={() => sendMessage()}
                    disabled={loading || !input.trim()}
                    className="w-8 h-8 rounded-xl bg-primary text-white flex items-center justify-center disabled:opacity-40 cursor-pointer transition-all"
                    style={{ border: "none" }}
                  >
                    <Send size={14} />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </motion.section>

      {/* FAQ 分类 */}
      <motion.section
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
      >
        <h3 className="font-display font-bold text-[18px] text-text mb-5">常见育儿问题</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {FAQ_CATEGORIES.map((cat) => (
            <motion.div
              key={cat.key}
              className="premium-card p-5"
              whileHover={{ y: -2 }}
            >
              <div className="flex items-center gap-2.5 mb-3">
                <div className="w-8 h-8 rounded-lg bg-primary-light flex items-center justify-center">
                  <cat.icon size={15} className="text-primary" />
                </div>
                <h4 className="font-bold text-[14px] text-text">{cat.label}</h4>
              </div>
              <div className="space-y-1.5">
                {cat.questions.map((q) => (
                  <button
                    key={q}
                    onClick={() => { setShowChat(true); setTimeout(() => sendMessage(q), 100); }}
                    className="w-full flex items-center gap-1.5 px-3 py-2 rounded-xl text-[12px] text-text-secondary hover:text-primary hover:bg-primary-light/30 cursor-pointer transition-colors text-left"
                    style={{ background: "none", border: "none" }}
                  >
                    <ChevronRight size={12} className="flex-shrink-0 text-text-tertiary" />
                    {q}
                  </button>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* 底部免责声明 */}
      <p className="mt-16 text-center text-[11px] text-text-tertiary">
        ⚠️ AI 回答仅供学习参考，不构成医疗建议。如有健康疑虑，请咨询儿科或遗传专科医生。
      </p>
    </div>
  );
}
