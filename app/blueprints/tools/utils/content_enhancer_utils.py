from app.blueprints.tools.utils.openai_client import openai_client

def enhance_content(text: str) -> tuple[str | None, str | None]:
    prompt = f"""
Enhance the following content to make it more engaging, persuasive, and professional without changing the original meaning. Improve tone, clarity, vocabulary, and sentence structure.

Text:
{text}
"""
    try:
        result = openai_client.chat_completion(
            prompt,
            max_tokens=400,
            temperature=0.7,
            top_p=0.95
        )
        return result, None
    except Exception as e:
        return None, str(e)
