from app.blueprints.tools.utils.openai_client import openai_client


def generate_title_tag(topic: str) -> tuple[str | None, str | None]:
    prompt = f"""
Generate 3 optimized and engaging HTML title tags for the following page/topic:

Topic: {topic}

Each title tag should be under 60 characters, relevant to SEO, and designed to improve click-through rates in search engines.
"""
    try:
        result = openai_client.chat_completion(
            prompt, max_tokens=200, temperature=0.7, top_p=0.9
        )
        return result, None
    except Exception as e:
        return None, str(e)
