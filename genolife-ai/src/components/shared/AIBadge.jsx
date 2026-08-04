/**
 * AI badge — tiny label marking AI-generated content.
 */
export default function AIBadge({ text = "AI-generated" }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-ai-light text-ai text-[11px] font-medium">
      <span className="text-xs">🤖</span>
      {text}
    </span>
  );
}
