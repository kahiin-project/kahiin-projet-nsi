# kahiin-projet-nsi

## Description
Kahiin-projet-nsi est un projet open-source conçu pour les classes, permettant aux enseignants de créer, partager et gérer des quiz interactifs. Le projet comprend plusieurs composants, notamment une application android, une base de données et une interface utilisateur.

## Fonctionnalités
- Création et édition de quiz
- Gestion des utilisateurs et des sessions
- Intégration avec une base de données pour stocker les quiz
- Interface utilisateur interactive
- Support multilingue

## Installation

1. (conseillé mais facultatif) Installez [Docker](https://docs.docker.com/get-docker/).
2. Clonez le dépôt :
    ```sh
    git clone --recursive https://github.com/kahiin-project/kahiin-projet-nsi.git
    cd kahiin-projet-nsi
    ```
3. Demarrez le kahiin project laucher:
    ```sh
        python source/main.py
    ```
4. Choisissez votre mode de lancement


## Utilisation
Une fois l'application démarrée, vous pouvez y accéder à `http://localhost:8080`.

### Création de Quiz
1. Connectez-vous à l'application.
2. Naviguez vers la section "Créer".
3. Remplissez les informations du quiz et ajoutez des questions.
4. Enregistrez le quiz.

### Gestion des Utilisateurs
1. Connectez-vous à l'application.
2. Naviguez vers la section "Compte".
3. Gérez vos informations personnelles et vos paramètres.

## Documentation
La documentation complète du projet est disponible dans le dossier [docs](docs/).

## Crédits
- **[Flask](https://palletsprojects.com/p/flask/)**: Le framework web hébergeant le serveur.
- **[Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)**: Gestion des requêtes Socket.IO.
- **[qrcode](https://github.com/lincolnloop/python-qrcode)**: Utilisé pour générer les QR codes dans la page du tableau.
- **[Socket.IO](https://cdn.socket.io/4.7.5/socket.io.min.js)**: Utilisé pour la communication serveur-client.
- **[CryptoJS 4.1.1](https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js)**: Utilisé pour hacher les mots de passe.
- **[Marked](https://cdn.jsdelivr.net/npm/marked@1.1.0/marked.min.js)**: Utilisé pour rendre le Markdown.
- **KaTeX**: Utilisé pour rendre les formules mathématiques.

## Licence
Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Télécharger l'application

Rendez vous sur les [release](https://github.com/kahiin-project/kahiin-app/releases) de kahiin-app pour télécharger l'application android.
