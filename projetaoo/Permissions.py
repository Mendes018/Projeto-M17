from functools import wraps
from flask import flash, redirect, url_for, session, render_template


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('id_user') is None:
            flash('Por favor, faça login para aceder a esta página.', 'error')
            return redirect(url_for('users.login'))
        return f(*args, **kwargs)
    return decorated_function


def IsAdmin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('id_user') is None:
            flash('Fazer login para aceder a esta página.', 'error')
            return redirect(url_for('users.login'))
        
        if session.get('user_type') != 'admin':
            flash('Acesso negado. Apenas administradores podem aceder a esta página.', 'error')
            return redirect(url_for('home.home'))
        
        return f(*args, **kwargs)
    return decorated_function