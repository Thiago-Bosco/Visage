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
# Clean and fix the URL
database_url = "postgresql://postgres.fnwfjminutnkeuboskte:Ubunto323231%40@aws-0-us-east-2.pooler.supabase.com:6543/postgres"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 20,
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
        initial_products = [
            Product(
                name="Suavecito Pomade Original",
                description="Pomada à base d'água com fixação forte e brilho médio. Fácil de aplicar e remover.",
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
            ),
            Product(
                name="Honest Amish Beard Oil",
                description="Óleo 100% natural com óleos essenciais orgânicos para hidratar e amaciar a barba.",
                price=52.00,
                cost_price=30.00,
                stock_quantity=25,
                min_stock_level=5,
                max_stock_level=50,
                supplier="Honest Amish",
                sku="HA-OIL-001",
                image_url="https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=300&h=300&fit=crop&auto=format",
                category="Óleos",
                in_stock=True
            ),
            Product(
                name="American Crew Daily Shampoo",
                description="Shampoo diário para cabelos normais a oleosos, com sistema de limpeza suave.",
                price=38.50,
                cost_price=22.00,
                stock_quantity=8,
                min_stock_level=10,
                max_stock_level=40,
                supplier="American Crew",
                sku="AC-SHA-001",
                image_url="https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=300&h=300&fit=crop&auto=format",
                category="Shampoos",
                in_stock=True
            ),
            Product(
                name="Layrite Superhold Pomade",
                description="Pomada de fixação extra forte com acabamento natural, ideal para penteados elaborados.",
                price=42.90,
                cost_price=24.00,
                stock_quantity=30,
                min_stock_level=8,
                max_stock_level=60,
                supplier="Layrite",
                sku="LAY-POM-002",
                image_url="https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?w=300&h=300&fit=crop&auto=format",
                category="Pomadas",
                in_stock=True
            ),
            Product(
                name="Proraso After Shave Balm",
                description="Bálsamo pós-barba com eucalipto e mentol, acalma e hidrata a pele após o barbear.",
                price=28.90,
                cost_price=16.00,
                stock_quantity=3,
                min_stock_level=5,
                max_stock_level=30,
                supplier="Proraso",
                sku="PRO-BAL-001",
                image_url="https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=300&h=300&fit=crop&auto=format",
                category="Pós-Barba",
                in_stock=True
            ),
            Product(
                name="The Art of Shaving Kit",
                description="Kit completo com óleo pré-barbear, creme de barbear, bálsamo pós-barba e pincel.",
                price=185.00,
                cost_price=120.00,
                stock_quantity=12,
                min_stock_level=3,
                max_stock_level=20,
                supplier="The Art of Shaving",
                sku="AOS-KIT-001",
                image_url="https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300&h=300&fit=crop&auto=format",
                category="Kits",
                in_stock=True
            ),
            Product(
                name="Beardbrand Beard Wash",
                description="Shampoo específico para barba que limpa sem ressecar, mantendo os pelos macios.",
                price=35.90,
                cost_price=20.00,
                stock_quantity=18,
                min_stock_level=8,
                max_stock_level=40,
                supplier="Beardbrand",
                sku="BB-WASH-001",
                image_url="https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=300&fit=crop&auto=format",
                category="Shampoos",
                in_stock=True
            ),
            Product(
                name="Murray's Superior Pomade",
                description="Pomada clássica à base de petróleo com fixação extra forte e brilho intenso.",
                price=25.90,
                cost_price=12.00,
                stock_quantity=40,
                min_stock_level=10,
                max_stock_level=80,
                supplier="Murray's",
                sku="MUR-POM-001",
                image_url="https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=300&h=300&fit=crop&auto=format",
                category="Pomadas",
                in_stock=True
            ),
            Product(
                name="Clubman Pinaud After Shave",
                description="Loção pós-barba clássica com fragrância tradicional, refresca e tonifica a pele.",
                price=22.50,
                cost_price=12.50,
                stock_quantity=22,
                min_stock_level=6,
                max_stock_level=35,
                supplier="Clubman",
                sku="CLB-ASH-001",
                image_url="https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=300&h=300&fit=crop&auto=format",
                category="Pós-Barba",
                in_stock=True
            ),
            Product(
                name="Viking Revolution Beard Oil",
                description="Óleo para barba com argan e jojoba, promove crescimento e elimina coceira.",
                price=48.90,
                cost_price=28.00,
                stock_quantity=15,
                min_stock_level=5,
                max_stock_level=30,
                supplier="Viking Revolution",
                sku="VR-OIL-001",
                image_url="https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=300&h=300&fit=crop&auto=format",
                category="Óleos",
                in_stock=True
            )
        ]
        
        for product in initial_products:
            db.session.add(product)
        
        db.session.commit()
        logging.info("Produtos iniciais criados com sucesso!")

# Configure Flask-WTF (CSRF disabled for now)
from flask_wtf.csrf import CSRFProtect
# csrf = CSRFProtect(app)  # Disabled temporarily

# Import routes apenas
from routes import *  # noqa: F401, F403
