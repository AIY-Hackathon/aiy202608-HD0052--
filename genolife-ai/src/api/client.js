/**
 * GenoLife AI — API 客户端
 * =========================
 * 封装后端 API 调用，对齐 docs/api_contract.md 契约。
 *
 * 使用方式：
 *   1. 默认连接 http://localhost:8000
 *   2. 通过环境变量 VITE_API_BASE 覆盖
 *   3. USE_MOCK = true 时使用本地 mockData（开发无后端也可运行）
 */
import {
  userProfile,
  healthSummary,
  geneCards,
  riskDimensions,
  calculateHealthScore,
  calculateRiskDimensions,
  generateTrendData,
  generateRecommendations,
  thirtyDayPlan,
} from "../data/mockData";

// API 地址（Vite 环境变量）
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

// 开发阶段使用 mock 数据；后端就绪后改为 false
export const USE_MOCK = true;

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
  if (USE_MOCK) {
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

export async function getAnalysis(reportId) {
  if (USE_MOCK) {
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
      },
    };
  }
  return request(`/analysis/${reportId}`);
}

// ============ POST /api/upload — 上传 VCF ============

export async function uploadReport(file) {
  if (USE_MOCK) {
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

export async function simulate(factors) {
  if (USE_MOCK) {
    await delay(200);
    const optimizedFactors = { sleep: 8, exercise: 5, diet: 8, stress: 3 };
    return {
      healthScore: calculateHealthScore(factors),
      optimizedScore: calculateHealthScore(optimizedFactors),
      riskDimensions: calculateRiskDimensions(factors),
      trendData: generateTrendData(factors),
      recommendations: generateRecommendations(factors),
    };
  }
  return request("/simulate", {
    method: "POST",
    body: JSON.stringify({ factors }),
  });
}

// ============ GET /api/recommendations — 建议 + 30 天计划 ============

export async function getRecommendations(factors = {}) {
  if (USE_MOCK) {
    await delay(200);
    const params = new URLSearchParams(
      Object.entries(factors).map(([k, v]) => [k, String(v)])
    );
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

// ============ 工具 ============

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default {
  API_BASE,
  getProfile,
  getAnalysis,
  uploadReport,
  simulate,
  getRecommendations,
};
