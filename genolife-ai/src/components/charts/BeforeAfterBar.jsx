import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

/**
 * Before/After comparison bar chart for risk dimensions.
 */
export default function BeforeAfterBar({ before, after, height = 280 }) {
  const data = before.map((b, i) => ({
    dimension: b.label,
    Before: b.score,
    After: after[i]?.score || b.score,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}
        barGap={4} barSize={28}>
        <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
        <XAxis
          dataKey="dimension"
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          tickLine={false}
          axisLine={false}
          domain={[0, 100]}
        />
        <Tooltip
          contentStyle={{
            borderRadius: 12,
            border: "1px solid #E5E7EB",
            boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
            fontSize: 13,
          }}
        />
        <Legend wrapperStyle={{ fontSize: 13, paddingTop: 8 }} />
        <Bar dataKey="Before" fill="#DC5B51" radius={[6, 6, 0, 0]} />
        <Bar dataKey="After" fill="#0D9488" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
