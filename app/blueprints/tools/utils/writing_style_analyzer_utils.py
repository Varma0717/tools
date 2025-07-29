from app.blueprints.tools.utils.openai_client import openai_client

def analyze_writing_style(text: str) -> tuple[str | None, str | None]:
    prompt = f"""
Analyze the following text and describe the writing style. Focus on tone, complexity, formality, sentence structure, and vocabulary. 
Then give a short summary of how it might be improved for clarity or impact.

Text:
{text}
"""
    try:
        result = openai_client.chat_completion(
            prompt,
            max_tokens=350,
            temperature=0.6,
            top_p=0.9
        )
        return result, None
    except Exception as e:
        return None, str(e)
