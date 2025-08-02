from tools.utils.openai_client import openai_client

def paraphrase_text(text: str) -> tuple[str | None, str | None]:
    prompt = f"""
Paraphrase the following content into a more natural, fluent, and original version. Preserve the meaning but rewrite the sentences and structure using human-like language. Avoid AI-like repetition or generic phrases.

Text:
{text}
"""
    try:
        result = openai_client.chat_completion(
            prompt,
            max_tokens=400,
            temperature=0.7,
            top_p=0.9
        )
        return result, None
    except Exception as e:
        return None, str(e)
