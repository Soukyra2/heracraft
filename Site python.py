# app_single_file.py - Application Flask/JSON Thème Sombre MODERNE

import json
import os
from datetime import datetime, timedelta

# Imports Flask et outils de sécurité
from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages 
from werkzeug.security import generate_password_hash, check_password_hash
from jinja2 import Environment, DictLoader 

# #################################################################
# 0. CONFIGURATION ET UTILITAIRES
# #################################################################

# 🚨 CHEMIN DU FICHIER DE DONNÉES (CHEMIN ABSOLU SPÉCIFIÉ)
DATA_FILE = r'heracraft/data.json'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def create_initial_data():
    """Crée la structure de données initiale avec un SuperAdmin par défaut."""
    admin_hash = generate_password_hash("password123") 
    now_str = datetime.now().strftime(DATE_FORMAT)
    return {
        "last_user_id": 1, "last_article_id": 1, "last_shop_item_id": 1,
        "users": [{ 
            "id": 1, 
            "pseudo": "SuperAdmin", 
            "email": "admin@example.com", 
            "password_hash": admin_hash, 
            "grade": "Administrateur", 
            "status": "Actif", 
            "suspension_reason": None, 
            "suspension_end_date": None,
            "gemmes": 500
        }],
        "articles": [{ 
            "id": 1, 
            "titre": "Article Initial de Bienvenue", 
            "contenu": "Ceci est le premier article, créé automatiquement au lancement de l'application.", 
            "auteur_id": 1, 
            "date_publication": now_str
        }],
        "shop_items": [{
            "id": 1,
            "nom": "Clé de Caisse Basique",
            "description": "Une clé pour ouvrir une caisse de récompenses standard en jeu.",
            "prix_gemmes": 50,
            "date_ajout": now_str
        }]
    }

def load_data():
    """Charge les données depuis le fichier JSON ou le crée/met à jour si nécessaire. (Fonction inchangée)"""
    dir_name = os.path.dirname(DATA_FILE)
    if dir_name and not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except OSError as e:
            print(f"ERREUR : Impossible de créer le répertoire {dir_name}. Détail: {e}")
            return create_initial_data() 

    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        data = create_initial_data()
        save_data(data)
        return data
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # MAJ de la structure pour les anciens utilisateurs
            for user in data.get('users', []):
                if 'status' not in user:
                    user['status'] = 'Actif'
                    user['suspension_reason'] = None
                    user['suspension_end_date'] = None
                if 'gemmes' not in user:
                    user['gemmes'] = 0
            if 'shop_items' not in data:
                 data['shop_items'] = []
            if 'last_shop_item_id' not in data:
                 data['last_shop_item_id'] = len(data['shop_items']) 
            return data
    except json.JSONDecodeError:
        print(f"ATTENTION : Le fichier {DATA_FILE} est corrompu. Recréation de la structure initiale.")
        data = create_initial_data()
        save_data(data)
        return data
    except Exception as e:
        print(f"ERREUR INCONNUE lors du chargement de {DATA_FILE}: {e}")
        return create_initial_data()

def save_data(data):
    """Sauvegarde les données dans le fichier JSON. (Fonction inchangée)"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"ERREUR FATALE: Impossible d'écrire dans le fichier {DATA_FILE}. Détail: {e}")

def get_user_by_id(user_id):
    """Récupère un utilisateur par son ID. (Fonction inchangée)"""
    data = load_data()
    for user in data['users']:
        if user['id'] == user_id:
            return user
    return None

# #################################################################
# 1. DEFINITION DES TEMPLATES HTML EN PYTHON
# #################################################################

TEMPLATES = {
    # 1. TEMPLATE DE BASE (MISE EN PAGE ET STYLES MODERNES)
    'layout.html': """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}HeraCraft - Modern Dark{% endblock %}</title>
    <style>
        :root {
            --primary-color: #39ff14; /* Vert Néon/Cyber */
            --secondary-color: #909090; 
            --success-color: #4CAF50;
            --error-color: #FF4444;
            --bg-color: #0d1117; /* Fond très sombre */
            --container-bg: #161b22; /* Contenant légèrement plus clair */
            --text-color: #f0f6fc; /* Texte blanc cassé */
            --header-bg: #010409; 
            --accent-color: #ffd700; /* Jaune Or */
            --warning-color: #ffaa00; 
            --gemme-color: #66CCFF; /* Bleu Ciel pour les Gemmes */
            --shop-bg: #21262d; 
            --border-color: #30363d;
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: var(--bg-color); color: var(--text-color); min-height: 100vh; }
        header { background-color: var(--header-bg); color: white; padding: 1em 0; box-shadow: 0 4px 8px rgba(0,0,0,0.4); border-bottom: 2px solid var(--border-color); }
        .header-content { width: 90%; max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        header a { color: var(--text-color); margin: 0 10px; text-decoration: none; transition: color 0.3s, transform 0.2s; font-weight: 500; }
        header a:hover { color: var(--primary-color); transform: translateY(-1px); }
        
        /* Conteneur principal modernisé */
        .container { 
            width: 90%; 
            max-width: 800px; 
            margin: 40px auto; 
            background-color: var(--container-bg); 
            padding: 30px 40px; 
            border-radius: 12px; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.5); 
            border: 1px solid var(--border-color); 
        }
        
        /* Titres */
        h2 { color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 10px; margin-bottom: 25px; font-weight: 600; }
        
        /* Articles/Sections */
        .article, .shop-item, .user-list-item { 
            background-color: var(--shop-bg); 
            border: 1px solid var(--border-color); 
            padding: 20px; 
            margin-bottom: 15px; 
            border-radius: 8px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        .article h3 { color: var(--accent-color); margin-top: 0; }
        
        /* Flash Messages */
        .flash { padding: 15px; margin-bottom: 20px; border-radius: 6px; font-weight: bold; border: 1px solid; animation: fadeIn 0.5s; }
        .flash.success { background-color: #1c3a1c; color: var(--success-color); border-color: #387c38; }
        .flash.error { background-color: #4a1c1c; color: var(--error-color); border-color: #8c3838; }
        
        /* Formulaires */
        input[type="text"], input[type="email"], input[type="password"], textarea, select, input[type="date"], input[type="time"], input[type="number"] { 
            width: 100%; padding: 12px; 
            border: 1px solid var(--border-color); 
            border-radius: 6px; 
            box-sizing: border-box; 
            background-color: #21262d; /* Champ de saisie */
            color: var(--text-color); 
            margin-bottom: 15px;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 5px rgba(57, 255, 20, 0.5);
            outline: none;
        }
        label { display: block; margin-bottom: 5px; color: var(--secondary-color); font-size: 0.9em; }
        
        /* Boutons */
        button[type="submit"], .shop-buy-btn { 
            background-color: var(--primary-color); 
            color: #0d1117; /* Texte sombre sur bouton clair */
            padding: 12px 25px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: bold;
            transition: background-color 0.3s, transform 0.2s, box-shadow 0.3s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        button[type="submit"]:hover { 
            background-color: #6eff33; 
            transform: translateY(-2px);
            box-shadow: 0 6px 10px rgba(0,0,0,0.4);
        }
        
        /* Shop */
        .shop-item { display: flex; justify-content: space-between; align-items: center; }
        .shop-price { font-size: 1.2em; font-weight: bold; color: var(--gemme-color); }
        .shop-buy-btn { background-color: var(--gemme-color); color: var(--header-bg); text-decoration: none; padding: 10px 20px; }
        .shop-buy-btn:hover { background-color: #99FFFF; }

        /* Statuts */
        .status-actif { color: var(--success-color); }
        .status-banni { color: var(--error-color); font-weight: bold; }
        .status-suspendu { color: var(--warning-color); font-weight: bold; }
        
        /* Animation */
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1 style="font-size: 1.8em; margin: 0; color: var(--accent-color);">Hera<span style="color: var(--primary-color);">Craft</span></h1>
            <nav style="display: flex;">
                <a href="{{ url_for('accueil') }}">Accueil</a>
                <a href="{{ url_for('wiki') }}">📚 Wiki</a>
                <a href="{{ url_for('shop') }}">🛒 Shop</a>
                
                {% if session.get('loggedin') %}
                    {% if session.get('grade') == 'Administrateur' %}
                        <a href="{{ url_for('creer_article') }}" style="color: var(--accent-color);">➕ Publier</a>
                        <a href="{{ url_for('gestion_utilisateurs') }}" style="color: var(--accent-color);">⚙️ Grades</a>
                        <a href="{{ url_for('gestion_gemmes') }}" style="color: var(--gemme-color);">💎 Gemmes</a> 
                        <a href="{{ url_for('gerer_comptes_admin') }}" style="color: var(--error-color);">🚫 Bans/Susp.</a>
                    {% endif %}
                    <a href="{{ url_for('mon_compte') }}">👤 Mon Compte</a>
                    <a href="{{ url_for('deconnexion') }}" style="color: var(--secondary-color);">Déconnexion</a>
                {% else %}
                    <a href="{{ url_for('connexion') }}">Connexion</a>
                    <a href="{{ url_for('inscription') }}">Inscription</a>
                {% endif %}
            </nav>
        </div>
    </header>

    {% if page_id != 'wiki' %}
        <div class="container">
    {% endif %}

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="flash {{ category }}">{{ message | safe }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}

    {% if page_id != 'wiki' %}
        </div>
    {% endif %}
</body>
</html>
""",

    # 2. TEMPLATE ACCUEIL (Style mis à jour)
    'accueil.html': """
{% extends 'layout.html' %}
{% block title %}Accueil - HeraCraft{% endblock %}
{% block content %}
    
    <div class="heracraft-presentation" style="background-color: #21262d; border: 1px solid var(--border-color); color: var(--text-color); padding: 25px; border-radius: 8px; margin-bottom: 30px; text-align: center;">
        <h2 style="color: var(--accent-color); border-bottom: none;">🎉 Bienvenue sur le site d'HeraCraft ! ⛏️</h2>
        <p>
            HeraCraft est votre serveur Minecraft préféré ! 
            Retrouvez ici toutes les nouvelles, les mises à jour et les événements de la communauté.
            Rejoignez-nous en jeu et sur notre site !
        </p>
    </div>
    
    <h2 style="color: var(--primary-color);">📰 Dernières Actualités</h2>
    
    {% if articles %}
        {% for article in articles %}
            <div class="article">
                <h3>{{ article.titre }}</h3>
                <p>
                    <small style="color: var(--secondary-color);">
                        Publié par {{ article.nom_auteur }} (Grade: {{ article.grade_auteur }}) le {{ article.date_publication }}
                    </small>
                </p>
                <p>{{ article.contenu | truncate(300, true) }}</p>
            </div>
        {% endfor %}
    {% else %}
        <p>Aucun article n'a été trouvé.</p>
        {% if session.get('grade') == 'Administrateur' %}
            <p><a href="{{ url_for('creer_article') }}" style="color: var(--primary-color);">Cliquez ici pour publier le premier article !</a></p>
        {% endif %}
    {% endif %}
{% endblock %}
""",

    # 3. TEMPLATE CONNEXION (Style mis à jour)
    'connexion.html': """
{% extends 'layout.html' %}
{% block title %}Connexion{% endblock %}
{% block content %}
    <h2 style="color: var(--accent-color);">🔑 Connexion</h2>
    
    <form method="POST">
        <div>
            <label for="pseudo">Pseudo ou Email :</label>
            <input type="text" id="pseudo" name="pseudo" required>
        </div>
        <div>
            <label for="mot_de_passe">Mot de passe :</label>
            <input type="password" id="mot_de_passe" name="mot_de_passe" required>
        </div>
        <button type="submit">Se connecter</button>
    </form>
    
    <p style="margin-top: 20px;"><span style="color: var(--secondary-color);">Pas encore de compte ?</span> <a href="{{ url_for('inscription') }}" style="color: var(--primary-color);">Inscrivez-vous ici</a>.</p>
{% endblock %}
""",

    # 4. TEMPLATE INSCRIPTION (Style mis à jour)
    'inscription.html': """
{% extends 'layout.html' %}
{% block title %}Inscription{% endblock %}
{% block content %}
    <h2 style="color: var(--accent-color);">✍️ Inscription</h2>
    
    <form method="POST">
        <div>
            <label for="pseudo">Pseudo :</label>
            <input type="text" id="pseudo" name="pseudo" required>
        </div>
        <div>
            <label for="email">Email :</label>
            <input type="email" id="email" name="email" required>
        </div>
        <div>
            <label for="mot_de_passe">Mot de passe :</label>
            <input type="password" id="mot_de_passe" name="mot_de_passe" required>
        </div>
        <button type="submit">S'inscrire</button>
    </form>
    
    <p style="margin-top: 20px;"><span style="color: var(--secondary-color);">Déjà un compte ?</span> <a href="{{ url_for('connexion') }}" style="color: var(--primary-color);">Connectez-vous ici</a>.</p>
{% endblock %}
""",

    # 5. TEMPLATE CRÉER ARTICLE (Style mis à jour)
    'creer_article.html': """
{% extends 'layout.html' %}
{% block title %}Créer un Article{% endblock %}
{% block content %}
    <h2 style="color: var(--accent-color);">📝 Publier un Nouvel Article</h2>
    
    <form method="POST">
        <div>
            <label for="titre">Titre :</label>
            <input type="text" id="titre" name="titre" required>
        </div>
        <div>
            <label for="contenu">Contenu :</label>
            <textarea id="contenu" name="contenu" rows="10" required></textarea>
        </div>
        <button type="submit">Publier l'Article</button>
    </form>
{% endblock %}
""",
    
    # 6. TEMPLATE : GESTION DES UTILISATEURS (Grades)
    'gestion_utilisateurs.html': """
{% extends 'layout.html' %}
{% block title %}Gestion des Utilisateurs{% endblock %}
{% block content %}
    <h2 style="color: var(--accent-color);">⚙️ Gérer les Grades des Utilisateurs</h2>
    <p style="color: var(--secondary-color);">Cliquez sur "Modifier" pour changer le grade d'un membre.</p>

    {% for user in users %}
        <div class="user-list-item" style="display: flex; justify-content: space-between; align-items: center;">
            <span>
                Pseudo: {{ user.pseudo }} (ID: {{ user.id }}) - Grade actuel: <span style="color: {{ 'red' if user.grade == 'Administrateur' else 'var(--primary-color)' }}; font-weight: bold;">{{ user.grade }}</span>
            </span>
            <a href="{{ url_for('modifier_utilisateur', user_id=user.id) }}" style="color: var(--accent-color); text-decoration: none; padding: 5px 10px; background-color: #30363d; border-radius: 4px; transition: background-color 0.2s;">Modifier</a>
        </div>
    {% endfor %}
{% endblock %}
""",
    
    # 7. TEMPLATE : MODIFIER UN UTILISATEUR (Grades et Réinitialisation de MDP)
    'modifier_utilisateur.html': """
{% extends 'layout.html' %}
{% block title %}Modifier {{ user.pseudo }}{% endblock %}
{% block content %}
    <h2 style="color: var(--accent-color);">Modifier le Compte de {{ user.pseudo }}</h2>
    <p style="color: var(--secondary-color);">Email: {{ user.email }} | Statut: <span class="status-{{ user.status | lower }}">{{ user.status }}</span> | Grade actuel: {{ user.grade }}</p>
    
    <h3 style="margin-top: 30px; color: var(--primary-color);">Changer le Grade</h3>
    <div style="background-color: var(--shop-bg); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <form method="POST">
            <input type="hidden" name="action" value="update_grade">
            <div>
                <label for="grade">Nouveau Grade :</label>
                <select id="grade" name="grade">
                    <option value="Membre" {% if user.grade == 'Membre' %}selected{% endif %}>Membre</option>
                    <option value="Administrateur" {% if user.grade == 'Administrateur' %}selected{% endif %}>Administrateur</option>
                </select>
            </div>
            <button type="submit">Sauvegarder le Grade</button>
        </form>
    </div>
    
    <hr style="margin: 40px 0; border-color: #444;">

    <h3 style="color: var(--error-color);">Réinitialiser le Mot de Passe (Force Reset)</h3>
    <div style="background-color: #331a1a; padding: 20px; border-radius: 8px; border: 1px solid #551b1b;">
        <form method="POST">
            <input type="hidden" name="action" value="reset_password">
            <div>
                <label for="new_password">Nouveau Mot de Passe :</label>
                <input type="password" id="new_password" name="new_password" required>
            </div>
            <div>
                <label for="confirm_password">Confirmer le Nouveau Mot de Passe :</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            <button type="submit" style="background-color: var(--error-color);">Réinitialiser (Force)</button>
        </form>
    </div>
    
    <p style="margin-top: 20px;"><a href="{{ url_for('gestion_utilisateurs') }}" style="color: var(--secondary-color);">Retour à la gestion des grades</a></p>
{% endblock %}
""",

    # 8. TEMPLATE : MON COMPTE (Style mis à jour)
    'mon_compte.html': """
{% extends 'layout.html' %}
{% block title %}Mon Compte{% endblock %}
{% block content %}
    <h2 style="color: var(--accent-color);">👤 Mon Compte</h2>
    <p style="color: var(--secondary-color);">Vous êtes connecté en tant que {{ user.pseudo }} (Grade: <span style="color: {{ 'red' if user.grade == 'Administrateur' else 'var(--primary-color)' }}; font-weight: bold;">{{ user.grade }}</span>).</p>
    
    <div style="background-color: #21262d; padding: 15px; border-radius: 6px; margin-bottom: 30px;">
        <h3 style="margin-top: 0; margin-bottom: 5px; color: var(--gemme-color);">💎 Votre solde de Gemmes : {{ user.gemmes }}</h3>
    </div>

    <h3 style="margin-top: 30px; color: var(--warning-color);">Changer le mot de passe</h3>
    
    <form method="POST">
        <div>
            <label for="ancien_mot_de_passe">Ancien mot de passe :</label>
            <input type="password" id="ancien_mot_de_passe" name="ancien_mot_de_passe" required>
        </div>
        <div>
            <label for="nouveau_mot_de_passe">Nouveau mot de passe :</label>
            <input type="password" id="nouveau_mot_de_passe" name="nouveau_mot_de_passe" required>
        </div>
        <div>
            <label for="confirmation_nouveau_mot_de_passe">Confirmer le nouveau mot de passe :</label>
            <input type="password" id="confirmation_nouveau_mot_de_passe" name="confirmation_nouveau_mot_de_passe" required>
        </div>
        <button type="submit">Modifier le mot de passe</button>
    </form>
{% endblock %}
""",

    # 9. TEMPLATE : WIKI (Styles mis à jour dans Layout)
    'wiki.html': """
{% extends 'layout.html' %}
{% block title %}HeraCraft Wiki{% endblock %}
{% block content %}
    <style>
        .wiki-layout { 
            display: flex; 
            max-width: 1200px; 
            margin: 0 auto; 
            background-color: var(--container-bg); 
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.4); 
            border-radius: 10px;
        }
        .sidebar-nav { 
            width: 250px; 
            background-color: #10141b; 
            padding: 20px 0; 
            flex-shrink: 0; 
            border-right: 1px solid var(--border-color);
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        }
        .sidebar-nav label { 
            display: block; 
            padding: 12px 20px; 
            color: #d0d0d0; 
            text-decoration: none; 
            cursor: pointer; 
            border-left: 3px solid transparent; 
            transition: background-color 0.2s, border-left-color 0.2s; 
        }
        .sidebar-nav label:hover {
            background-color: #161b22;
        }
        .tab-radio { display: none; }
        .wiki-section { display: none; }
        #radio-index:checked ~ .wiki-layout .sidebar-nav label[for="radio-index"], #radio-intro:checked ~ .wiki-layout .sidebar-nav label[for="radio-intro"], #radio-commands:checked ~ .wiki-layout .sidebar-nav label[for="radio-commands"], #radio-grades:checked ~ .wiki-layout .sidebar-nav label[for="radio-grades"], #radio-claim:checked ~ .wiki-layout .sidebar-nav label[for="radio-claim"], #radio-shops:checked ~ .wiki-layout .sidebar-nav label[for="radio-shops"] { 
            border-left-color: var(--primary-color); 
            background-color: var(--container-bg); 
            color: var(--text-color); 
            font-weight: bold; 
        }
        .content-wrapper { flex-grow: 1; padding: 40px; min-height: calc(100vh - 58px - 80px); }
        .code-example { background-color: #21262d; padding: 10px; border-radius: 4px; color: var(--primary-color); font-family: monospace; }
        .wiki-layout h3 { color: var(--accent-color); margin-top: 25px; border-top: 1px solid var(--border-color); padding-top: 15px; }
    </style>
    
    <input type="radio" id="radio-index" name="wiki-tab" class="tab-radio" checked>
    <input type="radio" id="radio-intro" name="wiki-tab" class="tab-radio">
    <input type="radio" id="radio-commands" name="wiki-tab" class="tab-radio">
    <input type="radio" id="radio-grades" name="wiki-tab" class="tab-radio">
    <input type="radio" id="radio-claim" name="wiki-tab" class="tab-radio">
    <input type="radio" id="radio-shops" name="wiki-tab" class="tab-radio">

    <div class="wiki-layout">
        <div class="sidebar-nav">
            <label for="radio-index" style="color: var(--primary-color); font-size: 1.1em;">📝 Table des matières</label>
            <h3>SECTIONS PRINCIPALES</h3>
            <label for="radio-intro">🌳 Présentation Générale</label>
            <label for="radio-commands">⌨️ Commandes</label>
            <label for="radio-grades">⚔️ Grades</label>
            <label for="radio-claim">🔒 Claim</label>
            <label for="radio-shops">💰 Économie & Shops</label>
            <h3 style="border-top: none;">&nbsp;</h3>
            <div class="nav-item" style="color:var(--secondary-color); font-size: 0.8em; padding: 10px 20px;">Propulsé par HeraCraft</div>
        </div>

        <div class="content-wrapper">
            <div id="section-index" class="wiki-section">
                <h1 style="color: var(--accent-color);">HeraCraft Wiki - Index Principal</h1>
                <p style="color: var(--secondary-color);">Sélectionnez une catégorie pour accéder à son contenu.</p>
            </div>
            <div id="section-intro" class="wiki-section"> <h1>🌳 Introduction & Règles</h1> <p>HeraCraft est un serveur de survie semi-moddé...</p> </div>
            <div id="section-commands" class="wiki-section"> <h1>⌨️ Commandes Essentielles</h1> <div class="code-example">/home /sethome /tpa [joueur]</div> </div>
            <div id="section-grades" class="wiki-section"> <h1>⚔️ Progression & Grades</h1> <div class="code-example">/grades</div> </div>
            <div id="section-claim" class="wiki-section"> <h1>🔒 Monde & Protection (Claim)</h1> <div class="code-example">/claimlist /trust [joueur]</div> </div>
            <div id="section-shops" class="wiki-section"> <h1>💰 Économie & Shops</h1> <div class="code-example">Création de boutique...</div> </div>
        </div>
    </div>
{% endblock %}
""",

    # 10. TEMPLATE : GÉRER LES COMPTES ADMIN (Style mis à jour)
    'gerer_comptes_admin.html': """
{% extends 'layout.html' %}
{% block title %}Gestion des Bans/Suspensions{% endblock %}
{% block content %}
    <h2 style="color: var(--error-color);">🚫 Gestion des Comptes (Suspension / Ban)</h2>
    <p style="color: var(--secondary-color);">Cliquez sur "Gérer" pour modifier le statut (actif, suspendu, banni).</p>

    {% for user in users %}
        <div class="user-list-item" style="display: flex; justify-content: space-between; align-items: center;">
            <span>
                **Pseudo:** {{ user.pseudo }} (ID: {{ user.id }}) - Statut: <span class="status-{{ user.status | lower }}">{{ user.status }}</span>
                {% if user.status == 'Suspendu' %}
                    <small style="color: var(--warning-color);"> (Jusqu'au {{ user.suspension_end_date }})</small>
                {% elif user.status == 'Banni' %}
                    <small style="color: var(--error-color);"> (Définitif)</small>
                {% endif %}
            </span>
            {% if user.id != session.get('id') %}
            <a href="{{ url_for('gerer_compte_detail', user_id=user.id) }}" style="color: var(--accent-color); text-decoration: none; padding: 5px 10px; background-color: #30363d; border-radius: 4px; transition: background-color 0.2s;">Gérer</a>
            {% else %}
            <span style="color: var(--secondary-color);"> (Vous) </span>
            {% endif %}
        </div>
    {% endfor %}
{% endblock %}
""",

    # 11. TEMPLATE : GÉRER UN COMPTE ADMIN (Détail Bans/Suspensions)
    'gerer_compte_detail.html': """
{% extends 'layout.html' %}
{% block title %}Gérer {{ user.pseudo }}{% endblock %}
{% block content %}
    <h2 style="color: var(--error-color);">Gérer le Statut du Compte de {{ user.pseudo }}</h2>
    <p style="color: var(--secondary-color);">Email: {{ user.email }} | Grade: {{ user.grade }}</p>
    <p style="font-size: 1.2em; font-weight: bold; margin-bottom: 20px;">Statut actuel: <span class="status-{{ user.status | lower }}">{{ user.status }}</span> | 💎 Solde : **{{ user.gemmes }}**</p>

    <hr style="margin: 30px 0; border-color: #444;">

    <h3 style="margin-top: 30px; color: var(--warning-color);">🚫 Changer le Statut</h3>
    <div style="background-color: var(--shop-bg); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <form method="POST">
            <input type="hidden" name="action" value="update_status">
            <div>
                <label for="status">Nouveau Statut :</label>
                <select id="status" name="status" onchange="toggleSuspensionFields(this.value)">
                    <option value="Actif" {% if user.status == 'Actif' %}selected{% endif %}>Actif</option>
                    <option value="Suspendu" {% if user.status == 'Suspendu' %}selected{% endif %}>Suspendu Temporairement</option>
                    <option value="Banni" {% if user.status == 'Banni' %}selected{% endif %}>Banni Définitivement</option>
                </select>
            </div>

            <div id="suspension-fields" style="border-left: 3px solid var(--warning-color); padding-left: 15px; margin-top: 15px; margin-bottom: 15px; display: {% if user.status == 'Suspendu' %}block{% else %}none{% endif %};">
                <h4>Détails de la suspension</h4>
                <label for="suspension_reason">Raison :</label>
                <textarea id="suspension_reason" name="suspension_reason" rows="3" required>{{ user.suspension_reason if user.suspension_reason else '' }}</textarea>
                
                <label for="suspension_end_date">Date de fin de suspension :</label>
                <input type="date" id="suspension_date" name="suspension_date" value="{{ user.suspension_end_date.split(' ')[0] if user.suspension_end_date and user.status == 'Suspendu' else '' }}">
                <input type="time" id="suspension_time" name="suspension_time" value="{{ user.suspension_end_date.split(' ')[1] if user.suspension_end_date and user.status == 'Suspendu' else '00:00:00' }}" step="1">
            </div>

            <button type="submit">Appliquer le Statut</button>
        </form>
    </div>
    
    <hr style="margin: 40px 0; border-color: #444;">

    <h3 style="margin-top: 50px; color: var(--error-color);">Supprimer Définitivement le Compte</h3>
    <form method="POST" onsubmit="return confirm('Êtes-vous SÛR de vouloir supprimer DÉFINITIVEMENT le compte de {{ user.pseudo }} ? Cette action est irréversible.')">
        <button type="submit" name="action" value="delete_account" style="background-color: var(--error-color);">SUPPRIMER DÉFINITIVEMENT</button>
    </form>
    
    <script>
        function toggleSuspensionFields(status) {
            var fields = document.getElementById('suspension-fields');
            if (status === 'Suspendu') {
                fields.style.display = 'block';
            } else {
                fields.style.display = 'none';
            }
        }
        document.addEventListener('DOMContentLoaded', function() {
            toggleSuspensionFields(document.getElementById('status').value);
        });
    </script>
{% endblock %}
""",

    # 12. TEMPLATE : GESTION DES GEMMES (Liste)
    'gestion_gemmes.html': """
{% extends 'layout.html' %}
{% block title %}Gestion des Gemmes{% endblock %}
{% block content %}
    <h2 style="color: var(--gemme-color);">💎 Gérer le Solde de Gemmes des Utilisateurs</h2>
    <p style="color: var(--secondary-color);">Cliquez sur "Ajuster" pour ajouter ou retirer des Gemmes.</p>

    {% for user in users %}
        <div class="user-list-item" style="display: flex; justify-content: space-between; align-items: center;">
            <span>
                Pseudo: {{ user.pseudo }} (ID: {{ user.id }}) - Grade: {{ user.grade }} - Solde actuel: {{ user.gemmes }} 💎
            </span>
            <a href="{{ url_for('gerer_gemmes_detail', user_id=user.id) }}" style="color: var(--gemme-color); text-decoration: none; padding: 5px 10px; background-color: #30363d; border-radius: 4px; transition: background-color 0.2s;">Ajuster</a>
        </div>
    {% endfor %}
{% endblock %}
""",

    # 13. TEMPLATE : GÉRER LES GEMMES (Détail)
    'gerer_gemmes_detail.html': """
{% extends 'layout.html' %}
{% block title %}Ajuster les Gemmes de {{ user.pseudo }}{% endblock %}
{% block content %}
    <h2 style="color: var(--gemme-color);">Ajuster les Gemmes de {{ user.pseudo }}</h2>
    <p style="color: var(--secondary-color);">Grade: {{ user.grade }} | Statut: <span class="status-{{ user.status | lower }}">{{ user.status }}</span></p>
    <p style="font-size: 1.4em; font-weight: bold; margin-bottom: 30px;">💎 Solde Actuel : **{{ user.gemmes }}**</p>

    <hr style="margin: 30px 0; border-color: #444;">

    <h3 style="margin-top: 30px; color: var(--primary-color);">Opération sur le Solde de Gemmes</h3>
    <div style="background-color: var(--shop-bg); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
        <form method="POST">
            <input type="hidden" name="action" value="update_gemmes">
            
            <div style="display: flex; gap: 10px; align-items: flex-end;">
                <div style="flex-grow: 1;">
                    <label for="gemmes_amount">Montant à ajouter/retirer :</label>
                    <input type="number" id="gemmes_amount" name="gemmes_amount" min="1" required style="width: 100%; margin-bottom: 0;">
                </div>
                <div style="width: 150px;">
                    <label for="gemmes_operation">Opération :</label>
                    <select id="gemmes_operation" name="gemmes_operation" style="width: 100%; margin-bottom: 0;">
                        <option value="add">Ajouter</option>
                        <option value="remove">Retirer</option>
                    </select>
                </div>
                <button type="submit" style="width: 100px; padding: 10px 0; margin-bottom: 15px; background-color: var(--gemme-color); color: var(--header-bg);">Appliquer</button>
            </div>
        </form>
    </div>
    
    <p style="margin-top: 20px;"><a href="{{ url_for('gestion_gemmes') }}" style="color: var(--secondary-color);">← Retour à la liste des Gemmes</a></p>
{% endblock %}
""",

    # 14. TEMPLATE : SHOP (Liste des articles - Style mis à jour)
    'shop.html': """
{% extends 'layout.html' %}
{% block title %}Boutique HeraCraft{% endblock %}
{% block content %}
    <h2 style="color: var(--gemme-color);">🛒 Boutique HeraCraft</h2>
    
    {% if session.get('loggedin') %}
        <p style="text-align: right; font-size: 1.2em; font-weight: bold; color: var(--gemme-color);">💎 Votre solde : **{{ user.gemmes }} Gemmes**</p>
    {% else %}
        <p style="text-align: right; color: var(--warning-color);">Connectez-vous pour voir votre solde de Gemmes.</p>
    {% endif %}

    <hr style="border-color: #444; margin-bottom: 30px;">
    
    {% if session.get('grade') == 'Administrateur' %}
        <div class="shop-admin-link" style="margin-bottom: 30px;">
            <a href="{{ url_for('ajouter_article_shop') }}" style="color: var(--accent-color); text-decoration: none; font-weight: bold;">
                ➕ Ajouter un article (Admin)
            </a>
        </div>
    {% endif %}

    {% if items %}
        {% for item in items %}
            <div class="shop-item">
                <div>
                    <h3 style="margin-top: 0; color: var(--accent-color);">{{ item.nom }}</h3>
                    <p style="color: var(--secondary-color);">{{ item.description }}</p>
                </div>
                <div style="text-align: right; min-width: 150px;">
                    <div class="shop-price">{{ item.prix_gemmes }} 💎</div>
                    {% if session.get('loggedin') %}
                        {% if user.gemmes >= item.prix_gemmes %}
                            <a href="{{ url_for('acheter_article_shop', item_id=item.id) }}" class="shop-buy-btn" onclick="return confirm('Êtes-vous sûr de vouloir acheter {{ item.nom }} pour {{ item.prix_gemmes }} Gemmes ?')">
                                Acheter
                            </a>
                        {% else %}
                            <span style="color: var(--error-color); font-weight: bold; margin-top: 5px; display: block; font-size: 0.9em;">
                                Solde insuffisant
                            </span>
                        {% endif %}
                    {% else %}
                         <span style="color: var(--secondary-color); margin-top: 5px; display: block; font-size: 0.9em;">
                            Connectez-vous
                        </span>
                    {% endif %}
                </div>
            </div>
        {% endfor %}
    {% else %}
        <p>Aucun article n'est actuellement en vente dans la boutique.</p>
    {% endif %}
{% endblock %}
""",

    # 15. NOUVEAU TEMPLATE : AJOUTER ARTICLE SHOP (Admin)
    'ajouter_article_shop.html': """
{% extends 'layout.html' %}
{% block title %}Ajouter Article Shop{% endblock %}
{% block content %}
    <h2 style="color: var(--accent-color);">➕ Ajouter un nouvel Article à la Boutique</h2>
    
    <form method="POST">
        <div>
            <label for="nom">Nom de l'Article :</label>
            <input type="text" id="nom" name="nom" required>
        </div>
        <div>
            <label for="description">Description :</label>
            <textarea id="description" name="description" rows="4" required></textarea>
        </div>
        <div>
            <label for="prix_gemmes">Prix en Gemmes (💎) :</label>
            <input type="number" id="prix_gemmes" name="prix_gemmes" min="1" required>
        </div>
        <button type="submit">Ajouter à la Boutique</button>
    </form>
{% endblock %}
""",
}


# #################################################################
# 2. INITIALISATION ET ROUTES DE L'APPLICATION
# #################################################################

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_longue_et_unique_pour_json' 
app.jinja_env = Environment(loader=DictLoader(TEMPLATES))
app.jinja_env.globals['url_for'] = url_for
app.jinja_env.globals['session'] = session 
app.jinja_env.globals['get_flashed_messages'] = get_flashed_messages

def truncate(s, length, killwords=False):
    if len(s) <= length:
        return s
    if killwords:
        return s[:length] + '...'
    words = s.split(' ')
    result = ''
    for word in words:
        if len(result) + len(word) > length:
            break
        result += word + ' '
    return result.strip() + '...'

app.jinja_env.filters['truncate'] = truncate

# --- ROUTES PRINCIPALES (Fonctions inchangées) ---

@app.route('/')
@app.route('/accueil')
def accueil():
    data = load_data() 
    articles_display = []
    users_map = {user['id']: user for user in data['users']}
    articles_list = data['articles']
    
    for article in articles_list: 
        author = users_map.get(article['auteur_id'], {'pseudo': 'Inconnu', 'grade': 'Visiteur'})
        article_display = article.copy()
        article_display['nom_auteur'] = author['pseudo']
        article_display['grade_auteur'] = author['grade']
        articles_display.append(article_display)
        
    articles_display.sort(key=lambda x: datetime.strptime(x['date_publication'], DATE_FORMAT), reverse=True)
    
    return render_template('accueil.html', articles=articles_display, page_id='accueil')

@app.route('/wiki')
def wiki():
    return render_template('wiki.html', page_id='wiki')

@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        identifier = request.form['pseudo']
        password_attempt = request.form['mot_de_passe']
        data = load_data()
        
        user = None
        for u in data['users']:
            if u['pseudo'] == identifier or u['email'] == identifier:
                user = u
                break
        
        if user and check_password_hash(user['password_hash'], password_attempt):
            # VÉRIFICATION DU STATUT DU COMPTE
            if user['status'] == 'Banni':
                flash('❌ Votre compte est banni définitivement du site.', 'error')
                return redirect(url_for('connexion'))
                
            if user['status'] == 'Suspendu':
                end_date_str = user.get('suspension_end_date')
                end_reason = user.get('suspension_reason', 'Raison non spécifiée.')
                
                if end_date_str:
                    try:
                        end_date = datetime.strptime(end_date_str, DATE_FORMAT)
                        if datetime.now() < end_date:
                            flash(f'⚠️ Votre compte est suspendu jusqu\'au {end_date_str} pour la raison suivante : "{end_reason}"', 'error')
                            return redirect(url_for('connexion'))
                        else:
                            # La suspension est terminée, on réactive le compte
                            user['status'] = 'Actif'
                            user['suspension_reason'] = None
                            user['suspension_end_date'] = None
                            save_data(data)
                            flash('✅ Votre suspension est terminée. Votre compte est réactivé.', 'success')
                    except ValueError:
                        flash('⚠️ Votre compte est suspendu mais la date de fin est invalide. Contactez un administrateur.', 'error')
                        return redirect(url_for('connexion'))
                else:
                    flash(f'⚠️ Votre compte est suspendu pour une durée indéterminée. Raison : "{end_reason}"', 'error')
                    return redirect(url_for('connexion'))


            session['loggedin'] = True
            session['id'] = user['id']
            session['grade'] = user['grade']
            flash(f"👋 Bienvenue ! Vous êtes connecté en tant que **{user['grade']}**.", 'success')
            return redirect(url_for('accueil'))
        else:
            flash('❌ Pseudo/Email ou mot de passe incorrect.', 'error')
            
    return render_template('connexion.html', page_id='connexion')

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        email = request.form['email']
        password = request.form['mot_de_passe']
        hashed_password = generate_password_hash(password)
        data = load_data()
        
        if any(u['pseudo'] == pseudo or u['email'] == email for u in data['users']):
            flash('❌ Ce pseudo ou cet email est déjà utilisé.', 'error')
        else:
            data['last_user_id'] += 1
            new_id = data['last_user_id']
            
            new_user = {
                "id": new_id,
                "pseudo": pseudo,
                "email": email,
                "password_hash": hashed_password,
                "grade": "Membre",
                "status": "Actif", 
                "suspension_reason": None,
                "suspension_end_date": None,
                "gemmes": 0 
            }
            data['users'].append(new_user)
            save_data(data)
            
            flash('✅ Inscription réussie ! Vous pouvez vous connecter.', 'success')
            return redirect(url_for('connexion'))
            
    return render_template('inscription.html', page_id='inscription')

@app.route('/deconnexion')
def deconnexion():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('grade', None)
    flash('👋 Vous êtes déconnecté.', 'success')
    return redirect(url_for('accueil'))

# --- ROUTES UTILISATEUR (Fonctions inchangées) ---

@app.route('/mon_compte', methods=['GET', 'POST'])
def mon_compte():
    if not session.get('loggedin'):
        flash('⛔ Vous devez être connecté pour accéder à cette page.', 'error')
        return redirect(url_for('connexion'))
    
    user_id = session['id']
    user = get_user_by_id(user_id)
    
    if request.method == 'POST':
        old_password_attempt = request.form['ancien_mot_de_passe']
        new_password = request.form['nouveau_mot_de_passe']
        confirm_password = request.form['confirmation_nouveau_mot_de_passe']

        if not check_password_hash(user['password_hash'], old_password_attempt):
            flash('❌ Ancien mot de passe incorrect. Le mot de passe n\'a pas été modifié.', 'error')
            return redirect(url_for('mon_compte'))

        if new_password != confirm_password:
            flash('❌ Les nouveaux mots de passe ne correspondent pas.', 'error')
            return redirect(url_for('mon_compte'))

        hashed_new_password = generate_password_hash(new_password)
        
        data = load_data()
        for u in data['users']:
            if u['id'] == user_id:
                u['password_hash'] = hashed_new_password
                break
        
        save_data(data)
        
        flash('✅ Votre mot de passe a été mis à jour avec succès.', 'success')
        return redirect(url_for('mon_compte'))

    return render_template('mon_compte.html', user=user, page_id='mon_compte')

@app.route('/creer_article', methods=['GET', 'POST'])
def creer_article():
    if not session.get('loggedin') or session.get('grade') != 'Administrateur':
        flash('⛔ Accès refusé. Seuls les Admins peuvent créer des articles.', 'error')
        return redirect(url_for('accueil'))
    
    if request.method == 'POST':
        titre = request.form['titre']
        contenu = request.form['contenu']
        auteur_id = session['id']
        
        data = load_data()
        data['last_article_id'] += 1
        new_id = data['last_article_id']

        new_article = {
            "id": new_id,
            "titre": titre,
            "contenu": contenu,
            "auteur_id": auteur_id,
            "date_publication": datetime.now().strftime(DATE_FORMAT)
        }
        
        data['articles'].append(new_article)
        save_data(data)
        
        flash('✅ Article créé et publié !', 'success')
        return redirect(url_for('accueil'))
        
    return render_template('creer_article.html', page_id='creer_article')

# --- ROUTES SHOP (Fonctions inchangées) ---

@app.route('/shop')
def shop():
    data = load_data()
    user = get_user_by_id(session.get('id')) if session.get('loggedin') else None
    
    items_list = sorted(data['shop_items'], key=lambda x: x['id'])
    
    return render_template('shop.html', items=items_list, user=user, page_id='shop')

@app.route('/shop/acheter/<int:item_id>')
def acheter_article_shop(item_id):
    if not session.get('loggedin'):
        flash('⛔ Vous devez être connecté pour effectuer un achat.', 'error')
        return redirect(url_for('connexion'))

    data = load_data()
    user_id = session['id']
    user_index = next((i for i, u in enumerate(data['users']) if u['id'] == user_id), -1)
    user = data['users'][user_index]
    
    item = next((i for i in data['shop_items'] if i['id'] == item_id), None)

    if not item:
        flash('❌ Article non trouvé dans la boutique.', 'error')
        return redirect(url_for('shop'))
        
    price = item['prix_gemmes']
    
    if user['status'] != 'Actif':
        flash('❌ Vous ne pouvez pas acheter d\'articles si votre compte est Banni ou Suspendu.', 'error')
        return redirect(url_for('shop'))

    if user['gemmes'] >= price:
        user['gemmes'] -= price
        
        # LOGIQUE D'ATTRIBUTION D'OBJET ICI
        
        flash(f'✅ Achat réussi ! {item["nom"]} acheté pour {price} 💎. (Nouveau solde : {user["gemmes"]} Gemmes). L\'article vous sera livré en jeu sous peu.', 'success')
        save_data(data)
    else:
        flash(f'❌ Achat échoué. Solde de Gemmes insuffisant. Il vous manque {price - user["gemmes"]} 💎 pour acheter {item["nom"]}.', 'error')
    
    return redirect(url_for('shop'))


# --- ROUTES ADMIN (SHOP - Fonction inchangée) ---

@app.route('/admin/ajouter_article_shop', methods=['GET', 'POST'])
def ajouter_article_shop():
    if not session.get('loggedin') or session.get('grade') != 'Administrateur':
        flash('⛔ Accès refusé. Seuls les Administrateurs peuvent ajouter des articles au shop.', 'error')
        return redirect(url_for('accueil'))
    
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        
        try:
            prix_gemmes = int(request.form['prix_gemmes'])
            if prix_gemmes <= 0:
                flash('❌ Le prix doit être un nombre entier positif.', 'error')
                return redirect(url_for('ajouter_article_shop'))
        except ValueError:
            flash('❌ Le prix des Gemmes doit être un nombre entier valide.', 'error')
            return redirect(url_for('ajouter_article_shop'))
            
        data = load_data()
        data['last_shop_item_id'] += 1
        new_id = data['last_shop_item_id']
        
        new_item = {
            "id": new_id,
            "nom": nom,
            "description": description,
            "prix_gemmes": prix_gemmes,
            "date_ajout": datetime.now().strftime(DATE_FORMAT)
        }
        
        data['shop_items'].append(new_item)
        save_data(data)
        
        flash(f'✅ Article {nom} ajouté à la boutique pour {prix_gemmes} 💎.', 'success')
        return redirect(url_for('shop'))
        
    return render_template('ajouter_article_shop.html', page_id='ajouter_article_shop')

# --- ROUTES ADMIN (GRANDS ET MOT DE PASSE - Fonctions inchangées) ---

@app.route('/admin/gestion_utilisateurs')
def gestion_utilisateurs():
    if not session.get('loggedin') or session.get('grade') != 'Administrateur':
        flash('⛔ Accès refusé. Seuls les Administrateurs peuvent gérer les utilisateurs.', 'error')
        return redirect(url_for('accueil'))
    
    data = load_data()
    users_list = [u for u in data['users'] if u['id'] != session.get('id')]
    
    return render_template('gestion_utilisateurs.html', users=users_list, page_id='gestion_utilisateurs')

@app.route('/admin/modifier_utilisateur/<int:user_id>', methods=['GET', 'POST'])
def modifier_utilisateur(user_id):
    if not session.get('loggedin') or session.get('grade') != 'Administrateur':
        flash('⛔ Accès refusé. Seuls les Administrateurs peuvent modifier les grades.', 'error')
        return redirect(url_for('accueil'))

    user_to_modify = get_user_by_id(user_id)
    if not user_to_modify or user_to_modify['id'] == session.get('id'):
        flash('❌ Utilisateur non trouvé ou vous ne pouvez pas modifier votre propre grade/mdp via cette page.', 'error')
        return redirect(url_for('gestion_utilisateurs'))

    if request.method == 'POST':
        action = request.form.get('action')
        data = load_data()
        
        user_index = next((i for i, user in enumerate(data['users']) if user['id'] == user_id), -1)
        user = data['users'][user_index]
        
        if action == 'update_grade':
            new_grade = request.form.get('grade')
            
            if new_grade not in ['Membre', 'Administrateur']:
                flash('❌ Grade invalide.', 'error')
                return redirect(url_for('modifier_utilisateur', user_id=user_id))
            
            user['grade'] = new_grade
            save_data(data)
            
            flash(f'✅ Le grade de {user_to_modify["pseudo"]} a été mis à jour à {new_grade}.', 'success')
            return redirect(url_for('gestion_utilisateurs'))
            
        elif action == 'reset_password':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if new_password != confirm_password:
                flash('❌ Les nouveaux mots de passe ne correspondent pas.', 'error')
                return redirect(url_for('modifier_utilisateur', user_id=user_id))

            hashed_new_password = generate_password_hash(new_password)
            user['password_hash'] = hashed_new_password
            save_data(data)

            flash(f'⚠️ Le mot de passe de {user_to_modify["pseudo"]} a été réinitialisé avec succès par l\'administrateur.', 'error') 
            return redirect(url_for('modifier_utilisateur', user_id=user_id))
        
        else:
            flash('❌ Action inconnue.', 'error')
            
    return render_template('modifier_utilisateur.html', user=user_to_modify, page_id='modifier_utilisateur')


# --- ROUTES ADMIN (GESTION STATUT/GEMMES - Fonctions inchangées) ---

@app.route('/admin/gerer_comptes_admin')
def gerer_comptes_admin():
    if not session.get('loggedin') or session.get('grade') != 'Administrateur':
        flash('⛔ Accès refusé. Seuls les Administrateurs peuvent gérer les comptes.', 'error')
        return redirect(url_for('accueil'))
    
    data = load_data()
    users_list = data['users']
    
    return render_template('gerer_comptes_admin.html', users=users_list, page_id='gerer_comptes_admin')

@app.route('/admin/gerer_compte/<int:user_id>', methods=['GET', 'POST'])
def gerer_compte_detail(user_id):
    if not session.get('loggedin') or session.get('grade') != 'Administrateur':
        flash('⛔ Accès refusé. Seuls les Administrateurs peuvent gérer les comptes.', 'error')
        return redirect(url_for('accueil'))

    user_to_modify = get_user_by_id(user_id)
    if not user_to_modify:
        flash('❌ Utilisateur non trouvé.', 'error')
        return redirect(url_for('gerer_comptes_admin'))
    
    if user_to_modify['id'] == session.get('id') and request.method == 'POST':
        flash('❌ Vous ne pouvez pas modifier votre propre statut ou supprimer votre compte via cette page.', 'error')
        return redirect(url_for('gerer_comptes_admin'))


    if request.method == 'POST':
        action = request.form.get('action')
        data = load_data()
        
        user_index = next((i for i, user in enumerate(data['users']) if user['id'] == user_id), -1)
        user = data['users'][user_index] 

        if action == 'delete_account':
            data['articles'] = [a for a in data['articles'] if a['auteur_id'] != user_id]
            del data['users'][user_index]
            save_data(data)
            
            flash(f'🗑️ Le compte de {user["pseudo"]} a été supprimé définitivement.', 'success')
            return redirect(url_for('gerer_comptes_admin'))

        elif action == 'update_status':
            new_status = request.form.get('status')
            reason = request.form.get('suspension_reason', 'Raison non spécifiée.')
            
            suspension_end = None
            
            if new_status == 'Suspendu':
                date_part = request.form.get('suspension_date')
                time_part = request.form.get('suspension_time', '00:00:00')
                if date_part:
                    try:
                        suspension_end = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M:%S").strftime(DATE_FORMAT)
                    except ValueError:
                        flash('❌ Format de date ou d\'heure invalide pour la suspension.', 'error')
                        return redirect(url_for('gerer_compte_detail', user_id=user_id))
            
            user['status'] = new_status
            user['suspension_reason'] = reason if new_status != 'Actif' else None 
            user['suspension_end_date'] = suspension_end
            save_data(data)
            
            flash(f'✅ Le statut de {user["pseudo"]} est maintenant {new_status}.', 'success')
            return redirect(url_for('gerer_compte_detail', user_id=user_id))
        
        else:
            flash('❌ Action inconnue.', 'error')

    user_to_modify = get_user_by_id(user_id)
    return render_template('gerer_compte_detail.html', user=user_to_modify, page_id='gerer_compte_detail')


@app.route('/admin/gestion_gemmes')
def gestion_gemmes():
    if not session.get('loggedin') or session.get('grade') != 'Administrateur':
        flash('⛔ Accès refusé. Seuls les Administrateurs peuvent gérer les gemmes.', 'error')
        return redirect(url_for('accueil'))
    
    data = load_data()
    users_list = data['users'] 
    
    return render_template('gestion_gemmes.html', users=users_list, page_id='gestion_gemmes')

@app.route('/admin/gerer_gemmes/<int:user_id>', methods=['GET', 'POST'])
def gerer_gemmes_detail(user_id):
    if not session.get('loggedin') or session.get('grade') != 'Administrateur':
        flash('⛔ Accès refusé. Seuls les Administrateurs peuvent gérer les gemmes.', 'error')
        return redirect(url_for('accueil'))

    user_to_modify = get_user_by_id(user_id)
    if not user_to_modify:
        flash('❌ Utilisateur non trouvé.', 'error')
        return redirect(url_for('gestion_gemmes'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_gemmes':
            data = load_data()
            user_index = next((i for i, user in enumerate(data['users']) if user['id'] == user_id), -1)
            user = data['users'][user_index] 
            
            try:
                gemmes_amount = int(request.form.get('gemmes_amount'))
                operation = request.form.get('gemmes_operation')

                if gemmes_amount <= 0:
                    flash('❌ Le montant doit être supérieur à zéro.', 'error')
                    return redirect(url_for('gerer_gemmes_detail', user_id=user_id))

                if operation == 'add':
                    user['gemmes'] += gemmes_amount
                    flash(f'💎 {gemmes_amount} Gemmes ajoutées à {user["pseudo"]}. Nouveau solde : {user["gemmes"]}.', 'success')
                elif operation == 'remove':
                    user['gemmes'] = max(0, user['gemmes'] - gemmes_amount) 
                    flash(f'💎 {gemmes_amount} Gemmes retirées de {user["pseudo"]}. Nouveau solde : {user["gemmes"]}.', 'success')
                else:
                    flash('❌ Opération de gemmes invalide.', 'error')
                    return redirect(url_for('gerer_gemmes_detail', user_id=user_id))

                save_data(data)
            except ValueError:
                flash('❌ Le montant des gemmes doit être un nombre entier valide.', 'error')
            
            return redirect(url_for('gerer_gemmes_detail', user_id=user_id))

    return render_template('gerer_gemmes_detail.html', user=user_to_modify, page_id='gerer_gemmes_detail')


# #################################################################
# 3. LANCEMENT
# #################################################################

if __name__ == '__main__':
    load_data() 

    app.run(debug=True)
