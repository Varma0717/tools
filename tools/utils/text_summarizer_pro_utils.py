from tools.utils.openai_client import openai_client

def summarize_text_pro(text: str) -> tuple[str | None, str | None]:
    prompt = f"""
You are a professional summarizer. Summarize the following text in a clear and concise paragraph. Focus on the key ideas and avoid repetition. Do not add extra opinions.

Text:
{text}
"""
    try:
        result = openai_client.chat_completion(
            prompt,
            max_tokens=300,
            temperature=0.6,
            top_p=0.9
        )
        return result, None
    except Exception as e:
        return None, str(e)
