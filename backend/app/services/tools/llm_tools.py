import openai
from app.config.settings import settings

openai.api_key = settings.HF_API_KEY

def summarize_text(text: str):
    prompt = f"請用中文摘要以下文字：\n{text}"
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "你是一位摘要助手"}, {"role": "user", "content": prompt}]
    )
    return res.choices[0].message["content"]
