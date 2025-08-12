from functools import wraps
from flask import session, redirect, url_for, request, flash
import hashlib

# Credenciais únicas do admin
ADMIN_CREDENTIALS = {
    'visagecosmeticos': '270174CLcl'  # usuário único: visagecosmeticos
}

def hash_password(password):
    """Hash da senha para comparação segura"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(username, password):
    """Verifica se as credenciais estão corretas"""
    if username in ADMIN_CREDENTIALS:
        stored_password = ADMIN_CREDENTIALS[username]
        return password == stored_password
    return False

def login_required(f):
    """Decorator para proteger rotas que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            # Salva a URL que o usuário estava tentando acessar
            session['next_url'] = request.url
            flash('Você precisa fazer login para acessar esta área.', 'warning')
            return redirect(url_for('admin_crud.login'))
        return f(*args, **kwargs)
    return decorated_function

def is_admin_logged_in():
    """Verifica se o admin está logado"""
    return session.get('admin_logged_in', False)

def login_admin(username):
    """Faz o login do admin"""
    session['admin_logged_in'] = True
    session['admin_username'] = username
    session.permanent = True

def logout_admin():
    """Faz o logout do admin"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    session.pop('next_url', None)