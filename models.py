from app import db
from datetime import datetime
from sqlalchemy import Text

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    in_stock = db.Column(db.Boolean, default=True)
    
    # Inventory Management Fields
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=5)  # Alert threshold
    max_stock_level = db.Column(db.Integer, default=100)
    cost_price = db.Column(db.Float, default=0.0)  # Purchase cost
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier = db.Column(db.String(100))
    sku = db.Column(db.String(50), unique=True)  # Stock Keeping Unit
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def __str__(self):
        return self.name
    
    @property
    def is_low_stock(self):
        """Check if product is below minimum stock level"""
        return self.stock_quantity <= self.min_stock_level
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            return ((self.price - self.cost_price) / self.price) * 100
        return 0
    
    def update_stock(self, quantity_change, reason="Manual adjustment"):
        """Update stock quantity and log the movement"""
        old_quantity = self.stock_quantity
        self.stock_quantity = max(0, self.stock_quantity + quantity_change)
        self.in_stock = self.stock_quantity > 0
        
        # Create stock movement record
        movement = StockMovement(
            product_id=self.id,
            movement_type='increase' if quantity_change > 0 else 'decrease',
            quantity=abs(quantity_change),
            old_quantity=old_quantity,
            new_quantity=self.stock_quantity,
            reason=reason
        )
        db.session.add(movement)
        return movement

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Product
    product = db.relationship('Product', backref='cart_items')
    
    def __repr__(self):
        return f'<CartItem {self.product.name} x{self.quantity}>'
    
    @property
    def total_price(self):
        return self.product.price * self.quantity

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    whatsapp_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order #{self.id} - {self.customer_name}>'

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    # Relationships
    order = db.relationship('Order', backref='items')
    product = db.relationship('Product', backref='order_items')
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # 'increase', 'decrease', 'adjustment'
    quantity = db.Column(db.Integer, nullable=False)
    old_quantity = db.Column(db.Integer, nullable=False)
    new_quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))  # Reason for movement
    reference_id = db.Column(db.String(50))  # Order ID, Purchase ID, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), default='Sistema')  # Who made the change
    
    # Relationships
    product = db.relationship('Product', backref='stock_movements')
    
    def __repr__(self):
        return f'<StockMovement {self.product.name}: {self.movement_type} {self.quantity}>'

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='supplier_info', foreign_keys='Product.supplier_id')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'

class StockAlert(db.Model):
    __tablename__ = 'stock_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    alert_type = db.Column(db.String(20), default='low_stock')  # 'low_stock', 'out_of_stock'
    message = db.Column(db.String(255))
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    product = db.relationship('Product', backref='alerts')
    
    def __repr__(self):
        return f'<StockAlert {self.product.name}: {self.alert_type}>'
