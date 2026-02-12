from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from Permissions import IsAdmin

place_route = Blueprint('places', __name__)

# LISTAR TIPOS DE EVENTOS
@place_route.route('/')
@IsAdmin
def place_list():
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM places')
    places = cursor.fetchall()
    dbconnection.close()
    return render_template('places/list.html', places=places)


# CRIAR SALA DE ESPETÁCULOS
@place_route.route('/create', methods=['GET', 'POST'])
@IsAdmin
def place_add():
 
    if request.method == 'POST':
        # 1. Obter dados do formulário
        name = request.form.get('name')
        address = request.form.get('address')
        google_maps_link = request.form.get('google_maps_link')
        capacity = request.form.get('capacity')
        
        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:

            # 3. Executar o comando SQL
            cursor.execute("""
                INSERT INTO places (name, address, google_maps_link, capacity) 
                VALUES (?, ?, ?, ?)
            """, (name, address, google_maps_link, capacity))

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
        return redirect(url_for('places.place_list'))
        
    return render_template('places/create.html')    
    
@place_route.route('/edit/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def place_update(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM places WHERE id = ?', (id,))
    place = cursor.fetchone()
    dbconnection.close()

    if request.method == 'POST':
        # 1. Obter dados do formulário
        name = request.form.get('name')
        address = request.form.get('address')
        google_maps_link = request.form.get('google_maps_link')
        capacity = request.form.get('capacity')

        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:
            # 3. Executar o comando SQL
            cursor.execute("""
                UPDATE places SET name = ?, address = ?, google_maps_link = ?, capacity = ? WHERE id = ?
            """, (name, address, google_maps_link, capacity, id))

            # 4. Gravar as alterações
            conn.commit() 
            print("Nova sala de espetáculos gravada com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('places.place_list'))

    return render_template('places/edit.html', place=place)

@place_route.route('/delete/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def place_delete(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('DELETE FROM places WHERE id = ?', (id,))
    dbconnection.commit()
    dbconnection.close()
    return redirect(url_for('places.place_list'))


@place_route.route('/details/<int:id>', methods=['GET'])
@IsAdmin
def place_detail(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM places WHERE id = ?', (id,))
    place = cursor.fetchone()
    dbconnection.close()
    return render_template('places/details.html', place=place)
