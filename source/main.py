#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import time
import signal
import getpass

# Chemins des dossiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "kahiin-db")
APP_DIR = os.path.join(BASE_DIR, "kahiin-app")
SERVER_DIR = os.path.join(BASE_DIR, "kahiin")

# Variables globales
running_processes = []
db_initialized = False

LOGO = """
██╗  ██╗ █████╗ ██╗  ██╗██╗██╗███╗   ██╗
██║ ██╔╝██╔══██╗██║  ██║██║██║████╗  ██║
█████╔╝ ███████║███████║██║██║██╔██╗ ██║
██╔═██╗ ██╔══██║██╔══██║██║██║██║╚██╗██║
██║  ██╗██║  ██║██║  ██║██║██║██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝╚═╝  ╚═══╝
"""

def clear_screen():
    """Efface l'écran du terminal"""
    os.system('clear' if os.name != 'nt' else 'cls')

def is_db_initialized():
    """Vérifie si la base de données est déjà initialisée"""
    global db_initialized
    config_file = os.path.join(os.path.dirname(DB_DIR), "config.ini")
    env_file = os.path.join(DB_DIR, '.env')
    state_file = os.path.join(BASE_DIR, '.db_initialized')
    
    if os.path.exists(config_file) or os.path.exists(env_file) or os.path.exists(state_file):
        db_initialized = True
        return True
    return False

def mark_db_initialized(success=True):
    """Marque la base de données comme initialisée"""
    global db_initialized
    state_file = os.path.join(BASE_DIR, '.db_initialized')
    
    if success:
        try:
            with open(state_file, 'w') as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S"))
            db_initialized = True
        except Exception as e:
            print(f"Erreur lors de la création du fichier d'état: {e}")
    else:
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
            except:
                pass
        db_initialized = False

def run_process(command, cwd, name=None):
    """Exécute une commande et retourne le processus"""
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
        preexec_fn=os.setsid,
        bufsize=1
    )
    
    process_info = (process, name)
    running_processes.append(process_info)
    
    # Démarrer les threads pour gérer stdout et stderr
    threading.Thread(target=print_output, args=(process.stdout, name, False), daemon=True).start()
    threading.Thread(target=print_output, args=(process.stderr, name, True), daemon=True).start()
    
    return process

def print_output(pipe, prefix, is_error):
    """Affiche la sortie du processus"""
    for line in iter(pipe.readline, ''):
        if is_error:
            print(f"\033[91m[{prefix}] {line}\033[0m", end='')
        else:
            print(f"[{prefix}] {line}", end='')

def stop_all_processes():
    """Arrête tous les processus en cours"""
    for process_info in running_processes:
        process, _ = process_info
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except:
            pass
    running_processes.clear()
    print("Tous les processus ont été arrêtés.")

def print_status():
    """Affiche le statut des processus en cours"""
    if not running_processes:
        print("Aucun processus en cours d'exécution.")
        return
    
    print("\n=== PROCESSUS EN COURS ===")
    for process_info in running_processes:
        process, name = process_info
        if process.poll() is None:
            print(f"✓ {name} est en cours d'exécution (PID: {process.pid})")
        else:
            print(f"✗ {name} s'est terminé (code retour: {process.returncode})")
    print("========================\n")

def start_db():
    """Démarre la base de données Kahiin"""
    print("\nDémarrage de la base de données Kahiin...")
    print("Le processus s'exécute en arrière-plan. Vous pouvez continuer à utiliser le menu.")
    process = run_process("./start.sh", DB_DIR, "Base de données")
    input("\nAppuyez sur Entrée pour continuer...")
    return process

def start_server():
    """Démarre le serveur Kahiin"""
    clear_screen()
    print("\n" + "="*70)
    print("     DÉMARRAGE DU SERVEUR KAHIIN")
    print("="*70 + "\n")
    
    print("Le serveur nécessite des privilèges administrateur pour fonctionner.")
    sudo_password = getpass.getpass("Mot de passe sudo: ")
    
    print("\nDémarrage du serveur Kahiin...")
    print("Le serveur sera accessible à l'adresse : http://localhost:5000")
    print("Le processus s'exécute en arrière-plan. Vous pouvez continuer à utiliser le menu.\n")
    
    # Modification de la commande pour passer le mot de passe à sudo via -S
    process = subprocess.Popen(
        "echo '" + sudo_password + "' | sudo -S ./start.sh",
        cwd=SERVER_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        preexec_fn=os.setsid,
        bufsize=1
    )
    
    process_info = (process, "Serveur")
    running_processes.append(process_info)
    
    # Démarrer les threads pour gérer stdout et stderr
    threading.Thread(target=print_output, args=(process.stdout, "Serveur", False), daemon=True).start()
    threading.Thread(target=print_output, args=(process.stderr, "Serveur", True), daemon=True).start()
    
    input("\nAppuyez sur Entrée pour continuer...")
    return process

def build_app():
    """Construit l'application Android"""
    print("\nConstruction de l'application Android...")
    print("Le processus s'exécute en arrière-plan. Vous pouvez continuer à utiliser le menu.")
    process = run_process("./build.sh", APP_DIR, "Constructeur d'application Android")
    input("\nAppuyez sur Entrée pour continuer...")
    return process

def install_requirements():
    """Installe les dépendances nécessaires"""
    try:
        import pip
        pip.main(['install', 'mysql-connector-python', 'python-dotenv'])
        return True
    except:
        return False

def detect_os():
    """Détecte le système d'exploitation et renvoie le script approprié"""
    if os.name == 'nt':
        return "windows.bat"
    else:
        try:
            with open("/etc/os-release") as f:
                os_release = f.read().lower()
            if "arch" in os_release or "manjaro" in os_release:
                return "arch.sh"
            elif "centos" in os_release or "fedora" in os_release or "rhel" in os_release:
                return "centos-rhel.sh"
            else:
                return "ubuntu-debian.sh"
        except FileNotFoundError:
            return "ubuntu-debian.sh"

def init_db():
    """Initialise la base de données Kahiin"""
    global db_initialized
    
    clear_screen()
    print("\n" + "="*70)
    print("     INITIALISATION DE LA BASE DE DONNÉES KAHIIN")
    print("="*70 + "\n")
    
    print("Installation des dépendances nécessaires...")
    if not install_requirements():
        print("\033[91mÉchec de l'installation des dépendances.\033[0m")
        input("\nAppuyez sur Entrée pour continuer...")
        return None
    
    try:
        import mysql.connector
    except:
        print("\033[91mÉchec de l'importation des modules nécessaires.\033[0m")
        input("\nAppuyez sur Entrée pour continuer...")
        return None
    
    print("\n\033[96mVeuillez entrer les informations suivantes :\033[0m")
    
    db_user = input("\nNom d'utilisateur MySQL: ")
    db_password = getpass.getpass("Mot de passe MySQL: ")
    db_name = input("Nom de la base de données: ")
    db_host = input("Hôte [localhost]: ")
    db_host = db_host if db_host else "localhost"
    root_password = getpass.getpass("Mot de passe root MySQL: ")
    
    print("\n\033[96mConfiguration email :\033[0m")
    email = input("Adresse email pour les notifications: ")
    email_password = getpass.getpass("Mot de passe email: ")
    smtp_server = input("Serveur SMTP: ")
    smtp_port = input("Port SMTP [587]: ")
    smtp_port = smtp_port if smtp_port else "587"
    encryption_key = getpass.getpass("Clé de chiffrement (au moins 16 caractères): ")
    
    os_script = detect_os()
    script_path = os.path.join("initDB", os_script)
    
    print(f"\n\033[92mInitialisation avec {os_script}...\033[0m")
    print("Exécution en cours...\n")
    
    if os.path.exists(os.path.join(DB_DIR, script_path)):
        full_path = os.path.join(DB_DIR, script_path)
        
        if os.name != 'nt':  # Linux/Mac
            os.chmod(full_path, 0o755)
        
        # Construire la commande
        if os.name == 'nt':  # Windows
            command = f"{script_path} {db_name} {db_user} {db_password} {db_host} {email} {email_password} {smtp_server} {smtp_port} {encryption_key} {root_password}"
        else:  # Linux/Mac
            command = f"./{script_path} {db_name} {db_user} {db_password} {db_host} {email} {email_password} {smtp_server} {smtp_port} {encryption_key} {root_password}"
        
        # Exécuter la commande
        return_code = os.system(f"cd {DB_DIR} && {command}")
        
        if return_code == 0:
            print("\n\033[92mInitialisation de la base de données terminée avec succès.\033[0m")
            mark_db_initialized(True)
        else:
            print(f"\n\033[91mÉchec de l'initialisation de la base de données (code retour: {return_code}).\033[0m")
            mark_db_initialized(False)
    else:
        print(f"\n\033[91mLe script {os_script} n'a pas été trouvé.\033[0m")
    
    input("\nAppuyez sur Entrée pour continuer...")

def drop_db():
    """Supprime la base de données Kahiin"""
    global db_initialized
    
    clear_screen()
    print("\n" + "="*70)
    print("     SUPPRESSION DE LA BASE DE DONNÉES KAHIIN")
    print("="*70 + "\n")
    
    confirmation = input("\033[91mATTENTION: Cette action va supprimer définitivement la base de données.\033[0m\nTapez 'CONFIRMER' pour continuer: ")
    
    if confirmation != "CONFIRMER":
        print("\nSuppression annulée.")
        input("\nAppuyez sur Entrée pour continuer...")
        return
    
    os_script = detect_os()
    script_path = os.path.join("dropDB", os_script)
    
    if os.path.exists(os.path.join(DB_DIR, script_path)):
        full_path = os.path.join(DB_DIR, script_path)
        
        if os.name != 'nt':  # Linux/Mac
            os.chmod(full_path, 0o755)
        
        # Construire et exécuter la commande
        if os.name == 'nt':  # Windows
            command = f"{script_path}"
        else:  # Linux/Mac
            command = f"./{script_path}"
        
        print(f"\n\033[92mSuppression avec {os_script}...\033[0m")
        return_code = os.system(f"cd {DB_DIR} && {command}")
        
        if return_code == 0:
            print("\n\033[92mSuppression de la base de données terminée avec succès.\033[0m")
            # Supprimer le fichier d'état
            state_file = os.path.join(BASE_DIR, '.db_initialized')
            if os.path.exists(state_file):
                os.remove(state_file)
            db_initialized = False
        else:
            print(f"\n\033[91mÉchec de la suppression de la base de données (code retour: {return_code}).\033[0m")
    else:
        print(f"\n\033[91mLe script {os_script} n'a pas été trouvé.\033[0m")
    
    input("\nAppuyez sur Entrée pour continuer...")

def docker_up():
    """Démarre les conteneurs Docker pour Kahiin"""
    clear_screen()
    print("\n" + "="*70)
    print("     DÉMARRAGE DE KAHIIN AVEC DOCKER")
    print("="*70 + "\n")
    
    if not check_docker() or not check_docker_compose():
        print("\033[91mDocker et/ou Docker Compose ne sont pas installés!\033[0m")
        print("Veuillez installer Docker et Docker Compose pour utiliser cette fonctionnalité.")
        input("\nAppuyez sur Entrée pour continuer...")
        return
    
    # Créer le fichier .env pour docker-compose s'il n'existe pas
    docker_env_path = os.path.join(BASE_DIR, '.env')
    if not os.path.exists(docker_env_path) and db_initialized:
        try:
            db_env_path = os.path.join(DB_DIR, '.env')
            if os.path.exists(db_env_path):
                with open(db_env_path, 'r') as src, open(docker_env_path, 'w') as dest:
                    dest.write(src.read())
                    dest.write("DB_ROOT_PASSWORD=rootpassword\n")
                print("Fichier de configuration Docker créé à partir des paramètres existants.")
            else:
                with open(docker_env_path, 'w') as f:

                    f.write(f"DB_NAME={input("Le nom de la base de données : ")}\n")
                    f.write(f"DB_USER={input("Le nom d'utilisateur de la base de données : ")}\n")
                    f.write(f"DB_PASSWORD={getpass.getpass('Le mot de passe de la base de données : ')}\n")
                    f.write(f"DB_HOST={input('L\'hôte de la base de données [localhost] : ')}\n")
                    f.write(f"DB_ROOT_PASSWORD={getpass.getpass('Le mot de passe root de la base de données : ')}\n")
                    f.write(f"EMAIL={input('Adresse email pour les verifications : ')}\n")
                    f.write(f"EMAIL_PASSWORD={getpass.getpass('Le mot de passe de l\'adresse email : ')}\n")
                    f.write(f"SMTP_SERVER={input('Serveur SMTP : ')}\n")
                    f.write(f"SMTP_PORT={input('Port SMTP [587] : ')}\n")
                    f.write(f"ENCRYPTION_KEY={getpass.getpass('Clé de chiffrement (au moins 16 caractères) : ')}\n")
                    
                print("Fichier de configuration Docker créé avec des paramètres par défaut.")
        except Exception as e:
            print(f"\033[91mErreur lors de la création du fichier .env: {e}\033[0m")
    
    print("Démarrage des conteneurs Docker...")
    run_process("docker-compose -f docker-compose.yml up -d", BASE_DIR, "Docker Compose")
    print("\nKahiin est accessible à l'adresse : http://localhost:5000")
    input("\nAppuyez sur Entrée pour continuer...")

def docker_down():
    """Arrête les conteneurs Docker de Kahiin"""
    clear_screen()
    print("\n" + "="*70)
    print("     ARRÊT DES CONTENEURS DOCKER KAHIIN")
    print("="*70 + "\n")
    
    if not check_docker() or not check_docker_compose():
        print("\033[91mDocker et/ou Docker Compose ne sont pas installés!\033[0m")
        input("\nAppuyez sur Entrée pour continuer...")
        return
    
    print("Arrêt des conteneurs Docker...")
    os.system(f"cd {BASE_DIR} && docker-compose -f docker-compose.yml down")
    print("Les conteneurs Docker ont été arrêtés.")
    input("\nAppuyez sur Entrée pour continuer...")

def docker_status():
    """Affiche le statut des conteneurs Docker de Kahiin"""
    clear_screen()
    print("\n" + "="*70)
    print("     STATUT DES CONTENEURS DOCKER KAHIIN")
    print("="*70 + "\n")
    
    if not check_docker():
        print("\033[91mDocker n'est pas installé!\033[0m")
        input("\nAppuyez sur Entrée pour continuer...")
        return
    
    print("Conteneurs Docker actuellement en cours d'exécution:")
    os.system("docker ps --filter name=kahiin")
    input("\nAppuyez sur Entrée pour continuer...")

def check_docker():
    """Vérifie si Docker est installé"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_docker_compose():
    """Vérifie si Docker Compose est installé"""
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def show_main_menu():
    """Affiche le menu principal"""
    clear_screen()
    print(LOGO)
    print("\n" + "="*70)
    print("                     KAHIIN PROJECT LAUNCHER")
    print("="*70)
    
    print("\n [1] Lancer Kahiin")
    
    if not db_initialized:
        print(" [2] Initialiser la Base de Données Kahiin")
    else:
        print(" [2] Démarrer la Base de Données Kahiin")
        print(" [3] Supprimer la Base de Données Kahiin")
    
    print(" [4] Construire l'Application Android")
    print(" [5] Afficher le Statut des Processus")
    print(" [6] Arrêter Tous les Processus")
    print("\n [d] Lancer avec Docker")
    print(" [s] Statut Docker")
    print(" [x] Arrêter Docker")
    print("\n [q] Quitter")
    
    print("\n" + "="*70)
    return input("\nChoix: ").lower()

def simple_main():
    global db_initialized
    
    # Vérifier si la base de données est déjà initialisée
    is_db_initialized()
    
    while True:
        choice = show_main_menu()
        
        if choice == '1':
            start_server()
        elif choice == '2' and not db_initialized:
            init_db()
        elif choice == '2' and db_initialized:
            start_db()
        elif choice == '3' and db_initialized:
            drop_db()
        elif choice == '4':
            build_app()
        elif choice == '5':
            print_status()
            input("\nAppuyez sur Entrée pour continuer...")
        elif choice == '6':
            stop_all_processes()
            input("\nAppuyez sur Entrée pour continuer...")
        elif choice == 'd':
            docker_up()
        elif choice == 's':
            docker_status()
        elif choice == 'x':
            docker_down()
        elif choice == 'q':
            stop_all_processes()
            print("Fermeture du lanceur Kahiin...")
            break
        else:
            print("\nOption non valide. Veuillez réessayer.")
            input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    try:
        simple_main()
    except KeyboardInterrupt:
        print("\nInterruption détectée. Arrêt des processus...")
        stop_all_processes()
    finally:
        sys.exit(0)