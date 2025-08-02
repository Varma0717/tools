import io
import csv
from collections import defaultdict, Counter
from flask import Blueprint, request, jsonify, render_template
from flask_wtf.csrf import validate_csrf, CSRFError

conversion_funnel_tracker_bp = Blueprint('conversion_funnel_tracker', __name__, url_prefix='/tools/conversion-funnel-tracker')

@conversion_funnel_tracker_bp.route('/')
def conversion_funnel_tracker():
    return render_template('tools/conversion_funnel_tracker.html')

@conversion_funnel_tracker_bp.route('/ajax', methods=['POST'])
def conversion_funnel_tracker_ajax():
    try:
        csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
        validate_csrf(csrf_token)
    except CSRFError:
        return jsonify({"error": "Invalid CSRF token"}), 400

    if 'logfile' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    logfile = request.files['logfile']
    if logfile.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        stream = io.StringIO(logfile.stream.read().decode("utf-8", errors="ignore"))
        reader = csv.DictReader(stream)

        # Expected CSV columns: user_id, funnel_step
        # e.g. user_id, funnel_step
        # 123, visit
        # 123, signup
        # 456, visit
        # 456, signup
        # 456, purchase

        user_steps = defaultdict(set)
        funnel_order = ['visit', 'signup', 'purchase']

        for row in reader:
            user = row.get('user_id') or row.get('UserID') or ''
            step = row.get('funnel_step') or row.get('step') or ''
            if not user or not step:
                continue
            user_steps[user].add(step.lower())

        # Count users at each funnel step (considering sequential funnel)
        funnel_counts = Counter()
        for steps in user_steps.values():
            for step in funnel_order:
                if step in steps:
                    funnel_counts[step] += 1
                else:
                    break  # user did not complete this step, stop counting further steps

        # Calculate drop-offs between steps
        drop_offs = {}
        for i in range(len(funnel_order) - 1):
            step_current = funnel_order[i]
            step_next = funnel_order[i + 1]
            count_current = funnel_counts.get(step_current, 0)
            count_next = funnel_counts.get(step_next, 0)
            if count_current > 0:
                drop_offs[f"{step_current}_to_{step_next}"] = round((count_current - count_next) / count_current * 100, 2)
            else:
                drop_offs[f"{step_current}_to_{step_next}"] = None

        return jsonify({
            "funnel_order": funnel_order,
            "funnel_counts": funnel_counts,
            "drop_offs": drop_offs,
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
