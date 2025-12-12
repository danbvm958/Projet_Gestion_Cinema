import sqlite3
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS

# Création de l'application Flask
app = Flask(__name__)
app.secret_key = 'change'
CORS(app, supports_credentials=True, origins=['http://127.0.0.1:5000', 'http://localhost:5000'])

class Films:
    """Classe représentant un film dans la base de données"""
    
    # Initialise un film avec toutes ses informations
    def __init__(self, title, year, genre, duration, classification, poster_url=None):
        """Initialise un film avec ses informations"""
        self.title = title
        self.year = year
        self.genre = genre
        self.duration = duration
        self.classification = classification
        self.poster_url = poster_url

    # Enregistre le film dans la base de données SQLite
    def save_to_db(self):
        """Enregistre le film dans la base de données SQLite"""
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
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
        cursor.execute('''
            INSERT INTO films (title, year, genre, duration, classification, poster_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.title, self.year, self.genre, self.duration, self.classification, self.poster_url))
        conn.commit()
        conn.close()


class Users:
    """Classe représentant un utilisateur du système"""
    
    # Crée un utilisateur avec son nom, mot de passe et rôle (admin ou user)
    def __init__(self, username, password, role='user'):
        """Initialise un utilisateur avec nom d'utilisateur, mot de passe et rôle (admin ou user)"""
        self.username = username
        self.password = password
        self.role = role
    
    # Enregistre l'utilisateur dans la table 'users' de la base de données
    def save_to_db(self):
        """Enregistre l'utilisateur dans la base de données"""
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', (self.username, self.password, self.role))
        conn.commit()
        conn.close()

# Route pour créer un nouveau compte utilisateur
@app.route('/register', methods=['POST'])
def register():
    """Enregistre un nouvel utilisateur dans la base de données"""
    # Récupère les données JSON de la requête
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400
    required = ['username', 'password']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant: {key}"}), 400
    
    # Par défaut, les nouveaux utilisateurs sont 'user', sauf si un rôle est spécifié
    role = data.get('role', 'user')
    if role not in ['admin', 'user']:
        role = 'user'
    
    try:
        new_user = Users(
            username=data['username'],
            password=data['password'],
            role=role
        )
        new_user.save_to_db()
        return jsonify({'message': 'Utilisateur enregistré avec succès', 'role': role}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Ce nom d\'utilisateur existe déjà'}), 400

# Route pour connecter un utilisateur existant
@app.route('/login', methods=['POST'])
def login():
    """Connecte un utilisateur et crée une session"""
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400
    username = data['username']
    password = data['password']
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, password, role FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        session['username'] = result[1]
        session['role'] = result[3] if len(result) > 3 else 'user'
        return jsonify({
            'message': 'Connexion réussie',
            'username': result[1],
            'role': session['role']
        }), 200
    else:
        return jsonify({'message': 'Identifiants invalides'}), 401

# Route pour vérifier si l'utilisateur est connecté
@app.route('/check_session', methods=['GET'])
def check_session():
    """Vérifie si l'utilisateur a une session active"""
    if 'username' in session:
        return jsonify({
            'message': 'Session valide',
            'username': session['username'],
            'role': session.get('role', 'user')
        }), 200
    else:
        return jsonify({'message': 'Aucune session active'}), 401

# Route pour ajouter un film (admin uniquement)
@app.route('/add_film', methods=['POST'])
def add_film():
    """Ajoute un nouveau film à la base de données (réservé aux admins)"""
    # Vérifier que l'utilisateur est admin
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Accès refusé. Réservé aux administrateurs.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Requête invalide, JSON attendu.'}), 400
    required = ['title', 'year', 'genre', 'duration', 'classification']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant: {key}"}), 400
    new_film = Films(
        title=data['title'],
        year=data['year'],
        genre=data['genre'],
        duration=data['duration'],
        classification=data['classification'],
        poster_url=data.get('poster_url', '')
    )
    new_film.save_to_db()
    return jsonify({'message': 'Film added successfully'}), 201

# Route pour récupérer tous les films en format JSON
@app.route('/films', methods=['GET'])
def get_films():
    """Retourne la liste de tous les films disponibles"""
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, year, genre, duration, classification, poster_url
        FROM films
        ORDER BY title
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    films = [
        {
            'id': row[0],
            'title': row[1],
            'year': row[2],
            'genre': row[3],
            'duration': row[4],
            'classification': row[5],
            'poster_url': row[6] if len(row) > 6 else ''
        }
        for row in rows
    ]
    return jsonify(films), 200

# Route pour mettre à jour l'affiche d'un film (réservé aux admins)
@app.route('/update_film_poster/<int:film_id>', methods=['PUT'])
def update_film_poster(film_id):
    """Met à jour l'URL de l'affiche d'un film (réservé aux admins)"""
    # Vérifier que l'utilisateur est admin
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Accès refusé. Réservé aux administrateurs.'}), 403
    
    data = request.get_json()
    if not data or 'poster_url' not in data:
        return jsonify({'message': 'URL de l\'affiche manquante'}), 400
    
    poster_url = data['poster_url']
    
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    
    # Vérifier que le film existe
    cursor.execute('SELECT id FROM films WHERE id = ?', (film_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Film introuvable'}), 404
    
    # Mettre à jour l'affiche
    cursor.execute('UPDATE films SET poster_url = ? WHERE id = ?', (poster_url, film_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Affiche mise à jour avec succès'}), 200


# Route de la page d'accueil affichant toutes les séances
@app.route('/')
def accueil():
    """Affiche la page d'accueil avec les séances disponibles"""
    return render_template('home.html')

# Route de la page de gestion des films (admin uniquement)
@app.route('/admin/films')
def ajout_film():
    """Affiche la page de gestion des films (réservé aux admins)"""
    # Vérifier que l'utilisateur est admin
    if 'username' not in session or session.get('role') != 'admin':
        return render_template('error.html', message='Accès refusé. Réservé aux administrateurs.'), 403
    return render_template('admin_films.html')

# Route affichant le formulaire d'inscription
@app.route('/register')
def inscription():
    """Affiche la page d'inscription"""
    return render_template('register.html')

# Route affichant le formulaire de connexion
@app.route('/login')
def connection():
    """Affiche la page de connexion"""
    return render_template('login.html')

# Route pour déconnecter l'utilisateur
@app.route('/logout', methods=['POST'])
def logout():
    """Déconnecte l'utilisateur en supprimant sa session"""
    # clear() supprime toutes les données de la session
    session.clear()
    return jsonify({'message': 'Déconnexion réussie'}), 200

# Route pour réserver des places pour une séance
@app.route('/reserve', methods=['POST'])
def reserve_seat():
    """Réserve une ou plusieurs places pour une séance (limite de 5 places par film)"""
    if 'username' not in session:
        return jsonify({'message': 'Veuillez vous connecter pour réserver.'}), 401

    data = request.get_json()
    if not data or 'seance_id' not in data:
        return jsonify({'message': 'ID de séance manquant.'}), 400

    seance_id = data['seance_id']
    
    # int() convertit une chaîne de caractères en nombre entier
    try:
        seats_requested = int(data.get('seats', 1))
    except (ValueError, TypeError):
        return jsonify({'message': 'Nombre de places invalide.'}), 400
    
    # Validation: entre 1 et 5 places maximum
    if seats_requested < 1 or seats_requested > 5:
        return jsonify({'message': 'Vous pouvez réserver entre 1 et 5 places maximum.'}), 400

    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()

    try:
        # 1. Récupérer la salle de la séance et le film
        cursor.execute('SELECT salle, film_id FROM seances WHERE id = ?', (seance_id,))
        seance_row = cursor.fetchone()
        if not seance_row:
            return jsonify({'message': 'Séance introuvable.'}), 404
        
        salle_number = seance_row[0]
        film_id = seance_row[1]

        # 2. Récupérer la capacité de la salle
        cursor.execute('SELECT capacity FROM salles WHERE number = ?', (salle_number,))
        salle_row = cursor.fetchone()
        if not salle_row:
            # Fallback si la salle n'est pas dans la table salles (ne devrait pas arriver si bien géré)
            return jsonify({'message': 'Salle introuvable configuration manquante.'}), 500
        
        capacity = salle_row[0]

        # 3. Compter les réservations actuelles
        cursor.execute('SELECT SUM(seats) FROM reservations WHERE seance_id = ?', (seance_id,))
        result = cursor.fetchone()
        current_reserved = result[0] if result[0] else 0

        # 4. Vérifier la disponibilité
        if current_reserved + seats_requested > capacity:
            remaining = capacity - current_reserved
            return jsonify({'message': f'Complet ou places insuffisantes. Restant : {remaining}'}), 409

        # 5. Récupérer l'ID utilisateur
        cursor.execute('SELECT id FROM users WHERE username = ?', (session['username'],))
        user_row = cursor.fetchone()
        if not user_row:
            return jsonify({'message': 'Utilisateur introuvable.'}), 404
        
        user_id = user_row[0]
        
        # 6. Vérifier le nombre total de places réservées par cet utilisateur pour ce film
        cursor.execute('''
            SELECT SUM(r.seats) 
            FROM reservations r
            JOIN seances s ON r.seance_id = s.id
            WHERE r.user_id = ? AND s.film_id = ?
        ''', (user_id, film_id))
        
        user_total_for_film = cursor.fetchone()[0] or 0
        
        if user_total_for_film + seats_requested > 5:
            remaining_allowed = 5 - user_total_for_film
            return jsonify({
                'message': f'Limite dépassée : vous avez déjà {user_total_for_film} place(s) pour ce film. Maximum 5 places par film. Vous pouvez encore réserver {remaining_allowed} place(s).'
            }), 409

        # 7. Enregistrer la réservation
        cursor.execute('''
            INSERT INTO reservations (user_id, seance_id, seats)
            VALUES (?, ?, ?)
        ''', (user_id, seance_id, seats_requested))
        
        conn.commit()
        return jsonify({'message': f'Réservation confirmée : {seats_requested} place(s) !'}), 201

    except Exception as e:
        return jsonify({'message': f'Erreur serveur: {str(e)}'}), 500
    finally:
        conn.close()

# Route affichant la page des réservations de l'utilisateur
@app.route('/my-bookings')
def mes_reservations_page():
    """Affiche la page des réservations de l'utilisateur connecté"""
    if 'username' not in session:
        return render_template('error.html', message='Veuillez vous connecter pour voir vos réservations.'), 403
    return render_template('my_bookings.html')

# Route API pour récupérer les réservations de l'utilisateur en JSON
@app.route('/api/mes_reservations', methods=['GET'])
def get_my_reservations():
    """Retourne la liste des réservations de l'utilisateur connecté"""
    if 'username' not in session:
        return jsonify({'message': 'Non connecté'}), 401

    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()

    # Récupérer l'ID utilisateur
    cursor.execute('SELECT id FROM users WHERE username = ?', (session['username'],))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        return jsonify({'message': 'Utilisateur introuvable'}), 404
    
    user_id = user_row[0]

    # On récupère les réservations avec les infos du film et de la séance
    cursor.execute('''
        SELECT 
            r.id, 
            f.title, 
            s.horaire, 
            s.salle, 
            r.seats, 
            r.timestamp,
            f.poster_url
        FROM reservations r
        JOIN seances s ON r.seance_id = s.id
        JOIN films f ON s.film_id = f.id
        WHERE r.user_id = ?
        ORDER BY s.horaire DESC
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()

    reservations = [
        {
            'id': row[0],
            'film': row[1],
            'horaire': row[2],
            'salle': row[3],
            'seats': row[4],
            'timestamp': row[5],
            'poster_url': row[6] if row[6] else ''
        }
        for row in rows
    ]

    return jsonify(reservations), 200

import seances
import salle

if __name__ == '__main__':
    app.run(debug=True)