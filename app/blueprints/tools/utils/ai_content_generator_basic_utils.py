from app.blueprints.tools.utils.openai_client import openai_client

def generate_ai_content(topic: str, desc: str = "") -> tuple[str | None, str | None]:
    prompt = f"""Write a detailed, original blog-style content piece for the topic below.

Topic: {topic}
"""
    if desc.strip():
        prompt += f"Description: {desc.strip()}\n"

    prompt += (
        "Include a clear introduction, 2–3 informative paragraphs, and a closing sentence. "
        "Keep the tone natural, friendly, and SEO-friendly. Avoid technical jargon unless necessary."
    )

    try:
        result = openai_client.chat_completion(
            prompt,
            max_tokens=450,
            temperature=0.7,
            top_p=0.9
        )
        return result, None
    except Exception as e:
        return None, str(e)
