import os
from openai import OpenAI
import threading


class OpenAIClient:
    def __init__(self):
        # existing initialization code, e.g. loading api_key, client, etc.
        api_keys = os.getenv("OPENROUTER_API_KEYS", "")
        if api_keys:
            self.api_key = api_keys.split(",")[0].strip()
        else:
            self.api_key = "dummy-key"  # fallback
        self.client = OpenAI(
            api_key=self.api_key, base_url="https://openrouter.ai/api/v1"
        )

    def chat_completion(self, prompt, max_tokens=450, temperature=0.7, top_p=0.95):
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://superseotoolkit.com",
                "X-Title": "Super SEO Toolkit",
            },
            model="google/gemma-3n-e4b-it:free",  # or the model you want
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        return response.choices[0].message.content.strip()


# Singleton instance for usage
openai_client = OpenAIClient()
