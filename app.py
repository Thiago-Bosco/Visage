import os
import logging

from flask import Flask
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

# configure the database for PostgreSQL (Supabase)
# Properly encode the password with @ symbol
import urllib.parse
password = "Ubunto323231@"
encoded_password = urllib.parse.quote(password, safe='')
database_url = f"postgresql://postgres.fnwfjminutnkeuboskte:{encoded_password}@aws-0-us-east-2.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 20,
    "connect_args": {
        "sslmode": "require"
    }
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    
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
        
        # Simplify - just add the one product for now
        for product in initial_products:
            db.session.add(product)
        
        db.session.commit()
        logging.info("Produto inicial criado com sucesso!")

# Configure Flask-WTF (CSRF disabled for now)
from flask_wtf.csrf import CSRFProtect
# csrf = CSRFProtect(app)  # Disabled temporarily

# Import routes apenas
from routes import *  # noqa: F401, F403
