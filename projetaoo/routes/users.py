from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from Permissions import IsAdmin

user_route = Blueprint('users', __name__)

# ... (Previous code remains, skipping to login/logout)

@user_route.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = dbconnection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        dbconnection.close()
        
        if user:
            # user structure: id, name, email, mobile, nif, password, user_type
            session['id_user'] = user[0]
            session['user_name'] = user[1]
            session['user_type'] = user[6]
            flash(f'Bem-vindo, {user[1]}!', 'success')
            return redirect(url_for('home.home'))
        else:
            flash('Email ou senha incorretos.', 'error')
            
    return render_template('users/login.html')

@user_route.route('/logout')
def logout():
    session.clear()
    flash('Sessão terminada.', 'success')
    return redirect(url_for('home.home'))

# LISTAR UTILIZADORES
@user_route.route('/')
@IsAdmin
def user_list():
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    dbconnection.close()
    return render_template('users/list.html', users=users)


# CRIAR UTILIZADOR
@user_route.route('/create', methods=['GET', 'POST'])
@IsAdmin
def user_add():
 
    if request.method == 'POST':
        # 1. Obter dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        nif = request.form.get('nif')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:

            # 3. Executar o comando SQL
            cursor.execute("""
                INSERT INTO users (name, email, mobile, nif, password, user_type) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, email, mobile, nif, password, user_type))

            # 4. Gravar as alterações
            conn.commit() 
            print("Utilizador gravado com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('users.user_list'))
        
    return render_template('users/create.html')    
    
@user_route.route('/edit/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def user_update(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
    user = cursor.fetchone()
    dbconnection.close()

    if request.method == 'POST':
        # 1. Obter dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        nif = request.form.get('nif')
        user_type = request.form.get('user_type')

        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:
            # 3. Executar o comando SQL
            cursor.execute("""
                UPDATE users SET name = ?, email = ?, mobile = ?, nif = ?, user_type = ? WHERE id = ?
            """, (name, email, mobile, nif, user_type, id))

            # 4. Gravar as alterações
            conn.commit() 
            print("Utilizador atualizado com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de utilizadores
        return redirect(url_for('users.user_list'))

    return render_template('users/edit.html', user=user)

@user_route.route('/delete/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def user_delete(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (id,))
    dbconnection.commit()
    dbconnection.close()
    return redirect(url_for('users.user_list'))


@user_route.route('/details/<int:id>', methods=['GET'])
@IsAdmin
def user_detail(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
    user = cursor.fetchone()
    dbconnection.close()
    return render_template('users/details.html', user=user)