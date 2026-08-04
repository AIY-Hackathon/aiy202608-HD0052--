import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

/**
 * Health risk trend line chart — current vs optimized projection.
 */
export default function RiskTrendLine({ data, height = 300 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
        <XAxis
          dataKey="year"
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          tickLine={false}
          axisLine={false}
          label={{ value: "Years from now", position: "insideBottom", offset: -4, style: { fontSize: 11, fill: "#9CA3AF" } }}
        />
        <YAxis
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          tickLine={false}
          axisLine={false}
          domain={[0, 100]}
          label={{ value: "Risk %", angle: -90, position: "insideLeft", offset: 8, style: { fontSize: 11, fill: "#9CA3AF" } }}
        />
        <Tooltip
          contentStyle={{
            borderRadius: 12,
            border: "1px solid #E5E7EB",
            boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
            fontSize: 13,
          }}
        />
        <Legend
          wrapperStyle={{ fontSize: 13, paddingTop: 8 }}
        />
        <Line
          type="monotone"
          dataKey="current"
          name="Current Lifestyle"
          stroke="#DC5B51"
          strokeWidth={2.5}
          dot={{ r: 4, fill: "#DC5B51" }}
          strokeDasharray="6 3"
        />
        <Line
          type="monotone"
          dataKey="optimized"
          name="Optimized Lifestyle"
          stroke="#0D9488"
          strokeWidth={3}
          dot={{ r: 4, fill: "#0D9488" }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
