import sqlite3

def init_db():
    # Conecta ao banco (cria o arquivo se não existir)
    conn = sqlite3.connect('database/eventos_bilhetes.db')
    cursor = conn.cursor()

    # Habilitar chaves estrangeiras no SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Tabela Eventos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            id_event_type INTEGER,
            duration INTEGER,
            id_place INTEGER,
            reserved_seats BOOLEAN,
            id_organizer INTEGER,
            FOREIGN KEY (id_place) REFERENCES places(id)
            FOREIGN KEY (id_organizer) REFERENCES organizers(id)
            FOREIGN KEY (id_event_type) REFERENCES event_types(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    # Tabela Salas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            latitude TEXT,
            longitude TEXT,
            google_maps_link TEXT,
            capacity INTEGER
        )
    ''')

    # 2. Tabela Lugares
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_place INTEGER,
            sector TEXT,
            first_row TEXT,
            last_row TEXT,
            first_number INTEGER,
            last_number INTEGER,
            FOREIGN KEY (id_place) REFERENCES places(id)
        )
    ''')

    # Tabela Sessões
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_event INTEGER,
            session_date DATETIME,
            base_price DECIMAL(10,2),
            FOREIGN KEY (id_event) REFERENCES events(id)
        )
    ''')

    # Tabela Organizadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            mobile TEXT,
            nif TEXT NOT NULL
        )
    ''')

    # Tabela Bilhetes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_session INTEGER,
            seat_row TEXT,
            seat_number INTEGER,
            id_user INTEGER,
            paid_price DECIMAL(10,2),
            checkin DATETIME,
            FOREIGN KEY (id_session) REFERENCES sessions(id),
            FOREIGN KEY (id_user) REFERENCES users(id)
        )
    ''')

    # Tabela Utilizadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            mobile TEXT,
            nif TEXT NOT NULL,
            password PASSWORD NOT NULL,
            user_type TEXT CHECK(user_type IN ('admin','operator')) DEFAULT 'operator'
        )
    ''')

    if cursor.execute('''SELECT count(*) FROM users WHERE user_type = 'admin' ''').fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (name, email, mobile, nif, password, user_type) VALUES ('admin', 'admin@admin', '123456789', '123456789', 'admin', 'admin')
        ''')

    conn.commit()
    conn.close()
    print("Base de dados 'eventos_bilhetes.db' criada/verificada com sucesso!")
