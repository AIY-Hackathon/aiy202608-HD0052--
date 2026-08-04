import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer } from "recharts";

/**
 * Five-dimension genetic risk radar chart.
 */
export default function RiskRadar({ data, height = 320 }) {
  const chartData = data.map((d) => ({
    dimension: d.label,
    You: d.score,
    Baseline: d.baseline,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RadarChart data={chartData} cx="50%" cy="50%" outerRadius="75%">
        <PolarGrid stroke="#E5E7EB" strokeWidth={1} />
        <PolarAngleAxis
          dataKey="dimension"
          tick={{ fontSize: 13, fill: "#6B7280", fontWeight: 500 }}
        />
        <Radar
          name="You"
          dataKey="You"
          stroke="#1E3A5F"
          fill="#1E3A5F"
          fillOpacity={0.15}
          strokeWidth={2}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
