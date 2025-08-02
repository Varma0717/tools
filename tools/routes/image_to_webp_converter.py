from flask import Blueprint, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
from flask_wtf.csrf import CSRFProtect
from PIL import Image
import io
import os
import secrets

csrf = CSRFProtect()

image_to_webp_converter_bp = Blueprint('image_to_webp_converter', __name__, url_prefix='/tools')

class WebPForm(FlaskForm):
    image = FileField('Upload Image', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'bmp', 'tiff'], 'Images only!')])
    submit = SubmitField('Convert to WebP')

def convert_to_webp(file_storage):
    img = Image.open(file_storage)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=85)
    buf.seek(0)
    return buf

@image_to_webp_converter_bp.route('/image-to-webp-converter', methods=['GET', 'POST'])
def image_to_webp_converter():
    form = WebPForm()
    webp_img_url = None
    filedata = None
    if form.validate_on_submit():
        image_file = form.image.data
        if image_file:
            buf = convert_to_webp(image_file)
            filename = secrets.token_hex(8) + ".webp"
            filepath = os.path.join("static", "uploads", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(buf.read())
            webp_img_url = "/" + filepath
            filedata = filename
        else:
            flash("No image uploaded!", "danger")
    return render_template('tools/image_to_webp_converter.html', form=form, webp_img_url=webp_img_url, filedata=filedata)
