from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
import os
import requests
import json

csrf = CSRFProtect()
faq_schema_generator_bp = Blueprint('faq_schema_generator', __name__, url_prefix='/tools')

OPENROUTER_API_KEYS = [k.strip() for k in os.getenv("OPENROUTER_API_KEYS", "").split(",") if k.strip()]

def generate_faq_schema_via_ai(faq_text):
    try:
        if not OPENROUTER_API_KEYS:
            return None, "No OpenRouter API key configured."
        api_key = OPENROUTER_API_KEYS[0]
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://devsites.lol/",  # Adjust as needed
            "X-Title": "SEO Tools AI"
        }
        prompt = (
            "Convert the following FAQs into valid JSON-LD FAQPage schema markup according to Google guidelines. "
            "Each pair is formatted as Q: ... A: ...\n\n"
            f"{faq_text}\n\n"
            "Output only the JSON-LD code."
        )
        data = {
            "model": "openai/gpt-3.5-turbo",  # or use another valid model as per OpenRouter docs
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 400,
            "temperature": 0.0
        }
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        # Extract schema text
        schema = result['choices'][0]['message']['content'].strip()
        # Optional: prettify if JSON
        try:
            start = schema.find('{')
            end = schema.rfind('}') + 1
            if start > -1 and end > start:
                schema_json = schema[start:end]
                parsed = json.loads(schema_json)
                schema = json.dumps(parsed, indent=2)
        except Exception:
            pass
        return schema, None
    except Exception as e:
        return None, f"Error: {str(e)}"

@faq_schema_generator_bp.route('/faq-schema-generator', methods=['GET'])
def faq_schema_generator():
    csrf_token = generate_csrf()
    return render_template('tools/faq_schema_generator.html', csrf_token=csrf_token)

@faq_schema_generator_bp.route('/faq-schema-generator/ajax', methods=['POST'])
@csrf.exempt
def faq_schema_generator_ajax():
    data = request.get_json()
    faq_text = data.get('faqs', '').strip()
    if not faq_text or "Q:" not in faq_text or "A:" not in faq_text:
        return jsonify({"error": "Please enter at least one Q: ... A: ... pair."}), 400
    schema, error = generate_faq_schema_via_ai(faq_text)
    if schema:
        return jsonify({"schema": schema})
    else:
        return jsonify({"error": error or "Could not generate schema."}), 500
