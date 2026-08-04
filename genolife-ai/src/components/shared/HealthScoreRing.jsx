import { useEffect, useRef, useState } from "react";

/**
 * Animated circular health score ring.
 * SVG ring that fills from 0 to the target score on mount/update.
 */
export default function HealthScoreRing({ score, size = 200, strokeWidth = 10, label = "Health Score" }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const [displayScore, setDisplayScore] = useState(0);
  const prevScore = useRef(0);

  useEffect(() => {
    const start = prevScore.current;
    const end = score;
    const duration = 800;
    const startTime = performance.now();

    function animate(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start + (end - start) * eased);
      setDisplayScore(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    }

    requestAnimationFrame(animate);
    prevScore.current = score;
  }, [score]);

  const offset = circumference - (displayScore / 100) * circumference;

  const color =
    displayScore >= 85 ? "var(--color-risk-low)" :
    displayScore >= 70 ? "var(--color-risk-moderate)" :
    "var(--color-risk-high)";

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background track */}
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
          style={{ transition: "stroke-dashoffset 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)" }}
        />
      </svg>

      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="font-display font-bold tracking-tight leading-none"
          style={{ fontSize: size * 0.22, color }}
        >
          {displayScore}
        </span>
        <span
          className="font-sans text-text-tertiary mt-1 tracking-wide uppercase"
          style={{ fontSize: size * 0.08 }}
        >
          {label}
        </span>
      </div>
    </div>
  );
}
