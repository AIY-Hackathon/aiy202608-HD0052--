"""
POST /api/ai/chat — DeepSeek AI 问答助手
========================================
代理 DeepSeek API，为基因科普提供 AI 问答。

安全设计：
  - 系统提示词限定为基因科普助手
  - 禁止输出医疗诊断建议
  - 自动附带免责声明
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.schemas import ApiResponse

router = APIRouter(prefix="/api/ai", tags=["ai"])

# 从 .env 加载 DeepSeek 配置
def _load_deepseek_config() -> dict:
    env = {}
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k] = v
    except FileNotFoundError:
        pass
    return {
        "api_key": os.getenv("DEEPSEEK_API_KEY", env.get("DEEPSEEK_API_KEY", "")),
        "api_base": os.getenv("DEEPSEEK_API_BASE", env.get("DEEPSEEK_API_BASE", "https://api.deepseek.com")),
        "model": os.getenv("DEEPSEEK_MODEL", env.get("DEEPSEEK_MODEL", "deepseek-chat")),
    }


# 系统提示词：限定为婴儿基因健康科普助手
SYSTEM_PROMPT = """你是一个专业的婴儿基因健康科普助手，服务于 GenoLife AI 新生儿基因筛查平台。

职责：
- 用通俗易懂的语言帮助家长理解宝宝的基因筛查报告内容
- 解释基因变异、遗传风险、G×E（基因×环境）交互、新生儿筛查等概念
- 帮助家长了解儿科遗传病的早期干预、发育监测和照护策略
- 解释科学术语（如 SNP、致病性变异、VUS、携带者筛查 等）
- 提供循证的育儿科普知识（喂养、睡眠、发育刺激、疫苗接种等）
- 关注家长的心理需求，缓解焦虑，传递科学乐观主义

约束：
- 绝对禁止做出临床诊断或治疗建议
- 禁止使用"您的宝宝患有""确诊""应当用药"等表述
- 使用"提示…风险""建议关注…""建议咨询…医生"等温和措辞
- 强调基因只是宝宝健康的一部分，早期照护和环境因素同样重要
- 强调基因≠命运：许多遗传风险可通过科学照护显著改善
- 每次回答后附加：⚠️ 以上内容仅供学习参考，不构成医疗建议。如有健康疑虑，请咨询儿科或遗传专科医生。

输出格式要求（重要）：
- 使用 Markdown 结构化输出，让内容清晰易读
- 较长的回答用 **加粗** 突出关键词，用列表（-）分点说明
- 需要分步说明时使用数字列表
- 解释名词时用「术语」标注
- 避免大段无结构文字，每段不超过 2-3 行

语言：
- 用户用中文提问则用中文回答，用英文提问则用英文回答。"""


class ChatRequest(BaseModel):
    """AI 问答请求。"""

    message: str = Field(..., min_length=1, max_length=2000, description="用户提问")
    selected_text: str | None = Field(None, max_length=2000, description="用户框选的内容")
    history: list[dict] | None = Field(None, description="对话历史")


@router.post("/chat", response_model=ApiResponse)
def chat(req: ChatRequest):
    """DeepSeek AI 问答助手。"""
    config = _load_deepseek_config()
    if not config["api_key"]:
        return ApiResponse.fail("AI_NOT_CONFIGURED", "AI 助手尚未配置 API Key")

    # 构建消息
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 框选内容作为上下文
    if req.selected_text:
        messages.append({
            "role": "system",
            "content": f"用户选中了以下内容，请优先针对这段内容进行解释：\n「{req.selected_text}」",
        })

    # 对话历史
    if req.history:
        for h in req.history[-6:]:  # 保留最近 6 条
            role = "assistant" if h.get("role") == "assistant" else "user"
            messages.append({"role": role, "content": h.get("content", "")})

    messages.append({"role": "user", "content": req.message})

    # 调用 DeepSeek API
    try:
        import urllib.request

        url = f"{config['api_base']}/chat/completions"
        payload = json.dumps({
            "model": config["model"],
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.7,
        }).encode()

        http_req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['api_key']}",
            },
        )
        with urllib.request.urlopen(http_req, timeout=60) as resp:
            data = json.loads(resp.read().decode())

        answer = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return ApiResponse.ok({
            "answer": answer,
            "usage": usage,
        })
    except Exception as e:
        return ApiResponse.fail("AI_REQUEST_FAILED", f"AI 服务调用失败: {e}")
