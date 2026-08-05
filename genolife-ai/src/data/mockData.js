/**
 * GenoLife AI — Mock Data（儿科版）
 * 所有数据模拟真实基因分析 API 的返回结果。
 * 面向新生儿 VCF 基因风险评估，帮助家长了解基因筛查结果。
 */

export const userProfile = {
  name: "宝宝",
  healthScore: 72,
  geneticAge: 0,
  chronologicalAge: 0,
};

export const healthSummary = {
  score: 72,
  level: "moderate",
  levelLabel: "中等遗传风险意识",
  aiSummary:
    "宝宝的基因筛查结果提示部分遗传风险需要关注，但科学的早期照护和定期随访可显著改善发育轨迹。基因不是命运，父母的日常照护对孩子的健康发展具有深远影响。",
};

export const healthMetrics = [
  { key: "metabolic", label: "代谢与内分泌", score: 55, suffix: "%", status: "moderate" },
  { key: "neurodevelopmental", label: "神经发育", score: 48, suffix: "%", status: "moderate" },
  { key: "cardiovascular", label: "心血管与血液", score: 42, suffix: "%", status: "low" },
  { key: "immunodeficiency", label: "免疫与感染", score: 60, suffix: "%", status: "moderate" },
];

export const geneticProfile = [
  { key: "metabolic", icon: "⚡", label: "代谢与内分泌", trait: "中等关注", detail: "PAH、G6PD 等基因的筛查结果影响代谢健康管理策略" },
  { key: "neurodevelopmental", icon: "🧠", label: "神经发育", trait: "需重点关注", detail: "SMN1、FMR1 等基因变异提示早期干预的重要性" },
  { key: "cardiovascular", icon: "❤️", label: "心血管与血液", trait: "常规监测", detail: "HBB、MYH7 等基因筛查结果指导心血管随访计划" },
  { key: "immunodeficiency", icon: "🛡️", label: "免疫与感染", trait: "中等关注", detail: "IL2RG、BTK 等基因变异提示感染预防的重要性" },
];

export const riskSummaryCards = [
  { key: "metabolic", label: "代谢与内分泌", level: "中等关注", levelColor: "text-risk-moderate", bg: "bg-amber-50/60", border: "border-amber-100", desc: "宝宝的代谢相关基因提示需要关注喂养方式和新生儿筛查随访。早期饮食管理可完全改变预后。" },
  { key: "neurodevelopmental", label: "神经发育", level: "需重点关注", levelColor: "text-risk-elevated", bg: "bg-red-50/60", border: "border-red-100", desc: "神经发育相关基因提示早期干预的紧迫性。发育刺激和康复训练可显著改善发育轨迹。" },
  { key: "immunodeficiency", label: "免疫与感染", level: "中等关注", levelColor: "text-risk-moderate", bg: "bg-amber-50/60", border: "border-amber-100", desc: "免疫相关基因提示感染预防和定期免疫球蛋白监测的重要性。按时接种疫苗和及时就医是关键。" },
];

export const geneCards = [
  {
    id: "pah",
    symbol: "PAH",
    name: "苯丙酮尿症(PKU)",
    category: "代谢与内分泌",
    riskLevel: "moderate",
    summary: "PAH 基因编码苯丙氨酸羟化酶。致病变异导致PKU——一种可通过饮食控制的可治疗先天性代谢缺陷。",
    interpretation:
      "PAH 致病变异影响苯丙氨酸代谢。未经治疗的PKU导致严重智力障碍，但严格的苯丙氨酸限制饮食可完全预防神经系统损伤。新生儿筛查+早期饮食干预是改变预后的关键。中国PKU发病率约1/11,000。",
    recommendations: [
      "严格遵循新生儿筛查随访和专科医生饮食指导",
      "记录喂养情况和生长发育曲线",
      "定期监测血苯丙氨酸水平",
    ],
    icon: "⚡",
  },
  {
    id: "g6pd",
    symbol: "G6PD",
    name: "G6PD缺乏症",
    category: "心血管与血液",
    riskLevel: "moderate",
    summary: "G6PD 缺乏症是全球最常见的遗传性酶缺乏症。接触氧化性触发因素可诱发急性溶血性贫血。",
    interpretation:
      "G6PD 缺乏症是最经典的基因×环境交互案例之一。避免已知触发因素（蚕豆、特定药物如磺胺类和阿司匹林、樟脑丸等）可完全预防溶血发作。全球约4亿人携带G6PD缺乏变异，中国南方发病率较高。",
    recommendations: [
      "避免蚕豆和特定药物（磺胺类、阿司匹林等）",
      "生病时告知医生G6PD缺乏情况",
      "关注黄疸和贫血迹象，及时就医",
    ],
    icon: "🩸",
  },
  {
    id: "smn1",
    symbol: "SMN1",
    name: "脊髓性肌萎缩(SMA)",
    category: "神经发育",
    riskLevel: "elevated",
    summary: "SMN1 纯合缺失/致病变异导致SMA——婴幼儿最常见的致死性神经肌肉疾病。治疗时机至关重要。",
    interpretation:
      "SMA 是最具时间紧迫性的G×E交互案例。症状前治疗（新生儿筛查+早期基因治疗/药物干预）与症状后治疗的预后差异巨大。SMN2拷贝数影响疾病严重程度。中国人群SMA携带率约1/40-1/50。",
    recommendations: [
      "尽早开始早期干预和康复训练",
      "与儿科神经专科医生保持定期随访",
      "关注运动发育里程碑，及时评估",
    ],
    icon: "🧠",
  },
  {
    id: "gjb2",
    symbol: "GJB2",
    name: "先天性听力损失",
    category: "感官与结构",
    riskLevel: "moderate",
    summary: "GJB2 致病变异是遗传性先天性听力损失最常见的原因，占遗传性听力损失的约50%。",
    interpretation:
      "GJB2 听力损失是G×E交互的典范案例：新生儿听力筛查+早期助听器/人工耳蜗（<12月龄）+语言康复可使语言发育接近正常水平。GJB2听力损失通常为非进行性。中国人群GJB2变异携带率较高。",
    recommendations: [
      "完成新生儿听力筛查和诊断性听力学评估",
      "根据筛查结果尽早适配助听器或评估人工耳蜗",
      "配合早期言语康复训练",
    ],
    icon: "👂",
  },
  {
    id: "cyp21a2",
    symbol: "CYP21A2",
    name: "先天性肾上腺皮质增生(CAH)",
    category: "代谢与内分泌",
    riskLevel: "elevated",
    summary: "CYP21A2 致病变异导致CAH——一种可通过新生儿筛查发现的类固醇激素合成障碍。盐耗型危象可危及生命。",
    interpretation:
      "CAH的G×E交互核心在于激素替代治疗的依从性。规律用药可预防盐耗危象，应激剂量调整应对于感染/手术等应激状态。新生儿筛查显著降低了CAH相关死亡率。",
    recommendations: [
      "严格遵循激素替代治疗方案",
      "感染或手术时遵医嘱进行应激剂量调整",
      "定期内分泌科随访和生长发育监测",
    ],
    icon: "⚡",
  },
  {
    id: "chd7",
    symbol: "CHD7",
    name: "CHARGE综合征",
    category: "心血管与血液",
    riskLevel: "moderate",
    summary: "CHD7 致病变异导致CHARGE综合征——涉及眼、心脏、鼻腔、发育、生殖器和耳部异常的多系统先天性疾病。",
    interpretation:
      "CHARGE综合征需要多学科综合管理——心脏手术、听力辅助、胃造口喂养和发育支持的协同是改善预后的核心。临床表型谱广，个体化照护方案至关重要。",
    recommendations: [
      "定期心脏、听力、眼科多学科评估",
      "关注喂养耐受性和生长发育情况",
      "根据器官受累情况制定个体化照护计划",
    ],
    icon: "❤️",
  },
  {
    id: "il2rg",
    symbol: "IL2RG",
    name: "X连锁严重联合免疫缺陷(SCID)",
    category: "免疫与感染",
    riskLevel: "elevated",
    summary: "IL2RG 致病变异导致SCID-X1——缺乏功能性T细胞和NK细胞，出生数月内面临致死性感染风险。",
    interpretation:
      "SCID-X1 是最具决定性的G×E交互案例：TREC新生儿筛查+早期造血干细胞移植/基因治疗可挽救生命并重建免疫功能。3.5月龄前移植生存率>95%。治疗前严格感染防护至关重要。",
    recommendations: [
      "严格遵循感染预防措施",
      "按时完成疫苗接种计划（遵医嘱调整）",
      "出现发热或感染迹象立即就医",
    ],
    icon: "🛡️",
  },
  {
    id: "cftr",
    symbol: "CFTR",
    name: "囊性纤维化(CF)",
    category: "代谢与内分泌",
    riskLevel: "moderate",
    summary: "CFTR 致病变异导致囊性纤维化——影响呼吸和消化系统的多系统疾病。CFTR调节剂是变异特异性靶向治疗。",
    interpretation:
      "CF的G×E交互涉及多方面环境调节：营养支持（胰酶、高热量饮食）、呼吸道清理、避免感染和CFTR调节剂药物的综合管理。新生儿筛查可尽早发现并开始干预。",
    recommendations: [
      "遵循营养支持和胰酶替代治疗方案",
      "定期呼吸道清理和肺功能评估",
      "避免呼吸道感染，按时接种疫苗",
    ],
    icon: "⚡",
  },
  {
    id: "hbb",
    symbol: "HBB",
    name: "镰状细胞病/地中海贫血",
    category: "心血管与血液",
    riskLevel: "moderate",
    summary: "HBB 致病变异导致镰状细胞病和β-地中海贫血——全球最常见的严重单基因遗传病。",
    interpretation:
      "新生儿筛查+预防性抗生素+疫苗接种+羟基脲治疗显著降低了儿童死亡率。HBB是基因筛查改变预后的典范——早期诊断和预防性管理完全改变了疾病自然史。",
    recommendations: [
      "定期血液科专科随访",
      "遵医嘱进行预防性抗生素和疫苗接种",
      "关注贫血、疼痛和感染等并发症迹象",
    ],
    icon: "🩸",
  },
];

/**
 * 测试用疾病 Profile — 模拟真实 analysisData.profile.geneCards 结构。
 *
 * 每个 geneCard 包含：
 *   - symbol: 基因符号（用于匹配遗传知识库）
 *   - name: 疾病名称
 *   - riskLevel: elevated | moderate | low
 *   - clinvarSignificance: Pathogenic | Likely_pathogenic | Uncertain_significance | Benign
 *
 * 通过文件名/reportId 中包含 profile key（如 "pah", "smn1"）触发对应 profile。
 * 无匹配时返回 null → 前端走向 ScreeningSummary。
 */
export const MOCK_DISEASE_PROFILES = {
  // ──── PKU ────
  pah: {
    genes: ["PAH"],
    summary: { score: 55, level: "elevated", levelLabel: "高遗传风险" },
    geneCards: [
      {
        id: "pah", symbol: "PAH", name: "苯丙酮尿症(PKU)",
        category: "代谢与内分泌", riskLevel: "elevated",
        clinvarSignificance: "Pathogenic",
        summary: "PAH 基因编码苯丙氨酸羟化酶。致病变异导致PKU。",
        interpretation: "PAH 致病变异影响苯丙氨酸代谢。未经治疗的PKU导致严重智力障碍，但严格的苯丙氨酸限制饮食可完全预防神经系统损伤。中国PKU发病率约1/11,000。",
        recommendations: ["严格遵循新生儿筛查随访和专科医生饮食指导", "记录喂养情况和生长发育曲线", "定期监测血苯丙氨酸水平"],
        icon: "⚡",
      },
    ],
    variants: [{
      id: "var_0", chromosome: "12", position: 103234000, reference: "A", alternative: "G",
      rs_id: "rs62514927", gene_name: "PAH", clinvar_significance: "Pathogenic", risk_score: 0.92,
    }],
    riskDimensions: [
      { key: "metabolic", label: "代谢与内分泌", score: 35, baseline: 50 },
      { key: "neurodevelopmental", label: "神经发育", score: 40, baseline: 50 },
    ],
  },

  // ──── SMA ────
  smn1: {
    genes: ["SMN1"],
    summary: { score: 40, level: "elevated", levelLabel: "高遗传风险" },
    geneCards: [
      {
        id: "smn1", symbol: "SMN1", name: "脊髓性肌萎缩(SMA)",
        category: "神经发育", riskLevel: "elevated",
        clinvarSignificance: "Pathogenic",
        summary: "SMN1 纯合缺失/致病变异导致SMA——婴幼儿最常见的致死性神经肌肉疾病。",
        interpretation: "SMA 是最具时间紧迫性的G×E交互案例。症状前治疗与症状后治疗的预后差异巨大。中国人群SMA携带率约1/40-1/50。",
        recommendations: ["尽早开始早期干预和康复训练", "与儿科神经专科医生保持定期随访", "关注运动发育里程碑"],
        icon: "🧠",
      },
    ],
    variants: [{
      id: "var_0", chromosome: "5", position: 70923300, reference: "A", alternative: "C",
      rs_id: "rs386134241", gene_name: "SMN1", clinvar_significance: "Pathogenic", risk_score: 0.95,
    }],
    riskDimensions: [
      { key: "neurodevelopmental", label: "神经发育", score: 25, baseline: 50 },
      { key: "metabolic", label: "代谢与内分泌", score: 55, baseline: 50 },
    ],
  },

  // ──── CF ────
  cftr: {
    genes: ["CFTR"],
    summary: { score: 50, level: "elevated", levelLabel: "高遗传风险" },
    geneCards: [
      {
        id: "cftr", symbol: "CFTR", name: "囊性纤维化(CF)",
        category: "代谢与内分泌", riskLevel: "elevated",
        clinvarSignificance: "Pathogenic",
        summary: "CFTR 致病变异导致囊性纤维化——影响呼吸和消化系统的多系统疾病。",
        interpretation: "CF的G×E交互涉及多方面环境调节。新生儿筛查+CFTR调节剂治疗可显著改善预后。",
        recommendations: ["遵循营养支持和胰酶替代治疗", "定期呼吸道清理和肺功能评估", "避免呼吸道感染"],
        icon: "⚡",
      },
    ],
    variants: [{
      id: "var_0", chromosome: "7", position: 117149050, reference: "T", alternative: "G",
      rs_id: "rs113993960", gene_name: "CFTR", clinvar_significance: "Pathogenic", risk_score: 0.88,
    }],
    riskDimensions: [
      { key: "metabolic", label: "代谢与内分泌", score: 35, baseline: 50 },
      { key: "neurodevelopmental", label: "神经发育", score: 55, baseline: 50 },
    ],
  },

  // ──── G6PD ────
  g6pd: {
    genes: ["G6PD"],
    summary: { score: 52, level: "moderate", levelLabel: "中等遗传风险" },
    geneCards: [
      {
        id: "g6pd", symbol: "G6PD", name: "G6PD缺乏症",
        category: "心血管与血液", riskLevel: "elevated",
        clinvarSignificance: "Pathogenic",
        summary: "G6PD 缺乏症是全球最常见的遗传性酶缺乏症。",
        interpretation: "G6PD 缺乏症是最经典的基因×环境交互案例之一。避免触发因素可完全预防溶血发作。全球约4亿人携带G6PD缺乏变异。",
        recommendations: ["避免蚕豆和特定药物", "告知医生G6PD缺乏情况", "关注黄疸和贫血迹象"],
        icon: "🩸",
      },
    ],
    variants: [{
      id: "var_0", chromosome: "X", position: 153759000, reference: "G", alternative: "A",
      rs_id: "rs1050828", gene_name: "G6PD", clinvar_significance: "Pathogenic", risk_score: 0.78,
    }],
    riskDimensions: [
      { key: "cardiovascular", label: "心血管与血液", score: 30, baseline: 50 },
      { key: "metabolic", label: "代谢与内分泌", score: 55, baseline: 50 },
    ],
  },

  // ──── CAH — CYP21A2 ────
  cyp21a2: {
    genes: ["CYP21A2"],
    summary: { score: 48, level: "elevated", levelLabel: "高遗传风险" },
    geneCards: [
      {
        id: "cyp21a2", symbol: "CYP21A2", name: "先天性肾上腺皮质增生(CAH)",
        category: "代谢与内分泌", riskLevel: "elevated",
        clinvarSignificance: "Pathogenic",
        summary: "CYP21A2 致病变异导致CAH——类固醇激素合成障碍。",
        interpretation: "CAH的G×E交互核心在于激素替代治疗的依从性。新生儿筛查显著降低了CAH相关死亡率。",
        recommendations: ["严格遵循激素替代治疗", "应激剂量调整", "定期内分泌科随访"],
        icon: "⚡",
      },
    ],
    variants: [{
      id: "var_0", chromosome: "6", position: 32006800, reference: "A", alternative: "G",
      rs_id: "rs77554567", gene_name: "CYP21A2", clinvar_significance: "Pathogenic", risk_score: 0.90,
    }],
    riskDimensions: [
      { key: "metabolic", label: "代谢与内分泌", score: 30, baseline: 50 },
    ],
  },

  // ──── SCID — IL2RG ────
  scid: {
    genes: ["IL2RG"],
    summary: { score: 35, level: "elevated", levelLabel: "高遗传风险" },
    geneCards: [
      {
        id: "il2rg", symbol: "IL2RG", name: "X连锁严重联合免疫缺陷(SCID)",
        category: "免疫与感染", riskLevel: "elevated",
        clinvarSignificance: "Pathogenic",
        summary: "IL2RG 致病变异导致SCID-X1——出生数月内面临致死性感染风险。",
        interpretation: "SCID-X1 是最具决定性的G×E交互案例。3.5月龄前移植生存率>95%。",
        recommendations: ["严格感染预防措施", "按时疫苗接种", "出现感染迹象立即就医"],
        icon: "🛡️",
      },
    ],
    variants: [{
      id: "var_0", chromosome: "X", position: 70328300, reference: "T", alternative: "C",
      rs_id: "rs193922400", gene_name: "IL2RG", clinvar_significance: "Pathogenic", risk_score: 0.97,
    }],
    riskDimensions: [
      { key: "immunodeficiency", label: "免疫与感染", score: 20, baseline: 50 },
    ],
  },

  // ──── CHARGE — CHD7 ────
  chd7: {
    genes: ["CHD7"],
    summary: { score: 55, level: "moderate", levelLabel: "中等遗传风险" },
    geneCards: [
      {
        id: "chd7", symbol: "CHD7", name: "CHARGE综合征",
        category: "心血管与血液", riskLevel: "elevated",
        clinvarSignificance: "Pathogenic",
        summary: "CHD7 致病变异导致CHARGE综合征——多系统先天性疾病。",
        interpretation: "CHARGE综合征需要多学科综合管理——心脏手术、听力辅助、胃造口喂养和发育支持。",
        recommendations: ["多学科评估", "关注喂养和生长发育", "个体化照护计划"],
        icon: "❤️",
      },
    ],
    variants: [{
      id: "var_0", chromosome: "8", position: 61541600, reference: "G", alternative: "A",
      rs_id: "rs121434392", gene_name: "CHD7", clinvar_significance: "Pathogenic", risk_score: 0.93,
    }],
    riskDimensions: [
      { key: "cardiovascular", label: "心血管与血液", score: 35, baseline: 50 },
    ],
  },

  // ──── Congenital Hearing Loss — GJB2 ────
  gjb2: {
    genes: ["GJB2"],
    summary: { score: 58, level: "moderate", levelLabel: "中等遗传风险" },
    geneCards: [
      {
        id: "gjb2", symbol: "GJB2", name: "先天性听力损失",
        category: "感官与结构", riskLevel: "elevated",
        clinvarSignificance: "Likely_pathogenic",
        summary: "GJB2 致病变异是遗传性先天性听力损失最常见的原因。",
        interpretation: "新生儿听力筛查+早期助听器/人工耳蜗（<12月龄）+语言康复可使语言发育接近正常水平。",
        recommendations: ["新生儿听力筛查和诊断性听力学评估", "尽早适配助听器或评估人工耳蜗", "早期言语康复训练"],
        icon: "👂",
      },
    ],
    variants: [{
      id: "var_0", chromosome: "13", position: 20763600, reference: "C", alternative: "T",
      rs_id: "rs80338939", gene_name: "GJB2", clinvar_significance: "Likely_pathogenic", risk_score: 0.72,
    }],
    riskDimensions: [
      { key: "sensory", label: "感官与结构", score: 30, baseline: 50 },
    ],
  },

  // ──── Thalassemia — HBB ────
  hbb: {
    genes: ["HBB"],
    summary: { score: 54, level: "moderate", levelLabel: "中等遗传风险" },
    geneCards: [
      {
        id: "hbb", symbol: "HBB", name: "镰状细胞病/地中海贫血",
        category: "心血管与血液", riskLevel: "elevated",
        clinvarSignificance: "Pathogenic",
        summary: "HBB 致病变异导致镰状细胞病和β-地中海贫血。",
        interpretation: "新生儿筛查+预防性抗生素+疫苗接种+羟基脲治疗显著降低了儿童死亡率。早期诊断和预防性管理完全改变了疾病自然史。",
        recommendations: ["定期血液科专科随访", "预防性抗生素和疫苗接种", "关注贫血、疼痛和感染迹象"],
        icon: "🩸",
      },
    ],
    variants: [{
      id: "var_0", chromosome: "11", position: 5248250, reference: "A", alternative: "T",
      rs_id: "rs334", gene_name: "HBB", clinvar_significance: "Pathogenic", risk_score: 0.86,
    }],
    riskDimensions: [
      { key: "cardiovascular", label: "心血管与血液", score: 32, baseline: 50 },
    ],
  },
};

/**
 * 根据 VCF 文件名或 reportId 匹配测试 profile。
 * 遍历 profile key，如果文件名或 reportId 中包含 key（不区分大小写）即匹配。
 * 无匹配时返回 null → 前端用空 geneCards → ScreeningSummary。
 */
export function matchMockProfile(filenameOrId) {
  if (!filenameOrId) return null;
  const lower = filenameOrId.toLowerCase();
  for (const [key, profile] of Object.entries(MOCK_DISEASE_PROFILES)) {
    if (lower.includes(key)) return profile;
  }
  return null;
}

export const riskDimensions = [
  { key: "metabolic", label: "代谢与内分泌", score: 55, baseline: 50 },
  { key: "cardiovascular", label: "心血管与血液", score: 42, baseline: 50 },
  { key: "neurodevelopmental", label: "神经发育", score: 48, baseline: 50 },
  { key: "immunodeficiency", label: "免疫与感染", score: 60, baseline: 50 },
  { key: "sensory", label: "感官与结构", score: 50, baseline: 50 },
];

export const simulationDefaults = {
  nutrition_type: 7,
  sleep_quality: 7,
  development_stimulation: 6,
  medical_adherence: 9,
  environmental_safety: 8,
};

export const simulationFactors = [
  {
    key: "nutrition_type",
    label: "喂养方式",
    icon: "🍼",
    type: "categorical",
    options: [
      { label: "母乳喂养", value: 10, desc: "最佳营养和免疫保护" },
      { label: "混合喂养", value: 6, desc: "母乳+配方奶组合" },
      { label: "配方喂养", value: 3, desc: "科学配方奶喂养" },
    ],
    min: 0,
    max: 10,
    step: 1,
    unit: "/10",
    description: "选择宝宝的喂养方式",
  },
  {
    key: "sleep_quality",
    label: "睡眠质量",
    icon: "😴",
    min: 0,
    max: 10,
    step: 1,
    unit: "/10",
    description: "婴儿睡眠规律性和时长",
  },
  {
    key: "development_stimulation",
    label: "早期刺激",
    icon: "🎯",
    min: 0,
    max: 10,
    step: 1,
    unit: "/10",
    description: "感官刺激、互动游戏、语言暴露",
  },
  {
    key: "medical_adherence",
    label: "医疗依从性",
    icon: "🏥",
    min: 0,
    max: 10,
    step: 1,
    unit: "/10",
    description: "筛查随访、专科预约、用药按时程度",
  },
  {
    key: "environmental_safety",
    label: "环境安全",
    icon: "🏠",
    min: 0,
    max: 10,
    step: 1,
    unit: "/10",
    description: "无毒素暴露、安全睡眠环境、感染防护",
  },
];

/**
 * 计算健康评分（婴儿成长因子版）。
 * 每个因子对遗传基线的偏离产生贡献。
 */
export function calculateHealthScore(factors, geneticBaseline = 100) {
  const { nutrition_type, sleep_quality, development_stimulation, medical_adherence, environmental_safety } = factors;

  const nutritionImpact = ((nutrition_type - 7) / 10) * 8;
  const sleepImpact = ((sleep_quality - 7) / 10) * 8;
  const stimulationImpact = ((development_stimulation - 6) / 10) * 10;
  const adherenceImpact = ((medical_adherence - 9) / 10) * 12;
  const safetyImpact = ((environmental_safety - 8) / 10) * 8;

  const totalDeviation = nutritionImpact + sleepImpact + stimulationImpact + adherenceImpact + safetyImpact;
  let score = Math.round(geneticBaseline + totalDeviation);
  score = Math.max(35, Math.min(98, score));

  return score;
}

export function calculateRiskDimensions(factors) {
  const { nutrition_type, sleep_quality, development_stimulation, medical_adherence, environmental_safety } = factors;

  return [
    {
      key: "metabolic",
      label: "代谢与内分泌",
      score: Math.round(55 - (nutrition_type - 7) * 3 - (medical_adherence - 9) * 2),
      baseline: 50,
    },
    {
      key: "cardiovascular",
      label: "心血管与血液",
      score: Math.round(42 - (medical_adherence - 9) * 3 - (environmental_safety - 8) * 2),
      baseline: 50,
    },
    {
      key: "neurodevelopmental",
      label: "神经发育",
      score: Math.round(48 - (development_stimulation - 6) * 3 - (sleep_quality - 7) * 2 - (nutrition_type - 7) * 1.5),
      baseline: 50,
    },
    {
      key: "immunodeficiency",
      label: "免疫与感染",
      score: Math.round(60 - (medical_adherence - 9) * 3 - (environmental_safety - 8) * 2.5 - (nutrition_type - 7) * 1.5),
      baseline: 50,
    },
    {
      key: "sensory",
      label: "感官与结构",
      score: Math.round(50 - (development_stimulation - 6) * 2 - (medical_adherence - 9) * 2 - (environmental_safety - 8) * 1.5),
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

  if (factors.nutrition_type < 8) {
    recs.push({
      id: "n1",
      pillar: "nutrition",
      icon: "🍼",
      title: "优化喂养方式",
      description:
        "母乳喂养为宝宝提供最佳营养和免疫保护。如因特殊情况无法纯母乳，请咨询医生选择最适合的配方方案。",
      difficulty: "moderate",
      impact: 5,
      time: "立即开始",
    });
  }
  if (factors.sleep_quality < 8) {
    recs.push({
      id: "sl1",
      pillar: "sleep",
      icon: "😴",
      title: "建立规律睡眠习惯",
      description:
        "婴儿睡眠直接影响大脑发育和生长激素分泌。建立固定的睡前程序（洗澡→喂养→安抚→入睡），确保安全的睡眠环境。",
      difficulty: "moderate",
      impact: 4,
      time: "今晚开始",
    });
  }
  if (factors.development_stimulation < 7) {
    recs.push({
      id: "ds1",
      pillar: "development",
      icon: "🎯",
      title: "增加早期感官刺激",
      description:
        "互动游戏、语言暴露和适龄感官刺激对宝宝神经发育至关重要，尤其对有神经发育风险基因的宝宝。每天至少15分钟专注的亲子互动。",
      difficulty: "easy",
      impact: 5,
      time: "每天进行",
    });
  }
  if (factors.medical_adherence < 9) {
    recs.push({
      id: "ma1",
      pillar: "medical",
      icon: "🏥",
      title: "加强医疗随访依从性",
      description:
        "新生儿筛查异常结果的随访、专科预约和按时用药直接决定宝宝的预后。请确保不遗漏任何关键随访和检查。",
      difficulty: "moderate",
      impact: 5,
      time: "本周内",
    });
  }
  if (factors.environmental_safety < 8) {
    recs.push({
      id: "es1",
      pillar: "safety",
      icon: "🏠",
      title: "改善家居环境安全",
      description:
        "避免毒素暴露、确保安全睡眠环境（SIDS预防）、做好感染防护，为宝宝提供安全的成长空间。",
      difficulty: "easy",
      impact: 4,
      time: "立即开始",
    });
  }
  if (factors.medical_adherence >= 9 && factors.nutrition_type >= 8) {
    recs.push({
      id: "g1",
      pillar: "general",
      icon: "🎯",
      title: "您在为宝宝打下坚实的健康基础",
      description:
        "坚持科学的喂养和照护方案，定期儿科随访。持续的优质照护是改变基因表达的关键。",
      difficulty: "easy",
      impact: 2,
      time: "持续进行",
    });
  }

  return recs;
}

export const thirtyDayPlan = {
  goal: "建立科学的婴儿照护方案，优化早期发育轨迹，守护宝宝健康成长",
  weeks: [
    {
      label: "第 1 个月 — 基础建立",
      theme: "建立喂养与睡眠规律，完成新生儿筛查随访",
      tasks: [
        { day: "第 1 周", title: "建立喂养日记", desc: "记录每次喂养时间、时长和方式（母乳/配方/混合），了解宝宝的喂养规律和需求量。" },
        { day: "第 2 周", title: "建立睡眠日志", desc: "记录宝宝睡眠时间和质量，建立昼夜节律。确保安全睡眠环境（仰卧、硬床垫、无松软物品）。" },
        { day: "第 3 周", title: "整理医疗档案", desc: "汇总新生儿筛查报告（PKU、CAH、G6PD等）、听力筛查结果和疫苗接种记录。" },
        { day: "第 4 周", title: "儿科随访确认", desc: "确认所有新生儿筛查异常结果的随访已安排，按时完成满月体检和疫苗接种。" },
      ],
    },
    {
      label: "第 2 个月 — 激活发育",
      theme: "丰富感官刺激，促进早期神经发育",
      tasks: [
        { day: "第 5 周", title: "建立每日亲子互动时间", desc: "每天至少20分钟专注的亲子互动——说话、唱歌、眼神交流、轻柔抚触。" },
        { day: "第 6 周", title: "引入适龄感官刺激", desc: "使用黑白卡、摇铃、触觉玩具等，丰富宝宝的视觉、听觉和触觉体验。" },
        { day: "第 7 周", title: "学习发育里程碑", desc: "了解1-3个月的发育里程碑（抬头、追视、社交微笑），掌握需要关注的红旗信号。" },
        { day: "第 8 周", title: "完成2月龄疫苗接种", desc: "按时接种五联/肺炎等疫苗，记录接种后反应。如宝宝有免疫相关基因变异，提前与医生沟通。" },
      ],
    },
    {
      label: "第 3 个月 — 整合强化",
      theme: "优化照护质量，建立家庭节奏",
      tasks: [
        { day: "第 9 周", title: "环境安全全面检查", desc: "检查家居安全隐患——过敏原、清洁用品存放、水温安全、坠落防护。G6PD缺乏症宝宝特别注意避免樟脑丸等氧化性物质。" },
        { day: "第 10 周", title: "建立规律作息", desc: "逐步建立固定的喂养-清醒-睡眠周期，帮助宝宝建立可预测的日常节奏。" },
        { day: "第 11 周", title: "与专科医生沟通", desc: "整理宝宝发育情况和问题清单，准备下一次专科随访的讨论要点（如涉及特定基因变异，了解最新的管理指南）。" },
        { day: "第 12 周", title: "阶段性回顾与规划", desc: "对比第1个月的记录，评估宝宝发育趋势。设定下个季度的照护目标和关注重点。" },
      ],
    },
  ],
};
