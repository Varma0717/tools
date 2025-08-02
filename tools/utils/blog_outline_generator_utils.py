from tools.utils.openai_client import openai_client

def generate_blog_outline(topic: str, desc: str = "") -> tuple[str | None, str | None]:
    prompt = f"""Write a concise and complete blog outline for the following topic:
Topic: {topic}
"""
    if desc.strip():
        prompt += f"Description: {desc.strip()}\n"

    prompt += (
        "Include an introduction, 3-4 key sections with H2/H3 titles, and a conclusion. "
        "Focus on SEO. Provide clear bullet points for each section."
    )
    
    try:
        outline = openai_client.chat_completion(
            prompt,
            max_tokens=300,           # Reduce max tokens for shorter output
            temperature=0.65,         # Lower temperature for less randomness
            top_p=0.9                 # Adjust top_p for better quality
        )
        return outline, None
    except Exception as e:
        return None, str(e)
