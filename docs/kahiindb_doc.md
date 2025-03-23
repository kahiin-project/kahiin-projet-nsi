# Documentation technique de Kahiin-DB

## Table des matières
1. [Introduction](#introduction)
2. [Architecture du système](#architecture-du-système)
3. [Configuration initiale](#configuration-initiale)
4. [Workflows principaux](#workflows-principaux)
   - [Gestion des comptes utilisateurs](#gestion-des-comptes-utilisateurs)
   - [Gestion des quiz et questions](#gestion-des-quiz-et-questions)
   - [Téléchargement et partage](#téléchargement-et-partage)
5. [Composants du système](#composants-du-système)
   - [API REST](#api-rest)
   - [Stockage des données](#stockage-des-données)
   - [Sécurité](#sécurité)
6. [Fonctionnalités avancées](#fonctionnalités-avancées)
7. [Documentation fonctionnelle](#documentation-fonctionnelle)
8. [Conclusion](#conclusion)

## Introduction

Kahiin-DB est une base de données centralisée pour l'application Kahiin, permettant aux enseignants de partager et de réutiliser des quiz et des questions. L'application repose sur une architecture client-serveur utilisant Flask pour l'API REST et MySQL pour le stockage persistant des données.

Le système permet de :
- Stocker des quiz et questions dans un format standardisé
- Partager des ressources pédagogiques entre utilisateurs
- Télécharger et importer du contenu dans l'application Kahiin principale

Cette documentation détaille le fonctionnement complet de Kahiin-DB, depuis la gestion des utilisateurs jusqu'au partage de contenu pédagogique.

## Architecture du système

L'application Kahiin-DB utilise:
- **Backend**: Python avec le framework Flask
- **API**: REST pour les échanges client-serveur
- **Stockage**: Base de données MySQL pour les données utilisateurs et les métadonnées, fichiers système pour les contenus de quiz
- **Sécurité**: Chiffrement des mots de passe avec SHA-256, protection des données sensibles avec Fernet

L'architecture repose sur un modèle de services REST où les clients envoient des requêtes HTTP au serveur qui gère l'état et la persistance des données dans MySQL.

## Configuration initiale

Au démarrage, le système vérifie l'existence des éléments essentiels:
- Base de données MySQL configurée et accessible
- Dossier `quizFiles` pour stocker les fichiers de quiz
- Fichier de configuration chiffré pour les accès à la base de données et aux services d'email

L'initialisation de la base de données est gérée par des scripts spécifiques selon le système d'exploitation:
- `initDB/ubuntu-debian.sh`: Pour les distributions basées sur Debian
- `initDB/centos-rhel.sh`: Pour les distributions basées sur Red Hat
- `initDB/arch.sh`: Pour les distributions basées sur Arch Linux
- `initDB/windows.bat`: Pour Windows

Ces scripts créent:
- Une base de données MySQL
- Un utilisateur dédié avec les permissions appropriées
- Les tables nécessaires au fonctionnement du système

## Workflows principaux

### Gestion des comptes utilisateurs

1. **Inscription d'un utilisateur**:
   - L'utilisateur fournit une adresse email et un mot de passe (hashé en SHA-256)
   - Le système vérifie la validité de l'email et l'unicité dans la base de données
   - Un email de vérification est envoyé à l'utilisateur avec un lien de confirmation
   - Le compte est créé mais reste inactif jusqu'à la confirmation

2. **Vérification du compte**:
   - L'utilisateur clique sur le lien de vérification dans l'email
   - Le système valide le token de vérification et active le compte
   - Une page de confirmation s'affiche selon la langue choisie

3. **Connexion et gestion de session**:
   - L'utilisateur s'authentifie avec email et mot de passe
   - Le système génère un token d'accès stocké dans la table `connexions`
   - Ce token est utilisé pour authentifier les requêtes ultérieures

4. **Réinitialisation de mot de passe**:
   - L'utilisateur demande une réinitialisation via son email
   - Le système envoie un lien avec un token sécurisé
   - Le nouveau mot de passe est stocké temporairement dans `waiting_passwords`
   - Lors de la validation, le mot de passe est mis à jour dans la table `accounts`

### Gestion des quiz et questions

1. **Téléversement de quiz**:
   - L'utilisateur envoie un fichier XML via l'API
   - Le système vérifie la structure du XML et les attributs requis
   - Le fichier est sauvegardé avec un ID unique dans le dossier `quizFiles`
   - Les métadonnées (sujet, langue) sont extraites et stockées dans la base de données

2. **Publication de questions individuelles**:
   - L'utilisateur peut publier des questions détachées d'un quiz
   - Les données sont stockées dans les tables `question_posts` et `question_contents`
   - Le système attribue un ID unique à chaque question

3. **Recherche et filtrage**:
   - Les utilisateurs peuvent rechercher des quiz et questions selon différents critères:
     - Sujet
     - Langue
     - Auteur (via ID)
   - L'API renvoie les résultats filtrés au format JSON

### Téléchargement et partage

1. **Téléchargement de quiz**:
   - L'utilisateur demande un quiz via son ID
   - Le système vérifie les droits d'accès
   - Le fichier XML est servi au client

2. **Consultation des contenus personnels**:
   - L'endpoint `/myposts` permet de récupérer tous les quiz et questions publiés par l'utilisateur
   - Les réponses sont formatées pour faciliter l'intégration avec Kahiin

3. **Suppression de contenu**:
   - L'utilisateur peut supprimer ses propres quiz et questions
   - Le système vérifie que l'utilisateur est bien le propriétaire du contenu
   - Les fichiers et entrées dans la base de données sont supprimés

## Composants du système

### API REST

1. **Endpoints d'authentification**:
   - `POST /signup`: Inscription d'un nouvel utilisateur
   - `POST /login`: Connexion d'un utilisateur existant
   - `POST /reset-password`: Demande de réinitialisation de mot de passe
   - `GET /verif`: Confirmation d'email ou de réinitialisation de mot de passe

2. **Endpoints de gestion de compte**:
   - `POST /getInfos`: Récupération des informations du compte
   - `POST /editInfos`: Modification des informations du compte
   - `DELETE /account`: Suppression du compte

3. **Endpoints de gestion de contenu**:
   - `GET /quiz`: Recherche de quiz selon des critères
   - `POST /quiz`: Téléversement d'un nouveau quiz
   - `DELETE /quiz`: Suppression d'un quiz existant
   - `GET /questions`: Recherche de questions selon des critères
   - `GET /question-content`: Récupération du contenu d'une question spécifique
   - `POST /question`: Publication d'une nouvelle question
   - `DELETE /question`: Suppression d'une question
   - `GET /myposts`: Récupération des contenus publiés par l'utilisateur
   - `GET /download`: Téléchargement d'un fichier de quiz

### Stockage des données

La base de données MySQL comprend les tables suivantes:

1. **`accounts`**:
   - `id_acc`: Identifiant unique de l'utilisateur
   - `email`: Adresse email unique
   - `password_hash`: Hash SHA-256 du mot de passe

2. **`user_infos`**:
   - `id_acc`: Clé étrangère vers `accounts`
   - `name`: Nom d'affichage de l'utilisateur
   - `academy`: Académie ou institution de l'utilisateur

3. **`connexions`**:
   - `id_acc`: Clé étrangère vers `accounts`
   - `token`: Token d'authentification (32 octets)

4. **`verifications`**:
   - `id_acc`: Clé étrangère vers `accounts`
   - `token`: Token de vérification (32 octets)
   - `type`: Type de vérification ('account', 'reset_password')

5. **`waiting_passwords`**:
   - `id_acc`: Clé étrangère vers `accounts`
   - `password_hash`: Nouveau mot de passe en attente de confirmation

6. **`quiz`**:
   - `id_file`: Identifiant unique du fichier quiz
   - `name`: Nom du quiz
   - `id_acc`: Clé étrangère vers l'auteur
   - `subject`: Sujet du quiz
   - `language`: Langue du quiz

7. **`question_posts`**:
   - `id_question`: Identifiant unique de la question
   - `id_acc`: Clé étrangère vers l'auteur
   - `subject`: Sujet de la question
   - `language`: Langue de la question

8. **`question_contents`**:
   - `id_question`: Clé étrangère vers `question_posts`
   - `title`: Énoncé de la question
   - `shown_answers`: Réponses proposées (format JSON)
   - `correct_answers`: Réponses correctes (format JSON)
   - `duration`: Durée en secondes
   - `type`: Type de question (réponse unique, QCM)

### Sécurité

Le système implémente plusieurs mécanismes de sécurité:

1. **Protection des mots de passe**:
   - Stockage uniquement sous forme de hashes SHA-256
   - Vérification sécurisée sans stockage en clair

2. **Authentification par tokens**:
   - Tokens de 32 octets générés aléatoirement
   - Validation requise pour toutes les opérations sensibles

3. **Protection des configurations**:
   - Chiffrement des informations sensibles avec Fernet
   - Utilisation de PBKDF2 pour dériver les clés de chiffrement

4. **Sécurisation des communications**:
   - Validation des données entrantes
   - Protection contre les injections SQL

## Fonctionnalités avancées

1. **Sécurité des mots de passe**:
   - Stockage des mots de passe uniquement sous forme hashée (SHA-256)
   - Vérification sécurisée via `check_password_hash`

2. **Protection des données sensibles**:
   - Configuration chiffrée avec Fernet (clé dérivée via PBKDF2)
   - Jetons d'authentification sécurisés (32 octets)

3. **Vérification par email**:
   - Envoi d'emails de confirmation pour les inscriptions
   - Procédure sécurisée de réinitialisation de mot de passe

4. **Validation des fichiers**:
   - Vérification de la structure XML des quiz téléversés
   - Contrôle d'intégrité des données via `verify_xml_structure`

5. **Support multilingue**:
   - Interface utilisateur et emails disponibles en plusieurs langues (EN, FR, ES, IT, DE)
   - Contenu catégorisé par langue pour faciliter la recherche

## Documentation fonctionnelle

### Fonctionnalités utilisateurs

1. **Gestion de compte**:
   - Création de compte avec vérification par email
   - Modification des informations personnelles
   - Réinitialisation de mot de passe
   - Suppression de compte

2. **Gestion de contenu**:
   - Publication de quiz au format XML
   - Création et partage de questions individuelles
   - Recherche de contenu par sujet, langue ou auteur
   - Suppression de son propre contenu

3. **Téléchargement de contenu**:
   - Téléchargement de quiz pour utilisation avec Kahiin
   - Recherche et filtrage du contenu communautaire
   - Consultation de ses propres publications

### Fonctionnalités administratives

1. **Gestion de la base de données**:
   - Scripts d'initialisation pour différents systèmes d'exploitation
   - Utilitaires de maintenance et de sauvegarde
   - Scripts de suppression de la base de données

2. **Configuration système**:
   - Paramétrage des connexions MySQL
   - Configuration du serveur SMTP pour les emails
   - Gestion des clés de chiffrement
