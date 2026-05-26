from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    short_desc = db.Column(db.String(300))
    full_desc = db.Column(db.Text)
    tech_stack = db.Column(db.String(500))
    client_name = db.Column(db.String(150))
    client_country = db.Column(db.String(80))
    project_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='published')  # published | draft
    featured = db.Column(db.Boolean, default=False)
    cover_image = db.Column(db.String(300))
    gallery_images = db.Column(db.Text)  # JSON list of paths
    results = db.Column(db.Text)
    github_url = db.Column(db.String(300))
    live_url = db.Column(db.String(300))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def tech_list(self):
        return [t.strip() for t in (self.tech_stack or '').split(',') if t.strip()]


class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(170), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    order = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, default=True)
    pricing_basic = db.Column(db.Text)
    pricing_standard = db.Column(db.Text)
    pricing_premium = db.Column(db.Text)


class Testimonial(db.Model):
    __tablename__ = 'testimonial'
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150))
    country = db.Column(db.String(80))
    rating = db.Column(db.Integer, default=5)
    text = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(300))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)


class BlogPost(db.Model):
    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(270), unique=True, nullable=False)
    content = db.Column(db.Text)
    category = db.Column(db.String(80))
    tags = db.Column(db.String(300))
    cover_image = db.Column(db.String(300))
    meta_title = db.Column(db.String(200))
    meta_desc = db.Column(db.String(300))
    status = db.Column(db.String(20), default='published')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = 'contact_message'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(150))
    service = db.Column(db.String(100))
    budget = db.Column(db.String(80))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unread')  # unread | read | replied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))


class SiteSetting(db.Model):
    __tablename__ = 'site_setting'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get(cls, key, default=''):
        row = cls.query.filter_by(key=key).first()
        return row.value if row else default

    @classmethod
    def set(cls, key, value):
        row = cls.query.filter_by(key=key).first()
        if row:
            row.value = value
            row.updated_at = datetime.utcnow()
        else:
            db.session.add(cls(key=key, value=value))
        db.session.commit()


class Skill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(80))
    proficiency = db.Column(db.Integer, default=80)
    icon = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
