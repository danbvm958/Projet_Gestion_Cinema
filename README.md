# 🎬 Système de Gestion de Cinéma - CY Tech

Application web complète de gestion de cinéma développée avec Flask et SQLite.

## 📋 Fonctionnalités

### Gestion des utilisateurs
- **Inscription** : Création de compte utilisateur
- **Connexion** : Authentification avec système de sessions
- **Rôles** : Distinction admin/utilisateur avec permissions

### Gestion des films (Admin)
- Ajout de films avec informations complètes (titre, année, genre, durée, classification)
- Affichage de posters de films
- Consultation de la liste des films

### Gestion des salles (Admin)
- Création de salles avec capacités personnalisées
- 5 salles par défaut (capacités : 100, 80, 120, 60, 150)

### Gestion des séances (Admin)
- Création de séances (film + salle + horaire)
- Vérification automatique des chevauchements d'horaires
- Suppression de séances
- Calcul automatique des places disponibles

### Système de réservation (Utilisateurs)
- Réservation de 1 à 5 places par séance
- Limite de 5 places maximum par film (toutes séances confondues)
- Vérification de la disponibilité en temps réel
- Consultation de l'historique des réservations

## 🏗️ Structure du projet

```
Gestion-de-cinema/
├── app.py              # Application principale et routes utilisateurs
├── seances.py          # Gestion des séances
├── salle.py            # Gestion des salles
├── recreate_db.py      # Script de création de la base de données
├── requirements.txt    # Dépendances Python
├── cinema.db           # Base de données SQLite (générée automatiquement)
├── static/
│   └── css/
│       └── styles.css  # Styles CSS du thème cinéma
└── templates/          # Pages HTML
    ├── home.html           # Page d'accueil
    ├── login.html          # Connexion
    ├── register.html       # Inscription
    ├── sessions.html       # Liste des séances
    ├── my_bookings.html    # Réservations utilisateur
    ├── admin_films.html    # Gestion films (admin)
    ├── admin_seances.html  # Gestion séances (admin)
    └── error.html          # Page d'erreur
```

## 🚀 Installation et démarrage

### 1. Créer l'environnement virtuel

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Initialiser la base de données

```bash
python recreate_db.py
```

Cela crée :
- Les tables nécessaires
- Un compte admin (username: `admin`, password: `admin123`)
- 5 salles par défaut

### 4. Lancer l'application

```bash
flask run
```

L'application sera accessible sur `http://127.0.0.1:5000`

## 🔑 Comptes par défaut

**Administrateur :**
- Username : `admin`
- Password : `admin123`

## 📚 Documentation du code

### Classes principales

#### `Films` (app.py)
Représente un film avec ses informations (titre, année, genre, durée, classification, poster)

#### `Users` (app.py)
Représente un utilisateur avec authentification et rôle

#### `Seance` (seances.py)
Représente une séance avec vérification automatique des chevauchements

#### `Room` (salle.py)
Représente une salle de cinéma avec sa capacité

### Routes principales

**Publiques :**
- `/` : Page d'accueil
- `/login` : Connexion
- `/register` : Inscription

**Utilisateurs connectés :**
- `/sessions` : Liste des séances
- `/my-bookings` : Mes réservations
- `/reserve` (POST) : Réserver des places

**Administrateurs :**
- `/admin/films` : Gestion des films
- `/admin/sessions` : Gestion des séances
- `/add_film` (POST) : Ajouter un film
- `/add_seance` (POST) : Ajouter une séance
- `/delete_seance/<id>` (DELETE) : Supprimer une séance

## 🎯 Vérifications implémentées

✅ Pas de doublons sur les utilisateurs, salles, films  
✅ Impossible d'ajouter une séance avec un film inexistant  
✅ Vérification des chevauchements d'horaires dans une même salle  
✅ Impossible de réserver sur une séance complète  
✅ Limite de 5 places par personne et par film  
✅ Vérification des capacités en temps réel  

## 🛠️ Technologies utilisées

- **Backend** : Flask (Python)
- **Base de données** : SQLite
- **Frontend** : HTML, CSS, JavaScript vanilla
- **Authentification** : Flask sessions
- **Design** : Thème cinéma moderne (dark mode)

## 📝 Notes importantes

- La base de données est créée automatiquement au premier lancement
- Les sessions utilisateurs utilisent des cookies sécurisés
- Le design est responsive et adapté aux mobiles
- Les dates et heures sont au format français

## 🐛 Dépannage

**Problème avec l'environnement virtuel :**
1. Supprimer le dossier `venv`
2. Recréer : `python -m venv venv`
3. Activer l'environnement
4. Réinstaller : `pip install -r requirements.txt`


**Port déjà utilisé :**
```bash
flask run --port 5001
```

## 👥 Auteurs

Projet développé dans le cadre du cours de Python - CY Tech Ing1 GIA 2
Dan Nicolas Ilann Boudria
