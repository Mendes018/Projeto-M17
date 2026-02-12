from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from Permissions import IsAdmin

event_type_route = Blueprint('event_types', __name__)

# LISTAR TIPOS DE EVENTOS
@event_type_route.route('/')
@IsAdmin
def event_type_list():
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM event_types')
    event_types = cursor.fetchall()
    dbconnection.close()
    return render_template('event_types/list.html', event_types=event_types)


# CRIAR TIPO DE EVENTO
@event_type_route.route('/create', methods=['GET', 'POST'])
@IsAdmin
def event_type_add():
 
    if request.method == 'POST':
        # 1. Obter dados do formulário
        name = request.form.get('name')
        
        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:

            # 3. Executar o comando SQL
            cursor.execute("""
                INSERT INTO event_types (name) 
                VALUES (?)
            """, (name,))

            # 4. Gravar as alterações
            conn.commit() 
            print("Tipo de evento gravado com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('event_types.event_type_list'))
        
    return render_template('event_types/create.html')    
    
@event_type_route.route('/edit/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def event_type_update(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM event_types WHERE id = ?', (id,))
    event_type = cursor.fetchone()
    dbconnection.close()

    if request.method == 'POST':
        # 1. Obter dados do formulário
        name = request.form.get('name')

        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:
            # 3. Executar o comando SQL
            cursor.execute("""
                UPDATE event_types SET name = ? WHERE id = ?
            """, (name, id))

            # 4. Gravar as alterações
            conn.commit() 
            print("Tipo de evento gravado com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('event_types.event_type_list'))

    return render_template('event_types/edit.html', event_type=event_type)

@event_type_route.route('/delete/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def event_type_delete(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('DELETE FROM event_types WHERE id = ?', (id,))
    dbconnection.commit()
    dbconnection.close()
    return redirect(url_for('event_types.event_type_list'))


@event_type_route.route('/details/<int:id>', methods=['GET'])
@IsAdmin
def event_type_detail(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM event_types WHERE id = ?', (id,))
    event_type = cursor.fetchone()
    dbconnection.close()
    return render_template('event_types/details.html', event_type=event_type)
