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


# 系统提示词：限定基因科普助手
SYSTEM_PROMPT = """你是一个专业的基因健康科普助手，服务 GenoLife AI 平台。

职责：
- 用通俗易懂的语言解释基因、变异、遗传风险、生活方式交互等概念
- 帮助用户理解他们的基因报告内容
- 解释科学术语（如 SNP、单倍型、PRS、GxE 交互等）

约束：
- 绝对禁止做出临床诊断或治疗建议
- 禁止使用"您患有""确诊""应当服药"等表述
- 强调基因只是健康的一部分，生活方式和环境同样重要
- 每次回答后附加：⚠️ 以上内容仅供学习参考，不构成医疗建议。

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
