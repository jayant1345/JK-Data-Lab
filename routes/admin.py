import json
import csv
import io
from datetime import datetime, date
from flask import (Blueprint, render_template, request, flash, redirect,
                   url_for, abort, Response, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Admin, Project, Service, Testimonial, BlogPost, ContactMessage, SiteSetting, Skill
from utils.helpers import slugify, unique_slug, save_image, delete_image, paginate_query

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Auth ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin, remember=False)
            admin.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'projects': Project.query.count(),
        'services': Service.query.count(),
        'testimonials': Testimonial.query.count(),
        'messages': ContactMessage.query.count(),
        'unread': ContactMessage.query.filter_by(status='unread').count(),
        'blog_posts': BlogPost.query.count(),
    }
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_messages=recent_messages)


# ── Projects ──────────────────────────────────────────────────────────────────

@admin_bp.route('/projects')
@login_required
def projects():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    q = Project.query
    if search:
        q = q.filter(Project.title.ilike(f'%{search}%'))
    projects = paginate_query(q.order_by(Project.created_at.desc()), page)
    return render_template('admin/projects.html', projects=projects, search=search)


@admin_bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def project_new():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Title is required.', 'error')
            return redirect(url_for('admin.project_new'))
        slug = unique_slug(slugify(title), Project)
        cover = save_image(request.files.get('cover_image'), 'projects')
        proj = Project(
            title=title, slug=slug,
            category=request.form.get('category', ''),
            short_desc=request.form.get('short_desc', ''),
            full_desc=request.form.get('full_desc', ''),
            tech_stack=request.form.get('tech_stack', ''),
            client_name=request.form.get('client_name', ''),
            client_country=request.form.get('client_country', ''),
            results=request.form.get('results', ''),
            github_url=request.form.get('github_url', ''),
            live_url=request.form.get('live_url', ''),
            status=request.form.get('status', 'published'),
            featured=bool(request.form.get('featured')),
            cover_image=cover,
            project_date=_parse_date(request.form.get('project_date')),
        )
        db.session.add(proj)
        db.session.commit()
        flash('Project created successfully.', 'success')
        return redirect(url_for('admin.projects'))
    return render_template('admin/project_form.html', project=None)


@admin_bp.route('/projects/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
def project_edit(pid):
    proj = Project.query.get_or_404(pid)
    if request.method == 'POST':
        proj.title = request.form.get('title', proj.title).strip()
        proj.slug = unique_slug(slugify(proj.title), Project, exclude_id=proj.id)
        proj.category = request.form.get('category', proj.category)
        proj.short_desc = request.form.get('short_desc', '')
        proj.full_desc = request.form.get('full_desc', '')
        proj.tech_stack = request.form.get('tech_stack', '')
        proj.client_name = request.form.get('client_name', '')
        proj.client_country = request.form.get('client_country', '')
        proj.results = request.form.get('results', '')
        proj.github_url = request.form.get('github_url', '')
        proj.live_url = request.form.get('live_url', '')
        proj.status = request.form.get('status', 'published')
        proj.featured = bool(request.form.get('featured'))
        proj.project_date = _parse_date(request.form.get('project_date'))
        new_cover = request.files.get('cover_image')
        if new_cover and new_cover.filename:
            delete_image(proj.cover_image)
            proj.cover_image = save_image(new_cover, 'projects')
        proj.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Project updated.', 'success')
        return redirect(url_for('admin.projects'))
    return render_template('admin/project_form.html', project=proj)


@admin_bp.route('/projects/<int:pid>/delete', methods=['POST'])
@login_required
def project_delete(pid):
    proj = Project.query.get_or_404(pid)
    delete_image(proj.cover_image)
    db.session.delete(proj)
    db.session.commit()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin.projects'))


# ── Services ──────────────────────────────────────────────────────────────────

@admin_bp.route('/services')
@login_required
def services():
    svcs = Service.query.order_by(Service.order).all()
    return render_template('admin/services.html', services=svcs)


@admin_bp.route('/services/<int:sid>/edit', methods=['GET', 'POST'])
@login_required
def service_edit(sid):
    svc = Service.query.get_or_404(sid)
    if request.method == 'POST':
        svc.title = request.form.get('title', svc.title)
        svc.description = request.form.get('description', '')
        svc.icon = request.form.get('icon', svc.icon)
        svc.order = int(request.form.get('order', svc.order))
        svc.visible = bool(request.form.get('visible'))
        svc.pricing_basic = request.form.get('pricing_basic', '')
        svc.pricing_standard = request.form.get('pricing_standard', '')
        svc.pricing_premium = request.form.get('pricing_premium', '')
        db.session.commit()
        flash('Service updated.', 'success')
        return redirect(url_for('admin.services'))
    return render_template('admin/service_form.html', service=svc)


# ── Testimonials ──────────────────────────────────────────────────────────────

@admin_bp.route('/testimonials')
@login_required
def testimonials():
    page = request.args.get('page', 1, type=int)
    items = paginate_query(Testimonial.query.order_by(Testimonial.date.desc()), page)
    return render_template('admin/testimonials.html', testimonials=items)


@admin_bp.route('/testimonials/new', methods=['GET', 'POST'])
@login_required
def testimonial_new():
    if request.method == 'POST':
        photo = save_image(request.files.get('photo'), 'testimonials')
        t = Testimonial(
            client_name=request.form.get('client_name', ''),
            company=request.form.get('company', ''),
            country=request.form.get('country', ''),
            rating=int(request.form.get('rating', 5)),
            text=request.form.get('text', ''),
            photo=photo,
            visible=bool(request.form.get('visible')),
            date=_parse_date(request.form.get('date')) or date.today(),
        )
        db.session.add(t)
        db.session.commit()
        flash('Testimonial added.', 'success')
        return redirect(url_for('admin.testimonials'))
    return render_template('admin/testimonial_form.html', testimonial=None)


@admin_bp.route('/testimonials/<int:tid>/edit', methods=['GET', 'POST'])
@login_required
def testimonial_edit(tid):
    t = Testimonial.query.get_or_404(tid)
    if request.method == 'POST':
        t.client_name = request.form.get('client_name', t.client_name)
        t.company = request.form.get('company', '')
        t.country = request.form.get('country', '')
        t.rating = int(request.form.get('rating', 5))
        t.text = request.form.get('text', '')
        t.visible = bool(request.form.get('visible'))
        t.date = _parse_date(request.form.get('date')) or t.date
        new_photo = request.files.get('photo')
        if new_photo and new_photo.filename:
            delete_image(t.photo)
            t.photo = save_image(new_photo, 'testimonials')
        db.session.commit()
        flash('Testimonial updated.', 'success')
        return redirect(url_for('admin.testimonials'))
    return render_template('admin/testimonial_form.html', testimonial=t)


@admin_bp.route('/testimonials/<int:tid>/delete', methods=['POST'])
@login_required
def testimonial_delete(tid):
    t = Testimonial.query.get_or_404(tid)
    delete_image(t.photo)
    db.session.delete(t)
    db.session.commit()
    flash('Testimonial deleted.', 'success')
    return redirect(url_for('admin.testimonials'))


# ── Blog ──────────────────────────────────────────────────────────────────────

@admin_bp.route('/blog')
@login_required
def blog():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    q = BlogPost.query
    if search:
        q = q.filter(BlogPost.title.ilike(f'%{search}%'))
    posts = paginate_query(q.order_by(BlogPost.created_at.desc()), page)
    return render_template('admin/blog.html', posts=posts, search=search)


@admin_bp.route('/blog/new', methods=['GET', 'POST'])
@login_required
def blog_new():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = unique_slug(slugify(title), BlogPost)
        cover = save_image(request.files.get('cover_image'), 'blog')
        post = BlogPost(
            title=title, slug=slug,
            content=request.form.get('content', ''),
            category=request.form.get('category', ''),
            tags=request.form.get('tags', ''),
            cover_image=cover,
            meta_title=request.form.get('meta_title', ''),
            meta_desc=request.form.get('meta_desc', ''),
            status=request.form.get('status', 'published'),
        )
        db.session.add(post)
        db.session.commit()
        flash('Blog post created.', 'success')
        return redirect(url_for('admin.blog'))
    return render_template('admin/blog_form.html', post=None)


@admin_bp.route('/blog/<int:bid>/edit', methods=['GET', 'POST'])
@login_required
def blog_edit(bid):
    post = BlogPost.query.get_or_404(bid)
    if request.method == 'POST':
        post.title = request.form.get('title', post.title)
        post.slug = unique_slug(slugify(post.title), BlogPost, exclude_id=post.id)
        post.content = request.form.get('content', '')
        post.category = request.form.get('category', '')
        post.tags = request.form.get('tags', '')
        post.meta_title = request.form.get('meta_title', '')
        post.meta_desc = request.form.get('meta_desc', '')
        post.status = request.form.get('status', 'published')
        post.updated_at = datetime.utcnow()
        new_cover = request.files.get('cover_image')
        if new_cover and new_cover.filename:
            delete_image(post.cover_image)
            post.cover_image = save_image(new_cover, 'blog')
        db.session.commit()
        flash('Blog post updated.', 'success')
        return redirect(url_for('admin.blog'))
    return render_template('admin/blog_form.html', post=post)


@admin_bp.route('/blog/<int:bid>/delete', methods=['POST'])
@login_required
def blog_delete(bid):
    post = BlogPost.query.get_or_404(bid)
    delete_image(post.cover_image)
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted.', 'success')
    return redirect(url_for('admin.blog'))


# ── Messages ──────────────────────────────────────────────────────────────────

@admin_bp.route('/messages')
@login_required
def messages():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    q = ContactMessage.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    msgs = paginate_query(q.order_by(ContactMessage.created_at.desc()), page)
    return render_template('admin/messages.html', messages=msgs, status_filter=status_filter)


@admin_bp.route('/messages/<int:mid>/status', methods=['POST'])
@login_required
def message_status(mid):
    msg = ContactMessage.query.get_or_404(mid)
    msg.status = request.form.get('status', msg.status)
    db.session.commit()
    flash('Message status updated.', 'success')
    return redirect(url_for('admin.messages'))


@admin_bp.route('/messages/<int:mid>/delete', methods=['POST'])
@login_required
def message_delete(mid):
    msg = ContactMessage.query.get_or_404(mid)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'success')
    return redirect(url_for('admin.messages'))


@admin_bp.route('/messages/export')
@login_required
def messages_export():
    msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Company', 'Service', 'Budget', 'Message', 'Status', 'Date'])
    for m in msgs:
        writer.writerow([m.id, m.name, m.email, m.company, m.service, m.budget, m.message, m.status, m.created_at])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=messages.csv'})


# ── Settings ──────────────────────────────────────────────────────────────────

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        for key in request.form:
            SiteSetting.set(key, request.form[key])
        flash('Settings saved.', 'success')
        return redirect(url_for('admin.settings'))
    settings_dict = {s.key: s.value for s in SiteSetting.query.all()}
    return render_template('admin/settings.html', settings=settings_dict)


@admin_bp.route('/settings/export-db')
@login_required
def export_db():
    data = {
        'projects': [_model_to_dict(p) for p in Project.query.all()],
        'services': [_model_to_dict(s) for s in Service.query.all()],
        'testimonials': [_model_to_dict(t) for t in Testimonial.query.all()],
        'settings': {s.key: s.value for s in SiteSetting.query.all()},
    }
    return Response(
        json.dumps(data, indent=2, default=str),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=jkdatalab_backup.json'},
    )


# ── Skills ────────────────────────────────────────────────────────────────────

@admin_bp.route('/skills')
@login_required
def skills():
    skills = Skill.query.order_by(Skill.order).all()
    return render_template('admin/skills.html', skills=skills)


@admin_bp.route('/skills/new', methods=['GET', 'POST'])
@login_required
def skill_new():
    if request.method == 'POST':
        s = Skill(
            name=request.form.get('name', ''),
            category=request.form.get('category', ''),
            proficiency=int(request.form.get('proficiency', 80)),
            icon=request.form.get('icon', ''),
            order=int(request.form.get('order', 0)),
        )
        db.session.add(s)
        db.session.commit()
        flash('Skill added.', 'success')
        return redirect(url_for('admin.skills'))
    return render_template('admin/skill_form.html', skill=None)


@admin_bp.route('/skills/<int:sid>/edit', methods=['GET', 'POST'])
@login_required
def skill_edit(sid):
    s = Skill.query.get_or_404(sid)
    if request.method == 'POST':
        s.name = request.form.get('name', s.name)
        s.category = request.form.get('category', s.category)
        s.proficiency = int(request.form.get('proficiency', s.proficiency))
        s.icon = request.form.get('icon', s.icon)
        s.order = int(request.form.get('order', s.order))
        db.session.commit()
        flash('Skill updated.', 'success')
        return redirect(url_for('admin.skills'))
    return render_template('admin/skill_form.html', skill=s)


@admin_bp.route('/skills/<int:sid>/delete', methods=['POST'])
@login_required
def skill_delete(sid):
    s = Skill.query.get_or_404(sid)
    db.session.delete(s)
    db.session.commit()
    flash('Skill deleted.', 'success')
    return redirect(url_for('admin.skills'))


# ── Test Email ────────────────────────────────────────────────────────────────

@admin_bp.route('/test-email')
@login_required
def test_email():
    import smtplib
    import socket
    from flask import Response as FlaskResponse
    cfg = current_app.config

    server   = cfg.get('MAIL_SERVER', 'smtp.zoho.in')
    port     = cfg.get('MAIL_PORT', 465)
    use_ssl  = cfg.get('MAIL_USE_SSL', True)
    username = cfg.get('MAIL_USERNAME') or ''
    password = cfg.get('MAIL_PASSWORD') or ''
    sender   = cfg.get('MAIL_DEFAULT_SENDER') or username
    receiver = cfg.get('CONTACT_RECEIVER', 'kinjal@jkdatalab.com')
    mode     = 'SSL (port 465)' if use_ssl else 'STARTTLS (port 587)'

    diag_rows = (
        f"<tr><td>MAIL_SERVER</td><td>{server}</td></tr>"
        f"<tr><td>MAIL_PORT</td><td>{port} ({mode})</td></tr>"
        f"<tr><td>MAIL_USERNAME</td><td>{username or '<b style=color:red>NOT SET</b>'}</td></tr>"
        f"<tr><td>MAIL_PASSWORD</td><td>{'*** (set)' if password else '<b style=color:red>NOT SET</b>'}</td></tr>"
        f"<tr><td>MAIL_DEFAULT_SENDER</td><td>{sender or '<b style=color:red>NOT SET</b>'}</td></tr>"
        f"<tr><td>CONTACT_RECEIVER</td><td>{receiver}</td></tr>"
    )

    result = ''
    color  = 'green'

    if not username or not password:
        result = 'MAIL_USERNAME or MAIL_PASSWORD is missing in Railway Variables.'
        color  = 'red'
    else:
        try:
            socket.setdefaulttimeout(10)
            if use_ssl:
                smtp = smtplib.SMTP_SSL(server, port, timeout=10)
            else:
                smtp = smtplib.SMTP(server, port, timeout=10)
                smtp.ehlo()
                smtp.starttls()
            smtp.login(username, password)
            body  = f"Subject: JK Data Lab Test Email\nFrom: {sender}\nTo: {receiver}\n\nThis is a test from JK Data Lab admin panel."
            smtp.sendmail(sender, [receiver], body)
            smtp.quit()
            result = f'SUCCESS — email sent to {receiver}. Check your inbox (and spam).'
            color  = 'green'
        except smtplib.SMTPAuthenticationError as e:
            result = f'AUTH FAILED — wrong username or app password. Detail: {e}'
            color  = 'red'
        except smtplib.SMTPException as e:
            result = f'SMTP ERROR — {e}'
            color  = 'red'
        except socket.timeout:
            result = f'TIMEOUT — cannot reach {server}:{port} from Railway. Try the other port.'
            color  = 'red'
        except Exception as e:
            result = f'ERROR — {type(e).__name__}: {e}'
            color  = 'red'
        finally:
            socket.setdefaulttimeout(None)

    html = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;padding:2rem;">
<h2>Email Diagnostics</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse;margin-bottom:1.5rem;">
<tr><th>Setting</th><th>Value</th></tr>{diag_rows}</table>
<h3 style="color:{color}">Result: {result}</h3>
<p><a href="/admin/messages">← Back to Messages</a></p>
</body></html>"""
    return FlaskResponse(html, mimetype='text/html')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, '%Y-%m-%d').date()
    except ValueError:
        return None


def _model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
