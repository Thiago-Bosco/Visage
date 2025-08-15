import os
import logging

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app without instance_path to avoid read-only filesystem issues
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuração do banco - SOMENTE Supabase/PostgreSQL
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("❌ Variável DATABASE_URL não configurada! Configure para o Supabase.")

# Garantir SSL no Supabase
if "supabase.co" in database_url and "?sslmode=require" not in database_url:
    database_url += "?sslmode=require"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 30,
    "pool_size": 5,
    "max_overflow": 10
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database extension
db.init_app(app)

def init_database():
    """Initialize database tables and default data"""
    try:
        with app.app_context():
            import models  # Import models

            # Test connection
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("✅ Conexão com Supabase estabelecida com sucesso!")

            # Create tables (only if they don't exist in Supabase)
            db.create_all()

            # Create initial admin user
            from models import AdminUser
            if AdminUser.query.count() == 0:
                admin = AdminUser(username='visagecosmeticos')
                admin.set_password('270174CLcl')
                db.session.add(admin)
                db.session.commit()
                print("Usuário administrador criado: visagecosmeticos")

            # Create initial product
            from models import Product
            if Product.query.count() == 0:
                p1 = Product(
                    name="Suavecito Pomade Original",
                    description="Pomada à base d'água com fixação forte e brilho médio.",
                    price=45.90,
                    cost_price=25.00,
                    stock_quantity=50,
                    min_stock_level=10,
                    max_stock_level=100,
                    supplier="Suavecito",
                    sku="SUV-POM-001",
                    image_url="https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=300&h=300&fit=crop&auto=format",
                    category="Pomadas",
                    in_stock=True
                )
                db.session.add(p1)
                db.session.commit()
                logging.info("Produto inicial criado com sucesso!")

    except Exception as e:
        print(f"❌ ERRO na conexão com Supabase: {str(e)}")

# Initialize database only if running directly (not during import)
if __name__ != '__main__':
    try:
        # Load admin CRUD module
        import admin_crud
        print("Admin CRUD customizado carregado com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar admin customizado: {e}")
    
    # Load routes
    try:
        from routes import *
    except Exception as e:
        print(f"Erro ao carregar rotas: {e}")

# Handlers de erro
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f'Erro interno: {str(e)}')
    return render_template('error.html'), getattr(e, 'code', 500)

# Importa rotas apenas se não foi importado antes
if 'routes' not in locals():
    from routes import *
