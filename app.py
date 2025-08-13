import os
import logging

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database - using PostgreSQL (Supabase)
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("⚠️ WARNING: DATABASE_URL not found. Please configure it in your deployment platform.")
    print("For Vercel: Add DATABASE_URL in Environment Variables")
    print("For Replit: Add DATABASE_URL in Secrets")
    # Use a placeholder for now to prevent crashes
    database_url = "postgresql://placeholder:placeholder@localhost:5432/placeholder"

# Debug: verificar se a URL está configurada (sem mostrar a senha)
if database_url:
    url_parts = database_url.split('@')
    if len(url_parts) > 1:
        host_part = url_parts[1]
        print(f"Conectando ao host: {host_part}")
    else:
        print("URL do banco configurada")
else:
    print("ERRO: DATABASE_URL não encontrada")

# Configurar SSL para Supabase
if "supabase.com" in database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url + "?sslmode=require"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 30,
    "pool_size": 5,
    "max_overflow": 10
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize the app with the extension
db.init_app(app)

try:
    with app.app_context():
        # Import models to ensure tables are created
        import models  # noqa: F401
        
        # Test connection first
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        print("✅ Conexão com Supabase estabelecida com sucesso!")
        
        db.create_all()
        
        # Carregar apenas o admin customizado, sem Flask-Admin
        try:
            import admin_crud  # noqa: F401
            print("Admin CRUD customizado carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao carregar admin customizado: {e}")
        
        # Create admin user if none exists
        from models import AdminUser
        if AdminUser.query.count() == 0:
            admin = AdminUser()
            admin.username = 'visagecosmeticos'
            admin.set_password('270174CLcl')
            db.session.add(admin)
            db.session.commit()
            print("Usuário administrador criado: visagecosmeticos")
        
        # Create some initial products if none exist
        from models import Product
        if Product.query.count() == 0:
            initial_products = []
            
            # Product 1
            p1 = Product()
            p1.name = "Suavecito Pomade Original"
            p1.description = "Pomada à base d'água com fixação forte e brilho médio. Fácil de aplicar e remover."
            p1.price = 45.90
            p1.cost_price = 25.00
            p1.stock_quantity = 50
            p1.min_stock_level = 10
            p1.max_stock_level = 100
            p1.supplier = "Suavecito"
            p1.sku = "SUV-POM-001"
            p1.image_url = "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=300&h=300&fit=crop&auto=format"
            p1.category = "Pomadas"
            p1.in_stock = True
            initial_products.append(p1)
            
            # Add the products to database
            for product in initial_products:
                db.session.add(product)
            
            db.session.commit()
            logging.info("Produto inicial criado com sucesso!")

except Exception as e:
    print(f"❌ ERRO na conexão com Supabase: {str(e)}")
    print("Verifique:")
    print("1. Se a URL do Supabase está correta")
    print("2. Se a senha está correta")
    print("3. Se o banco permite conexões externas")
    print("4. Se o projeto Supabase está ativo")
    
    # Import routes mesmo com erro de DB para mostrar página de erro
    try:
        import admin_crud  # noqa: F401
        from routes import *  # noqa: F401, F403
    except:
        pass

# Configurar tratamento de erros globais para usuários finais
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Log interno para desenvolvedores
    logging.error(f'Erro interno: {str(e)}')
    
    # Mensagem amigável para usuários
    if hasattr(e, 'code') and e.code == 404:
        return render_template('error.html'), 404
    
    # Para outros erros, retornar mensagem genérica
    return render_template('error.html'), 500

# Configure Flask-WTF (CSRF disabled for now)
from flask_wtf.csrf import CSRFProtect
# csrf = CSRFProtect(app)  # Disabled temporarily

# Import routes apenas se não houve erro de DB
if 'routes' not in locals():
    from routes import *  # noqa: F401, F403
