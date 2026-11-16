"""
Trekking Management Application - V2
Modern Application Development II (MAD-II)
Student Roll No: 23f2000278

Main Flask Application Entrypoint.
Initializes configuration, database, CORS, route blueprints, and static single-page app serving.
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from database import db
from init_db import seed_database

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.trek_routes import trek_bp
from routes.booking_routes import booking_bp
from routes.admin_routes import admin_bp
from routes.staff_routes import staff_bp

def create_app(config_class=Config):
    """Application factory for Flask API."""
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    app.config.from_object(config_class)

    # Enable CORS for frontend development
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize Database
    db.init_app(app)

    # Ensure required directories exist
    os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
    os.makedirs(Config.REPORTS_DIR, exist_ok=True)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(trek_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)

    # Programmatic database table creation & superuser seed
    with app.app_context():
        db.create_all()
        # Seed default superuser admin and sample routes if database is fresh
        from models.user import User
        if not User.query.filter_by(role='admin').first():
            seed_database(app)

    # Health check & public landing stats
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'application': 'Trekking Management Application - V2',
            'roll_number': Config.STUDENT_ROLL_NO
        }), 200

    @app.route('/api/public/stats', methods=['GET'])
    def public_stats():
        """Public endpoint for landing page displaying platform stats without requiring authentication."""
        from models import Trek, Booking, User
        total_treks = Trek.query.count()
        total_trekkers = User.query.filter_by(role='user').count()
        completed_treks = Trek.query.filter_by(status='Completed').count()
        return jsonify({
            'total_treks': total_treks,
            'total_trekkers': total_trekkers,
            'completed_treks': completed_treks,
            'satisfaction_rate': '98.5%'
        }), 200

    # Serve Vue Frontend single page application
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/dist'))
        if path != "" and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        if os.path.exists(os.path.join(dist_dir, 'index.html')):
            return send_from_directory(dist_dir, 'index.html')
        return jsonify({
            'message': 'Trekking Management Application API is online.',
            'docs': 'Visit frontend Vite dev server at http://localhost:5173 or run npm run build in frontend directory.',
            'version': '2.0.0',
            'author_roll_number': Config.STUDENT_ROLL_NO
        }), 200

    return app

if __name__ == '__main__':
    application = create_app()
    # Programmatic database and admin creation
    seed_database(application)
    port = int(os.environ.get('PORT', 5001))
    print(f"\n=======================================================")
    print(f"  Trekking Management Application - V2 (MAD-II)")
    print(f"  Student Roll No: 23f2000278")
    print(f"  API Server running on: http://127.0.0.1:{port}")
    print(f"  Pre-configured Superuser Admin: admin@gmail.com / admin123")
    print(f"=======================================================\n")
    application.run(host='0.0.0.0', port=port, debug=True)
