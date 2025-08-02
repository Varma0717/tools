from tools.utils.openai_client import openai_client

def calculate_seo_score(text: str) -> tuple[str | None, str | None]:
    prompt = f"""
Analyze the following content and give it an SEO score between 0 and 100. Consider the following SEO factors:

- Keyword relevance and placement
- Content length and structure (headings, paragraphs)
- Use of meta tags and formatting
- Readability and clarity
- Avoidance of keyword stuffing

Return:
1. A score out of 100
2. A short paragraph explaining what was good and what can be improved

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
