from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
import os
import requests
import sys

csrf = CSRFProtect()
meta_description_generator_bp = Blueprint('meta_description_generator', __name__, url_prefix='/tools')

# Unicode-safe print for cPanel and weird servers
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding or 'utf-8'
    if enc.upper().startswith('UTF'):
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='replace').decode(enc)
        print(*(f(obj) for obj in objects), sep=sep, end=end, file=file)

OPENROUTER_API_KEYS = [k.strip() for k in os.getenv("OPENROUTER_API_KEYS", "").split(",") if k.strip()]

def generate_meta_description(text):
    try:
        if not OPENROUTER_API_KEYS:
            return None, "No OpenRouter API keys set."
        api_key = OPENROUTER_API_KEYS[0]  # Only first key. Use random.choice(...) for rotation.
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://devsites.lol/",  # Optional but recommended
            "X-Title": "SEO Tools AI"
        }
        data = {
            "model": "openai/gpt-3.5-turbo",  # TRY "openrouter/gpt-3.5-turbo" or other model if you get model errors
            "messages": [
                {"role": "user", "content": (
                    "Write a concise, compelling SEO meta description (155-160 characters) "
                    "for the following content or topic:\n\n" + text
                )}
            ],
            "max_tokens": 80,
            "temperature": 0.7
        }
        uprint("DEBUG payload:", data)
        response = requests.post(url, headers=headers, json=data, timeout=30)
        uprint("DEBUG status:", response.status_code)
        uprint("DEBUG response text:", response.text)
        if response.status_code != 200:
            # Return the error as-is for frontend display
            try:
                api_err = response.json()
                err_msg = api_err.get("error", api_err)
                return None, f"OpenRouter error: {err_msg}"
            except Exception:
                return None, f"OpenRouter error: {response.text}"
        result = response.json()
        meta = result['choices'][0]['message']['content'].strip()
        if len(meta) > 160:
            meta = meta[:157].rstrip('.') + "..."
        return meta, None
    except Exception as e:
        uprint("ERROR in generate_meta_description:", repr(e))
        return None, str(e)

@meta_description_generator_bp.route('/meta-description-generator', methods=['GET'])
def meta_description_generator():
    csrf_token = generate_csrf()
    return render_template('tools/meta_description_generator.html', csrf_token=csrf_token)

@meta_description_generator_bp.route('/meta-description-generator/ajax', methods=['POST'])
@csrf.exempt
def meta_description_generator_ajax():
    data = request.get_json()
    text = data.get('content', '').strip()
    if not text or len(text) < 10:
        return jsonify({"error": "Please enter enough content or topic."}), 400
    meta, error = generate_meta_description(text)
    if meta:
        return jsonify({"meta": meta})
    else:
        return jsonify({"error": f"{error}"}), 500
