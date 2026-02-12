from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from Permissions import IsAdmin

seat_route = Blueprint('seats', __name__)

# LISTAR TIPOS DE EVENTOS
@seat_route.route('/<int:id_place>', methods=['GET'])
@IsAdmin
def seat_list(id_place):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM Seats WHERE id_place = ?', (id_place,))
    seats = cursor.fetchall()
    cursor.execute('SELECT * FROM Places WHERE id = ?', (id_place,))
    place = cursor.fetchone()
    dbconnection.close()
    return render_template('seats/list.html', seats=seats, place=place)


# CRIAR TIPO DE EVENTO
@seat_route.route('/<int:id_place>/create', methods=['GET', 'POST'])
@IsAdmin
def seat_add(id_place):
    if request.method == 'POST':
        # 1. Obter dados do formulário
        sector = request.form.get('sector')
        first_row = request.form.get('first_row')
        last_row = request.form.get('last_row')
        first_number = request.form.get('first_number')
        last_number = request.form.get('last_number')
        
        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:

            # 3. Executar o comando SQL
            cursor.execute("""
                INSERT INTO seats (id_place, sector, first_row, last_row, first_number, last_number) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_place, sector, first_row, last_row, first_number, last_number))

            # 4. Gravar as alterações
            conn.commit() 
            print("Lugar gravado com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            conn.rollback() # Cancela se houver erro

        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('seats.seat_list', id_place=id_place))
        
    return render_template('seats/create.html', id_place=id_place)
    
@seat_route.route('/edit/<int:id>', methods=['GET', 'POST'])
def seat_update(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM seats WHERE id = ?', (id,))
    seat = cursor.fetchone()
    id_place = seat[1]
    dbconnection.close()

    if request.method == 'POST':
        # 1. Obter dados do formulário
        sector = request.form.get('sector')
        first_row = request.form.get('first_row')
        last_row = request.form.get('last_row')
        first_number = request.form.get('first_number')
        last_number = request.form.get('last_number')

        # 2. Ligar à BD
        conn = sqlite3.connect('database/eventos_bilhetes.db')
        cursor = conn.cursor()
        try:
            # 3. Executar o comando SQL
            cursor.execute("""
                UPDATE seats SET sector = ?, first_row = ?, last_row = ?, first_number = ?, last_number = ? WHERE id = ?
            """, (sector, first_row, last_row, first_number, last_number, id))

            # 4. Gravar as alterações
            conn.commit() 
            print("Lugar atualizado com sucesso!")

        except Exception as e:
            print(f"Erro ao atualizar: {e}")
            conn.rollback() # Cancela se houver erro
        finally:
            # 5. Fechar a ligação à BD
            conn.close()

        # 6. Redirecionar para a lista de eventos
        return redirect(url_for('seats.seat_list', id_place=id_place))

    return render_template('seats/edit.html', seat=seat)

@seat_route.route('/delete/<int:id>', methods=['GET', 'POST'])
@IsAdmin
def seat_delete(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT id_place FROM seats WHERE id = ?', (id,))
    id_place = cursor.fetchone()
    id_place=id_place[0]
    cursor.execute('DELETE FROM seats WHERE id = ?', (id,))
    dbconnection.commit()
    dbconnection.close()
    return redirect(url_for('seats.seat_list', id_place=id_place))


@seat_route.route('/details/<int:id>', methods=['GET'])
def seat_detail(id):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT id_place FROM seats WHERE id = ?', (id,))
    id_place = cursor.fetchone()
    cursor.execute('SELECT * FROM seats WHERE id = ?', (id,))
    seat = cursor.fetchone()
    dbconnection.close()
    return render_template('seats/details.html', id_place=id_place, seat=seat)

@seat_route.route('/<int:id_place>/map', methods=['GET'])
@IsAdmin
def seat_map(id_place):
    conn = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM Places WHERE id = ?', (id_place,))
    place_name = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM seats WHERE id_place = ?', (id_place,))
    seats = cursor.fetchall()
    conn.close()

    processed_sectors = []
    
    for sector in seats:
        sector_name = sector[2]
        first_row_char = sector[3]
        last_row_char = sector[4]
        first_number = sector[5]
        last_number = sector[6]
        seats_list = []
        
        # tratar as letras das filas, convertendo-as para números (A é o código 65 em ASCII)
        first_row_number = ord(first_row_char) - 65
        last_row_number = ord(last_row_char) - 65
        
        for row in range(first_row_number, last_row_number + 1):
            row_letter = chr(row + 65)
            for number in range(first_number, last_number + 1):
                seats_list.append({
                    'label': f"{row_letter}{number}",
                    'row': row_letter, 
                    'number': number,
                    'x': 40 + (number - first_number) * 60,
                    'y': 40 + (row - first_row_number) * 60,
                    'width': 50, 'height': 50
                })

        width = 40 + (last_number - first_number + 1) * 60 + 20
        height = 40 + (last_row_number - first_row_number + 1) * 60 + 20

        row_labels = [{'label': chr(r+65), 'x': 10, 'y': 40 + (r-first_row_number)*60 + 25} for r in range(first_row_number, last_row_number + 1)]
        col_labels = [{'label': str(n), 'x': 40 + (n-first_number)*60 + 25, 'y': 25} for n in range(first_number, last_number+1)]

        processed_sectors.append({
            'name': sector_name, 
            'width': width, 
            'height': height, 
            'seats': seats_list,
            'row_labels': row_labels, 
            'col_labels': col_labels
        })

    return render_template('seats/map.html', place_name=place_name, sectors=processed_sectors, id_place=id_place)
