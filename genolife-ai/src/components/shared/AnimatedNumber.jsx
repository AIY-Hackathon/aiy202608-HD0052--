import { useEffect, useRef, useState } from "react";

/**
 * Animated number that counts from its previous value to a new target.
 */
export default function AnimatedNumber({ value, duration = 600, className = "", suffix = "", prefix = "" }) {
  const [display, setDisplay] = useState(value);
  const prevValue = useRef(value);

  useEffect(() => {
    const start = prevValue.current;
    const end = value;
    // 保护：非数字时直接用原始值显示
    if (typeof end !== "number" || isNaN(end)) {
      prevValue.current = end;
      setDisplay(end);
      return;
    }
    if (typeof start !== "number" || isNaN(start) || start === end) {
      prevValue.current = end;
      setDisplay(end);
      return;
    }

    const startTime = performance.now();

    function tick(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(start + (end - start) * eased));

      if (progress < 1) {
        requestAnimationFrame(tick);
      }
    }

    requestAnimationFrame(tick);
    prevValue.current = value;
  }, [value, duration]);

  return (
    <span className={className}>
      {prefix}{display}{suffix}
    </span>
  );
}
