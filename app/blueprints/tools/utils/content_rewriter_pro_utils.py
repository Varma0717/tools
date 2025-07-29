from app.blueprints.tools.utils.openai_client import openai_client

def rewrite_content_pro(text: str) -> tuple[str | None, str | None]:
    prompt = f"""
Rewrite the following content in a professional, human-like tone. Improve sentence structure, clarity, and flow, while preserving the original meaning. Avoid plagiarism and keep it natural.

Text:
{text}
"""
    try:
        result = openai_client.chat_completion(
            prompt,
            max_tokens=450,
            temperature=0.65,
            top_p=0.9
        )
        return result, None
    except Exception as e:
        return None, str(e)
