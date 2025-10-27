import openai
from loguru import logger
from app.config.settings import settings

openai.api_key = settings.HF_API_KEY  # 可改為 openai key

class BaseAgent:
    """所有 AI Agent 的共同基底類別。"""
    name = "BaseAgent"
    description = "抽象代理人基底類別"
    tools = {}

    def __init__(self):
        pass

    async def ask_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.4):
        """
        使用該 Agent 專屬的 LLM 生成回答。
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=500
            )
            return response.choices[0].message["content"]
        except Exception as e:
            logger.error(f"[{self.name}] LLM 回答失敗: {e}")
            return f"⚠️ 無法生成 {self.name} 回覆：{e}"

    async def run_tool(self, tool_name: str, *args, **kwargs):
        """
        執行 Agent 註冊的工具。
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return f"⚠️ {self.name} 無此工具：{tool_name}"
        try:
            return tool(*args, **kwargs)
        except Exception as e:
            logger.error(f"[{self.name}] 工具 {tool_name} 執行失敗：{e}")
            return f"⚠️ 工具執行錯誤：{e}"

    async def run(self, query: str):
        """
        每個 Agent 都要實作自己的 run() 方法。
        """
        raise NotImplementedError
