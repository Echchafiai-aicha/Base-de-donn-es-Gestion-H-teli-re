import sqlite3
import streamlit as st
from datetime import date

# Connexion SQLite
conn = sqlite3.connect('hotel.db', check_same_thread=False)
c = conn.cursor()

# Initialisation DB
def init_db():
    c.execute('''
        CREATE TABLE IF NOT EXISTS Client (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prenom TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Chambre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Reservation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_debut TEXT,
            date_fin TEXT,
            id_client INTEGER,
            id_chambre INTEGER,
            FOREIGN KEY(id_client) REFERENCES Client(id),
            FOREIGN KEY(id_chambre) REFERENCES Chambre(id)
        )
    ''')
    conn.commit()

init_db()

# Styles CSS pour un thème sombre moderne + animations
st.markdown("""
<style>
    /* Background & text */
    .main {
        background-color: #121212;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 2rem;
    }
    /* Titres */
    h1, h2, h3 {
        color: #bb86fc;
        text-align: center;
        animation: fadeInDown 1s ease forwards;
    }
    /* Boutons */
    button[kind="primary"] {
        background-color: #3700b3 !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        box-shadow: 0 0 10px #bb86fc !important;
        transition: background-color 0.3s ease;
    }
    button[kind="primary"]:hover {
        background-color: #6200ee !important;
    }
    /* Selectbox style */
    div[role="listbox"] > div {
        background-color: #1f1b2e !important;
        color: #bb86fc !important;
        border-radius: 8px !important;
    }
    /* Inputs */
    input, .stDateInput > div {
        background-color: #1f1b2e !important;
        color: #e0e0e0 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px !important;
        margin-bottom: 1rem !important;
    }
    /* Animations */
    @keyframes fadeInDown {
        0% {
            opacity: 0;
            transform: translateY(-20px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    /* Success message */
    .stAlert > div {
        background-color: #03dac6 !important;
        color: #000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    /* Warning message */
    .stWarning > div {
        background-color: #cf6679 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour récupérer les clients
def get_clients():
    c.execute("SELECT * FROM Client")
    return c.fetchall()

# Fonction pour récupérer chambres disponibles sur période
def get_chambres_disponibles(date_debut, date_fin):
    query = '''
    SELECT * FROM Chambre WHERE id NOT IN (
        SELECT id_chambre FROM Reservation
        WHERE NOT (date_fin < ? OR date_debut > ?)
    )
    '''
    dispo = c.execute(query, (date_debut, date_fin)).fetchall()
    return dispo

# Ajouter réservation
def add_reservation(date_debut, date_fin, id_client, id_chambre):
    c.execute('''
        INSERT INTO Reservation (date_debut, date_fin, id_client, id_chambre)
        VALUES (?, ?, ?, ?)
    ''', (date_debut, date_fin, id_client, id_chambre))
    conn.commit()

# Ajouter client simple (test ou nouveau)
def add_client(nom, prenom):
    c.execute('INSERT INTO Client (nom, prenom) VALUES (?, ?)', (nom, prenom))
    conn.commit()

# Ajouter chambre simple (test ou nouveau)
def add_chambre(numero):
    c.execute('INSERT INTO Chambre (numero) VALUES (?)', (numero,))
    conn.commit()

# --- Interface ---

st.markdown("<div class='main'>", unsafe_allow_html=True)

st.title("🏨 Gestion Réservations Hôtel")
st.markdown("---")

# Section ajout clients test et chambres test
with st.expander("➕ Ajouter clients & chambres de test (clic une fois)"):
    if st.button("Ajouter clients & chambres test"):
        # On ajoute que s'il n'existe pas
        clients = get_clients()
        if clients:
            st.warning("Clients/chambres test déjà ajoutés.")
        else:
            add_client("Dupont", "Jean")
            add_client("Martin", "Claire")
            add_chambre("101")
            add_chambre("102")
            add_chambre("103")
            st.success("Clients et chambres test ajoutés.")

st.markdown("---")

st.subheader("📅 Ajouter une réservation")

clients = get_clients()
if not clients:
    st.warning("Aucun client enregistré. Ajoute des clients d'abord.")
else:
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date début", value=date.today())
    with col2:
        date_fin = st.date_input("Date fin", value=date.today())

    if date_debut > date_fin:
        st.error("❌ La date de début doit être avant la date de fin.")
    else:
        chambres_dispo = get_chambres_disponibles(str(date_debut), str(date_fin))
        if not chambres_dispo:
            st.warning("⚠️ Aucune chambre disponible sur cette période.")
        else:
            choix_client = st.selectbox("Choisir un client", options=[f"{c[1]} {c[2]} (ID:{c[0]})" for c in clients])
            id_client = [c[0] for c in clients if f"{c[1]} {c[2]} (ID:{c[0]})" == choix_client][0]

            choix_chambre = st.selectbox("Choisir une chambre", options=[f"Chambre {ch[1]} (ID:{ch[0]})" for ch in chambres_dispo])
            id_chambre = [ch[0] for ch in chambres_dispo if f"Chambre {ch[1]} (ID:{ch[0]})" == choix_chambre][0]

            if st.button("Ajouter réservation"):
                add_reservation(str(date_debut), str(date_fin), id_client, id_chambre)
                st.success("🎉 Réservation ajoutée avec succès !")

st.markdown("---")

st.subheader("📋 Liste des réservations")
c.execute('''
SELECT r.id, r.date_debut, r.date_fin, c.nom, c.prenom, ch.numero
FROM Reservation r
JOIN Client c ON r.id_client = c.id
JOIN Chambre ch ON r.id_chambre = ch.id
ORDER BY r.date_debut DESC
''')
reservations = c.fetchall()

if reservations:
    for r in reservations:
        st.markdown(f"- 🛏️ **Chambre {r[5]}** réservée par **{r[3]} {r[4]}** du **{r[1]}** au **{r[2]}**")
else:
    st.info("Aucune réservation enregistrée.")

st.markdown("</div>", unsafe_allow_html=True)
