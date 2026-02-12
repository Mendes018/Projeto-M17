from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from Permissions import IsAdmin

event_route = Blueprint('events', __name__)

# LISTAR EVENTOS
@event_route.route('/')
@IsAdmin
def event_list():
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT a.*, b.name event_type, c.name place, d.name organizer FROM events a LEFT JOIN event_types b ON a.id_event_type = b.id LEFT JOIN places c ON a.id_place = c.id LEFT JOIN organizers d ON a.id_organizer = d.id')
    eventos = cursor.fetchall()
    dbconnection.close()
    return render_template('events/list.html', eventos=eventos)

# CRIAR EVENTO
@event_route.route('/create', methods=['GET', 'POST'])
@IsAdmin
def event_add():
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT id, name FROM event_types')
    event_types = cursor.fetchall()
    cursor.execute('SELECT id, name FROM places')
    places = cursor.fetchall()
    cursor.execute('SELECT id, name FROM organizers')
    organizers = cursor.fetchall()
    dbconnection.close()
    if request.method == 'POST':
        # 1. Obter dados do formulário
        title = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration')
        reserved_seats = request.form.get('reserved_seats')
        id_event_type = request.form.get('id_event_type')
        id_place = request.form.get('id_place')
        id_organizer = request.form.get('id_organizer')

        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:
            # 3. Executar o comando SQL
            cursor.execute("""
                INSERT INTO events (title, description, id_event_type, duration, id_place, reserved_seats, id_organizer) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, id_event_type, duration, id_place, reserved_seats, id_organizer))

            # 4. Gravar as alterações
            conn.commit() 
            print("Evento gravado com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('events.event_list'))
    return render_template('events/create.html', event_types=event_types, places=places, organizers=organizers)    
    
@event_route.route('/edit/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def event_update(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM events WHERE id = ?', (id,))
    evento = cursor.fetchone()
    cursor.execute('SELECT id, name FROM event_types')
    event_types = cursor.fetchall()
    cursor.execute('SELECT id, name FROM places')
    places = cursor.fetchall()
    cursor.execute('SELECT id, name FROM organizers')
    organizers = cursor.fetchall()
    dbconnection.close()

    if request.method == 'POST':
        # 1. Obter dados do formulário
        title = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration')
        reserved_seats = request.form.get('reserved_seats')
        id_event_type = request.form.get('id_event_type')
        id_place = request.form.get('id_place')
        id_organizer = request.form.get('id_organizer')

        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:
            # 3. Executar o comando SQL
            cursor.execute("""
                UPDATE events SET title = ?, description = ?, id_event_type = ?, duration = ?, id_place = ?, reserved_seats = ?, id_organizer = ? WHERE id = ?
            """, (title, description, id_event_type, duration, id_place, reserved_seats, id_organizer, id))

            # 4. Gravar as alterações
            conn.commit() 
            print("Evento gravado com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('events.event_list'))

    return render_template('events/edit.html', evento=evento, event_types=event_types, places=places, organizers=organizers)

@event_route.route('/delete/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def event_delete(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('DELETE FROM events WHERE id = ?', (id,))
    dbconnection.commit()
    dbconnection.close()
    return redirect(url_for('events.event_list'))


@event_route.route('/details/<int:id>', methods=['GET'])
@IsAdmin
def event_detail(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT a.*, b.name event_type, c.name place, d.name organizer FROM events a LEFT JOIN event_types b ON a.id_event_type = b.id LEFT JOIN places c ON a.id_place = c.id LEFT JOIN organizers d ON a.id_organizer = d.id where a.id = ?', (id,))
    evento = cursor.fetchone()
    dbconnection.close()
    return render_template('events/details.html', evento=evento)



