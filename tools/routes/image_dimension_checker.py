from flask import Blueprint, render_template, request, jsonify
from flask_wtf.csrf import CSRFProtect, validate_csrf, CSRFError, generate_csrf
from wtforms import FileField, SubmitField
from flask_wtf.file import FileAllowed
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
 
from PIL import Image
import io

csrf = CSRFProtect()

image_dimension_checker_bp = Blueprint('image_dimension_checker', __name__, url_prefix='/tools')

class DimensionForm(FlaskForm):
    image = FileField('Upload Image', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff'], 'Images only!')
    ])
    submit = SubmitField('Check Dimensions')

@image_dimension_checker_bp.route('/image-dimension-checker', methods=['GET'])
def image_dimension_checker():
    form = DimensionForm()
    return render_template('tools/image_dimension_checker.html', form=form, csrf_token=generate_csrf())

@image_dimension_checker_bp.route('/image-dimension-checker/ajax', methods=['POST'])
def image_dimension_checker_ajax():
    try:
        validate_csrf(request.headers.get('X-CSRFToken'))
    except Exception as e:
        return jsonify({'success': False, 'error': 'CSRF validation failed.'}), 400

    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image uploaded.'}), 400

    image_file = request.files['image']
    try:
        img = Image.open(image_file)
        dimensions = img.size  # (width, height)
        img_format = img.format
        return jsonify({
            'success': True,
            'dimensions': dimensions,
            'format': img_format
        })
    except Exception as e:
        return jsonify({'success': False, 'error': 'Invalid image file.'}), 400
