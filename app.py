import streamlit as st
import sqlite3
import hashlib

def connessione_db():
    return sqlite3.connect("magazzino.db", check_same_thread=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registra_utente(nome, email, password, ruolo):
    conn = connessione_db()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        cursor.execute("INSERT INTO utenti (nome, email, password, ruolo) VALUES (?, ?, ?, ?)", 
                       (nome, email, hashed_pw, ruolo))
        conn.commit()
        st.success("Registrazione completata! Ora puoi accedere.")
    except sqlite3.IntegrityError:
        st.error("Email già in uso!")
    finally:
        conn.close()

def login_utente(email, password):
    conn = connessione_db()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute("SELECT * FROM utenti WHERE email = ? AND password = ?", (email, hashed_pw))
    utente = cursor.fetchone()
    conn.close()
    return utente

# Creazione della tabella se non esiste
conn = connessione_db()
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS utenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        ruolo TEXT NOT NULL
    )
""")
conn.commit()
conn.close()

st.title("Gestione Magazzino 🏬")

if "utente" not in st.session_state:
    st.session_state.utente = None

if st.session_state.utente is None:
    st.sidebar.subheader("Login")
    email = st.sidebar.text_input("Email", key="email_login")
    password = st.sidebar.text_input("Password", type="password", key="password_login")

    if st.sidebar.button("Accedi"):
        utente = login_utente(email, password)
        if utente:
            st.session_state.utente = utente
            st.sidebar.success(f"Benvenuto, {utente[1]}!")
            st.rerun()
        else:
            st.sidebar.error("Credenziali errate!")

    st.sidebar.subheader("Registrati")
    nome_reg = st.sidebar.text_input("Nome", key="nome_reg")
    email_reg = st.sidebar.text_input("Email", key="email_reg")
    password_reg = st.sidebar.text_input("Password", type="password", key="pw_reg")
    ruolo_reg = st.sidebar.selectbox("Ruolo", ["Admin", "Utente"], key="ruolo_reg")

    if st.sidebar.button("Registrati"):
        registra_utente(nome_reg, email_reg, password_reg, ruolo_reg)

else:
    st.sidebar.write(f"👤 Utente: {st.session_state.utente[1]}")
    if st.sidebar.button("Logout"):
        st.session_state.utente = None
        st.rerun()

if st.session_state.utente is not None:
    menu = ["Visualizza Prodotti", "Aggiungi Prodotto", "Modifica Prodotto", "Elimina Prodotto"]
    scelta = st.sidebar.selectbox("Scegli un'operazione:", menu)

    def visualizza_prodotti():
        conn = connessione_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM prodotti")
        prodotti = cursor.fetchall()
        conn.close()
        return prodotti

    if scelta == "Visualizza Prodotti":
        st.subheader("Lista Prodotti")
        prodotti = visualizza_prodotti()
        for prodotto in prodotti:
            st.write(f"🆔 {prodotto[0]} | 📦 {prodotto[1]} | 📖 {prodotto[2]} | 🔢 {prodotto[3]} | 💰 {prodotto[4]} €")

    elif scelta == "Aggiungi Prodotto":
        st.subheader("Aggiungi un nuovo prodotto")
        nome = st.text_input("Nome del prodotto")
        descrizione = st.text_area("Descrizione")
        quantita = st.number_input("Quantità", min_value=1)
        prezzo = st.number_input("Prezzo (€)", min_value=0.01, format="%.2f")
        if st.button("Aggiungi"):
            conn = connessione_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO prodotti (nome, descrizione, quantita, prezzo) VALUES (?, ?, ?, ?)",
                           (nome, descrizione, quantita, prezzo))
            conn.commit()
            conn.close()
            st.success(f"Prodotto '{nome}' aggiunto con successo!")

    elif scelta == "Modifica Prodotto":
        st.subheader("Modifica un prodotto esistente")
        prodotti = visualizza_prodotti()
        ids = [prodotto[0] for prodotto in prodotti]
        id_prodotto = st.selectbox("Seleziona un prodotto da modificare (ID)", ids)

        prodotto_selezionato = next((p for p in prodotti if p[0] == id_prodotto), None)
        if prodotto_selezionato:
            nome = st.text_input("Nome", prodotto_selezionato[1])
            descrizione = st.text_area("Descrizione", prodotto_selezionato[2])
            quantita = st.number_input("Quantità", min_value=1, value=prodotto_selezionato[3])
            prezzo = st.number_input("Prezzo (€)", min_value=0.01, value=prodotto_selezionato[4], format="%.2f")

            if st.button("Modifica"):
                conn = connessione_db()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE prodotti 
                    SET nome = ?, descrizione = ?, quantita = ?, prezzo = ?
                    WHERE id = ?
                ''', (nome, descrizione, quantita, prezzo, id_prodotto))
                conn.commit()
                conn.close()
                st.success(f"Prodotto ID {id_prodotto} aggiornato!")

    elif scelta == "Elimina Prodotto":
        st.subheader("Elimina un prodotto")
        prodotti = visualizza_prodotti()
        if prodotti:
            ids = [prodotto[0] for prodotto in prodotti]
            id_prodotto = st.selectbox("Seleziona un prodotto da eliminare (ID)", ids)

            prodotto_selezionato = next((p for p in prodotti if p[0] == id_prodotto), None)
            if prodotto_selezionato:
                st.write(f"🆔 {prodotto_selezionato[0]} | 📦 {prodotto_selezionato[1]} | 📖 {prodotto_selezionato[2]} | 🔢 {prodotto_selezionato[3]} | 💰 {prodotto_selezionato[4]} €")

                if st.button("Elimina Prodotto"):
                    conn = connessione_db()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM prodotti WHERE id = ?", (id_prodotto,))
                    conn.commit()
                    conn.close()
                    st.success(f"Prodotto ID {id_prodotto} eliminato con successo!")
                    st.rerun()
        else:
            st.info("Nessun prodotto disponibile da eliminare.")
