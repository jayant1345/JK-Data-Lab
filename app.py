import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv

from config import config
from models import db, Admin
from routes.public import public_bp
from routes.admin import admin_bp
from routes.api import api_bp

load_dotenv()

mail = Mail()
login_manager = LoginManager()


def create_app(env=None):
    app = Flask(__name__)
    env = env or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config.get(env, config['default']))

    db.init_app(app)
    mail.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'error'

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'projects'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'testimonials'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'blog'), exist_ok=True)

    return app


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from utils.seed_data import seed_all
        seed_all(app)
    app.run(debug=True, host='0.0.0.0', port=5000)
