import os
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_IMAGE_SIZE = (1200, 1200)
THUMBNAIL_SIZE = (400, 400)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file, subfolder='products'):
    """Save and process uploaded image. Returns relative URL path."""
    if not file or not allowed_file(file.filename):
        return None

    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    safe_filename = secure_filename(filename)

    # Ensure directory exists
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, safe_filename)

    # Process image with Pillow (re-encode to strip metadata)
    img = Image.open(file.stream)
    img = img.convert('RGB')

    # Resize if too large
    img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)
    img.save(filepath, quality=85, optimize=True)

    # Return URL path relative to static
    return f'/static/uploads/{subfolder}/{safe_filename}'


def save_thumbnail(file, subfolder='thumbnails'):
    """Save a thumbnail version of the image."""
    if not file or not allowed_file(file.filename):
        return None

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'{uuid.uuid4().hex}_thumb.{ext}'
    safe_filename = secure_filename(filename)

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, safe_filename)

    img = Image.open(file.stream)
    img = img.convert('RGB')
    img.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
    img.save(filepath, quality=80, optimize=True)

    return f'/static/uploads/{subfolder}/{safe_filename}'


def delete_image(image_url):
    """Delete an image file from disk."""
    if not image_url or not image_url.startswith('/static/uploads/'):
        return False

    filepath = os.path.join(current_app.root_path, image_url.lstrip('/'))
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
