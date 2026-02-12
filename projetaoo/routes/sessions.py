from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

session_route = Blueprint('sessions', __name__)

# LISTAR TIPOS DE EVENTOS
@session_route.route('/<int:id_event>', methods=['GET'])
def session_list(id_event):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM Sessions WHERE id_event = ?', (id_event,))
    sessions = cursor.fetchall()
    cursor.execute('SELECT * FROM Events WHERE id = ?', (id_event,))
    event = cursor.fetchone()
    dbconnection.close()
    return render_template('sessions/list.html', sessions=sessions, event=event)


# CRIAR TIPO DE EVENTO
@session_route.route('/<int:id_event>/create', methods=['GET', 'POST'])
def session_add(id_event):
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    if request.method == 'POST':
        # 1. Obter dados do formulário
        session_date = request.form.get('session_date')
        base_price = request.form.get('base_price')
        
        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:

            # 3. Executar o comando SQL
            cursor.execute("""
                INSERT INTO sessions (id_event, session_date, base_price) 
                VALUES (?, ?, ?)
            """, (id_event, session_date, base_price))

            # 4. Gravar as alterações
            conn.commit() 
            print("Sessão gravada com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro

        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('sessions.session_list', id_event=id_event))
        
    return render_template('sessions/create.html', id_event=id_event, min_date=now)
    
@session_route.route('/edit/<int:id>', methods=['GET', 'POST'])
def session_update(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (id,))
    session = cursor.fetchone()
    id_event = session[1]
    dbconnection.close()

    if request.method == 'POST':
        # 1. Obter dados do formulário
        session_date = request.form.get('session_date')
        base_price = request.form.get('base_price')

        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:
            # 3. Executar o comando SQL
            cursor.execute("""
                UPDATE sessions SET session_date = ?, base_price = ? WHERE id = ?
            """, (session_date, base_price, id))

            # 4. Gravar as alterações
            conn.commit() 
            print("Sessão atualizada com sucesso!")

        except Exception as e:
            print(f"Erro ao atualizar: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('sessions.session_list', id_event=id_event))

    return render_template('sessions/edit.html', session=session)

@session_route.route('/delete/<int:id>', methods=['GET', 'POST'])
def session_delete(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT id_event FROM sessions WHERE id = ?', (id,))
    id_event = cursor.fetchone()
    id_event=id_event[0]
    cursor.execute('DELETE FROM sessions WHERE id = ?', (id,))
    dbconnection.commit()
    dbconnection.close()
    return redirect(url_for('sessions.session_list', id_event=id_event))


@session_route.route('/details/<int:id>', methods=['GET'])
def session_detail(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT id_event FROM sessions WHERE id = ?', (id,))
    id_event = cursor.fetchone()
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (id,))
    session = cursor.fetchone()
    dbconnection.close()
    return render_template('sessions/details.html', id_event=id_event, session=session)
