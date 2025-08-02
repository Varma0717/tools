from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
import fitz
import io

csrf = CSRFProtect()

pdf_to_text_extractor_bp = Blueprint('pdf_to_text_extractor', __name__, url_prefix='/tools')

@pdf_to_text_extractor_bp.route('/pdf-to-text-extractor', methods=['GET'])
def pdf_to_text_extractor():
    csrf_token = generate_csrf()
    return render_template('tools/pdf_to_text_extractor.html', csrf_token=csrf_token)

@pdf_to_text_extractor_bp.route('/pdf-to-text-extractor/ajax', methods=['POST'])
@csrf.exempt
def pdf_to_text_extractor_ajax():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded!'}), 400
    file = request.files['pdf_file']
    if not file or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed!'}), 400
    # Max file size 50MB
    file.seek(0, 2)
    file_size = file.tell()
    if file_size > 50 * 1024 * 1024:
        return jsonify({'error': 'File too large! Maximum allowed is 50 MB.'}), 400
    file.seek(0)
    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text()
        if not text.strip():
            return jsonify({'error': 'No extractable text found in this PDF.'}), 200
        # (Optional) Limit: first 50000 characters
        text = text[:50000] + ("..." if len(text) > 50000 else "")
        return jsonify({"success": True, "text": text})
    except Exception as e:
        return jsonify({'error': f'Text extraction failed! ({str(e)})'}), 500
