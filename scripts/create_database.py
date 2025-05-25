 # scripts/create_database.py
import sqlite3

def create_database():
    # Connexion à la base de données
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()

    # Suppression des tables existantes (pour éviter les conflits)
    cursor.executescript('''
    DROP TABLE IF EXISTS Chambre_Reservation;
    DROP TABLE IF EXISTS Evaluation;
    DROP TABLE IF EXISTS Reservation;
    DROP TABLE IF EXISTS Chambre;
    DROP TABLE IF EXISTS Type_Chambre;
    DROP TABLE IF EXISTS Prestation;
    DROP TABLE IF EXISTS Client;
    DROP TABLE IF EXISTS Hotel;
    ''')

    # Création des tables
    cursor.execute('''
    CREATE TABLE Hotel (
        Id_Hotel INTEGER PRIMARY KEY AUTOINCREMENT,
        Ville TEXT NOT NULL,
        Pays TEXT NOT NULL,
        Code_postal INTEGER NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE Client (
        Id_Client INTEGER PRIMARY KEY AUTOINCREMENT,
        Adresse TEXT NOT NULL,
        Ville TEXT NOT NULL,
        Code_postal INTEGER NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        Telephone TEXT NOT NULL,
        Nom_complet TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE Type_Chambre (
        Id_Type INTEGER PRIMARY KEY AUTOINCREMENT,
        Type TEXT UNIQUE NOT NULL,
        Tarif REAL NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE Chambre (
        Id_Chambre INTEGER PRIMARY KEY AUTOINCREMENT,
        Numero INTEGER UNIQUE NOT NULL,
        Etage INTEGER NOT NULL,
        Fumeur INTEGER NOT NULL CHECK(Fumeur IN (0, 1)),
        Id_Hotel INTEGER NOT NULL,
        Id_Type INTEGER NOT NULL,
        FOREIGN KEY (Id_Hotel) REFERENCES Hotel(Id_Hotel),
        FOREIGN KEY (Id_Type) REFERENCES Type_Chambre(Id_Type)
    )
    ''')

    cursor.execute('''
    CREATE TABLE Prestation (
        Id_Prestation INTEGER PRIMARY KEY AUTOINCREMENT,
        Prix REAL NOT NULL,
        Description TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE Reservation (
        Id_Reservation INTEGER PRIMARY KEY AUTOINCREMENT,
        Date_arrivee DATE NOT NULL,
        Date_depart DATE NOT NULL,
        Id_Client INTEGER NOT NULL,
        FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client)
    )
    ''')

    cursor.execute('''
    CREATE TABLE Chambre_Reservation (
        Id_Chambre INTEGER NOT NULL,
        Id_Reservation INTEGER NOT NULL,
        PRIMARY KEY (Id_Chambre, Id_Reservation),
        FOREIGN KEY (Id_Chambre) REFERENCES Chambre(Id_Chambre),
        FOREIGN KEY (Id_Reservation) REFERENCES Reservation(Id_Reservation)
    )
    ''')

    cursor.execute('''
    CREATE TABLE Evaluation (
        Id_Evaluation INTEGER PRIMARY KEY AUTOINCREMENT,
        Date_evaluation DATE NOT NULL,
        Note INTEGER NOT NULL CHECK(Note BETWEEN 1 AND 5),
        Commentaire TEXT,
        Id_Client INTEGER NOT NULL,
        FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client)
    )
    ''')

    # Insertion des données
    # Hotels
    hotels = [
        (1, 'Paris', 'France', 75001),
        (2, 'Lyon', 'France', 69002)
    ]
    cursor.executemany('INSERT INTO Hotel VALUES (?, ?, ?, ?)', hotels)

    # Clients
    clients = [
        (1, '12 Rue de Paris', 'Paris', 75001, 'jean.dupont@email.fr', '0612345678', 'Jean Dupont'),
        (2, '5 Avenue Victor Hugo', 'Lyon', 69002, 'marie.leroy@email.fr', '0623456789', 'Marie Leroy'),
        (3, '8 Boulevard Saint-Michel', 'Marseille', 13005, 'paul.moreau@email.fr', '0634567890', 'Paul Moreau'),
        (4, '27 Rue Nationale', 'Lille', 59800, 'lucie.martin@email.fr', '0645678901', 'Lucie Martin'),
        (5, '3 Rue des Fleurs', 'Nice', 6000, 'emma.giraud@email.fr', '0656789012', 'Emma Giraud')
    ]
    cursor.executemany('INSERT INTO Client VALUES (?, ?, ?, ?, ?, ?, ?)', clients)

    # Types de chambre
    types_chambre = [
        (1, 'Simple', 80),
        (2, 'Double', 120)
    ]
    cursor.executemany('INSERT INTO Type_Chambre VALUES (?, ?, ?)', types_chambre)

    # Chambres
    chambres = [
        (1, 201, 2, 0, 1, 1),
        (2, 502, 5, 1, 1, 2),
        (3, 305, 3, 0, 2, 1),
        (4, 410, 4, 0, 2, 2),
        (5, 104, 1, 1, 2, 2),
        (6, 202, 2, 0, 1, 1),
        (7, 307, 3, 1, 1, 2),
        (8, 101, 1, 0, 1, 1)
    ]
    cursor.executemany('INSERT INTO Chambre VALUES (?, ?, ?, ?, ?, ?)', chambres)

    # Prestations
    prestations = [
        (1, 15, 'Petit-déjeuner'),
        (2, 30, 'Navette aéroport'),
        (3, 0, 'Wi-Fi gratuit'),
        (4, 50, 'Spa et bien-être'),
        (5, 20, 'Parking sécurisé')
    ]
    cursor.executemany('INSERT INTO Prestation VALUES (?, ?, ?)', prestations)

    # Réservations
    reservations = [
        (1, '2025-06-15', '2025-06-18', 1),
        (2, '2025-07-01', '2025-07-05', 2),
        (3, '2025-08-10', '2025-08-14', 3),
        (4, '2025-09-05', '2025-09-07', 4),
        (5, '2025-09-20', '2025-09-25', 5),
        (6, '2025-11-12', '2025-11-14', 2),
        (7, '2026-01-15', '2026-01-18', 4),
        (8, '2026-02-01', '2026-02-05', 2)
    ]
    cursor.executemany('INSERT INTO Reservation VALUES (?, ?, ?, ?)', reservations)

    # Chambres réservées
    chambre_reservations = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8)
    ]
    cursor.executemany('INSERT INTO Chambre_Reservation VALUES (?, ?)', chambre_reservations)

    # Évaluations
    evaluations = [
        (1, '2025-06-15', 5, 'Excellent séjour, personnel très accueillant.', 1),
        (2, '2025-07-01', 4, 'Chambre propre, bon rapport qualité/prix.', 2),
        (3, '2025-08-10', 3, 'Séjour correct mais bruyant la nuit.', 3),
        (4, '2025-09-05', 5, 'Service impeccable, je recommande.', 4),
        (5, '2025-09-20', 4, 'Très bon petit-déjeuner, hôtel bien situé.', 5)
    ]
    cursor.executemany('INSERT INTO Evaluation VALUES (?, ?, ?, ?, ?)', evaluations)

    conn.commit()
    conn.close()
    print("Base de données créée avec succès!")

if __name__ == '__main__':
    create_database()