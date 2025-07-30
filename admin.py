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
    """Enhanced admin view for Product model with inventory features"""
    
    # List view configuration
    column_list = ['image_url', 'name', 'category', 'price', 'cost_price', 'stock_quantity', 'min_stock_level', 'profit_margin', 'supplier', 'sku', 'in_stock']
    column_searchable_list = ['name', 'description', 'category', 'supplier', 'sku']
    column_filters = ['category', 'in_stock', 'supplier', 'created_at']
    column_sortable_list = ['id', 'name', 'category', 'price', 'cost_price', 'stock_quantity', 'min_stock_level', 'created_at']
    column_default_sort = ('created_at', True)
    
    # Form configuration
    form_columns = ['name', 'description', 'price', 'cost_price', 'stock_quantity', 'min_stock_level', 'max_stock_level', 
                   'supplier', 'sku', 'image_url', 'category', 'in_stock']
    
    form_extra_fields = {
        'stock_adjustment': IntegerField('Ajuste de Estoque', 
                                       description='Digite um número positivo para adicionar ou negativo para remover estoque',
                                       validators=[Optional()]),
        'adjustment_reason': StringField('Motivo do Ajuste', 
                                       description='Descreva o motivo do ajuste de estoque',
                                       validators=[Optional()])
    }
    
    form_widget_args = {
        'description': {'rows': 5},
        'price': {'step': '0.01'},
        'cost_price': {'step': '0.01'},
        'stock_quantity': {'min': 0},
        'min_stock_level': {'min': 0},
        'max_stock_level': {'min': 1}
    }
    
    # Custom formatting
    column_formatters = {
        'price': lambda v, c, m, p: f'R$ {m.price:.2f}',
        'cost_price': lambda v, c, m, p: f'R$ {m.cost_price:.2f}',
        'profit_margin': lambda v, c, m, p: f'{m.profit_margin:.1f}%',
        'stock_quantity': lambda v, c, m, p: f'<span class="badge bg-{"danger" if m.stock_quantity <= m.min_stock_level else "warning" if m.stock_quantity <= m.min_stock_level * 2 else "success"}">{m.stock_quantity}</span>',
        'in_stock': lambda v, c, m, p: '✅ Sim' if m.in_stock else '❌ Não',
        'name': lambda v, c, m, p: f'<strong>{m.name}</strong>' if m.in_stock else f'<span class="text-muted">{m.name}</span>',
        'image_url': lambda v, c, m, p: f'<img src="{m.image_url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" alt="{m.name}">' if m.image_url else 'Sem imagem'
    }
    
    column_labels = {
        'id': 'ID',
        'name': 'Nome',
        'category': 'Categoria',
        'price': 'Preço de Venda',
        'cost_price': 'Preço de Custo',
        'stock_quantity': 'Estoque Atual',
        'min_stock_level': 'Estoque Mínimo',
        'max_stock_level': 'Estoque Máximo',
        'profit_margin': 'Margem (%)',
        'supplier': 'Fornecedor',
        'sku': 'SKU',
        'in_stock': 'Disponível',
        'created_at': 'Criado em',
        'updated_at': 'Atualizado em',
        'description': 'Descrição',
        'image_url': 'Imagem'
    }
    
    def on_model_change(self, form, model, is_created):
        """Handle stock adjustments on product update"""
        if hasattr(form, 'stock_adjustment') and form.stock_adjustment.data:
            adjustment = form.stock_adjustment.data
            reason = form.adjustment_reason.data or 'Ajuste via admin'
            
            if not is_created:
                # Create stock movement
                movement = StockMovement(
                    product_id=model.id,
                    movement_type='increase' if adjustment > 0 else 'decrease',
                    quantity=abs(adjustment),
                    old_quantity=model.stock_quantity,
                    new_quantity=model.stock_quantity + adjustment,
                    reason=reason,
                    created_by='Admin'
                )
                model.stock_quantity = max(0, model.stock_quantity + adjustment)
                model.in_stock = model.stock_quantity > 0
                db.session.add(movement)
        
        # Auto-update in_stock based on quantity
        model.in_stock = model.stock_quantity > 0
    
    # Enable features
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True
    page_size = 20

class StockMovementAdminView(ModelView):
    """Admin view for Stock Movement tracking"""
    
    column_list = ['created_at', 'product', 'movement_type', 'quantity', 'old_quantity', 'new_quantity', 'reason', 'created_by']
    column_searchable_list = ['reason', 'created_by']
    column_filters = ['movement_type', 'created_at', 'created_by']
    column_sortable_list = ['created_at', 'movement_type', 'quantity']
    column_default_sort = ('created_at', True)
    
    column_formatters = {
        'movement_type': lambda v, c, m, p: f'<span class="badge bg-{"success" if m.movement_type == "increase" else "danger"}">{m.movement_type.title()}</span>',
        'quantity': lambda v, c, m, p: f'+{m.quantity}' if m.movement_type == 'increase' else f'-{m.quantity}',
        'created_at': lambda v, c, m, p: m.created_at.strftime('%d/%m/%Y %H:%M')
    }
    
    column_labels = {
        'created_at': 'Data/Hora',
        'product': 'Produto',
        'movement_type': 'Tipo',
        'quantity': 'Quantidade',
        'old_quantity': 'Estoque Anterior',
        'new_quantity': 'Estoque Atual',
        'reason': 'Motivo',
        'created_by': 'Criado por'
    }
    
    # Read-only view
    can_create = False
    can_edit = False
    can_delete = False
    can_export = True
    page_size = 50

class SupplierAdminView(ModelView):
    """Admin view for Supplier management"""
    
    column_list = ['name', 'contact_person', 'email', 'phone', 'is_active', 'created_at']
    column_searchable_list = ['name', 'contact_person', 'email', 'phone']
    column_filters = ['is_active', 'created_at']
    column_sortable_list = ['name', 'contact_person', 'created_at']
    
    column_formatters = {
        'is_active': lambda v, c, m, p: '✅ Ativo' if m.is_active else '❌ Inativo',
        'created_at': lambda v, c, m, p: m.created_at.strftime('%d/%m/%Y')
    }
    
    column_labels = {
        'name': 'Nome',
        'contact_person': 'Pessoa de Contato',
        'email': 'E-mail',
        'phone': 'Telefone',
        'address': 'Endereço',
        'is_active': 'Status',
        'created_at': 'Criado em'
    }
    
    form_columns = ['name', 'contact_person', 'email', 'phone', 'address', 'is_active']
    
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True

class OrderAdminView(ModelView):
    """Admin view for Order model"""
    
    column_list = ['id', 'customer_name', 'customer_phone', 'total_amount', 'status', 'whatsapp_sent', 'created_at']
    column_searchable_list = ['customer_name', 'customer_phone']
    column_filters = ['status', 'whatsapp_sent', 'created_at']
    column_sortable_list = ['id', 'customer_name', 'total_amount', 'created_at']
    column_default_sort = ('created_at', True)
    
    column_formatters = {
        'total_amount': lambda v, c, m, p: f'R$ {m.total_amount:.2f}',
        'status': lambda v, c, m, p: f'<span class="badge bg-{"success" if m.status == "completed" else "warning" if m.status == "pending" else "danger"}">{m.status.title()}</span>',
        'whatsapp_sent': lambda v, c, m, p: '✅ Sim' if m.whatsapp_sent else '❌ Não',
        'created_at': lambda v, c, m, p: m.created_at.strftime('%d/%m/%Y %H:%M')
    }
    
    column_labels = {
        'id': 'ID',
        'customer_name': 'Cliente',
        'customer_phone': 'Telefone',
        'total_amount': 'Total',
        'status': 'Status',
        'whatsapp_sent': 'WhatsApp Enviado',
        'created_at': 'Data do Pedido'
    }
    
    form_columns = ['customer_name', 'customer_phone', 'status']
    
    can_create = False
    can_edit = True
    can_delete = True
    can_export = True
    page_size = 20

# Initialize Flask-Admin
admin = Admin(
    app, 
    name='Administração - Visage',
    template_mode='bootstrap4',
    base_template='admin/layout.html',
    index_view=SecureAdminIndexView(name='Dashboard')
)

# Add views
admin.add_view(ProductAdminView(Product, db.session, name='Produtos', category='Estoque'))
admin.add_view(StockMovementAdminView(StockMovement, db.session, name='Movimentações', category='Estoque'))
admin.add_view(SupplierAdminView(Supplier, db.session, name='Fornecedores', category='Estoque'))
admin.add_view(InventoryManagementView(name='Gerenciar Estoque', category='Estoque'))

admin.add_view(OrderAdminView(Order, db.session, name='Pedidos', category='Vendas'))

logging.info("Flask-Admin configurado com sucesso!")