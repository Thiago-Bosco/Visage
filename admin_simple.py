from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from app import app, db
from models import Product, Order, StockMovement, Supplier

class SimpleAdminView(BaseView):
    @expose('/')
    def index(self):
        # Dashboard simples
        total_products = Product.query.count()
        total_orders = Order.query.count()
        low_stock_products = Product.query.filter(Product.stock_quantity <= 5).count()
        
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin - Visage</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <h1>Dashboard - Visage Admin</h1>
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="card bg-primary text-white">
                            <div class="card-body">
                                <h5>Total de Produtos</h5>
                                <h2>{{ total_products }}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-success text-white">
                            <div class="card-body">
                                <h5>Total de Pedidos</h5>
                                <h2>{{ total_orders }}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-warning text-white">
                            <div class="card-body">
                                <h5>Estoque Baixo</h5>
                                <h2>{{ low_stock }}</h2>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-4">
                    <a href="/admin/products" class="btn btn-primary">Gerenciar Produtos</a>
                    <a href="/admin/orders" class="btn btn-success">Ver Pedidos</a>
                    <a href="/" class="btn btn-secondary">Voltar ao Site</a>
                </div>
            </div>
        </body>
        </html>
        '''
        return render_template_string(html, 
                                    total_products=total_products,
                                    total_orders=total_orders, 
                                    low_stock=low_stock_products)

# Simples e funcional
admin = Admin(app, name='Admin Visage', index_view=SimpleAdminView(name='Dashboard'))

# Views básicas que funcionam
class SimpleProductView(ModelView):
    column_list = ('name', 'price', 'stock_quantity', 'in_stock')
    form_excluded_columns = ('created_at', 'updated_at')

class SimpleOrderView(ModelView):
    column_list = ('id', 'customer_name', 'total_amount', 'status', 'created_at')
    can_create = False
    can_delete = False

# Adicionar views
admin.add_view(SimpleProductView(Product, db.session, name='Produtos'))
admin.add_view(SimpleOrderView(Order, db.session, name='Pedidos'))

print("Admin simples configurado!")