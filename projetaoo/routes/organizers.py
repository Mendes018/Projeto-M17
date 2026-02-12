from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from Permissions import IsAdmin

organizer_route = Blueprint('organizers', __name__)

# LISTAR ORGANIZADORES
@organizer_route.route('/')
@IsAdmin
def organizer_list():
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM organizers')
    organizers = cursor.fetchall()
    dbconnection.close()
    return render_template('organizers/list.html', organizers=organizers)

# CRIAR EVENTO
@organizer_route.route('/create', methods=['GET', 'POST'])
@IsAdmin
def organizer_add():

    if request.method == 'POST':
        # 1. Obter dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        nif = request.form.get('nif')

        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:
            # 3. Executar o comando SQL
            cursor.execute("""
                INSERT INTO organizers (name, email, mobile, nif) 
                VALUES (?, ?, ?, ?)
            """, (name, email, mobile, nif))

            # 4. Gravar as alterações
            conn.commit() 
            print("Organizador gravado com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('organizers.organizer_list'))
    return render_template('organizers/create.html')
    
@organizer_route.route('/edit/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def organizer_update(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM organizers WHERE id = ?', (id,))
    organizer = cursor.fetchone()
    dbconnection.close()

    if request.method == 'POST':
        # 1. Obter dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        nif = request.form.get('nif')
        
        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:
            # 3. Executar o comando SQL
            cursor.execute("""
                UPDATE organizers SET name = ?, email = ?, mobile = ?, nif = ? WHERE id = ?
            """, (name, email, mobile, nif, id))

            # 4. Gravar as alterações
            conn.commit() 
            print("Organizador gravado com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('organizers.organizer_list'))

    return render_template('organizers/edit.html', organizer=organizer)

@organizer_route.route('/delete/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def organizer_delete(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('DELETE FROM organizers WHERE id = ?', (id,))
    dbconnection.commit()
    dbconnection.close()
    return redirect(url_for('organizers.organizer_list'))


@organizer_route.route('/details/<int:id>', methods=['GET'])
@IsAdmin
def organizer_detail(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM organizers WHERE id = ?', (id,))
    organizer = cursor.fetchone()
    dbconnection.close()
    return render_template('organizers/details.html', organizer=organizer)



