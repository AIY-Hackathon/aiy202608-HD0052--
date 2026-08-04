/**
 * GenoLife AI — Mock Data
 * All data simulates what a real genetic analysis API would return.
 */

export const userProfile = {
  name: "Alex",
  healthScore: 72,
  geneticAge: 34,
  chronologicalAge: 30,
};

export const healthSummary = {
  score: 72,
  level: "moderate",
  levelLabel: "Moderate Genetic Risk",
  aiSummary:
    "Your genetic profile indicates a moderate tendency toward metabolic risk, balanced by favorable cognitive and athletic gene variants. Lifestyle choices can significantly shift your projected health trajectory.",
};

export const geneCards = [
  {
    id: "apoe",
    symbol: "APOE",
    name: "Cognitive Health",
    category: "Brain & Longevity",
    riskLevel: "moderate",
    summary: "You carry one ε4 allele. This is associated with a moderately increased risk for late-onset cognitive decline.",
    interpretation:
      "The APOE ε4 variant affects how your body transports cholesterol and fats. About 25% of the population carries one copy. Importantly, lifestyle factors like regular exercise, a Mediterranean diet, and cognitive engagement have been shown to substantially offset this genetic predisposition.",
    recommendations: [
      "Prioritize 150+ minutes of aerobic exercise weekly",
      "Follow a Mediterranean-style diet rich in omega-3s",
      "Engage in regular cognitive activities (reading, puzzles, learning new skills)",
    ],
    icon: "🧠",
  },
  {
    id: "fto",
    symbol: "FTO",
    name: "Metabolic Tendency",
    category: "Metabolism",
    riskLevel: "elevated",
    summary: "Your FTO variant is associated with a slightly higher tendency toward weight gain, particularly with a high-sugar diet.",
    interpretation:
      "The FTO gene influences how your brain responds to hunger signals and how your body stores fat. People with this variant may feel less satiety after meals. The good news: studies show that regular physical activity reduces the effect of this variant by up to 30%.",
    recommendations: [
      "Focus on high-protein, high-fiber meals to increase satiety",
      "Limit added sugars and refined carbohydrates",
      "Aim for 10,000 steps daily",
    ],
    icon: "⚡",
  },
  {
    id: "actn3",
    symbol: "ACTN3",
    name: "Muscle Performance",
    category: "Athletic Performance",
    riskLevel: "advantage",
    summary: "You have the 'power' variant of ACTN3. Your muscle fibers are optimized for sprint and power activities.",
    interpretation:
      "The ACTN3 gene produces a protein found exclusively in fast-twitch muscle fibers. Your genotype (RR) means you produce this protein, giving you a natural advantage in explosive movements. This doesn't mean you'll be an Olympic sprinter, but you're likely to respond well to strength and power training.",
    recommendations: [
      "Include sprint intervals and explosive training in your routine",
      "Strength train 2-3x per week for optimal results",
      "Your recovery from high-intensity work tends to be efficient",
    ],
    icon: "💪",
  },
  {
    id: "clock",
    symbol: "CLOCK",
    name: "Sleep & Circadian Rhythm",
    category: "Sleep & Recovery",
    riskLevel: "moderate",
    summary: "Your CLOCK gene variant suggests you're naturally inclined toward an evening chronotype — a 'night owl' pattern.",
    interpretation:
      "The CLOCK gene regulates your circadian rhythm. Your variant is associated with a delayed sleep phase, meaning your natural energy peak occurs later in the day. While this isn't inherently problematic, misalignment between your natural rhythm and early-morning obligations can lead to chronic sleep debt.",
    recommendations: [
      "Get morning sunlight exposure to help reset your circadian clock",
      "Maintain a consistent sleep schedule, even on weekends",
      "Avoid blue light 1-2 hours before your target bedtime",
    ],
    icon: "🌙",
  },
];

export const riskDimensions = [
  { key: "metabolic", label: "Metabolic", score: 68, baseline: 50 },
  { key: "cognitive", label: "Cognitive", score: 42, baseline: 50 },
  { key: "cardiovascular", label: "Cardiovascular", score: 55, baseline: 50 },
  { key: "athletic", label: "Athletic", score: 22, baseline: 50 },
  { key: "sleep", label: "Sleep", score: 50, baseline: 50 },
];

export const simulationDefaults = {
  sleep: 6,
  exercise: 3,
  diet: 5,
  stress: 6,
};

export const simulationFactors = [
  {
    key: "sleep",
    label: "Sleep Quality",
    icon: "🌙",
    min: 3,
    max: 10,
    step: 0.5,
    unit: "hrs",
    description: "Hours of quality sleep per night",
  },
  {
    key: "exercise",
    label: "Physical Activity",
    icon: "🏃",
    min: 0,
    max: 7,
    step: 1,
    unit: "days",
    description: "Days of exercise per week",
  },
  {
    key: "diet",
    label: "Diet Quality",
    icon: "🥗",
    min: 1,
    max: 10,
    step: 1,
    unit: "/10",
    description: "Overall diet quality score",
  },
  {
    key: "stress",
    label: "Stress Level",
    icon: "🧘",
    min: 1,
    max: 10,
    step: 1,
    unit: "/10",
    description: "Perceived stress (1 = very low, 10 = very high)",
  },
];

/**
 * Calculate health score based on lifestyle factors and genetic baseline.
 * This is a simplified model for demo purposes.
 */
export function calculateHealthScore(factors, geneticBaseline = 72) {
  const { sleep, exercise, diet, stress } = factors;

  // Each factor contributes to a deviation from genetic baseline
  const sleepImpact = ((sleep - 6) / 7) * 8;    // -3.4 to +4.6
  const exerciseImpact = ((exercise - 3) / 7) * 10; // -4.3 to +5.7
  const dietImpact = ((diet - 5) / 9) * 12;     // -5.3 to +6.7
  const stressImpact = ((6 - stress) / 9) * 10;  // -5.6 to +5.6 (inverted: lower stress = higher score)

  const totalDeviation = sleepImpact + exerciseImpact + dietImpact + stressImpact;
  let score = Math.round(geneticBaseline + totalDeviation);
  score = Math.max(35, Math.min(98, score));

  return score;
}

export function calculateRiskDimensions(factors) {
  const { sleep, exercise, diet, stress } = factors;

  return [
    {
      key: "metabolic",
      label: "Metabolic",
      score: Math.round(68 - (diet - 5) * 3 - (exercise - 3) * 2 + (stress - 5) * 1.5),
      baseline: 50,
    },
    {
      key: "cognitive",
      label: "Cognitive",
      score: Math.round(42 - (sleep - 6) * 3 - (stress - 5) * 2 + (exercise - 3) * -0.5),
      baseline: 50,
    },
    {
      key: "cardiovascular",
      label: "Cardiovascular",
      score: Math.round(55 - (exercise - 3) * 4 - (diet - 5) * 2 + (stress - 5) * 2),
      baseline: 50,
    },
    {
      key: "athletic",
      label: "Athletic",
      score: Math.round(22 - (exercise - 3) * -3 + (sleep - 6) * -1),
      baseline: 50,
    },
    {
      key: "sleep",
      label: "Sleep",
      score: Math.round(50 + (sleep - 6) * -5 + (stress - 5) * 3),
      baseline: 50,
    },
  ].map((d) => ({ ...d, score: Math.max(5, Math.min(95, d.score)) }));
}

export function generateTrendData(factors) {
  const risks = calculateRiskDimensions(factors);
  const years = [0, 1, 3, 5, 10, 15, 20];
  const avgRisk = risks.reduce((s, r) => s + r.score, 0) / risks.length;

  return years.map((year) => ({
    year,
    current: Math.round(avgRisk + year * 1.8),
    optimized: Math.round(avgRisk * 0.7 + year * 0.9),
  }));
}

export function generateRecommendations(factors) {
  const recs = [];

  if (factors.sleep < 7) {
    recs.push({
      id: "s1",
      pillar: "sleep",
      icon: "🌙",
      title: "Increase sleep to 7-8 hours",
      description:
        "Your genetic profile shows heightened sensitivity to sleep deprivation. Adding just one more hour of sleep could reduce your metabolic risk markers.",
      difficulty: "moderate",
      impact: 4,
      time: "Tonight",
    });
  }
  if (factors.exercise < 4) {
    recs.push({
      id: "e1",
      pillar: "exercise",
      icon: "🏃",
      title: "Add one more workout day",
      description:
        "With your ACTN3 power-oriented genotype, you'll respond well to adding a high-intensity session each week.",
      difficulty: "moderate",
      impact: 5,
      time: "This week",
    });
  }
  if (factors.diet < 7) {
    recs.push({
      id: "d1",
      pillar: "diet",
      icon: "🥗",
      title: "Increase fiber-rich whole foods",
      description:
        "Your FTO variant means you benefit disproportionately from a high-fiber diet. Target 30g of fiber daily.",
      difficulty: "easy",
      impact: 4,
      time: "Start today",
    });
  }
  if (factors.stress > 5) {
    recs.push({
      id: "st1",
      pillar: "stress",
      icon: "🧘",
      title: "Add 10 minutes of daily mindfulness",
      description:
        "Your CLOCK gene variant makes your circadian rhythm sensitive to stress. Brief daily meditation can improve sleep quality and reduce cortisol.",
      difficulty: "easy",
      impact: 3,
      time: "10 min/day",
    });
  }
  if (factors.exercise >= 4 && factors.sleep >= 7) {
    recs.push({
      id: "g1",
      pillar: "general",
      icon: "🎯",
      title: "You're building strong habits",
      description:
        "Keep going! Consistency over time is what shifts your epigenetic expression. Consider adding variety to maintain engagement.",
      difficulty: "easy",
      impact: 2,
      time: "Ongoing",
    });
  }

  return recs;
}

export const thirtyDayPlan = {
  goal: "Improve metabolic health and reduce long-term cardiovascular risk",
  weeks: [
    {
      label: "Week 1 — Foundation",
      theme: "Awareness & Baseline",
      tasks: [
        { day: "Day 1-2", title: "Track your baseline", desc: "Log sleep, meals, and activity without changing anything." },
        { day: "Day 3-4", title: "Add 30 min walking", desc: "Simple daily walk — notice how you feel afterward." },
        { day: "Day 5-7", title: "Audit your plate", desc: "Take a photo of every meal. No judgment, just awareness." },
      ],
    },
    {
      label: "Week 2 — Activation",
      theme: "Small Changes, Big Impact",
      tasks: [
        { day: "Day 8-9", title: "Bedtime 30 min earlier", desc: "Your CLOCK gene responds well to gradual shifts." },
        { day: "Day 10-12", title: "2x HIIT sessions", desc: "Leverage your ACTN3 advantage with short, intense workouts." },
        { day: "Day 13-14", title: "Swap one processed snack", desc: "Replace with nuts or fruit. Your FTO variant will thank you." },
      ],
    },
    {
      label: "Week 3 — Integration",
      theme: "Building Momentum",
      tasks: [
        { day: "Day 15-17", title: "Meal prep Sunday", desc: "Plan and prep 3 days of high-fiber meals." },
        { day: "Day 18-19", title: "Morning light exposure", desc: "10 min outdoor morning light to reset circadian rhythm." },
        { day: "Day 20-21", title: "Try a new activity", desc: "Your ACTN3 favors variety in power-based activities." },
      ],
    },
    {
      label: "Week 4 — Sustain",
      theme: "Lifelong Habits",
      tasks: [
        { day: "Day 22-24", title: "Reflect on energy levels", desc: "Journal how you feel vs. Day 1. Notice the trends." },
        { day: "Day 25-27", title: "Share your progress", desc: "Social accountability reinforces genetic expression changes." },
        { day: "Day 28-30", title: "Plan the next 30 days", desc: "Set your next goal. Health is a continuous journey." },
      ],
    },
  ],
};
