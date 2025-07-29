from app.blueprints.tools.utils.openai_client import openai_client

def generate_auto_titles(keyword: str) -> tuple[str | None, str | None]:
    prompt = f"""
Generate 5 creative and SEO-optimized titles for the following topic or keyword:

Keyword: {keyword}

Keep each title under 70 characters. Make them catchy, clear, and relevant for digital content. No Explaination Needed, Only Titles.
"""
    try:
        result = openai_client.chat_completion(
            prompt,
            max_tokens=200,
            temperature=0.75,
            top_p=0.9
        )
        return result, None
    except Exception as e:
        return None, str(e)
