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

// 后端可用状态（启动时检测）
let _backendAvailable = null;

/**
 * 检测后端是否可达。
 * 结果缓存，整个生命周期只检测一次。
 */
export async function isBackendAvailable() {
  if (FORCE_MOCK) return false;
  if (_backendAvailable !== null) return _backendAvailable;

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

export async function getAnalysis(reportId) {
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
      },
    };
  }
  return request(`/analysis/${reportId}`);
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

export async function simulate(factors) {
  if (await shouldUseMock()) {
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
};
