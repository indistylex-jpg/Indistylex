import os
import uuid
from PIL import Image
from flask import current_app, url_for
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
MAX_IMAGE_SIZE = (1200, 1200)
THUMBNAIL_SIZE = (400, 400)

# Magic bytes for allowed image types
MAGIC_BYTES = {
    b'\xff\xd8\xff': 'jpeg',
    b'\x89PNG\r\n\x1a\n': 'png',
    b'RIFF': 'webp',  # WebP starts with RIFF
}


def _validate_magic_bytes(file_stream):
    """Validate file content matches an allowed image type by checking magic bytes."""
    header = file_stream.read(12)
    file_stream.seek(0)
    for magic, fmt in MAGIC_BYTES.items():
        if header.startswith(magic):
            return True
    # WebP has RIFF at start and WEBP at byte 8
    if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return True
    return False


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _prepare_image_for_save(img):
    """Convert image to RGB, preserving transparency on a white background."""
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        rgba = img.convert('RGBA')
        background = Image.new('RGB', rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.split()[-1])
        return background
    return img.convert('RGB')


def normalize_stored_image_path(path):
    """Normalize DB-stored image path to a static URL path."""
    if not path:
        return None
    path = path.strip()
    if path.startswith(('http://', 'https://')):
        return path
    if path.startswith('/static/'):
        return path
    if path.startswith('static/'):
        return f'/{path}'
    return f'/static/uploads/{path.lstrip("/")}'


def resolve_image_url(path, fallback='images/placeholders/product.png'):
    """Return a browser-ready image URL for templates and APIs."""
    normalized = normalize_stored_image_path(path)
    if not normalized:
        return url_for('static', filename=fallback)
    if normalized.startswith(('http://', 'https://')):
        return normalized
    if normalized.startswith('/static/'):
        return normalized
    return url_for('static', filename=normalized.lstrip('/'))


def image_disk_path(stored_path):
    """Map a stored image path to the on-disk upload path."""
    if not stored_path or stored_path.startswith(('http://', 'https://')):
        return None

    rel = stored_path.strip()
    for prefix in ('/static/uploads/', 'static/uploads/', '/uploads/', 'uploads/'):
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
            break
    rel = rel.lstrip('/')
    if not rel:
        return None
    return os.path.join(current_app.config['UPLOAD_FOLDER'], rel)


def save_image(file, subfolder='products'):
    """Save and process uploaded image. Returns stored relative path."""
    if not file or not allowed_file(file.filename):
        return None

    # Validate magic bytes to prevent disguised files
    if not _validate_magic_bytes(file.stream):
        return None

    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext == 'jpeg':
        ext = 'jpg'
    filename = f'{uuid.uuid4().hex}.{ext}'
    safe_filename = secure_filename(filename)

    # Ensure directory exists
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, safe_filename)

    # Process image with Pillow (re-encode to strip metadata)
    img = Image.open(file.stream)
    img = _prepare_image_for_save(img)
    img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)

    save_kwargs = {'quality': 85, 'optimize': True}
    if ext in ('jpg', 'jpeg'):
        img.save(filepath, format='JPEG', **save_kwargs)
    elif ext == 'png':
        img.save(filepath, format='PNG', optimize=True)
    elif ext == 'webp':
        img.save(filepath, format='WEBP', quality=85)
    else:
        img.save(filepath, **save_kwargs)

    # Store relative path — works with resolve_image_url()
    return f'{subfolder}/{safe_filename}'


def save_thumbnail(file, subfolder='thumbnails'):
    """Save a thumbnail version of the image."""
    if not file or not allowed_file(file.filename):
        return None

    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext == 'jpeg':
        ext = 'jpg'
    filename = f'{uuid.uuid4().hex}_thumb.{ext}'
    safe_filename = secure_filename(filename)

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, safe_filename)

    img = Image.open(file.stream)
    img = _prepare_image_for_save(img)
    img.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
    img.save(filepath, quality=80, optimize=True)

    return f'{subfolder}/{safe_filename}'


def delete_image(image_url):
    """Delete an image file from disk."""
    filepath = image_disk_path(image_url)
    if filepath and os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
