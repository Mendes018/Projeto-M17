from flask import Blueprint, render_template
import sqlite3

home_route = Blueprint('home', __name__)

@home_route.route('/')
def home():
    conn = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.id, e.title, s.session_date as next_session, p.name as place_name, e.description
        FROM Events e
        JOIN Sessions s ON e.id = s.id_event
        JOIN Places p ON e.id_place = p.id
        WHERE datetime(s.session_date) >= datetime('now')
        GROUP BY e.id
        ORDER BY next_session ASC
    """)
    events = cursor.fetchall()
    conn.close()
    
    upcoming_events = []
    for e in events:
        upcoming_events.append({
            'id': e[0],
            'title': e[1],
            'next_session': e[2],
            'place_name': e[3],
            'description': e[4]
        })

    return render_template('index.html', events=upcoming_events)