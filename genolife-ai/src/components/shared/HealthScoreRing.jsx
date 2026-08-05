import { useEffect, useRef, useState, useCallback } from "react";

/**
 * Premium Health Score Ring — SVG arc with spring animation and glow.
 * Used across all pages as the hero metric.
 */
export default function HealthScoreRing({
  score,
  size = 200,
  strokeWidth = 10,
  label = "Health Score",
  subtitle = "/100",
  showGlow = false,
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const [displayScore, setDisplayScore] = useState(0);
  const prevScore = useRef(0);
  const [pulsed, setPulsed] = useState(false);

  const animateScore = useCallback(() => {
    const start = prevScore.current;
    const end = score;
    // 保护：非数字时不执行动画（例如传入 "--" 或 null）
    if (typeof end !== "number" || isNaN(end) || typeof start !== "number" || isNaN(start)) {
      prevScore.current = end;
      // 如果 end 是有效数字，直接显示（例如从 "--" 变为实际分数）
      if (typeof end === "number" && !isNaN(end)) {
        setDisplayScore(end);
      }
      return;
    }
    const duration = 800;
    const startTime = performance.now();

    function tick(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayScore(Math.round(start + (end - start) * eased));
      if (progress < 1) requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);
    prevScore.current = score;
  }, [score]);

  useEffect(() => {
    animateScore();
  }, [animateScore]);

  // Pulse on score change
  useEffect(() => {
    if (score !== prevScore.current) {
      setPulsed(true);
      const timer = setTimeout(() => setPulsed(false), 1200);
      return () => clearTimeout(timer);
    }
  }, [score]);

  // 判断是否为数字（用于动画和弧线绘制）
  const isNumeric = typeof score === "number" && !isNaN(score);
  const offset = circumference - ((isNumeric ? displayScore : 0) / 100) * circumference;

  const color =
    !isNumeric ? "var(--color-text-tertiary)" :
    displayScore >= 85 ? "var(--color-risk-low)" :
    displayScore >= 70 ? "var(--color-risk-moderate)" :
    "var(--color-risk-high)";

  const glowColor =
    !isNumeric ? "transparent" :
    displayScore >= 85 ? "rgba(13,148,136,.25)" :
    displayScore >= 70 ? "rgba(232,166,64,.25)" :
    "rgba(220,91,81,.25)";

  return (
    <div className="relative flex items-center justify-center" style={{ width: size + 40, height: size + 40 }}>
      {/* Glow pulse */}
      {showGlow && (
        <div
          className={`absolute rounded-full transition-all duration-800 ${pulsed ? "scale-110" : "scale-100"}`}
          style={{
            width: size + 40,
            height: size + 40,
            background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)`,
            opacity: pulsed ? 0.8 : 0.3,
            transition: "opacity 0.8s ease, transform 0.8s ease",
          }}
        />
      )}

      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="relative z-10 drop-shadow-sm"
      >
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
        />
        {/* Score arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{
            transition: "stroke-dashoffset 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)",
            filter: `drop-shadow(0 0 6px ${glowColor})`,
          }}
        />
      </svg>

      {/* Center label */}
      <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
        <span
          className="font-display font-bold leading-none tracking-tighter tabular-nums"
          style={{ fontSize: size * 0.24, color }}
        >
          {isNumeric ? displayScore : score}
        </span>
        <span
          className="font-sans text-text-tertiary tracking-wider uppercase mt-0.5"
          style={{ fontSize: size * 0.07, letterSpacing: "0.1em" }}
        >
          {label}
        </span>
        {subtitle && (
          <span
            className="font-sans text-text-tertiary/60 mt-0.5"
            style={{ fontSize: size * 0.06 }}
          >
            {subtitle}
          </span>
        )}
      </div>
    </div>
  );
}
