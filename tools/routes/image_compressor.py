from flask import Blueprint, render_template, request, flash, send_file
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

image_compressor_bp = Blueprint('image_compressor', __name__, url_prefix='/tools')

class ImageCompressorForm(FlaskForm):
    image = FileField('Upload Image', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff'], 'Images only!')])
    submit = SubmitField('Compress Image')

def compress_image(file_storage, quality=75):
    img = Image.open(file_storage)
    img_format = img.format or "JPEG"
    # Always convert PNGs to RGB for JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", optimize=True, quality=quality)
    buf.seek(0)
    return buf

@image_compressor_bp.route('/image-compressor', methods=['GET', 'POST'])
def image_compressor():
    form = ImageCompressorForm()
    compressed_img_url = None
    filedata = None
    if form.validate_on_submit():
        image_file = form.image.data
        if image_file:
            buf = compress_image(image_file)
            filename = secrets.token_hex(8) + ".jpg"
            filepath = os.path.join("static", "uploads", filename)
            # Ensure the uploads directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(buf.read())
            compressed_img_url = "/" + filepath
            filedata = filename
        else:
            flash("No image uploaded!", "danger")
    return render_template('tools/image_compressor.html', form=form, compressed_img_url=compressed_img_url, filedata=filedata)
