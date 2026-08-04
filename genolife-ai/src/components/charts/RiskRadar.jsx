import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";

/**
 * Five-dimension genetic risk radar chart — premium styling.
 */
export default function RiskRadar({ data, height = 320 }) {
  const chartData = data.map((d) => ({
    dimension: d.label,
    You: d.score,
    Baseline: d.baseline,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RadarChart data={chartData} cx="50%" cy="48%" outerRadius="72%">
        <PolarGrid stroke="#E5E7EB" strokeWidth={0.5} />
        <PolarAngleAxis
          dataKey="dimension"
          tick={{ fontSize: 12, fontWeight: 500, fill: "#6B7280" }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 100]}
          tick={false}
          axisLine={false}
        />
        {/* Population baseline */}
        <Radar
          name="Baseline"
          dataKey="Baseline"
          stroke="#D1D5DB"
          fill="#F3F4F6"
          fillOpacity={0.4}
          strokeWidth={1.5}
          strokeDasharray="4 4"
        />
        {/* Your risk profile */}
        <Radar
          name="You"
          dataKey="You"
          stroke="#1E3A5F"
          fill="#1E3A5F"
          fillOpacity={0.12}
          strokeWidth={2}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
