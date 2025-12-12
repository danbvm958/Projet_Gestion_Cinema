"""
Script de recréation de la base de données du cinéma
Crée toutes les tables nécessaires et insère les données par défaut
"""
import sqlite3

# Recrée toutes les tables de la base de données
def recreate_database():
    """Recrée toutes les tables de la base de données et insère les données par défaut"""
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    print("Recreating database...")
    
    # Table films
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            year INTEGER,
            genre TEXT,
            duration INTEGER,
            classification TEXT,
            poster_url TEXT
        )
    ''')
    
    # Table users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Table salles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER UNIQUE,
            capacity INTEGER
        )
    ''')
    
    # Table seances
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            film_id INTEGER,
            salle INTEGER,
            horaire TEXT,
            FOREIGN KEY(film_id) REFERENCES films(id)
        )
    ''')

    # Table reservations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            seance_id INTEGER,
            seats INTEGER DEFAULT 1,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(seance_id) REFERENCES seances(id)
        )
    ''')
    
    # Créer un utilisateur administrateur par défaut
    # IntegrityError est levée si l'utilisateur existe déjà (UNIQUE constraint)
    try:
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES ('admin', 'admin123', 'admin')
        ''')
        print("Admin user created.")
    except sqlite3.IntegrityError:
        print("Admin user already exists.")

    # Créer 5 salles avec différentes capacités
    salles = [
        (1, 100),
        (2, 80),
        (3, 120),
        (4, 60),
        (5, 150)
    ]
    for num, cap in salles:
        try:
            cursor.execute('INSERT INTO salles (number, capacity) VALUES (?, ?)', (num, cap))
        except sqlite3.IntegrityError:
            pass  # La salle existe déjà, on ignore l'erreur
    print("Default salles created.")

    conn.commit()
    conn.close()
    print("Database recreated successfully.")

if __name__ == "__main__":
    recreate_database()
