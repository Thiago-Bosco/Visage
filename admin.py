from flask import url_for, redirect, request, flash
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from app import app, db
from models import Product, Order, OrderItem
import logging

class SecureAdminIndexView(AdminIndexView):
    """Custom admin index view with dashboard statistics"""
    
    @expose('/')
    def index(self):
        # Get statistics
        total_products = Product.query.count()
        products_in_stock = Product.query.filter_by(in_stock=True).count()
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        
        return self.render('admin/index.html', 
                         total_products=total_products,
                         products_in_stock=products_in_stock,
                         total_orders=total_orders,
                         pending_orders=pending_orders)

class ProductAdminView(ModelView):
    """Admin view for Product model"""
    
    # List view configuration
    column_list = ['image_url', 'name', 'category', 'price', 'in_stock', 'created_at']
    column_searchable_list = ['name', 'description', 'category']
    column_filters = ['category', 'in_stock', 'created_at']
    column_sortable_list = ['id', 'name', 'category', 'price', 'created_at']
    column_default_sort = ('created_at', True)
    
    # Form configuration
    form_columns = ['name', 'description', 'price', 'image_url', 'category', 'in_stock']
    form_widget_args = {
        'description': {
            'rows': 5,
        },
        'price': {
            'step': '0.01'
        }
    }
    
    # Custom formatting
    column_formatters = {
        'price': lambda v, c, m, p: f'R$ {m.price:.2f}',
        'in_stock': lambda v, c, m, p: '✅ Sim' if m.in_stock else '❌ Não',
        'name': lambda v, c, m, p: f'<strong>{m.name}</strong>' if m.in_stock else f'<span class="text-muted">{m.name}</span>',
        'image_url': lambda v, c, m, p: f'<img src="{m.image_url}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;" alt="{m.name}">' if m.image_url else 'Sem imagem'
    }
    column_labels = {
        'id': 'ID',
        'name': 'Nome',
        'category': 'Categoria',
        'price': 'Preço',
        'in_stock': 'Em Estoque',
        'created_at': 'Criado em',
        'description': 'Descrição',
        'image_url': 'Imagem'
    }
    
    # Enable creation and editing
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True
    
    # Page size
    page_size = 20

class OrderAdminView(ModelView):
    """Admin view for Order model"""
    
    # List view configuration
    column_list = ['id', 'customer_name', 'customer_phone', 'total_amount', 'status', 'whatsapp_sent', 'created_at']
    column_searchable_list = ['customer_name', 'customer_phone']
    column_filters = ['status', 'whatsapp_sent', 'created_at']
    column_sortable_list = ['id', 'customer_name', 'total_amount', 'created_at']
    column_default_sort = ('created_at', True)
    
    # Custom formatting
    column_formatters = {
        'total_amount': lambda v, c, m, p: f'R$ {m.total_amount:.2f}',
        'whatsapp_sent': lambda v, c, m, p: '✅ Sim' if m.whatsapp_sent else '❌ Não',
        'status': lambda v, c, m, p: {
            'pending': '⏳ Pendente',
            'confirmed': '✅ Confirmado',
            'completed': '🏁 Finalizado',
            'cancelled': '❌ Cancelado'
        }.get(m.status, m.status)
    }
    
    column_labels = {
        'id': 'Pedido #',
        'customer_name': 'Nome do Cliente',
        'customer_phone': 'Telefone',
        'total_amount': 'Valor Total',
        'status': 'Status',
        'whatsapp_sent': 'WhatsApp Enviado',
        'created_at': 'Data do Pedido'
    }
    
    # Form configuration
    form_columns = ['customer_name', 'customer_phone', 'status']
    form_choices = {
        'status': [
            ('pending', 'Pendente'),
            ('confirmed', 'Confirmado'),
            ('completed', 'Finalizado'),
            ('cancelled', 'Cancelado')
        ]
    }
    
    # Permissions
    can_create = False  # Orders are created through the checkout process
    can_edit = True
    can_delete = False  # Don't allow deleting orders
    can_export = True
    
    # Page size
    page_size = 20
    
    # Custom details view to show order items
    def _details_formatter(self, context, model, name):
        """Format order details with items"""
        if name == 'items':
            items_html = '<ul>'
            for item in model.items:
                items_html += f'<li>{item.product.name} - Qtd: {item.quantity} - R$ {item.total_price:.2f}</li>'
            items_html += '</ul>'
            return items_html
        return super()._details_formatter(context, model, name)

class OrderItemAdminView(ModelView):
    """Admin view for OrderItem model"""
    
    # List view configuration
    column_list = ['id', 'order_id', 'product', 'quantity', 'unit_price', 'total_price']
    column_searchable_list = ['order.customer_name', 'product.name']
    column_filters = ['order_id', 'product_id']
    column_sortable_list = ['id', 'order_id', 'quantity', 'unit_price']
    
    # Custom formatting
    column_formatters = {
        'unit_price': lambda v, c, m, p: f'R$ {m.unit_price:.2f}',
        'total_price': lambda v, c, m, p: f'R$ {m.total_price:.2f}',
        'product': lambda v, c, m, p: m.product.name if m.product else 'N/A'
    }
    
    column_labels = {
        'id': 'ID',
        'order_id': 'Pedido #',
        'product': 'Produto',
        'quantity': 'Quantidade',
        'unit_price': 'Preço Unitário',
        'total_price': 'Total'
    }
    
    # Permissions
    can_create = False
    can_edit = False
    can_delete = False
    can_export = True
    
    # Page size
    page_size = 50

# Initialize Flask-Admin
admin = Admin(
    app, 
    name='Administração - Barbearia Premium',
    template_mode='bootstrap4',
    index_view=SecureAdminIndexView(name='Dashboard'),
    base_template='admin/base.html',
    static_url_path='/admin/static'
)

# Add model views
admin.add_view(ProductAdminView(Product, db.session, name='Produtos', category='Catálogo'))
admin.add_view(OrderAdminView(Order, db.session, name='Pedidos', category='Vendas'))
admin.add_view(OrderItemAdminView(OrderItem, db.session, name='Itens dos Pedidos', category='Vendas'))

logging.info("Flask-Admin configurado com sucesso!")
