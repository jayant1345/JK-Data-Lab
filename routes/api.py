from flask import Blueprint, jsonify, request
from models import Project, Service, Testimonial

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/projects')
def projects():
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    q = Project.query.filter_by(status='published')
    if category:
        q = q.filter_by(category=category)
    paginated = q.order_by(Project.featured.desc(), Project.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'projects': [_project_dict(p) for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'page': page,
    })


@api_bp.route('/services')
def services():
    svcs = Service.query.filter_by(visible=True).order_by(Service.order).all()
    return jsonify([{'id': s.id, 'title': s.title, 'description': s.description, 'icon': s.icon} for s in svcs])


def _project_dict(p):
    return {
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'category': p.category,
        'short_desc': p.short_desc,
        'tech_stack': p.tech_list(),
        'cover_image': p.cover_image,
        'featured': p.featured,
    }
