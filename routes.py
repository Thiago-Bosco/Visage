from flask import render_template, redirect, url_for, flash, request, session
from app import app, db
from models import Product, CartItem, Order, OrderItem, StockMovement
from forms import CheckoutForm, AddToCartForm
import uuid
import urllib.parse
import logging

def get_session_id():
    """Get or create a session ID for the current user"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

@app.route('/')
def index():
    """Display the product catalog"""
    products = Product.query.filter(Product.stock_quantity > 0).all()
    cart_count = get_cart_count()
    return render_template('index.html', products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add a product to the shopping cart"""
    try:
        product = Product.query.get_or_404(product_id)
        session_id = get_session_id()
        
        # Get quantity from form
        quantity = request.form.get('quantity', 1, type=int)
        if quantity < 1:
            quantity = 1
        
        # Check stock availability
        if quantity > product.stock_quantity:
            flash(f'Apenas {product.stock_quantity} unidades disponíveis de {product.name}!', 'warning')
            return redirect(url_for('index'))
        
        if quantity > 99:
            quantity = 99
        
        # Check if item already exists in cart
        existing_item = CartItem.query.filter_by(
            session_id=session_id,
            product_id=product_id
        ).first()
        
        if existing_item:
            # Check total quantity doesn't exceed stock
            total_quantity = existing_item.quantity + quantity
            if total_quantity > product.stock_quantity:
                flash(f'Quantidade total excede estoque disponível! Máximo: {product.stock_quantity}', 'warning')
                return redirect(url_for('index'))
            existing_item.quantity = total_quantity
        else:
            cart_item = CartItem(
                session_id=session_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        flash(f'{product.name} adicionado ao carrinho!', 'success')
        logging.info(f"Produto {product.name} adicionado ao carrinho com sucesso")
        
    except Exception as e:
        logging.error(f"Erro ao adicionar produto ao carrinho: {e}")
        flash('Erro ao adicionar produto ao carrinho.', 'error')
    
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    """Display the shopping cart"""
    session_id = get_session_id()
    cart_items = CartItem.query.filter_by(session_id=session_id).all()
    
    total = sum(item.total_price for item in cart_items)
    cart_count = len(cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total, cart_count=cart_count)

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    """Remove an item from the cart"""
    session_id = get_session_id()
    cart_item = CartItem.query.filter_by(id=item_id, session_id=session_id).first_or_404()
    
    product_name = cart_item.product.name
    db.session.delete(cart_item)
    db.session.commit()
    
    flash(f'{product_name} removido do carrinho!', 'info')
    return redirect(url_for('cart'))

@app.route('/update_cart/<int:item_id>', methods=['POST'])
def update_cart(item_id):
    """Update the quantity of an item in the cart"""
    session_id = get_session_id()
    cart_item = CartItem.query.filter_by(id=item_id, session_id=session_id).first_or_404()
    
    new_quantity = request.form.get('quantity', type=int)
    if new_quantity and new_quantity > 0:
        cart_item.quantity = new_quantity
        db.session.commit()
        flash('Quantidade atualizada!', 'success')
    else:
        flash('Quantidade inválida!', 'error')
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Handle the checkout process"""
    session_id = get_session_id()
    cart_items = CartItem.query.filter_by(session_id=session_id).all()
    
    if not cart_items:
        flash('Seu carrinho está vazio!', 'warning')
        return redirect(url_for('index'))
    
    form = CheckoutForm()
    total = sum(item.total_price for item in cart_items)
    
    if form.validate_on_submit():
        # Create order
        order = Order(
            customer_name=form.customer_name.data,
            customer_phone=form.customer_phone.data,
            total_amount=total
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items and update stock
        for cart_item in cart_items:
            product = cart_item.product
            
            # Check stock availability before processing
            if cart_item.quantity > product.stock_quantity:
                flash(f'Estoque insuficiente para {product.name}. Apenas {product.stock_quantity} disponíveis.', 'error')
                return redirect(url_for('cart'))
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Update stock quantity using the model method
            movement = product.update_stock(-cart_item.quantity, f'Venda - Pedido #{order.id}')
            movement.reference_id = str(order.id)
        
        # Clear cart
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        db.session.commit()
        
        # Generate WhatsApp message
        whatsapp_url = generate_whatsapp_message(order)
        
        # Mark order as WhatsApp sent
        order.whatsapp_sent = True
        db.session.commit()
        
        flash('Pedido finalizado! Você será redirecionado para o WhatsApp.', 'success')
        return redirect(whatsapp_url)
    
    cart_count = len(cart_items)
    return render_template('checkout.html', form=form, cart_items=cart_items, 
                         total=total, cart_count=cart_count)

def generate_whatsapp_message(order):
    """Generate WhatsApp URL with order details"""
    # WhatsApp number do vendedor
    whatsapp_number = "5519981896803"
    
    # Build message
    message = f"🎯 *NOVO PEDIDO - BARBEARIA*\n\n"
    message += f"👤 *Cliente:* {order.customer_name}\n"
    
    if order.customer_phone:
        message += f"📱 *Telefone:* {order.customer_phone}\n"
    
    message += f"📝 *Pedido #{order.id}*\n\n"
    message += "*🛍️ PRODUTOS:*\n"
    
    for item in order.items:
        message += f"• {item.product.name}\n"
        message += f"  Qtd: {item.quantity}x | R$ {item.unit_price:.2f} cada\n"
        message += f"  Subtotal: R$ {item.total_price:.2f}\n\n"
    
    message += f"💰 *TOTAL: R$ {order.total_amount:.2f}*\n\n"
    message += "✅ Pedido confirmado! Aguardo contato para combinar entrega/retirada."
    
    # Encode message for URL
    encoded_message = urllib.parse.quote(message)
    
    # Generate WhatsApp URL
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
    
    logging.info(f"WhatsApp URL generated for order {order.id}: {whatsapp_url}")
    
    return whatsapp_url

def get_cart_count():
    """Get the number of items in the current user's cart"""
    session_id = get_session_id()
    return CartItem.query.filter_by(session_id=session_id).count()

@app.context_processor
def inject_cart_count():
    """Make cart count available in all templates"""
    return dict(cart_count=get_cart_count())

@app.route('/clear_cart')
def clear_cart():
    """Clear all items from the cart"""
    session_id = get_session_id()
    CartItem.query.filter_by(session_id=session_id).delete()
    db.session.commit()
    
    flash('Carrinho limpo!', 'info')
    return redirect(url_for('cart'))
