# Projet Kahiin - Documentation technique

## Table des matières
1. [Introduction](#introduction)
2. [Architecture du système](#architecture-du-système)
3. [Configuration initiale](#configuration-initiale)
4. [Workflows principaux](#workflows-principaux)
   - [Création et gestion des quiz](#création-et-gestion-des-quiz)
   - [Configuration d'une session](#configuration-dune-session)
   - [Déroulement d'une session](#déroulement-dune-session)
   - [Gestion des scores et classements](#gestion-des-scores-et-classements)
5. [Composants du système](#composants-du-système)
   - [Classes principales](#classes-principales)
   - [Communication client-serveur](#communication-client-serveur)
   - [Stockage des données](#stockage-des-données)
6. [Fonctionnalités avancées](#fonctionnalités-avancées)
7. [Documentation Fonctionnelle](#documentation-fonctionnelle)
8. [Conclusion](#conclusion)

## Introduction

Kahiin est une application de quiz interactive conçue pour l'éducation, permettant aux enseignants de créer des sessions de questions-réponses interactives avec leurs élèves. L'application repose sur une architecture client-serveur utilisant Flask et des technologies de communication en temps réel pour fournir une expérience utilisateur fluide.

Le système comprend trois types d'interfaces utilisateur:
- L'interface **hôte** (host) pour les enseignants qui créent et gèrent les sessions
- L'interface **invité** (guest) pour les élèves qui participent aux sessions
- L'interface **tableau** (board) pour afficher les questions et les résultats sur un écran partagé

Cette documentation détaille le fonctionnement complet du système, depuis la création des quiz jusqu'à la gestion des sessions en temps réel.

## Architecture du système

L'application Kahiin utilise:
- **Backend**: Python avec le framework Flask
- **Frontend**: HTML, CSS, JavaScript
- **Communication**: WebSockets pour les communications en temps réel
- **Stockage**: Fichiers XML pour les quiz, JSON pour les paramètres et le tiroir de questions

L'architecture repose sur un modèle événementiel où les clients se connectent au serveur via WebSockets et le serveur gère l'état global du jeu.

## Configuration initiale

Au démarrage, le système vérifie l'existence des fichiers essentiels:
- `drawer.json`: Stocke les questions disponibles à réutiliser
- `settings.json`: Contient les paramètres globaux (langue, mot de passe administrateur, etc.)
- Dossier `quiz`: Contient les fichiers de quiz (.khn)

Si ces fichiers n'existent pas, ils sont créés avec des valeurs par défaut:
- Mot de passe administrateur par défaut: "1234" (hashé)
- Mode dyslexique: désactivé
- Langue: anglais

## Workflows principaux

### Création et gestion des quiz

1. **Création d'un nouveau quiz**:
   - L'hôte se connecte à l'interface d'administration avec le mot de passe
   - Il peut créer un nouveau quiz via l'option "Créer un quiz"
   - Un fichier XML de base est généré avec le format suivant:
     ```xml
     <quiz>
       <subject>Autre</subject>
       <language>fr</language>
       <questions></questions>
     </quiz>
     ```

2. **Ajout de questions**:
   - L'hôte peut ajouter des questions au quiz avec les attributs suivants:
     - Titre de la question
     - Type de question (réponse unique, QCM)
     - Durée en secondes
     - Réponses affichées
     - Réponses correctes
   - Chaque question est sauvegardée dans le XML du quiz

3. **Gestion du tiroir de questions**:
   - Les questions peuvent être sauvegardées dans le "tiroir" (`drawer.json`) pour être réutilisées
   - L'hôte peut copier des questions entre différents quiz via ce tiroir

4. **Édition des quiz existants**:
   - Possibilité de renommer les quiz
   - Modification de la langue ou du sujet
   - Réorganisation des questions par glisser-déposer
   - Suppression de questions

### Configuration d'une session

1. **Sélection du quiz**:
   - L'hôte sélectionne un quiz disponible depuis la liste
   - Le système charge le contenu du quiz via la méthode `handle_select_quiz`

2. **Configuration de la session**:
   - Paramètres modifiables:
     - Ordre aléatoire des questions
     - Terminer automatiquement la question quand tous ont répondu
     - Mode dyslexique

3. **Connexion des participants**:
   - Le système génère un QR code et une URL d'accès pour les participants
   - Les invités se connectent via l'interface guest avec un nom d'utilisateur
   - L'hôte voit la liste des participants se mettre à jour en temps réel
   - Les tableaux d'affichage (board) se connectent pour montrer les questions

### Déroulement d'une session

1. **Démarrage de la session**:
   - L'hôte démarre la session via le bouton "Démarrer la session"
   - Le système vérifie les prérequis (quiz chargé, participants connectés, tableau connecté)

2. **Cycle de questions**:
   - Pour chaque question:
     - L'hôte lance la question via "Question suivante"
     - Le système envoie les données de la question à tous les clients
     - Un chronomètre commence (durée définie par question)
     - Les participants soumettent leurs réponses
     - L'hôte peut:
       - Arrêter la question prématurément
       - Mettre en pause/reprendre la question
     - Lorsque le temps est écoulé, le système évalue les réponses et calcule les scores

3. **Affichage des classements**:
   - Après chaque question, l'hôte peut afficher le classement
   - Le système calcule:
     - Les 5 meilleurs participants
     - Les participants ayant gagné au moins 2 places depuis le dernier classement

4. **Fin de session**:
   - La session se termine quand toutes les questions ont été posées
   - L'hôte peut télécharger un fichier CSV avec les scores finaux

### Gestion des scores et classements

1. **Calcul des scores**:
   - La formule de calcul: `score = (1 - temps_réponse / temps_autorisé) * 500`
   - Un participant obtient des points seulement si sa réponse est correcte
   - Pour les QCM, toutes les bonnes réponses doivent être sélectionnées

2. **Leaderboard dynamique**:
   - Le système maintient un classement courant et un classement précédent
   - Les "utilisateurs promus" sont identifiés selon les règles:
     - N'étaient pas dans le top 5 précédent
     - Ont gagné au moins 2 places
     - Ne sont pas déjà dans la liste des promus

## Composants du système

### Classes principales

1. **Quiz**: Gère le parsing et le stockage des données du quiz
   ```python
   class Quiz:
       def __init__(self, root=None, tree=None):
           self.root = root
           self.tree = tree
           self.filename = None
           self.quiz = {"title": "", "questions": []}
   ```

2. **SleepManager**: Gère le temps pour les questions, y compris les pauses
   ```python
   class SleepManager:
       def __init__(self):
           self._stop_event = asyncio.Event()
           self._is_sleeping = False
           self._current_task = None
           self._duration = 0
           self._time_start = 0
           self._pause_time = 0
           self._is_paused = False
   ```

3. **GameTab**: Classe de base pour les connexions clients
   ```python
   class GameTab:
       def __init__(self, websocket, connections):
           self.websocket = websocket
           self.connections = connections
           self.connections.append(self)
   ```

4. **Client, Board, Host**: Classes spécialisées héritant de GameTab
   ```python
   class Client(GameTab):
       # Gère les participants avec leurs scores

   class Board(GameTab):
       # Gère les tableaux d'affichage

   class Host(GameTab):
       # Gère les hôtes/animateurs
   ```

5. **Game**: Gère l'état du jeu, notamment les classements
   ```python
   class Game:
       def __init__(self):
           self.previous_leaderboard = []
           self.current_leaderboard = []
           self.promoted_users = []
           self.running = False
   ```

### Communication client-serveur

Le système utilise un gestionnaire de WebSockets (`ws_manager`) pour la communication en temps réel:

1. **Événements de connexion**:
   - `connect`: Connexion initiale
   - `boardConnect`, `hostConnect`, `guestConnect`: Connexion spécifique aux rôles
   - `disconnect`: Déconnexion d'un client

2. **Événements de jeu**:
   - `startSession`: Début de la session
   - `nextQuestion`: Passage à la question suivante
   - `showLeaderboard`: Affichage du classement
   - `sendAnswer`: Envoi d'une réponse par un participant
   - `stopQuestion`, `pauseQuestion`, `unpauseQuestion`: Contrôle du déroulement

3. **Événements de configuration**:
   - `getSettings`, `setSettings`: Gestion des paramètres
   - `selectQuiz`, `createQuiz`: Manipulation des quiz
   - `editQuestion`, `moveQuestion`: Édition du contenu

### Stockage des données

1. **Format des quiz (.khn)**:
   Structure XML avec les éléments:
   - `<quiz>`: Élément racine
   - `<subject>`: Sujet du quiz
   - `<language>`: Langue du quiz
   - `<questions>`: Liste des questions
     - `<question>`: Une question individuelle avec attributs `type` et `duration`
       - `<title>`: Énoncé de la question
       - `<shown_answers>`: Réponses affichées
       - `<correct_answers>`: Réponses correctes

2. **Tiroir de questions (drawer.json)**:
   Format JSON contenant les questions disponibles à réutiliser

3. **Paramètres (settings.json)**:
   Contient les configurations globales:
   ```json
   {
     "language": "fr",
     "dyslexicMode": false,
     "adminPassword": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4",
     "randomOrder": false,
     "endOnAllAnswered": true
   }
   ```

## Fonctionnalités avancées

1. **Vérification du mot de passe**:
   - Utilisation d'un décorateur `verification_wrapper` pour sécuriser les opérations d'administration

2. **Gestion des erreurs**:
   - Détection et notification des situations problématiques:
     - Nom d'utilisateur déjà pris
     - Jeu déjà en cours
     - Aucun utilisateur connecté

3. **Intégration avec une base de données externe**:
   - Possibilité d'uploader/télécharger des quiz vers/depuis une base de données externe (kahiin_db_address)

4. **QR Code dynamique**:
   - Génération automatique d'un QR code pour faciliter la connexion des participants

5. **Exportation des résultats**:
   - Possibilité d'exporter les scores au format CSV

## Documentation Fonctionnelle

### Fonctionnalités de l'interface hôte

1. **Création de quiz**:
   - L'hôte peut créer un nouveau quiz en spécifiant le sujet et la langue.
   - Ajout de questions avec différents types (réponse unique, QCM).

2. **Gestion des sessions**:
   - L'hôte peut configurer et démarrer une session de quiz.
   - Suivi en temps réel des participants et de leurs réponses.

3. **Affichage des résultats**:
   - Affichage des classements après chaque question.
   - Exportation des résultats finaux au format CSV.

### Fonctionnalités de l'interface invité

1. **Connexion à une session**:
   - Les invités peuvent se connecter à une session en scannant un QR code ou en utilisant une URL.

2. **Participation aux quiz**:
   - Les invités peuvent répondre aux questions en temps réel.
   - Suivi de leur score et de leur position dans le classement.

### Fonctionnalités de l'interface tableau

1. **Affichage des questions**:
   - Les questions en cours sont affichées sur un écran partagé.

2. **Affichage des classements**:
   - Les classements sont mis à jour en temps réel et affichés après chaque question.

### Implémentation des WebSockets

Le code utilise la bibliothèque `websockets` pour gérer les connexions en temps réel. Voici un aperçu des composants clés:

- **Room**: Une classe qui gère les clients connectés à une salle spécifique.
- **Flask**: Utilisé pour le backend web, permettant de servir les pages et gérer les requêtes HTTP.
- **Asyncio**: Utilisé pour gérer les tâches asynchrones, permettant une gestion efficace des connexions WebSocket.
