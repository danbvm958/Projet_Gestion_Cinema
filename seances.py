# seances.py
import sqlite3
from flask import request, jsonify, render_template, session
# datetime permet de manipuler les dates et heures
from datetime import datetime, timedelta
from app import app

class Seance:
    """Classe représentant une séance de cinéma"""
    
    # Crée une séance avec le film, la salle et l'horaire
    def __init__(self, film_id, salle, horaire):
        """Initialise une séance avec le film, la salle et l'horaire"""
        self.film_id = film_id
        self.salle = salle

        # Si l'horaire est au format "HH:MM", on ajoute la date du jour
        if len(horaire) == 5:  # ex : "21:00"
            date = datetime.today().strftime("%Y-%m-%d")
            self.horaire = f"{date} {horaire}"
        else:
            self.horaire = horaire

    # Enregistre la séance après avoir vérifié qu'il n'y a pas de conflit d'horaire
    def save_to_db(self):
        """Enregistre la séance dans la base de données après vérifications"""
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()

        # Création de la table si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                film_id INTEGER,
                salle INTEGER,
                horaire TEXT,
                FOREIGN KEY(film_id) REFERENCES films(id)
            )
        ''')

        # Vérifier que le film existe et récupérer sa durée
        cursor.execute('SELECT title, duration FROM films WHERE id = ?', (self.film_id,))
        # fetchone() récupère une seule ligne du résultat
        film = cursor.fetchone()
        if not film:
            conn.close()
            # raise permet de lever une erreur qui arrête l'exécution
            raise Exception(f"Film ID {self.film_id} inexistant.")

        duree_film = film[1]  # colonne duration

        # Vérifier que la salle existe dans la table 'salles'
        cursor.execute('SELECT id FROM salles WHERE number = ?', (self.salle,))
        if not cursor.fetchone():
            conn.close()
            raise Exception(f"Salle numéro {self.salle} inexistante. Veuillez d'abord créer la salle.")

        # Calcul du début et de la fin de la séance
        # strptime() convertit une chaîne en objet datetime
        debut = datetime.strptime(self.horaire, "%Y-%m-%d %H:%M")
        # timedelta() permet d'ajouter une durée (ici en minutes)
        fin = debut + timedelta(minutes=duree_film)

        # Récupérer les autres séances de la même salle
        cursor.execute('''
            SELECT seances.horaire, films.duration
            FROM seances
            JOIN films ON seances.film_id = films.id
            WHERE seances.salle = ?
        ''', (self.salle,))
        autres_seances = cursor.fetchall()

        # Vérification des chevauchements avec les séances existantes
        for h_existante, duree_existante in autres_seances:
            debut2 = datetime.strptime(h_existante, "%Y-%m-%d %H:%M")
            fin2 = debut2 + timedelta(minutes=duree_existante)

            # Condition de chevauchement
            if debut < fin2 and fin > debut2:
                conn.close()
                raise Exception(
                    f"Chevauchement détecté : séance existante "
                    f"{debut2.strftime('%H:%M')}–{fin2.strftime('%H:%M')}."
                )

        # Enregistrer la séance
        cursor.execute('''
            INSERT INTO seances (film_id, salle, horaire)
            VALUES (?, ?, ?)
        ''', (self.film_id, self.salle, self.horaire))

        conn.commit()
        conn.close()


# Route pour ajouter une nouvelle séance (admin uniquement)
@app.route('/add_seance', methods=['POST'])
def add_seance():
    """Ajoute une nouvelle séance après vérification (réservé aux admins)"""
    # Vérifier que l'utilisateur est admin
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Accès refusé. Réservé aux administrateurs.'}), 403
    
    data = request.get_json()

    if not data:
        return jsonify({'message': 'JSON manquant.'}), 400

    required = ['film_id', 'salle']
    for key in required:
        if key not in data:
            return jsonify({'message': f"Champ manquant : {key}"}), 400

    try:
        salle = int(data['salle'])
    except (ValueError, TypeError):
        return jsonify({'message': 'Numéro de salle invalide.'}), 400
        
    if salle < 1 or salle > 5:
        return jsonify({'message': 'La salle doit être entre 1 et 5.'}), 400

    # Construire l'horaire complet à partir de date et horaire
    if 'date' in data and 'horaire' in data:
        horaire_complet = f"{data['date']} {data['horaire']}"
    elif 'horaire' in data:
        horaire_complet = data['horaire']
    else:
        return jsonify({'message': 'Champ manquant : horaire ou (date + horaire)'}), 400

    # Vérifier que la séance est dans le futur
    try:
        seance_datetime = datetime.strptime(horaire_complet, "%Y-%m-%d %H:%M")
        maintenant = datetime.now()
        
        if seance_datetime <= maintenant:
            return jsonify({'message': 'Impossible de créer une séance dans le passé. Veuillez choisir une date et heure futures.'}), 400
    except ValueError:
        return jsonify({'message': 'Format de date/horaire invalide. Format attendu : YYYY-MM-DD HH:MM'}), 400

    try:
        seance = Seance(
            film_id=data['film_id'],
            salle=salle,
            horaire=horaire_complet
        )
        seance.save_to_db()
        return jsonify({'message': 'Séance créée avec succès ✅'}), 201

    except Exception as e:
        return jsonify({'message': str(e)}), 400



# Route Flask : liste des séances (API JSON)

# Route API pour récupérer toutes les séances avec calcul des places disponibles
@app.route('/api/seances', methods=['GET'])
def get_seances():
    """Retourne la liste de toutes les séances avec places disponibles"""
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()

    # Requête complexe avec plusieurs JOIN pour récupérer toutes les infos nécessaires
    # COALESCE() retourne la première valeur non-NULL (ici 0 si aucune réservation)
    cursor.execute('''
        SELECT 
            s.id, 
            f.title, 
            s.salle, 
            s.horaire, 
            f.poster_url,
            sa.capacity,
            (SELECT COALESCE(SUM(r.seats), 0) FROM reservations r WHERE r.seance_id = s.id) as reserved_seats
        FROM seances s
        JOIN films f ON s.film_id = f.id
        JOIN salles sa ON s.salle = sa.number
        ORDER BY s.horaire
    ''')
    rows = cursor.fetchall()
    conn.close()

    seances = []
    for row in rows:
        capacity = row[5]
        reserved = row[6]
        remaining = capacity - reserved
        
        seances.append({
            'id': row[0], 
            'film': row[1], 
            'salle': row[2], 
            'horaire': row[3],
            'poster_url': row[4] if row[4] else '',
            'capacity': capacity,
            'remaining': remaining
        })
        
    return jsonify(seances), 200


# Route affichant la page de gestion des séances (admin uniquement)
@app.route('/admin/sessions')
def ajout_seance_page():
    """Affiche la page de gestion des séances (réservé aux admins)"""
    # Vérifier que l'utilisateur est admin
    if 'username' not in session or session.get('role') != 'admin':
        return render_template('error.html', message='Accès refusé. Réservé aux administrateurs.'), 403
    return render_template('admin_seances.html')

# Route affichant toutes les séances pour les utilisateurs connectés
@app.route('/sessions')
def seances_page():
    """Affiche la page de visualisation des séances (accessible à tous les connectés)"""
    if 'username' not in session:
        return render_template('error.html', message='Veuillez vous connecter pour accéder aux séances.'), 403
    return render_template('sessions.html')

# Route pour supprimer une séance et ses réservations (admin uniquement)
@app.route('/delete_seance/<int:seance_id>', methods=['DELETE'])
def delete_seance(seance_id):
    """Supprime une séance et toutes ses réservations (réservé aux admins)"""
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Accès refusé. Réservé aux administrateurs.'}), 403
    
    try:
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        
        # Vérifier si la séance existe
        cursor.execute('SELECT id FROM seances WHERE id = ?', (seance_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Séance introuvable.'}), 404
        
        # Supprimer les réservations associées
        cursor.execute('DELETE FROM reservations WHERE seance_id = ?', (seance_id,))
        
        # Supprimer la séance
        cursor.execute('DELETE FROM seances WHERE id = ?', (seance_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Séance supprimée avec succès.'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erreur: {str(e)}'}), 500
