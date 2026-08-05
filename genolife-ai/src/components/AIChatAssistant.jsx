import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, X, Send, Sparkles, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { API_BASE } from "../api/client";

/**
 * AI Chat Assistant — DeepSeek 基因科普问答浮窗
 * ==============================================
 * 右下角 AI 助手浮窗：
 *   - 用户可框选不理解的内容，自动填入提问框
 *   - 对话界面，DeepSeek 科普回答
 *   - 系统提示词限定基因科普助手
 */
export default function AIChatAssistant() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedText, setSelectedText] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // 监听用户框选内容
  useEffect(() => {
    const handleSelection = () => {
      const sel = window.getSelection()?.toString().trim();
      if (sel && sel.length > 5) {
        setSelectedText(sel.slice(0, 500));
      }
    };
    document.addEventListener("mouseup", handleSelection);
    return () => document.removeEventListener("mouseup", handleSelection);
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const resp = await fetch(`${API_BASE}/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          selected_text: selectedText || undefined,
          history: messages.slice(-6),
        }),
      });
      const body = await resp.json();
      if (body.success) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: body.data.answer },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `⚠️ ${body.error?.message || "AI 服务暂时不可用"}` },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ 无法连接 AI 服务，请确认后端已启动。" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* 浮动按钮 */}
      <motion.button
        onClick={() => setOpen((o) => !o)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="fixed bottom-24 right-6 z-50 w-12 h-12 rounded-full shadow-lg flex items-center justify-center cursor-pointer bg-gradient-to-br from-primary to-primary-600 text-white"
        style={{ border: "none" }}
        title="AI 基因科普助手"
        aria-label="AI 助手"
      >
        {open ? <X size={20} /> : <Bot size={22} />}
      </motion.button>

      {/* 对话浮窗 */}
      <AnimatePresence>
        {open && (
          <motion.div
            className="fixed bottom-40 right-6 z-50 w-[380px] max-w-[calc(100vw-3rem)] bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden flex flex-col"
            style={{ height: "520px" }}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
          >
            {/* 头部 */}
            <div className="px-5 py-4 bg-gradient-to-r from-primary to-primary-600 text-white flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-white/20 flex items-center justify-center">
                  <Sparkles size={16} />
                </div>
                <div>
                  <h3 className="text-[14px] font-bold">AI 基因科普助手</h3>
                  <p className="text-[10px] opacity-80">框选内容 → 自动填入提问</p>
                </div>
              </div>
            </div>

            {/* 框选提示 */}
            <AnimatePresence>
              {selectedText && (
                <motion.div
                  className="mx-4 mt-3 px-3 py-2 rounded-xl bg-amber-50 border border-amber-200"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <p className="text-[10px] font-bold text-amber-700 mb-0.5">
                    📎 已选中内容（点击发送将围绕此解释）
                  </p>
                  <p className="text-[11px] text-amber-800 line-clamp-2 leading-relaxed">
                    "{selectedText}"
                  </p>
                  <button
                    onClick={() => setSelectedText("")}
                    className="mt-1 text-[10px] text-amber-600 hover:text-amber-800 cursor-pointer"
                    style={{ background: "none", border: "none" }}
                  >
                    清除
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* 消息区 */}
            <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 bg-gray-50/50">
              {messages.length === 0 && (
                <div className="text-center py-8">
                  <Bot size={32} className="mx-auto mb-3 text-gray-300" />
                  <p className="text-[13px] text-text-tertiary">
                    你好！我是基因科普助手
                  </p>
                  <p className="text-[11px] text-gray-400 mt-1">
                    选中网页上不理解的基因内容，或直接提问
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2 justify-center">
                    {["什么是 APOE ε4？", "PRS 怎么计算？", "基因能改变吗？"].map((q) => (
                      <button
                        key={q}
                        onClick={() => { setInput(q); inputRef.current?.focus(); }}
                        className="px-3 py-1.5 rounded-full bg-white border border-gray-200 text-[11px] text-text-secondary hover:border-primary/40 hover:text-primary cursor-pointer transition-all"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((m, i) => (
                <div
                  key={i}
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

              {loading && (
                <div className="flex justify-start">
                  <div className="px-3.5 py-2.5 rounded-2xl bg-white border border-gray-100 shadow-sm flex items-center gap-2">
                    <Loader2 size={14} className="animate-spin text-primary" />
                    <span className="text-[12px] text-text-tertiary">AI 思考中...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* 输入区 */}
            <div className="px-4 py-3 border-t border-gray-100">
              <div className="flex items-center gap-2 bg-gray-50 rounded-2xl px-3 py-2">
                <input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                  placeholder="输入基因问题，或选中内容..."
                  className="flex-1 bg-transparent text-[13px] text-text outline-none placeholder:text-text-tertiary/70"
                />
                <button
                  onClick={sendMessage}
                  disabled={loading || !input.trim()}
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
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
