import json
import re
import io
import csv
from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError
from user_agents import parse as parse_ua
from functools import lru_cache

bot_detection_bp = Blueprint('bot_detection', __name__, url_prefix='/tools/bot-detection')

# Load bot regex patterns from embedded JSON (replace with external file for production)
BOT_PATTERNS_JSON = '''
[
  {"pattern": "googlebot", "family": "Googlebot"},
  {"pattern": "bingbot", "family": "Bingbot"},
  {"pattern": "slurp", "family": "Yahoo! Slurp"},
  {"pattern": "duckduckbot", "family": "DuckDuckBot"},
  {"pattern": "baiduspider", "family": "Baiduspider"},
  {"pattern": "yandex", "family": "YandexBot"},
  {"pattern": "sogou", "family": "Sogou"},
  {"pattern": "exabot", "family": "Exabot"},
  {"pattern": "facebot", "family": "Facebook Bot"},
  {"pattern": "ia_archiver", "family": "Alexa Crawler"},
  {"pattern": "twitterbot", "family": "Twitterbot"},
  {"pattern": "linkedinbot", "family": "LinkedInBot"},
  {"pattern": "applebot", "family": "Applebot"},
  {"pattern": "semrushbot", "family": "SEMrushBot"},
  {"pattern": "ahrefsbot", "family": "AhrefsBot"},
  {"pattern": "mj12bot", "family": "Majestic-12"},
  {"pattern": "dotbot", "family": "DotBot"},
  {"pattern": "gigabot", "family": "GigaBot"},
  {"pattern": "seznambot", "family": "SeznamBot"},
  {"pattern": "blexbot", "family": "BLEXBot"}
]
'''
BOT_PATTERNS = json.loads(BOT_PATTERNS_JSON)

# Precompile regex for performance
for bot in BOT_PATTERNS:
    bot['regex'] = re.compile(bot['pattern'], re.I)

@lru_cache(maxsize=5000)
def detect_bot(user_agent):
    ua_lower = user_agent.lower()
    for bot in BOT_PATTERNS:
        if bot['regex'].search(ua_lower):
            return True, bot['family']
    return False, None

@bot_detection_bp.route('/')
def bot_detection():
    return render_template('tools/bot_detection.html')

@bot_detection_bp.route('/ajax', methods=['POST'])
def bot_detection_ajax():
    try:
        csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    # Support both single UA string or uploaded CSV with many UAs
    if 'logfile' in request.files:
        logfile = request.files['logfile']
        if logfile.filename == '':
            return jsonify({"error": "Empty file uploaded"}), 400
        try:
            stream = io.StringIO(logfile.stream.read().decode("utf-8", errors="ignore"))
            reader = csv.reader(stream)

            results = []
            for row in reader:
                if not row:
                    continue
                ua = row[0].strip()
                if not ua:
                    continue
                is_bot, family = detect_bot(ua)
                results.append({
                    "user_agent": ua,
                    "is_bot": is_bot,
                    "bot_family": family if is_bot else "N/A"
                })
            return jsonify({"results": results})
        except Exception as e:
            return jsonify({"error": f"Failed to parse file: {str(e)}"}), 500

    # Single UA string input
    data = request.get_json() or {}
    ua_string = data.get('user_agent', '').strip()
    if not ua_string:
        return jsonify({"error": "User-Agent string is required."}), 400

    is_bot, family = detect_bot(ua_string)

    return jsonify({
        "user_agent": ua_string,
        "is_bot": is_bot,
        "bot_family": family if is_bot else "N/A",
        "message": "Likely a bot" if is_bot else "Likely NOT a bot"
    })
