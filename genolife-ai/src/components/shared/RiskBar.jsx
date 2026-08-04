/**
 * Styled risk bar: label + horizontal bar + percentage.
 */
export default function RiskBar({ label, score, baseline = 50, showScore = true }) {
  const isAbove = score > baseline;
  const barColor = score > 70 ? "bg-risk-high" : score > 50 ? "bg-risk-moderate" : "bg-risk-low";

  return (
    <div className="flex items-center gap-3">
      <span className="w-28 text-sm text-text-secondary font-medium">{label}</span>
      <div className="flex-1 h-2.5 rounded-full bg-gray-100 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${barColor}`}
          style={{ width: `${score}%` }}
        />
      </div>
      {showScore && (
        <span className="w-10 text-right text-sm font-semibold text-text tabular-nums">
          {score}%
        </span>
      )}
    </div>
  );
}
