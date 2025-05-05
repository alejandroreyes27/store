from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Instanciamos las extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Cargar configuración desde config.py

    # Inicializar las extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Context processor para contar facturas pendientes
    from flask_login import current_user
    from app.models.Factura import Factura

    @app.context_processor
    def inject_pending_facturas():
        pendientes = 0
        if current_user.is_authenticated and current_user.rolUser == 'administrador':
            pendientes = Factura.query.filter_by(revisada=False).count()
        return dict(pendientes_facturas=pendientes)
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    @login_manager.user_loader
    def load_user(idUser):
        from app.models.users import Users
        return Users.query.get(int(idUser))

    # Registrar blueprints y cargar modelos
    with app.app_context():
        # Importar modelos para que Flask-Migrate los detecte
        from app.models.Categoria import Categoria
        from app.models.Productos import Productos

        # Importar los nuevos modelos de Facturación
        from app.models.Factura import Factura
        from app.models.Detallefactura import DetalleFactura

        # Importar y registrar blueprints
        from app.routes.auth import bp as auth_bp
        from app.routes.Productos_routes import bp as productos_bp
        from app.routes.Carrito_routes import bp as carrito_bp
        from app.routes.Categoria_routes import bp as categoria_bp
        from app.routes.Facturacion_routes import bp as facturacion_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(productos_bp)
        app.register_blueprint(carrito_bp)
        app.register_blueprint(categoria_bp)
        app.register_blueprint(facturacion_bp)

    return app
