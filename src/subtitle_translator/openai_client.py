import openai
from openai import OpenAI
from .logger import log
from .config import ConfigManager

current_ai = ConfigManager().get('settings', 'currentAI')
api_key = ConfigManager().get(current_ai,"api_key")
base_url = ConfigManager().get(current_ai,"base_url")

def call_openai_chat_completion(messages, model, max_tokens=8192, temperature=0.3):
    retry_count = 0

    client = OpenAI(
        api_key = api_key,
        base_url = base_url
    )

    while retry_count < 3:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except openai.OpenAIError as e:
            retry_count += 1
            log(e)
            log("请求超时或API错误，正在进行第", retry_count)
    raise ValueError("请求重试多次后仍然失败，可能存在错误。")
