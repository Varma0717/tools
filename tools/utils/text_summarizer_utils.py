from tools.utils.openai_client import openai_client

def summarize_text(text: str) -> tuple[str | None, str | None]:
    prompt = f"""
Summarize the following text in a concise paragraph of 3–5 lines. Focus on the main ideas and key takeaways without losing the original meaning.

Text:
{text}
"""
    try:
        result = openai_client.chat_completion(
            prompt,
            max_tokens=200,
            temperature=0.5,
            top_p=0.9
        )
        return result, None
    except Exception as e:
        return None, str(e)
