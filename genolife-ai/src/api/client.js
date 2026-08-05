/**
 * GenoLife AI — API 客户端
 * =========================
 * 封装后端 API 调用，对齐 backend API 契约。
 *
 * 使用方式：
 *   1. 默认连接 http://localhost:8000
 *   2. 通过环境变量 VITE_API_BASE 覆盖
 *   3. 启动时自动检测后端可达性，不可达则降级 mock
 *   4. 设置 VITE_USE_MOCK=true 可强制使用 mock
 */
import {
  userProfile,
  healthSummary,
  geneCards,
  riskDimensions,
  geneticProfile,
  riskSummaryCards,
  simulationDefaults,
  simulationFactors,
  thirtyDayPlan,
  calculateHealthScore,
  calculateRiskDimensions,
  generateTrendData,
  generateRecommendations,
} from "../data/mockData";

// API 地址（Vite 环境变量）
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

// 是否强制使用 mock（VITE_USE_MOCK=true 时强制）
const FORCE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

// 后端可用状态（缓存 30 秒，避免页面刷新后永久锁定为 false）
let _backendAvailable = null;
let _lastCheckTime = 0;
const CACHE_TTL = 30_000; // 30 秒

/**
 * 检测后端是否可达。
 * 结果缓存 30 秒后重新检测。
 */
export async function isBackendAvailable() {
  if (FORCE_MOCK) return false;
  const now = Date.now();
  if (_backendAvailable !== null && now - _lastCheckTime < CACHE_TTL) return _backendAvailable;

  try {
    const resp = await fetch(`${API_BASE}/health`, {
      signal: AbortSignal.timeout(3000),
    });
    if (resp.ok) {
      const body = await resp.json();
      _backendAvailable = body.status === "ok";
    } else {
      _backendAvailable = false;
    }
  } catch {
    _backendAvailable = false;
  }

  _lastCheckTime = now;
  if (!_backendAvailable) {
    console.warn("[GenoLife] 后端不可达，使用本地 mock 数据");
  } else {
    console.log("[GenoLife] 后端已连接:", API_BASE);
  }
  return _backendAvailable;
}

/**
 * 检查是否应该使用 mock（后端不可达时自动降级）。
 */
async function shouldUseMock() {
  if (FORCE_MOCK) return true;
  return !(await isBackendAvailable());
}

/**
 * 统一请求封装
 * - 解析统一响应格式 {success, data, error}
 * - 非成功时抛错
 */
async function request(path, options = {}) {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    const detail = body.detail || body.error?.message || resp.statusText;
    throw new Error(detail);
  }

  const body = await resp.json();
  if (!body.success) {
    throw new Error(body.error?.message || "请求失败");
  }
  return body.data;
}

// ============ GET /api/profile — 基因分析档案 ============

export async function getProfile() {
  if (await shouldUseMock()) {
    await delay(300);
    return {
      user: userProfile,
      summary: healthSummary,
      geneCards,
      riskDimensions,
    };
  }
  return request("/profile");
}

// ============ GET /api/analysis/{report_id} — 分析结果 ============

export async function getAnalysis(reportId, options = {}) {
  const { population } = options;
  if (await shouldUseMock()) {
    await delay(300);
    return {
      report: {
        id: reportId,
        filename: "example.vcf",
        format: "vcf",
        status: "completed",
        variant_count: geneCards.length,
      },
      variants: geneCards.map((g, i) => ({
        id: `var_${i}`,
        chromosome: "7",
        position: 117149150 + i * 1000,
        reference: "A",
        alternative: "G",
        rs_id: `rs${100000 + i}`,
        gene_name: g.symbol,
        clinvar_significance:
          g.riskLevel === "elevated"
            ? "Pathogenic"
            : g.riskLevel === "moderate"
              ? "Uncertain_significance"
              : "Benign",
        risk_score: g.riskLevel === "elevated" ? 0.87 : 0.3,
      })),
      risk_scores: { alzheimer: 1.5, metabolic: 1.2 },
      overall_risk_level: "moderate",
      profile: {
        geneCards,
        riskDimensions,
        summary: { score: 72, level: "moderate", levelLabel: "中等遗传风险" },
      },
      ancestry: null,
    };
  }
  const params = population ? `?population=${encodeURIComponent(population)}` : "";
  return request(`/analysis/${reportId}${params}`);
}

// ============ POST /api/upload — 上传 VCF ============

export async function uploadReport(file) {
  if (await shouldUseMock()) {
    await delay(800);
    return {
      report_id: `rpt_${Date.now()}`,
      variant_count: geneCards.length,
      status: "completed",
      original_filename: file?.name || "example.vcf",
    };
  }

  const form = new FormData();
  form.append("file", file);
  const resp = await fetch(`${API_BASE}/upload`, { method: "POST", body: form });
  const body = await resp.json();
  if (!body.success) throw new Error(body.error?.message || "上传失败");
  return body.data;
}

// ============ POST /api/simulate — 生活方式模拟 ============

export async function simulate(factors, reportId = null) {
  if (await shouldUseMock()) {
    await delay(200);
    const optimizedFactors = { nutrition_type: 8, sleep_quality: 9, development_stimulation: 8, medical_adherence: 10, environmental_safety: 9 };
    return {
      healthScore: calculateHealthScore(factors),
      optimizedScore: calculateHealthScore(optimizedFactors),
      riskDimensions: calculateRiskDimensions(factors),
      trendData: generateTrendData(factors),
      recommendations: generateRecommendations(factors),
    };
  }
  const body = { factors };
  if (reportId) body.report_id = reportId;
  return request("/simulate", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// ============ GET /api/recommendations — 建议 + 30 天计划 ============

export async function getRecommendations(factors = {}) {
  if (await shouldUseMock()) {
    await delay(200);
    return {
      recommendations: generateRecommendations(factors),
      thirtyDayPlan,
    };
  }
  const params = new URLSearchParams(
    Object.entries(factors).map(([k, v]) => [k, String(v)])
  );
  return request(`/recommendations?${params.toString()}`);
}

// ============ GET /api/report/{id}/export — 报告导出 ============

export async function exportReport(reportId, options = {}) {
  const { format = "html" } = options;

  if (await shouldUseMock()) {
    await delay(800);
    if (format === "pdf") {
      // Mock 模式：生成纯文本说明文件供下载
      const textContent = `GenoLife AI — 基因健康报告（演示模式）

⚠️ PDF 导出需要后端 WeasyPrint 或 reportlab 支持。
请在终端运行：pip install reportlab
然后重新启动后端服务（python -m backend.main），再次尝试导出。

或者使用 Markdown 格式导出（无需后端 PDF 依赖），在本地用浏览器/Word 打开。`;
      return {
        format: "pdf",
        data: new Blob([textContent], { type: "text/plain;charset=utf-8" }),
        filename: `genolife-report-${reportId || "demo"}.txt`,
      };
    }
    // Mock HTML：生成包含基本信息的演示报告
    const mockHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GenoLife AI — 基因健康报告（演示）</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; line-height: 1.8; color: #1a1a2e; max-width: 800px; margin: 0 auto; padding: 40px 24px; }
  .cover { background: linear-gradient(170deg, #060A12 0%, #0C1525 50%, #111D30 100%); color: white; padding: 60px 40px; text-align: center; border-radius: 20px; margin-bottom: 40px; }
  .cover h1 { font-size: 28px; margin-bottom: 12px; }
  .cover h1 span { color: #7EB8AE; }
  .cover p { color: rgba(255,255,255,0.5); font-size: 14px; }
  .cover .score { font-size: 64px; font-weight: 800; color: #d97706; margin: 24px 0 8px; }
  .section { margin-bottom: 36px; }
  .section h2 { font-size: 20px; border-bottom: 2px solid #0d9488; padding-bottom: 8px; margin-bottom: 16px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #e5e7eb; padding: 10px 14px; text-align: left; font-size: 14px; }
  th { background: #f8fafc; font-weight: 600; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 700; }
  .badge-benign { background: #d1fae5; color: #059669; }
  .card { background: #f8fafc; border-radius: 14px; padding: 18px; margin-bottom: 10px; border-left: 4px solid #0d9488; }
  .card h3 { font-size: 16px; margin-bottom: 4px; }
  .card .meta { font-size: 12px; color: #6b7280; }
  .footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; font-size: 12px; color: #9ca3af; }
  .watermark { position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%) rotate(-25deg); font-size: 60px; color: rgba(0,0,0,0.03); pointer-events: none; white-space: nowrap; }
</style>
</head>
<body>
<div class="watermark">DEMO REPORT</div>

<div class="cover">
  <p style="font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:rgba(255,255,255,0.35);margin-bottom:48px;">GenoLife AI</p>
  <h1>Personal <span>Genetic Health</span><br>Report</h1>
  <p>AI 驱动的基因分析 — 了解遗传特质，做出明智健康决策</p>
  <div class="score">72<span style="font-size:18px;color:rgba(255,255,255,0.4);">/100</span></div>
  <p style="font-size:12px;color:rgba(255,255,255,0.3);">演示报告 · ${new Date().toISOString().slice(0, 10)}</p>
</div>

<div class="section">
  <h2>一、检测概览</h2>
  <table>
    <tr><th>项目</th><th>结果</th></tr>
    <tr><td>综合健康评分</td><td>72 / 100</td></tr>
    <tr><td>风险等级</td><td>中等关注 (Moderate)</td></tr>
    <tr><td>致病性变异</td><td>0 个</td></tr>
    <tr><td>意义不明确变异 (VUS)</td><td>2 个</td></tr>
    <tr><td>良性/可能良性变异</td><td>7 个</td></tr>
  </table>
  <p style="margin-top:12px;font-size:13px;color:#6b7280;font-style:italic;">
    ⚠️ 当前为演示模式。请启动后端服务并上传真实 VCF 文件以获取个性化报告。
  </p>
</div>

<div class="section">
  <h2>二、关键基因分析</h2>
  <div class="card">
    <h3>🧬 PAH — 苯丙氨酸羟化酶</h3>
    <p class="meta">代谢与内分泌 · 风险等级：<span class="badge badge-benign">低风险</span></p>
    <p style="font-size:13px;color:#4b5563;margin-top:8px;">该基因未发现显著风险变异，遗传影响较低。涉及苯丙氨酸代谢，与苯丙酮尿症(PKU)相关。</p>
  </div>
  <div class="card">
    <h3>🧠 SMN1 — 运动神经元存活蛋白1</h3>
    <p class="meta">神经发育 · 风险等级：<span style="display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:700;background:#fef3c7;color:#d97706;">中等关注</span></p>
    <p style="font-size:13px;color:#4b5563;margin-top:8px;">该基因存在中等程度的遗传影响，属于常见人群范围。与脊髓性肌萎缩症(SMA)相关。</p>
  </div>
  <div class="card">
    <h3>🩸 G6PD — 葡萄糖-6-磷酸脱氢酶</h3>
    <p class="meta">心血管与血液 · 风险等级：<span class="badge badge-benign">低风险</span></p>
    <p style="font-size:13px;color:#4b5563;margin-top:8px;">该基因未发现显著风险变异，遗传影响较低。与G6PD缺乏症（蚕豆病）相关。</p>
  </div>
</div>

<div class="section">
  <h2>三、健康维度评分</h2>
  <table>
    <tr><th>维度</th><th>评分</th><th>解读</th></tr>
    <tr><td>代谢与内分泌</td><td>45 / 100</td><td>✅ 相对良好</td></tr>
    <tr><td>心血管与血液</td><td>52 / 100</td><td>• 中等关注</td></tr>
    <tr><td>神经发育</td><td>68 / 100</td><td>• 中等关注</td></tr>
    <tr><td>免疫与感染</td><td>48 / 100</td><td>✅ 相对良好</td></tr>
    <tr><td>感官与结构</td><td>55 / 100</td><td>• 中等关注</td></tr>
  </table>
</div>

<div class="section">
  <h2>四、个性化照护建议</h2>
  <ol style="padding-left:20px;">
    <li style="margin-bottom:10px;"><strong>均衡营养</strong> — 根据宝宝月龄提供多样化的辅食，确保蛋白质、维生素和矿物质的充分摄入。</li>
    <li style="margin-bottom:10px;"><strong>优质睡眠</strong> — 建立规律的睡眠作息，新生儿每天保证14-17小时睡眠。</li>
    <li style="margin-bottom:10px;"><strong>早期发育刺激</strong> — 通过亲子互动、适龄玩具和语言交流促进宝宝认知和运动发育。</li>
    <li style="margin-bottom:10px;"><strong>定期儿科随访</strong> — 按照儿科医生建议定期进行生长发育评估。</li>
    <li style="margin-bottom:10px;"><strong>新生儿疾病筛查</strong> — 确保完成国家规定的新生儿疾病筛查项目。</li>
  </ol>
</div>

<div class="section">
  <h2>五、家长须知</h2>
  <ol style="padding-left:20px;">
    <li style="margin-bottom:8px;"><strong>基因不是命运</strong>：基因检测结果反映的是"倾向"和"风险"，而非确定性的命运。</li>
    <li style="margin-bottom:8px;"><strong>G×E 交互</strong>：基因（Gene）× 环境（Environment）交互是当代医学的核心认知。</li>
    <li style="margin-bottom:8px;"><strong>定期随访</strong>：请按照儿科医生的建议进行定期生长发育评估。</li>
    <li style="margin-bottom:8px;"><strong>新生儿筛查</strong>：本报告不能替代国家规定的新生儿疾病筛查。</li>
  </ol>
</div>

<div class="footer">
  <p><strong>GenoLife AI</strong> · Personal Genetic Health Report</p>
  <p>演示模式生成 · 教育科研工具，不属于医疗器械</p>
  <p>本报告不构成临床诊断或医疗建议</p>
</div>
</body>
</html>`;
    return {
      format: "html",
      data: mockHtml,
      filename: `genolife-report-${reportId || "demo"}.html`,
    };
  }

  // HTML：直接获取文本
  if (format === "html") {
    const resp = await fetch(`${API_BASE}/report/${reportId}/export?format=html`);
    if (!resp.ok) {
      const body = await resp.json().catch(() => ({}));
      throw new Error(body.detail || "报告生成失败");
    }
    const html = await resp.text();
    return {
      format: "html",
      data: html,
      filename: `genolife-report-${reportId}.html`,
    };
  }

  // PDF：获取二进制流
  const resp = await fetch(`${API_BASE}/report/${reportId}/export?format=pdf`);
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.detail || "PDF 生成失败");
  }
  const blob = await resp.blob();
  return {
    format: "pdf",
    data: blob,
    filename: `genolife-report-${reportId}.pdf`,
  };
}

// ============ GET /api/report/{id}/text — 文字报告（Markdown）============

export async function exportTextReport(reportId) {
  if (await shouldUseMock() || !reportId) {
    await delay(500);
    const mockMd = `# 🧬 GenoLife AI — 基因风险评估报告（演示）

**报告编号**：\`demo-${reportId || "001"}\`
**生成时间**：${new Date().toISOString().slice(0, 10)}

---

> ⚠️ **重要免责声明**：本报告为教育科研用途，不构成临床诊断。

---

## 一、检测概览

| 项目 | 结果 |
|------|------|
| **综合健康评分** | 72 / 100 |
| **风险等级** | 中等关注 (Moderate) |
| **致病性变异** | 0 个 |
| **意义不明确变异 (VUS)** | 2 个 |
| **良性/可能良性变异** | 7 个 |

> 当前为演示模式。请启动后端服务并上传真实 VCF 文件以获取个性化报告。

---

## 二、家长须知

1. **基因不是命运**：基因检测结果反映的是"倾向"和"风险"，而非确定性的命运。
2. **G×E 交互**：基因（Gene）× 环境（Environment）交互是当代医学的核心认知。
3. **定期随访**：请按照儿科医生的建议进行定期生长发育评估和必要的专科随访。
4. **新生儿筛查**：本报告不能替代国家规定的新生儿疾病筛查。

---

*本报告由 GenoLife AI 演示模式生成*
*GenoLife AI 是面向非医疗消费者的新生儿基因风险科普平台，不属于医疗器械。*
`;
    return {
      format: "text",
      data: mockMd,
      filename: `genolife-report-${reportId || "demo"}.md`,
    };
  }

  const resp = await fetch(`${API_BASE}/report/${reportId}/text`);
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new Error(body.detail || "文字报告生成失败");
  }
  const md = await resp.text();
  return {
    format: "text",
    data: md,
    filename: `genolife-report-${reportId}.md`,
  };
}

// ============ 工具 ============

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default {
  API_BASE,
  isBackendAvailable,
  getProfile,
  getAnalysis,
  uploadReport,
  simulate,
  getRecommendations,
  exportReport,
  exportTextReport,
};
