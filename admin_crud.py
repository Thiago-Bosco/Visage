from flask import render_template_string, request, redirect, url_for, flash, Blueprint, send_from_directory
from werkzeug.utils import secure_filename
from app import app, db
from models import Product, Order, StockMovement, Supplier, OrderItem
from datetime import datetime
import os
import uuid

# Criar blueprint para o admin
admin_bp = Blueprint('admin_crud', __name__, url_prefix='/admin')

# Configuração para upload de imagens
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Criar diretório de upload se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/')
def index():
    # Dashboard completo
    total_products = Product.query.count()
    total_orders = Order.query.count()
    low_stock_products = Product.query.filter(Product.stock_quantity <= 5).count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin CRUD - Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link" href="/admin/products">Produtos</a>
                    <a class="nav-link" href="/admin/orders">Pedidos</a>
                    <a class="nav-link" href="/admin/suppliers">Fornecedores</a>
                    <a class="nav-link" href="/">Site</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1><i class="fas fa-tachometer-alt"></i> Dashboard</h1>
            
            <div class="row mt-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-box fa-2x mb-2"></i>
                            <h5>Produtos</h5>
                            <h2>{{ total_products }}</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-shopping-cart fa-2x mb-2"></i>
                            <h5>Pedidos</h5>
                            <h2>{{ total_orders }}</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                            <h5>Estoque Baixo</h5>
                            <h2>{{ low_stock }}</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-chart-line fa-2x mb-2"></i>
                            <h5>Vendas Hoje</h5>
                            <h2>R$ 0</h2>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-5">
                <div class="col-md-8">
                    <h3>Ações Rápidas</h3>
                    <div class="list-group">
                        <a href="/admin/products/new" class="list-group-item list-group-item-action">
                            <i class="fas fa-plus text-primary"></i> Adicionar Novo Produto
                        </a>
                        <a href="/admin/products" class="list-group-item list-group-item-action">
                            <i class="fas fa-edit text-success"></i> Gerenciar Produtos
                        </a>
                        <a href="/admin/orders" class="list-group-item list-group-item-action">
                            <i class="fas fa-list text-info"></i> Ver Todos os Pedidos
                        </a>
                        <a href="/admin/suppliers" class="list-group-item list-group-item-action">
                            <i class="fas fa-truck text-warning"></i> Gerenciar Fornecedores
                        </a>
                    </div>
                </div>
                <div class="col-md-4">
                    <h3>Pedidos Recentes</h3>
                    <div class="list-group">
                        {% for order in recent_orders %}
                        <div class="list-group-item">
                            <strong>#{{ order.id }}</strong> - {{ order.customer_name }}<br>
                            <small class="text-muted">R$ {{ "%.2f"|format(order.total_amount) }}</small>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, 
                                total_products=total_products,
                                total_orders=total_orders, 
                                low_stock=low_stock_products,
                                recent_orders=recent_orders)

@admin_bp.route('/products')
def products_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Produtos - Admin Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link active" href="/admin/products">Produtos</a>
                    <a class="nav-link" href="/admin/orders">Pedidos</a>
                    <a class="nav-link" href="/admin/suppliers">Fornecedores</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1><i class="fas fa-box"></i> Gerenciar Produtos</h1>
                <a href="/admin/products/new" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Novo Produto
                </a>
            </div>
            
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead class="table-dark">
                        <tr>
                            <th>Imagem</th>
                            <th>Nome</th>
                            <th>Categoria</th>
                            <th>Preço</th>
                            <th>Estoque</th>
                            <th>Status</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for product in products.items %}
                        <tr>
                            <td>
                                {% if product.image_url %}
                                    <img src="{{ product.image_url }}" alt="{{ product.name }}" 
                                         style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;">
                                {% else %}
                                    <div class="bg-secondary text-white d-flex align-items-center justify-content-center"
                                         style="width: 50px; height: 50px; border-radius: 8px;">
                                        <i class="fas fa-image"></i>
                                    </div>
                                {% endif %}
                            </td>
                            <td><strong>{{ product.name }}</strong></td>
                            <td><span class="badge bg-info">{{ product.category or 'Sem categoria' }}</span></td>
                            <td><strong>R$ {{ "%.2f"|format(product.price) }}</strong></td>
                            <td>
                                <span class="badge bg-{% if product.stock_quantity <= 5 %}danger{% elif product.stock_quantity <= 10 %}warning{% else %}success{% endif %}">
                                    {{ product.stock_quantity }}
                                </span>
                            </td>
                            <td>
                                {% if product.in_stock %}
                                    <span class="badge bg-success">Disponível</span>
                                {% else %}
                                    <span class="badge bg-danger">Indisponível</span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <a href="/admin/products/edit/{{ product.id }}" class="btn btn-outline-primary">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <a href="/admin/products/delete/{{ product.id }}" class="btn btn-outline-danger"
                                       onclick="return confirm('Tem certeza que deseja excluir este produto?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, products=products)

@admin_bp.route('/products/new', methods=['GET', 'POST'])
def products_new():
    if request.method == 'POST':
        try:
            image_url = request.form.get('image_url')
            
            # Verificar se há upload de imagem
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename != '' and allowed_file(file.filename):
                    # Gerar nome único para o arquivo
                    filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    image_url = f'/static/uploads/{filename}'
            
            # Criar novo produto
            product = Product(
                name=request.form.get('name'),
                description=request.form.get('description'),
                price=float(request.form.get('price', 0)),
                cost_price=float(request.form.get('cost_price', 0)),
                stock_quantity=int(request.form.get('stock_quantity', 0)),
                min_stock_level=int(request.form.get('min_stock_level', 5)),
                max_stock_level=int(request.form.get('max_stock_level', 100)),
                supplier=request.form.get('supplier'),
                sku=request.form.get('sku'),
                image_url=image_url,
                category=request.form.get('category'),
                in_stock=request.form.get('in_stock') == 'on'
            )
            
            db.session.add(product)
            db.session.commit()
            
            flash('Produto criado com sucesso!', 'success')
            return redirect(url_for('admin_crud.products_list'))
            
        except Exception as e:
            flash(f'Erro ao criar produto: {str(e)}', 'error')
            db.session.rollback()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Novo Produto - Admin Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link active" href="/admin/products">Produtos</a>
                    <a class="nav-link" href="/admin/orders">Pedidos</a>
                    <a class="nav-link" href="/admin/suppliers">Fornecedores</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1><i class="fas fa-plus"></i> Novo Produto</h1>
                <a href="/admin/products" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="row">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-body">
                            <form method="POST" enctype="multipart/form-data">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Nome do Produto *</label>
                                            <input type="text" class="form-control" name="name" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Categoria</label>
                                            <select class="form-control" name="category">
                                                <option value="">Selecione uma categoria</option>
                                                <option value="Pomadas">Pomadas</option>
                                                <option value="Óleos">Óleos</option>
                                                <option value="Shampoos">Shampoos</option>
                                                <option value="Ceras">Ceras</option>
                                                <option value="Pós-Barba">Pós-Barba</option>
                                                <option value="Kits">Kits</option>
                                                <option value="Outros">Outros</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Descrição</label>
                                    <textarea class="form-control" name="description" rows="3"></textarea>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Preço de Venda (R$) *</label>
                                            <input type="number" class="form-control" name="price" step="0.01" min="0" required>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Preço de Custo (R$)</label>
                                            <input type="number" class="form-control" name="cost_price" step="0.01" min="0" value="0">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">SKU</label>
                                            <input type="text" class="form-control" name="sku">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Estoque Atual</label>
                                            <input type="number" class="form-control" name="stock_quantity" min="0" value="0">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Estoque Mínimo</label>
                                            <input type="number" class="form-control" name="min_stock_level" min="0" value="5">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Estoque Máximo</label>
                                            <input type="number" class="form-control" name="max_stock_level" min="1" value="100">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Fornecedor</label>
                                    <input type="text" class="form-control" name="supplier">
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Imagem do Produto</label>
                                            <input type="file" class="form-control" name="image_file" accept="image/*" onchange="previewImage(this)">
                                            <small class="form-text text-muted">Selecione uma imagem (PNG, JPG, JPEG, GIF, WEBP)</small>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">OU URL da Imagem</label>
                                            <input type="url" class="form-control" name="image_url" placeholder="https://exemplo.com/imagem.jpg">
                                            <small class="form-text text-muted">Deixe em branco se usar upload</small>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3" id="imagePreview" style="display: none;">
                                    <label class="form-label">Preview da Imagem:</label>
                                    <br>
                                    <img id="preview" src="" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px;">
                                </div>
                                
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="in_stock" id="in_stock" checked>
                                        <label class="form-check-label" for="in_stock">
                                            Produto disponível para venda
                                        </label>
                                    </div>
                                </div>
                                
                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <a href="/admin/products" class="btn btn-secondary me-md-2">Cancelar</a>
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-save"></i> Salvar Produto
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function previewImage(input) {
                if (input.files && input.files[0]) {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('preview').src = e.target.result;
                        document.getElementById('imagePreview').style.display = 'block';
                    }
                    reader.readAsDataURL(input.files[0]);
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def products_edit(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            image_url = request.form.get('image_url')
            
            # Verificar se há upload de nova imagem
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file and file.filename != '' and allowed_file(file.filename):
                    # Gerar nome único para o arquivo
                    filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    image_url = f'/static/uploads/{filename}'
                    
                    # Remover imagem antiga se for local
                    if product.image_url and '/static/uploads/' in product.image_url:
                        old_file = product.image_url.replace('/static/uploads/', '')
                        old_path = os.path.join(UPLOAD_FOLDER, old_file)
                        if os.path.exists(old_path):
                            os.remove(old_path)
            
            # Atualizar produto
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.price = float(request.form.get('price', 0))
            product.cost_price = float(request.form.get('cost_price', 0))
            product.stock_quantity = int(request.form.get('stock_quantity', 0))
            product.min_stock_level = int(request.form.get('min_stock_level', 5))
            product.max_stock_level = int(request.form.get('max_stock_level', 100))
            product.supplier = request.form.get('supplier')
            product.sku = request.form.get('sku')
            product.image_url = image_url or product.image_url  # Manter imagem atual se não houver nova
            product.category = request.form.get('category')
            product.in_stock = request.form.get('in_stock') == 'on'
            product.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('admin_crud.products_list'))
            
        except Exception as e:
            flash(f'Erro ao atualizar produto: {str(e)}', 'error')
            db.session.rollback()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Editar Produto - Admin Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link active" href="/admin/products">Produtos</a>
                    <a class="nav-link" href="/admin/orders">Pedidos</a>
                    <a class="nav-link" href="/admin/suppliers">Fornecedores</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1><i class="fas fa-edit"></i> Editar: {{ product.name }}</h1>
                <a href="/admin/products" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="row">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-body">
                            <form method="POST" enctype="multipart/form-data">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Nome do Produto *</label>
                                            <input type="text" class="form-control" name="name" value="{{ product.name }}" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Categoria</label>
                                            <select class="form-control" name="category">
                                                <option value="">Selecione uma categoria</option>
                                                <option value="Pomadas" {{ 'selected' if product.category == 'Pomadas' }}>Pomadas</option>
                                                <option value="Óleos" {{ 'selected' if product.category == 'Óleos' }}>Óleos</option>
                                                <option value="Shampoos" {{ 'selected' if product.category == 'Shampoos' }}>Shampoos</option>
                                                <option value="Ceras" {{ 'selected' if product.category == 'Ceras' }}>Ceras</option>
                                                <option value="Pós-Barba" {{ 'selected' if product.category == 'Pós-Barba' }}>Pós-Barba</option>
                                                <option value="Kits" {{ 'selected' if product.category == 'Kits' }}>Kits</option>
                                                <option value="Outros" {{ 'selected' if product.category == 'Outros' }}>Outros</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Descrição</label>
                                    <textarea class="form-control" name="description" rows="3">{{ product.description or '' }}</textarea>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Preço de Venda (R$) *</label>
                                            <input type="number" class="form-control" name="price" step="0.01" min="0" value="{{ product.price }}" required>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Preço de Custo (R$)</label>
                                            <input type="number" class="form-control" name="cost_price" step="0.01" min="0" value="{{ product.cost_price or 0 }}">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">SKU</label>
                                            <input type="text" class="form-control" name="sku" value="{{ product.sku or '' }}">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Estoque Atual</label>
                                            <input type="number" class="form-control" name="stock_quantity" min="0" value="{{ product.stock_quantity }}">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Estoque Mínimo</label>
                                            <input type="number" class="form-control" name="min_stock_level" min="0" value="{{ product.min_stock_level }}">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label class="form-label">Estoque Máximo</label>
                                            <input type="number" class="form-control" name="max_stock_level" min="1" value="{{ product.max_stock_level }}">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Fornecedor</label>
                                    <input type="text" class="form-control" name="supplier" value="{{ product.supplier or '' }}">
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Nova Imagem</label>
                                            <input type="file" class="form-control" name="image_file" accept="image/*" onchange="previewImage(this)">
                                            <small class="form-text text-muted">Deixe em branco para manter imagem atual</small>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">OU URL da Imagem</label>
                                            <input type="url" class="form-control" name="image_url" value="{{ product.image_url or '' }}">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3" id="imagePreview" style="display: none;">
                                    <label class="form-label">Preview da Nova Imagem:</label>
                                    <br>
                                    <img id="preview" src="" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px;">
                                </div>
                                
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="in_stock" id="in_stock" {{ 'checked' if product.in_stock }}>
                                        <label class="form-check-label" for="in_stock">
                                            Produto disponível para venda
                                        </label>
                                    </div>
                                </div>
                                
                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <a href="/admin/products" class="btn btn-secondary me-md-2">Cancelar</a>
                                    <button type="submit" class="btn btn-primary">
                                        <i class="fas fa-save"></i> Salvar Alterações
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>Preview da Imagem</h5>
                        </div>
                        <div class="card-body text-center">
                            {% if product.image_url %}
                                <img src="{{ product.image_url }}" alt="{{ product.name }}" 
                                     class="img-fluid rounded" style="max-height: 200px;">
                            {% else %}
                                <div class="bg-light d-flex align-items-center justify-content-center" 
                                     style="height: 200px; border-radius: 8px;">
                                    <i class="fas fa-image fa-3x text-muted"></i>
                                </div>
                                <p class="text-muted mt-2">Nenhuma imagem</p>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function previewImage(input) {
                if (input.files && input.files[0]) {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('preview').src = e.target.result;
                        document.getElementById('imagePreview').style.display = 'block';
                    }
                    reader.readAsDataURL(input.files[0]);
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html, product=product)

@admin_bp.route('/products/delete/<int:id>')
def products_delete(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir produto: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_crud.products_list'))

@admin_bp.route('/orders')
def orders_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    orders = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pedidos - Admin Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link" href="/admin/products">Produtos</a>
                    <a class="nav-link active" href="/admin/orders">Pedidos</a>
                    <a class="nav-link" href="/admin/suppliers">Fornecedores</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1><i class="fas fa-shopping-cart"></i> Gerenciar Pedidos</h1>
            
            <div class="table-responsive mt-4">
                <table class="table table-striped">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Cliente</th>
                            <th>Telefone</th>
                            <th>Total</th>
                            <th>Status</th>
                            <th>WhatsApp</th>
                            <th>Data</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for order in orders.items %}
                        <tr>
                            <td><strong>#{{ order.id }}</strong></td>
                            <td>{{ order.customer_name }}</td>
                            <td>{{ order.customer_phone or '-' }}</td>
                            <td><strong>R$ {{ "%.2f"|format(order.total_amount) }}</strong></td>
                            <td>
                                <span class="badge bg-{% if order.status == 'completed' %}success{% elif order.status == 'pending' %}warning{% else %}danger{% endif %}">
                                    {{ order.status.title() }}
                                </span>
                            </td>
                            <td>
                                {% if order.whatsapp_sent %}
                                    <i class="fas fa-check-circle text-success"></i>
                                {% else %}
                                    <i class="fas fa-times-circle text-danger"></i>
                                {% endif %}
                            </td>
                            <td>{{ order.created_at.strftime('%d/%m/%Y %H:%M') }}</td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <a href="/admin/orders/view/{{ order.id }}" class="btn btn-outline-info">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                    <a href="/admin/orders/edit/{{ order.id }}" class="btn btn-outline-primary">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, orders=orders)

@admin_bp.route('/orders/view/<int:id>')
def orders_view(id):
    order = Order.query.get_or_404(id)
    order_items = OrderItem.query.filter_by(order_id=id).all()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ver Pedido #{{ order.id }} - Admin Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link" href="/admin/products">Produtos</a>
                    <a class="nav-link active" href="/admin/orders">Pedidos</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1><i class="fas fa-eye"></i> Pedido #{{ order.id }}</h1>
                <a href="/admin/orders" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Informações do Cliente</h5>
                        </div>
                        <div class="card-body">
                            <p><strong>Nome:</strong> {{ order.customer_name }}</p>
                            <p><strong>Telefone:</strong> {{ order.customer_phone or 'Não informado' }}</p>
                            <p><strong>Email:</strong> {{ order.customer_email or 'Não informado' }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Informações do Pedido</h5>
                        </div>
                        <div class="card-body">
                            <p><strong>Status:</strong> 
                                <span class="badge bg-{% if order.status == 'completed' %}success{% elif order.status == 'pending' %}warning{% else %}danger{% endif %}">
                                    {{ order.status.title() }}
                                </span>
                            </p>
                            <p><strong>Total:</strong> R$ {{ "%.2f"|format(order.total_amount) }}</p>
                            <p><strong>Data:</strong> {{ order.created_at.strftime('%d/%m/%Y %H:%M') }}</p>
                            <p><strong>WhatsApp:</strong> 
                                {% if order.whatsapp_sent %}
                                    <i class="fas fa-check-circle text-success"></i> Enviado
                                {% else %}
                                    <i class="fas fa-times-circle text-danger"></i> Não enviado
                                {% endif %}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Itens do Pedido</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Produto</th>
                                    <th>Quantidade</th>
                                    <th>Preço Unitário</th>
                                    <th>Subtotal</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in order_items %}
                                <tr>
                                    <td>{{ item.product_name }}</td>
                                    <td>{{ item.quantity }}</td>
                                    <td>R$ {{ "%.2f"|format(item.unit_price) }}</td>
                                    <td>R$ {{ "%.2f"|format(item.quantity * item.unit_price) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                            <tfoot>
                                <tr class="table-dark">
                                    <th colspan="3">Total:</th>
                                    <th>R$ {{ "%.2f"|format(order.total_amount) }}</th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, order=order, order_items=order_items)

@admin_bp.route('/orders/edit/<int:id>', methods=['GET', 'POST'])
def orders_edit(id):
    order = Order.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            order.status = request.form.get('status')
            order.customer_name = request.form.get('customer_name')
            order.customer_phone = request.form.get('customer_phone')
            order.customer_email = request.form.get('customer_email')
            
            db.session.commit()
            flash('Pedido atualizado com sucesso!', 'success')
            return redirect(url_for('admin_crud.orders_list'))
        except Exception as e:
            flash(f'Erro ao atualizar pedido: {str(e)}', 'error')
            db.session.rollback()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Editar Pedido #{{ order.id }} - Admin Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link" href="/admin/products">Produtos</a>
                    <a class="nav-link active" href="/admin/orders">Pedidos</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1><i class="fas fa-edit"></i> Editar Pedido #{{ order.id }}</h1>
                <a href="/admin/orders" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="card">
                <div class="card-body">
                    <form method="POST">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Nome do Cliente</label>
                                    <input type="text" class="form-control" name="customer_name" value="{{ order.customer_name }}">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Status do Pedido</label>
                                    <select class="form-control" name="status">
                                        <option value="pending" {{ 'selected' if order.status == 'pending' }}>Pendente</option>
                                        <option value="processing" {{ 'selected' if order.status == 'processing' }}>Processando</option>
                                        <option value="completed" {{ 'selected' if order.status == 'completed' }}>Concluído</option>
                                        <option value="cancelled" {{ 'selected' if order.status == 'cancelled' }}>Cancelado</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Telefone</label>
                                    <input type="text" class="form-control" name="customer_phone" value="{{ order.customer_phone or '' }}">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" name="customer_email" value="{{ order.customer_email or '' }}">
                                </div>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/admin/orders" class="btn btn-secondary me-md-2">Cancelar</a>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> Salvar Alterações
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return render_template_string(html, order=order)

@admin_bp.route('/suppliers')
def suppliers_list():
    suppliers = Supplier.query.all()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fornecedores - Admin Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link" href="/admin/products">Produtos</a>
                    <a class="nav-link" href="/admin/orders">Pedidos</a>
                    <a class="nav-link active" href="/admin/suppliers">Fornecedores</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1><i class="fas fa-truck"></i> Gerenciar Fornecedores</h1>
                <a href="/admin/suppliers/new" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Novo Fornecedor
                </a>
            </div>
            
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead class="table-dark">
                        <tr>
                            <th>Nome</th>
                            <th>Contato</th>
                            <th>Email</th>
                            <th>Telefone</th>
                            <th>Status</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for supplier in suppliers %}
                        <tr>
                            <td><strong>{{ supplier.name }}</strong></td>
                            <td>{{ supplier.contact_person or '-' }}</td>
                            <td>{{ supplier.email or '-' }}</td>
                            <td>{{ supplier.phone or '-' }}</td>
                            <td>
                                {% if supplier.is_active %}
                                    <span class="badge bg-success">Ativo</span>
                                {% else %}
                                    <span class="badge bg-danger">Inativo</span>
                                {% endif %}
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <a href="/admin/suppliers/edit/{{ supplier.id }}" class="btn btn-outline-primary">
                                        <i class="fas fa-edit"></i>
                                    </a>
                                    <a href="/admin/suppliers/delete/{{ supplier.id }}" class="btn btn-outline-danger"
                                       onclick="return confirm('Tem certeza que deseja excluir este fornecedor?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, suppliers=suppliers)

@admin_bp.route('/suppliers/new', methods=['GET', 'POST'])
def suppliers_new():
    if request.method == 'POST':
        try:
            supplier = Supplier(
                name=request.form.get('name'),
                contact_person=request.form.get('contact_person'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                address=request.form.get('address'),
                is_active=request.form.get('is_active') == 'on'
            )
            
            db.session.add(supplier)
            db.session.commit()
            
            flash('Fornecedor criado com sucesso!', 'success')
            return redirect(url_for('admin_crud.suppliers_list'))
        except Exception as e:
            flash(f'Erro ao criar fornecedor: {str(e)}', 'error')
            db.session.rollback()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Novo Fornecedor - Admin Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link" href="/admin/products">Produtos</a>
                    <a class="nav-link" href="/admin/orders">Pedidos</a>
                    <a class="nav-link active" href="/admin/suppliers">Fornecedores</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1><i class="fas fa-plus"></i> Novo Fornecedor</h1>
                <a href="/admin/suppliers" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="card">
                <div class="card-body">
                    <form method="POST">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Nome do Fornecedor *</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Pessoa de Contato</label>
                                    <input type="text" class="form-control" name="contact_person">
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" name="email">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Telefone</label>
                                    <input type="text" class="form-control" name="phone">
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Endereço</label>
                            <textarea class="form-control" name="address" rows="3"></textarea>
                        </div>
                        
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="is_active" id="is_active" checked>
                                <label class="form-check-label" for="is_active">
                                    Fornecedor ativo
                                </label>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/admin/suppliers" class="btn btn-secondary me-md-2">Cancelar</a>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> Salvar Fornecedor
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return render_template_string(html)

@admin_bp.route('/suppliers/edit/<int:id>', methods=['GET', 'POST'])
def suppliers_edit(id):
    supplier = Supplier.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            supplier.name = request.form.get('name')
            supplier.contact_person = request.form.get('contact_person')
            supplier.email = request.form.get('email')
            supplier.phone = request.form.get('phone')
            supplier.address = request.form.get('address')
            supplier.is_active = request.form.get('is_active') == 'on'
            
            db.session.commit()
            flash('Fornecedor atualizado com sucesso!', 'success')
            return redirect(url_for('admin_crud.suppliers_list'))
        except Exception as e:
            flash(f'Erro ao atualizar fornecedor: {str(e)}', 'error')
            db.session.rollback()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Editar Fornecedor - Admin Visage</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/admin/">🏪 Visage Admin</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/admin/">Dashboard</a>
                    <a class="nav-link" href="/admin/products">Produtos</a>
                    <a class="nav-link" href="/admin/orders">Pedidos</a>
                    <a class="nav-link active" href="/admin/suppliers">Fornecedores</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1><i class="fas fa-edit"></i> Editar: {{ supplier.name }}</h1>
                <a href="/admin/suppliers" class="btn btn-secondary">
                    <i class="fas fa-arrow-left"></i> Voltar
                </a>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <div class="card">
                <div class="card-body">
                    <form method="POST">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Nome do Fornecedor *</label>
                                    <input type="text" class="form-control" name="name" value="{{ supplier.name }}" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Pessoa de Contato</label>
                                    <input type="text" class="form-control" name="contact_person" value="{{ supplier.contact_person or '' }}">
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" name="email" value="{{ supplier.email or '' }}">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Telefone</label>
                                    <input type="text" class="form-control" name="phone" value="{{ supplier.phone or '' }}">
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Endereço</label>
                            <textarea class="form-control" name="address" rows="3">{{ supplier.address or '' }}</textarea>
                        </div>
                        
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" name="is_active" id="is_active" {{ 'checked' if supplier.is_active }}>
                                <label class="form-check-label" for="is_active">
                                    Fornecedor ativo
                                </label>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="/admin/suppliers" class="btn btn-secondary me-md-2">Cancelar</a>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-save"></i> Salvar Alterações
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return render_template_string(html, supplier=supplier)

@admin_bp.route('/suppliers/delete/<int:id>')
def suppliers_delete(id):
    supplier = Supplier.query.get_or_404(id)
    try:
        db.session.delete(supplier)
        db.session.commit()
        flash('Fornecedor excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir fornecedor: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_crud.suppliers_list'))

# Registrar o blueprint no app
app.register_blueprint(admin_bp)

print("Admin CRUD customizado configurado sem Flask-Admin!")