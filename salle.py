import sqlite3
from flask import request, jsonify, render_template
from app import app

class Room:
    """Classe représentant une salle de cinéma"""
    
    # Crée une salle avec son numéro et sa capacité maximale
    def __init__(self, number, capacity):
        """Initialise une salle avec son numéro et sa capacité"""
        self.number = number
        self.capacity = capacity

    # Enregistre la salle dans la base de données
    def save_to_db(self):
        """Enregistre la salle dans la base de données"""
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER,
                capacity INTEGER
            )
        ''')

        cursor.execute('''
            INSERT INTO salles (number, capacity)
            VALUES (?, ?)
        ''', (self.number, self.capacity))

        conn.commit()
        conn.close()

# Route pour ajouter une nouvelle salle dans le cinéma
@app.route('/add_room', methods=['POST'])
def add_room():
    """Ajoute une nouvelle salle dans la base de données"""
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400

    required = ['number', 'capacity']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant : {key}"}), 400

    try:
        # Conversion en entier avec gestion d'erreur
        number = int(data['number'])
        capacity = int(data['capacity'])
    except ValueError:
        return jsonify({'message': 'number et capacity doivent être des entiers.'}), 400

    try:
        with sqlite3.connect('cinema.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS salles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number INTEGER UNIQUE,
                    capacity INTEGER
                )
            ''')
            cursor.execute("SELECT * FROM salles WHERE number = ?", (number,))
            if cursor.fetchone():
                return jsonify({'message': f"La salle numéro {number} existe déjà."}), 409

            cursor.execute("INSERT INTO salles (number, capacity) VALUES (?, ?)", (number, capacity))
            conn.commit()

        return jsonify({'message': 'Salle ajoutée avec succès', 'number': number, 'capacity': capacity}), 201

    except sqlite3.Error as e:
        return jsonify({'message': 'Erreur base de données', 'error': str(e)}), 500

# Route API pour récupérer toutes les salles en format JSON
@app.route('/salles', methods=['GET'])
def get_salles():
    """Retourne la liste de toutes les salles disponibles"""
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, number, capacity
        FROM salles
        ORDER BY number
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    salles = [
        {
            'id': row[0],
            'number': row[1],
            'capacity': row[2]
        }
        for row in rows
    ]
    return jsonify(salles), 200
