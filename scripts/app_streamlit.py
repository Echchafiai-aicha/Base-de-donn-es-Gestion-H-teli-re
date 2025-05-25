# scripts/app_streamlit.py
import streamlit as st
import sqlite3
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Gestion Hôtelière", layout="wide")

# Connexion à la base de données
conn = sqlite3.connect('hotel.db')

# Fonctions utilitaires
def get_reservations():
    query = '''
    SELECT r.Id_Reservation, c.Nom_complet, h.Ville, r.Date_arrivee, r.Date_depart
    FROM Reservation r
    JOIN Client c ON r.Id_Client = c.Id_Client
    JOIN Chambre_Reservation cr ON r.Id_Reservation = cr.Id_Reservation
    JOIN Chambre ch ON cr.Id_Chambre = ch.Id_Chambre
    JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
    '''
    return pd.read_sql(query, conn)

def get_clients():
    return pd.read_sql('SELECT * FROM Client', conn)

def get_available_rooms(start_date, end_date):
    query = '''
    SELECT ch.Id_Chambre, ch.Numero, ch.Etage, tc.Type, tc.Tarif, h.Ville
    FROM Chambre ch
    JOIN Type_Chambre tc ON ch.Id_Type = tc.Id_Type
    JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
    WHERE ch.Id_Chambre NOT IN (
        SELECT cr.Id_Chambre
        FROM Chambre_Reservation cr
        JOIN Reservation r ON cr.Id_Reservation = r.Id_Reservation
        WHERE (r.Date_arrivee <= ? AND r.Date_depart >= ?)
        OR (r.Date_arrivee <= ? AND r.Date_depart >= ?)
        OR (r.Date_arrivee >= ? AND r.Date_depart <= ?)
    )
    '''
    params = (end_date, start_date, end_date, end_date, start_date, end_date)
    return pd.read_sql(query, conn, params=params)

def add_client(nom, adresse, ville, cp, email, tel):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Client (Nom_complet, Adresse, Ville, Code_postal, Email, Telephone)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (nom, adresse, ville, cp, email, tel))
    conn.commit()
    st.success("Client ajouté avec succès!")

def add_reservation(id_client, id_chambre, date_arrivee, date_depart):
    cursor = conn.cursor()
    # Ajout de la réservation
    cursor.execute('''
    INSERT INTO Reservation (Date_arrivee, Date_depart, Id_Client)
    VALUES (?, ?, ?)
    ''', (date_arrivee, date_depart, id_client))
    # Récupération de l'ID de la nouvelle réservation
    id_reservation = cursor.lastrowid
    # Lien avec la chambre
    cursor.execute('''
    INSERT INTO Chambre_Reservation (Id_Chambre, Id_Reservation)
    VALUES (?, ?)
    ''', (id_chambre, id_reservation))
    conn.commit()
    st.success("Réservation ajoutée avec succès!")

# Interface utilisateur
st.title("Système de Gestion Hôtelière")

menu = st.sidebar.selectbox("Menu", [
    "Liste des réservations",
    "Liste des clients",
    "Chambres disponibles",
    "Ajouter un client",
    "Ajouter une réservation"
])

if menu == "Liste des réservations":
    st.header("Liste des réservations")
    st.dataframe(get_reservations(), use_container_width=True)

elif menu == "Liste des clients":
    st.header("Liste des clients")
    st.dataframe(get_clients(), use_container_width=True)

elif menu == "Chambres disponibles":
    st.header("Recherche de chambres disponibles")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Date d'arrivée")
    with col2:
        end_date = st.date_input("Date de départ")
    
    if start_date and end_date:
        if start_date >= end_date:
            st.error("La date d'arrivée doit être avant la date de départ")
        else:
            rooms = get_available_rooms(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            if len(rooms) > 0:
                st.dataframe(rooms, use_container_width=True)
            else:
                st.warning("Aucune chambre disponible pour cette période")

elif menu == "Ajouter un client":
    st.header("Ajouter un nouveau client")
    with st.form("client_form"):
        nom = st.text_input("Nom complet")
        adresse = st.text_input("Adresse")
        ville = st.text_input("Ville")
        cp = st.number_input("Code postal", min_value=0, step=1)
        email = st.text_input("Email")
        tel = st.text_input("Téléphone")
        
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            if nom and adresse and ville and email and tel:
                add_client(nom, adresse, ville, cp, email, tel)
            else:
                st.error("Veuillez remplir tous les champs obligatoires")

elif menu == "Ajouter une réservation":
    st.header("Ajouter une nouvelle réservation")
    
    # Sélection du client
    clients = get_clients()
    client_choice = st.selectbox(
        "Client",
        clients['Nom_complet'],
        format_func=lambda x: x
    )
    id_client = clients.loc[clients['Nom_complet'] == client_choice, 'Id_Client'].iloc[0]
    
    # Dates
    col1, col2 = st.columns(2)
    with col1:
        date_arrivee = st.date_input("Date d'arrivée")
    with col2:
        date_depart = st.date_input("Date de départ")
    
    if date_arrivee and date_depart and date_arrivee < date_depart:
        # Recherche des chambres disponibles
        rooms = get_available_rooms(date_arrivee.strftime('%Y-%m-%d'), date_depart.strftime('%Y-%m-%d'))
        
        if len(rooms) > 0:
            room_choice = st.selectbox(
                "Chambre disponible",
                rooms.apply(lambda x: f"{x['Numero']} - {x['Type']} (Étage {x['Etage']}, {x['Ville']}, {x['Tarif']}€/nuit)", axis=1)
            )
            id_chambre = rooms.iloc[rooms.apply(
                lambda x: f"{x['Numero']} - {x['Type']} (Étage {x['Etage']}, {x['Ville']}, {x['Tarif']}€/nuit)", axis=1
            ).tolist().index(room_choice)]['Id_Chambre']
            
            if st.button("Confirmer la réservation"):
                add_reservation(id_client, id_chambre, date_arrivee.strftime('%Y-%m-%d'), date_depart.strftime('%Y-%m-%d'))
        else:
            st.warning("Aucune chambre disponible pour cette période")

# Fermeture de la connexion
conn.close()