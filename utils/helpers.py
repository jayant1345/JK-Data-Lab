import os
import re
import json
import uuid
from datetime import datetime
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


def unique_slug(base_slug, model, exclude_id=None):
    slug = base_slug
    counter = 1
    while True:
        q = model.query.filter_by(slug=slug)
        if exclude_id:
            q = q.filter(model.id != exclude_id)
        if not q.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file, subfolder='projects', max_size=(1200, 800)):
    if not file or not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    img = Image.open(file)
    img.thumbnail(max_size, Image.LANCZOS)
    img.save(filepath, optimize=True, quality=85)
    return f"uploads/{subfolder}/{filename}"


def delete_image(rel_path):
    if not rel_path:
        return
    full = os.path.join(current_app.static_folder, rel_path)
    if os.path.exists(full):
        os.remove(full)


def paginate_query(query, page, per_page=10):
    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_site_settings():
    from models import SiteSetting
    settings = SiteSetting.query.all()
    return {s.key: s.value for s in settings}
