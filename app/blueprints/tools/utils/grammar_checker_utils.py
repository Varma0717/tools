from app.blueprints.tools.utils.openai_client import openai_client

def check_grammar(text: str) -> tuple[str | None, str | None]:
    prompt = f"""
Check the following text for grammatical mistakes, punctuation errors, and awkward phrasing.
Return a corrected version and a short summary of changes or suggestions if applicable.

Text:
{text}
"""
    try:
        result = openai_client.chat_completion(
            prompt,
            max_tokens=400,
            temperature=0.6,
            top_p=0.9
        )
        return result, None
    except Exception as e:
        return None, str(e)
