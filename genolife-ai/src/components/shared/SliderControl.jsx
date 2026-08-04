/**
 * Single lifestyle factor slider with icon, label, value display.
 */
export default function SliderControl({ factor, value, onChange }) {
  const pct = ((value - factor.min) / (factor.max - factor.min)) * 100;
  const gradientStyle = {
    background: `linear-gradient(to right, #0D9488 ${pct * 0.3}%, #E8A640 ${pct * 0.5}%, #DC5B51 ${pct}%)`,
  };

  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">{factor.icon}</span>
          <span className="text-[15px] font-medium text-text">{factor.label}</span>
        </div>
        <span className="text-sm font-semibold text-text tabular-nums min-w-[3rem] text-right">
          {value}{factor.unit}
        </span>
      </div>
      <input
        type="range"
        min={factor.min}
        max={factor.max}
        step={factor.step}
        value={value}
        onChange={(e) => onChange(factor.key, parseFloat(e.target.value))}
        className="w-full"
      />
      <div className="flex justify-between text-[11px] text-text-tertiary">
        <span>{factor.min}{factor.unit}</span>
        <span className="text-[11px] text-text-tertiary">{factor.description}</span>
        <span>{factor.max}{factor.unit}</span>
      </div>
    </div>
  );
}
