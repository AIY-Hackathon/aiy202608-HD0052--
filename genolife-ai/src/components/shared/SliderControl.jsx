/**
 * Premium lifestyle slider with dynamic gradient track.
 */
export default function SliderControl({ factor, value, onChange }) {
  const pct = ((value - factor.min) / (factor.max - factor.min)) * 100;
  const gradientStyle = {
    background: `linear-gradient(to right, #0D9488 0%, #1E3A5F ${pct}%, #E5E7EB ${pct}%)`,
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gray-50 flex items-center justify-center text-lg shadow-sm">
            {factor.icon}
          </div>
          <span className="text-[14px] font-semibold text-text">{factor.label}</span>
        </div>
        <div className="flex items-baseline gap-0.5">
          <span className="text-lg font-display font-bold text-text tabular-nums">
            {value}
          </span>
          <span className="text-[11px] text-text-tertiary font-medium">{factor.unit}</span>
        </div>
      </div>

      <div className="relative">
        <input
          type="range"
          min={factor.min}
          max={factor.max}
          step={factor.step}
          value={value}
          onChange={(e) => onChange(factor.key, parseFloat(e.target.value))}
          className="w-full relative z-10"
          style={gradientStyle}
        />
      </div>

      <div className="flex justify-between text-[11px] text-text-tertiary font-medium">
        <span>{factor.min}{factor.unit}</span>
        <span>{factor.description}</span>
        <span>{factor.max}{factor.unit}</span>
      </div>
    </div>
  );
}
