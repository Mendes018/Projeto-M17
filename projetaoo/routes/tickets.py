from flask import Blueprint, render_template, request, redirect, url_for, flash, session as flask_session
import sqlite3
from Permissions import login_required

ticket_route = Blueprint('tickets', __name__)

# Mostrar eventos para possível compra de bilhetes
@ticket_route.route('/<int:id_event>/choose_session', methods=['GET'])
@login_required
def choose_session(id_event):
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    cursor.execute('SELECT * FROM Events WHERE id = ?', (id_event,))
    event = cursor.fetchone()
    cursor.execute('SELECT * FROM Sessions WHERE id_event = ?', (id_event,))
    sessions = cursor.fetchall()
    dbconnection.close()
    return render_template('tickets/choose_session.html', event=event, sessions=sessions)

@ticket_route.route('/<int:id_session>/buy_from_seat_map', methods=['GET', 'POST'])
@login_required
def buy_from_seat_map(id_session):
    conn = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.session_date, s.base_price, e.title, p.name, p.id as id_place
        FROM Sessions s
        JOIN Events e ON s.id_event = e.id
        JOIN Places p ON e.id_place = p.id
        WHERE s.id = ?
    """, (id_session,))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Sessão não encontrada", 404
        
    session_data = {
        'id': row[0], 'session_date': row[1], 'base_price': row[2],
        'event_title': row[3], 'place_name': row[4], 'id_place': row[5]
    }
    
    id_user = flask_session.get('id_user')

    if request.method == 'POST':
        selected_seats_str = request.form.get('selected_seats')
        is_discounted = request.form.get('discount')
        
        if not selected_seats_str:
            conn.close()
            return "Nenhum lugar selecionado", 400

        selected_seats = selected_seats_str.split(',')
        base_price = session_data['base_price']
        final_price = base_price * 0.9 if is_discounted else base_price

        try:
            ticket_ids = []
            for seat_label in selected_seats:
                import re
                match = re.match(r"([A-Z]+)([0-9]+)", seat_label)
                if match:
                    seat_row = match.group(1)
                    seat_number = int(match.group(2))
                    
                    cursor.execute("""
                        INSERT INTO Tickets (id_session, id_user, seat_row, seat_number, paid_price) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (id_session, id_user, seat_row, seat_number, final_price))
                    ticket_ids.append(str(cursor.lastrowid))
            
            conn.commit()
            flash('Compra efetuada com sucesso!', 'success')
            return redirect(url_for('tickets.invoice', ids=','.join(ticket_ids)))

        except Exception as e:
            conn.rollback()
            print(f"Erro na compra: {e}")
            flash('Erro ao processar compra.', 'error')
            return redirect(url_for('tickets.buy_from_seat_map', id_session=id_session))
        finally:
            conn.close()

    # GET: Mapa de lugares
    
    # Obter lugares já vendidos
    cursor.execute('SELECT seat_row, seat_number FROM Tickets WHERE id_session = ?', (id_session,))
    sold_seats = set((row[0], row[1]) for row in cursor.fetchall())

    # Obter lugares da sala
    cursor.execute('SELECT * FROM seats WHERE id_place = ?', (session_data['id_place'],))
    seats_config = cursor.fetchall()
    conn.close()

    processed_sectors = []
    
    for row_data in seats_config:
        sector_name = row_data[2]
        first_row_char = row_data[3]
        last_row_char = row_data[4]
        first_num = row_data[5]
        last_num = row_data[6]

        seats_list = []
        
        start_r_idx = ord(first_row_char) - 65
        end_r_idx = ord(last_row_char) - 65
        
        for row_idx in range(start_r_idx, end_r_idx + 1):
            row_char = chr(row_idx + 65)
            for num_idx in range(first_num, last_num + 1):
                 status = 'taken' if (row_char, num_idx) in sold_seats else 'available'
                 seats_list.append({
                    'label': f"{row_char}{num_idx}",
                    'row': row_char, 
                    'number': num_idx,
                    'x': 40 + (num_idx - first_num) * 60,
                    'y': 40 + (row_idx - start_r_idx) * 60,
                    'width': 50, 'height': 50,
                    'status': status
                })

        width = 40 + (last_num - first_num + 1) * 60 + 20
        height = 40 + (end_r_idx - start_r_idx + 1) * 60 + 20

        processed_sectors.append({
            'name': sector_name, 
            'seats': seats_list,
            'width': width,
            'height': height
        })
        
    # Tamanho do mapa
    map_width = 800 
    map_height = 600

    return render_template('tickets/buy_from_seat_map.html', 
                           session=session_data, 
                           event={'title': session_data['event_title']},
                           place={'name': session_data['place_name']},
                           sectors=processed_sectors,
                           map_width=map_width, 
                           map_height=map_height,
                           session_user=id_user)

@ticket_route.route('/<int:id_session>/buy_from_capacity', methods=['GET', 'POST'])
@login_required
def buy_from_capacity(id_session):
    conn = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = conn.cursor()
    
    # Obter ID do utilizador
    id_user = flask_session.get('id_user')

    cursor.execute("""
        SELECT s.id, s.id_event, s.session_date, s.base_price, e.title, p.name, p.capacity 
        FROM Sessions s
        JOIN Events e ON s.id_event = e.id
        JOIN Places p ON e.id_place = p.id
        WHERE s.id = ?
    """, (id_session,))
    session = cursor.fetchone()

    cursor.execute('SELECT COUNT(*) FROM Tickets WHERE id_session = ?', (id_session,))
    sold_count = cursor.fetchone()
    available_seats = session[6] - sold_count[0]

    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        is_discounted = request.form.get('discount')
        if quantity > 0 and quantity <= available_seats:
            base_price = session[3] 
            final_price = base_price * 0.9 if is_discounted else base_price
            ticket_ids = []
            for i in range(quantity):
                cursor.execute("""
                    INSERT INTO Tickets (id_session, seat_row, seat_number, id_user, checkin, paid_price) 
                    VALUES (?, NULL, NULL, ?, NULL, ?)
                """, (id_session, id_user, final_price))
                ticket_ids.append(str(cursor.lastrowid))
            conn.commit()
            conn.close()
            return redirect(url_for('tickets.invoice', ids=','.join(ticket_ids))) 
        else:
            conn.close()
            return "Quantidade inválida ou lugares esgotados", 400

    conn.close()
    return render_template('tickets/buy_from_capacity.html', session=session, available_seats=available_seats)

@ticket_route.route('/invoice', methods=['GET'])
@login_required
def invoice():
    ids = request.args.get('ids', '')
    if not ids:
        return "Nenhuma fatura encontrada (IDs ausentes)", 400

    ticket_ids = ids.split(',')
    
    # Juntar os ID dos lugares vendidos para passar ao html da fatura
    placeholders = ','.join(['?'] * len(ticket_ids))
    
    dbconnection = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = dbconnection.cursor()
    
    query = f"""
        SELECT 
            t.id, t.seat_row, t.seat_number, t.paid_price,
            e.title, s.session_date,
            o.name as organizer_name, o.nif as organizer_nif, o.email as organizer_email,
            p.name as place_name, p.address as place_address
        FROM Tickets t
        JOIN Sessions s ON t.id_session = s.id
        JOIN Events e ON s.id_event = e.id
        JOIN Organizers o ON e.id_organizer = o.id
        JOIN Places p ON e.id_place = p.id
        WHERE t.id IN ({placeholders})
    """
    
    cursor.execute(query, ticket_ids)
    rows = cursor.fetchall()
    dbconnection.close()
    
    if not rows:
        return "Fatura não encontrada", 404
        
    # Group data (assuming all tickets in batch are for same event/organizer)
    first_row = rows[0]
    invoice_data = {
        'event_title': first_row[4],
        'session_date': first_row[5],
        'organizer': {
            'name': first_row[6],
            'nif': first_row[7],
            'email': first_row[8]
        },
        'place': {
            'name': first_row[9],
            'address': first_row[10]
        },
        'line_items': [],
        'total': 0
    }
    
    total = 0
    for row in rows:
        # row indices: 0:id, 1:row, 2:num, 3:price
        seat_desc = f"Lugar {row[1]}{row[2]}" if row[1] and row[2] else "Entrada Geral"
        price = row[3] if row[3] is not None else 0
        total += price
        invoice_data['line_items'].append({
            'description': seat_desc,
            'price': price
        })
        
    invoice_data['total'] = total

    return render_template('tickets/invoice.html', invoice=invoice_data)