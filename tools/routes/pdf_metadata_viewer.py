from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect
import PyPDF2
from werkzeug.utils import secure_filename

csrf = CSRFProtect()

pdf_metadata_viewer_bp = Blueprint('pdf_metadata_viewer', __name__, url_prefix='/tools')

def extract_pdf_metadata(file_storage):
    try:
        reader = PyPDF2.PdfReader(file_storage)
        meta = reader.metadata or {}
        data = {k.replace("/", ""): v for k, v in meta.items()}
        data["Pages"] = len(reader.pages)
        return data
    except Exception as e:
        return {"error": str(e)}

@pdf_metadata_viewer_bp.route('/pdf-metadata-viewer', methods=['GET'])
def pdf_metadata_viewer():
    return render_template('tools/pdf_metadata_viewer.html')

# AJAX POST endpoint for metadata extraction (no CSRF required)
@pdf_metadata_viewer_bp.route('/pdf-metadata-viewer', methods=['POST'])
@csrf.exempt
def pdf_metadata_viewer_api():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    pdf_file = request.files['file']
    if not pdf_file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file type"}), 400
    metadata = extract_pdf_metadata(pdf_file)
    if "error" in metadata:
        return jsonify({"error": metadata["error"]}), 500
    return jsonify({"metadata": metadata})
