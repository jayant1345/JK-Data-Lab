import time
import threading
import requests
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, abort, current_app
from models import db, Project, Service, Testimonial, BlogPost, ContactMessage, SiteSetting, Skill
from utils.helpers import get_site_settings

public_bp = Blueprint('public', __name__)

MIN_FILL_SECONDS = 3

# Rate limits are backed by the ContactMessage table (not an in-memory
# dict) because the app runs multiple gunicorn workers — a per-process
# dict only sees a fraction of requests and lets bots slip through
# whenever they land on a different worker.


def _rate_limited(ip):
    window = datetime.utcnow() - timedelta(hours=1)
    count = ContactMessage.query.filter(
        ContactMessage.ip_address == ip,
        ContactMessage.created_at > window,
    ).count()
    return count >= 3


def _name_rate_limited(name):
    window = datetime.utcnow() - timedelta(minutes=30)
    count = ContactMessage.query.filter(
        db.func.lower(ContactMessage.name) == name.strip().lower(),
        ContactMessage.created_at > window,
    ).count()
    return count >= 1


def _hcaptcha_valid(token, ip):
    secret = current_app.config.get('HCAPTCHA_SECRET_KEY')
    if not secret:
        # Not configured yet — don't block submissions while keys are
        # being set up, but this means hCaptcha isn't actually enforced.
        current_app.logger.warning("HCAPTCHA_SECRET_KEY not set — captcha check skipped")
        return True
    if not token:
        return False
    try:
        resp = requests.post(
            'https://api.hcaptcha.com/siteverify',
            data={'secret': secret, 'response': token, 'remoteip': ip},
            timeout=5,
        )
        return resp.json().get('success', False)
    except requests.RequestException as e:
        current_app.logger.error(f"hCaptcha verification request failed: {e}")
        return False


@public_bp.route('/')
def index():
    services = Service.query.filter_by(visible=True).order_by(Service.order).all()
    projects = Project.query.filter_by(status='published').order_by(Project.featured.desc(), Project.created_at.desc()).limit(6).all()
    testimonials = Testimonial.query.filter_by(visible=True).all()
    settings = get_site_settings()
    return render_template('index.html', services=services, projects=projects, testimonials=testimonials, settings=settings)


@public_bp.route('/about')
def about():
    skills = Skill.query.order_by(Skill.order).all()
    settings = get_site_settings()
    return render_template('about.html', skills=skills, settings=settings)


@public_bp.route('/services')
def services():
    svcs = Service.query.filter_by(visible=True).order_by(Service.order).all()
    settings = get_site_settings()
    return render_template('services.html', services=svcs, settings=settings)


@public_bp.route('/portfolio')
def portfolio():
    category = request.args.get('category', '')
    q = Project.query.filter_by(status='published')
    if category:
        q = q.filter_by(category=category)
    projects = q.order_by(Project.featured.desc(), Project.created_at.desc()).all()
    categories = db.session.query(Project.category).distinct().all()
    categories = [c[0] for c in categories]
    settings = get_site_settings()
    return render_template('portfolio.html', projects=projects, categories=categories, active_category=category, settings=settings)


@public_bp.route('/portfolio/<slug>')
def portfolio_detail(slug):
    project = Project.query.filter_by(slug=slug, status='published').first_or_404()
    project.views = (project.views or 0) + 1
    db.session.commit()
    related = Project.query.filter_by(category=project.category, status='published').filter(Project.id != project.id).limit(3).all()
    settings = get_site_settings()
    return render_template('portfolio_detail.html', project=project, related=related, settings=settings)


@public_bp.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(status='published').order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    settings = get_site_settings()
    return render_template('blog.html', posts=posts, settings=settings)


@public_bp.route('/blog/<slug>')
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, status='published').first_or_404()
    settings = get_site_settings()
    return render_template('blog_detail.html', post=post, settings=settings)


@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    settings = get_site_settings()
    if request.method == 'POST':
        ip = request.remote_addr

        # Honeypot: hidden field real users never fill in. Bots that
        # blindly fill every input trip this. Pretend success so the
        # bot doesn't learn to skip the field.
        if request.form.get('website', '').strip():
            flash('Thank you! Your message has been sent. We will respond within 24 hours.', 'success')
            return redirect(url_for('public.contact'))

        # Timing trap: the form is rendered with a timestamp; a real
        # human takes more than a few seconds to fill it in. A missing
        # or unparseable timestamp means the request never actually
        # loaded the form (a bot POSTing straight to this endpoint),
        # which is just as suspicious as answering too fast.
        try:
            rendered_at = int(request.form.get('ts', ''))
        except (TypeError, ValueError):
            rendered_at = None
        if rendered_at is None or (time.time() - rendered_at) < MIN_FILL_SECONDS:
            flash('Thank you! Your message has been sent. We will respond within 24 hours.', 'success')
            return redirect(url_for('public.contact'))

        if not _hcaptcha_valid(request.form.get('h-captcha-response', ''), ip):
            flash('Please complete the CAPTCHA verification and try again.', 'error')
            return redirect(url_for('public.contact'))

        if _rate_limited(ip):
            flash('Too many submissions. Please wait an hour before trying again.', 'error')
            return redirect(url_for('public.contact'))

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('public.contact'))

        if _name_rate_limited(name):
            flash('Thank you! Your message has been sent. We will respond within 24 hours.', 'success')
            return redirect(url_for('public.contact'))

        msg = ContactMessage(
            name=name,
            email=email,
            company=request.form.get('company', '').strip(),
            service=request.form.get('service', '').strip(),
            budget=request.form.get('budget', '').strip(),
            message=message,
            ip_address=ip,
        )
        db.session.add(msg)
        db.session.commit()

        # Send email via Resend API in background thread
        from utils.email import send_contact_email
        app_obj = current_app._get_current_object()
        form_data = dict(request.form)
        def _send_email():
            with app_obj.app_context():
                send_contact_email(form_data)
        threading.Thread(target=_send_email, daemon=True).start()

        flash('Thank you! Your message has been sent. We will respond within 24 hours.', 'success')
        return redirect(url_for('public.contact'))

    return render_template(
        'contact.html',
        settings=settings,
        form_ts=int(time.time()),
        hcaptcha_site_key=current_app.config.get('HCAPTCHA_SITE_KEY'),
    )


@public_bp.route('/robots.txt')
def robots():
    from flask import Response
    content = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    return Response(content, mimetype='text/plain')


@public_bp.route('/sitemap.xml')
def sitemap():
    from flask import Response, url_for
    pages = []
    for rule in ['public.index', 'public.about', 'public.services', 'public.portfolio', 'public.contact']:
        pages.append(url_for(rule, _external=True))
    for project in Project.query.filter_by(status='published').all():
        pages.append(url_for('public.portfolio_detail', slug=project.slug, _external=True))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in pages:
        xml += f'  <url><loc>{url}</loc></url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')
