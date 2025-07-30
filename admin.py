from flask import url_for, redirect, request, flash
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from flask_admin.model.template import macro
from app import app, db
from models import Product, Order, OrderItem, StockMovement, Supplier, StockAlert
from wtforms import TextAreaField, IntegerField, SelectField, StringField
from wtforms.validators import NumberRange, DataRequired, Optional
from wtforms.widgets import TextArea
from markupsafe import Markup
from datetime import datetime, timedelta
import logging

class SecureAdminIndexView(AdminIndexView):
    """Custom admin index view with inventory dashboard"""
    
    @expose('/')
    def index(self):
        # Basic statistics
        total_products = Product.query.count()
        products_in_stock = Product.query.filter(Product.stock_quantity > 0).count()
        low_stock_products = Product.query.filter(Product.stock_quantity <= Product.min_stock_level).count()
        out_of_stock = Product.query.filter(Product.stock_quantity == 0).count()
        
        # Order statistics
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        
        # Stock value calculation
        total_stock_value = db.session.query(db.func.sum(Product.stock_quantity * Product.cost_price)).scalar() or 0
        total_retail_value = db.session.query(db.func.sum(Product.stock_quantity * Product.price)).scalar() or 0
        
        # Recent stock movements
        recent_movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(5).all()
        
        # Low stock alerts
        low_stock_alerts = Product.query.filter(Product.stock_quantity <= Product.min_stock_level).limit(10).all()
        
        try:
            return self.render('admin/index.html', 
                             total_products=total_products,
                             products_in_stock=products_in_stock,
                             low_stock_products=low_stock_products,
                             out_of_stock=out_of_stock,
                             total_orders=total_orders,
                             pending_orders=pending_orders,
                             total_stock_value=total_stock_value,
                             total_retail_value=total_retail_value,
                             recent_movements=recent_movements,
                             low_stock_alerts=low_stock_alerts)
        except Exception as e:
            logging.error(f"Erro ao carregar admin dashboard: {e}")
            return f"<h1>Dashboard Admin - Visage</h1><p>Erro: {str(e)}</p>"

class InventoryManagementView(BaseView):
    """
    Custom view for inventory management operations.
    
    This view provides functionality for:
    - Adjusting product stock levels
    - Recording stock movements with reasons
    - Creating stock alerts when levels are low
    """
    
    @expose('/')
    def index(self):
        """Redirect to the stock adjustment page by default"""
        return self.redirect(url_for('inventorymanagementview.adjust_stock'))
    
    @expose('/adjust-stock', methods=['GET', 'POST'])
    def adjust_stock(self):
        """
        Handle stock adjustments for products.
        
        POST: Process stock adjustment form submission
        GET: Display the stock adjustment form
        """
        if request.method == 'POST':
            try:
                # Validate product selection
                product_id = request.form.get('product_id')
                if not product_id:
                    flash('Por favor, selecione um produto.', 'error')
                    products = Product.query.order_by(Product.name).all()
                    return self.render('admin/adjust_stock.html', products=products)
                
                # Validate quantity
                try:
                    quantity_change = int(request.form.get('quantity_change', 0))
                    if quantity_change == 0:
                        flash('A quantidade não pode ser zero.', 'error')
                        products = Product.query.order_by(Product.name).all()
                        return self.render('admin/adjust_stock.html', products=products)
                except ValueError:
                    flash('A quantidade deve ser um número inteiro.', 'error')
                    products = Product.query.order_by(Product.name).all()
                    return self.render('admin/adjust_stock.html', products=products)
                
                # Get and validate reason
                reason = request.form.get('reason', '').strip() or 'Ajuste manual'
                
                # Find the product and adjust stock
                product = Product.query.get(product_id)
                if not product:
                    flash('Produto não encontrado!', 'error')
                    products = Product.query.order_by(Product.name).all()
                    return self.render('admin/adjust_stock.html', products=products)
                
                old_quantity = product.stock_quantity
                
                # Prevent negative stock
                if old_quantity + quantity_change < 0:
                    flash(f'Erro: Quantidade insuficiente. O produto {product.name} possui apenas {old_quantity} unidades em estoque.', 'error')
                else:
                    # Create the movement record with full details
                    movement_type = 'increase' if quantity_change > 0 else 'decrease'
                    
                    # Use the product's method to update stock and create movement
                    movement = product.update_stock(quantity_change, reason)
                    if movement:
                        movement.created_by = 'Admin'
                        movement.movement_type = movement_type  # Ensure correct movement type
                        db.session.add(movement)
                        db.session.commit()
                        
                        # Handle stock alerts creation/resolution
                        self._manage_stock_alerts(product)
                        
                        # Provide detailed success message
                        if quantity_change > 0:
                            flash(f'Estoque do produto {product.name} aumentado em {quantity_change} unidades. Novo estoque: {product.stock_quantity}', 'success')
                        else:
                            flash(f'Estoque do produto {product.name} reduzido em {abs(quantity_change)} unidades. Novo estoque: {product.stock_quantity}', 'success')
                    else:
                        flash('Erro ao criar registro de movimentação.', 'error')
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                logging.error(f"Erro ao ajustar estoque: {str(e)}\n{error_details}")
                db.session.rollback()
                flash(f'Erro ao processar o ajuste de estoque: {str(e)}', 'error')
        
        # Get products sorted by name for better UX
        products = Product.query.order_by(Product.name).all()
        return self.render('admin/adjust_stock.html', products=products)
    
    def _manage_stock_alerts(self, product):
        """
        Create or resolve stock alerts based on product stock levels
        
        Args:
            product: The Product instance to check
        """
        try:
            # Check if we need to create a stock alert
            if product.stock_quantity <= product.min_stock_level:
                # Check if alert already exists
                existing_alert = StockAlert.query.filter_by(
                    product_id=product.id, 
                    is_resolved=False
                ).first()
                
                if not existing_alert:
                    # Create new alert
                    alert = StockAlert(
                        product_id=product.id,
                        alert_type='low_stock' if product.stock_quantity > 0 else 'out_of_stock',
                        message=f'Estoque abaixo do nível mínimo ({product.min_stock_level})',
                        is_resolved=False
                    )
                    db.session.add(alert)
            else:
                # Resolve any existing alerts for this product
                StockAlert.query.filter_by(
                    product_id=product.id, 
                    is_resolved=False
                ).update({
                    'is_resolved': True,
                    'resolved_at': datetime.now(),
                    'resolution_note': 'Estoque normalizado'
                })
            
            db.session.commit()
        except Exception as e:
            logging.error(f"Erro ao gerenciar alertas: {str(e)}")
            # We don't raise the exception here to avoid breaking the main flow
            # if alert management fails

class ProductAdminView(ModelView):
    """Admin básico e funcional para produtos"""
    
    # Configuração básica para funcionamento
    can_create = True
    can_edit = True 
    can_delete = True
    
    # Campos na lista
    column_list = ('name', 'category', 'price', 'stock_quantity', 'in_stock')
    
    # Formatação das colunas  
    column_formatters = {
        'price': lambda v, c, m, p: f'R$ {m.price:.2f}' if m.price else 'R$ 0,00',
        'in_stock': lambda v, c, m, p: '✅' if m.in_stock else '❌'
    }
    
    # Labels em português
    column_labels = {
        'name': 'Nome',
        'category': 'Categoria',
        'price': 'Preço', 
        'stock_quantity': 'Estoque',
        'in_stock': 'Disponível'
    }
    
    # Campos do formulário sem problemas
    form_excluded_columns = ['created_at', 'updated_at']

class StockMovementAdminView(ModelView):
    """Admin básico para movimentações"""
    
    can_create = False
    can_edit = False
    can_delete = False
    
    column_list = ('created_at', 'product', 'movement_type', 'quantity')
    column_default_sort = ('created_at', True)
    
    column_labels = {
        'created_at': 'Data',
        'product': 'Produto',
        'movement_type': 'Tipo', 
        'quantity': 'Quantidade'
    }

class SupplierAdminView(ModelView):
    """Admin básico para fornecedores"""
    
    column_list = ('name', 'contact_person', 'phone', 'is_active')
    
    column_labels = {
        'name': 'Nome',
        'contact_person': 'Contato', 
        'phone': 'Telefone',
        'is_active': 'Ativo'
    }

class OrderAdminView(ModelView):
    """Admin básico para pedidos"""
    
    can_create = False
    can_edit = True
    can_delete = False
    
    column_list = ('id', 'customer_name', 'total_amount', 'status', 'created_at')
    column_default_sort = ('created_at', True)
    
    column_formatters = {
        'total_amount': lambda v, c, m, p: f'R$ {m.total_amount:.2f}' if m.total_amount else 'R$ 0,00'
    }
    
    column_labels = {
        'id': 'ID',
        'customer_name': 'Cliente',
        'total_amount': 'Total', 
        'status': 'Status',
        'created_at': 'Data'
    }

# Initialize Flask-Admin
admin = Admin(
    app, 
    name='Administração - Visage',
    template_mode='bootstrap4',
    index_view=SecureAdminIndexView(name='Dashboard')
)

# Add views
admin.add_view(ProductAdminView(Product, db.session, name='Produtos', category='Estoque'))
admin.add_view(StockMovementAdminView(StockMovement, db.session, name='Movimentações', category='Estoque'))
admin.add_view(SupplierAdminView(Supplier, db.session, name='Fornecedores', category='Estoque'))
admin.add_view(InventoryManagementView(name='Gerenciar Estoque', category='Estoque'))

admin.add_view(OrderAdminView(Order, db.session, name='Pedidos', category='Vendas'))

logging.info("Flask-Admin configurado com sucesso!")