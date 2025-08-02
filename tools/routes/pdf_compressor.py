from flask import Blueprint, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import FileField, SelectField
from flask_wtf.file import FileAllowed, FileRequired
from flask_wtf.csrf import CSRFProtect, generate_csrf
import fitz
import io, os, secrets

csrf = CSRFProtect()

pdf_compressor_bp = Blueprint('pdf_compressor', __name__, url_prefix='/tools')

class PDFCompressorForm(FlaskForm):
    pdf_file = FileField('PDF File', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'PDFs only!')
    ])
    compression_level = SelectField('Compression Level', choices=[
        ('high', 'Maximum'), ('medium', 'Balanced'), ('low', 'Low')
    ], default='medium')

def compress_pdf(file_storage, level="medium"):
    # Adjust parameters based on compression level
    params = {
        "high": dict(deflate=True, garbage=4, clean=True),
        "medium": dict(deflate=True, garbage=2, clean=True),
        "low": dict(deflate=True, garbage=0, clean=True)
    }
    original = fitz.open(stream=file_storage.read(), filetype="pdf")
    buf = io.BytesIO()
    compress_opts = params.get(level, params["medium"])
    original.save(buf, encryption=0, **compress_opts)
    buf.seek(0)
    return buf

@pdf_compressor_bp.route('/pdf-compressor', methods=['GET'])
def pdf_compressor():
    form = PDFCompressorForm()
    csrf_token = generate_csrf()
    return render_template('tools/pdf_compressor.html', form=form, csrf_token=csrf_token)

@pdf_compressor_bp.route('/pdf-compressor/ajax', methods=['POST'])
@csrf.exempt  # Use manual CSRF if you wish
def pdf_compressor_ajax():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded!'}), 400
    file = request.files['pdf_file']
    if not file or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed!'}), 400
    # Server-side max 50 MB check
    file.seek(0, os.SEEK_END)
    original_size = round(file.tell() / 1024, 2)
    if original_size > 50 * 1024:
        return jsonify({'error': 'File is too large! Maximum allowed size is 50 MB.'}), 400
    file.seek(0)
    try:
        compression_level = request.form.get('compression_level', 'medium')
        buf = compress_pdf(file, compression_level)
        compressed_bytes = buf.getbuffer().nbytes
        compressed_size = round(compressed_bytes / 1024, 2)
        filename = secrets.token_hex(8) + ".pdf"
        filepath = os.path.join("static", "uploads", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(buf.read())
        download_url = "/" + filepath
        return jsonify({
            "success": True,
            "compressed_url": download_url,
            "original_size": original_size,
            "compressed_size": compressed_size
        })
    except Exception as e:
        return jsonify({'error': f'Compression failed! ({str(e)})'}), 500

