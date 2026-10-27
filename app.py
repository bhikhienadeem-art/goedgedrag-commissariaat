import streamlit as st
import sqlite3
import os
import hashlib
import pandas as pd
import base64

# Page configuration
st.set_page_config(
    page_title="Aanvraag Goedgedrag - Districtscommissariaat Wanica Centrum",
    page_icon="📜",
    layout="wide"
)

# Initialize Database
def init_db():
    conn = sqlite3.connect('wanica.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            id_number TEXT,
            phone_number TEXT,
            email TEXT,
            uitreksel_file TEXT,
            pasfoto_file TEXT,
            id_kaart_file TEXT,
            bankbewijs_file TEXT,
            status TEXT DEFAULT 'In behandeling',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Uploads Directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_file(uploaded_file):
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1]
        new_name = f"{hashlib.md5(uploaded_file.name.encode()).hexdigest()}_{uploaded_file.name}"
        path = os.path.join(UPLOAD_DIR, new_name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return new_name
    return None

# Custom CSS for Background & Card Styling
def add_custom_css():
    bg_image_path = "achtergrond.jpg"
    bg_css = ""
    if os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as f:
            encoded_bg = base64.b64encode(f.read()).decode()
        bg_css = f"""
            background: linear-gradient(rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.55)), url("data:image/jpg;base64,{encoded_bg}") no-repeat center center fixed;
            background-size: cover;
        """

    st.markdown(f"""
    <style>
        .stApp {{
            {bg_css}
        }}
        
        /* Header Styling */
        .custom-header {{
            background-color: #1b5e20;
            border-bottom: 5px solid #144517;
            padding: 20px 30px;
            border-radius: 10px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            flex-wrap: wrap;
            gap: 15px;
        }}
        .header-title h1 {{
            margin: 0;
            font-size: 24px;
            color: white;
            font-weight: 700;
        }}
        .header-title p {{
            margin: 2px 0 0 0;
            font-size: 14px;
            color: #e2e8f0;
        }}
        .header-contact {{
            font-size: 13.5px;
            text-align: right;
            line-height: 1.6;
        }}

        /* White Card Container for content visibility */
        .main-card {{
            background-color: rgba(255, 255, 255, 0.96);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 30px;
            color: #2d3748;
        }}
        
        /* Form Labels */
        .stTextInput label, .stFileUploader label, .stSelectbox label {{
            color: #2d3748 !important;
            font-weight: 600 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# Header HTML with Logo Base64 encoding
logo_path = "logo.png"
logo_html = ""

if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        encoded_logo = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="height: 75px; width: auto; background: white; padding: 4px; border-radius: 8px; margin-right: 20px;">'

st.markdown(f"""
<div class="custom-header">
    <div style="display: flex; align-items: center;">
        {logo_html}
        <div class="header-title">
            <h1>Districtscommissariaat Wanica Centrum</h1>
            <p>Online Diensten Portaal</p>
        </div>
    </div>
    <div class="header-contact">
        📍 <b>Adres:</b> Tawajarieweg No. 20<br>
        📞 <b>Tel:</b> +597-366660 / +597-366929 / +597-366939
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation
menu = st.sidebar.radio("Navigatie", ["Aanvraag Indienen (Burgers)", "Medewerkers Login / Dashboard"])

# ---------------------------------------------------------
# BURGERS FORMULIER
# ---------------------------------------------------------
if menu == "Aanvraag Indienen (Burgers)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📜 Aanvraag Verklaring Omtrent Gedrag")
    st.caption("Vul het onderstaande formulier in en upload de vereiste documenten.")

    with st.form("public_form", clear_on_submit=True):
        st.markdown("### 1. Persoonsgegevens")
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Volledige Naam *")
            id_number = st.text_input("ID / Paspoortnummer *")
        with col2:
            phone_number = st.text_input("Telefoonnummer *")
            email = st.text_input("E-mailadres *")

        st.markdown("### 2. Benodigde Documenten Uploaden")
        col3, col4 = st.columns(2)
        with col3:
            uitreksel = st.file_uploader("Uitreksel (PDF/Afbeelding) *", type=['pdf', 'jpg', 'jpeg', 'png'])
            pasfoto = st.file_uploader("Pasfoto *", type=['jpg', 'jpeg', 'png'])
        with col4:
            id_kaart = st.file_uploader("Kopie Geldig ID-kaart *", type=['pdf', 'jpg', 'jpeg', 'png'])
            bankbewijs = st.file_uploader("Bewijs van Bankovermaking *", type=['pdf', 'jpg', 'jpeg', 'png'])

        submitted = st.form_submit_button("Aanvraag Definitief Indienen", use_container_width=True)

        if submitted:
            if not (full_name and id_number and phone_number and email and uitreksel and pasfoto and id_kaart and bankbewijs):
                st.error("❌ Vul alstublieft alle verplichte velden in en upload alle 4 documenten.")
            else:
                u_name = save_file(uitreksel)
                p_name = save_file(pasfoto)
                i_name = save_file(id_kaart)
                b_name = save_file(bankbewijs)

                conn = sqlite3.connect('wanica.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO applications (full_name, id_number, phone_number, email, uitreksel_file, pasfoto_file, id_kaart_file, bankbewijs_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (full_name, id_number, phone_number, email, u_name, p_name, i_name, b_name))
                conn.commit()
                conn.close()

                st.success("✅ Uw aanvraag is succesvol ingediend! U ontvangt een bericht zodra deze in behandeling is genomen.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# MEDEWERKERS DASHBOARD
# ---------------------------------------------------------
else:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🔒 Medewerkers Portaal")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        user = st.text_input("Gebruikersnaam")
        pwd = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if user == "admin" and pwd == "admin":  # Beheerderswachtwoord
                st.session_state['logged_in'] = True
                st.session_state['username'] = user
                st.rerun()
            else:
                st.error("Ongeldige inloggegevens.")
    else:
        st.write(f"👋 Ingelogd als: **{st.session_state['username']}**")
        if st.button("Uitloggen"):
            st.session_state['logged_in'] = False
            st.rerun()

        st.divider()

        conn = sqlite3.connect('wanica.db')
        df = pd.read_sql_query("SELECT id, full_name, id_number, phone_number, email, status, created_at FROM applications ORDER BY id DESC", conn)
        conn.close()

        st.markdown("### 📋 Binnengekomen Aanvragen")
        if not df.empty:
            st.dataframe(df, use_container
