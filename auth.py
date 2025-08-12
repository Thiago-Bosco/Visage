from functools import wraps
from flask import session, redirect, url_for, request, flash
from datetime import datetime

def verify_password(username, password):
    """Verifica se as credenciais estão corretas no banco de dados"""
    from models import AdminUser
    user = AdminUser.query.filter_by(username=username, is_active=True).first()
    if user and user.check_password(password):
        # Atualiza último login
        user.last_login = datetime.utcnow()
        from app import db
        db.session.commit()
        return True
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