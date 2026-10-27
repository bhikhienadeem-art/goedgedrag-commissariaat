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

# Custom CSS for Enhanced UX and Modern Clean Design
def add_custom_css():
    bg_image_path = "achtergrond.jpg"
    bg_css = ""
    if os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as f:
            encoded_bg = base64.b64encode(f.read()).decode()
        bg_css = f"""
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url("data:image/jpg;base64,{encoded_bg}") no-repeat center center fixed;
            background-size: cover;
        """

    st.markdown(f"""
    <style>
        .stApp {{
            {bg_css}
        }}
        
        /* Modern Header Layout */
        .custom-header {{
            background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
            border-bottom: 5px solid #144517;
            padding: 24px 35px;
            border-radius: 14px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.35);
            flex-wrap: wrap;
            gap: 20px;
        }}
        .header-brand {{
            display: flex;
            align-items: center;
            gap: 22px;
        }}
        .header-title h1 {{
            margin: 0;
            font-size: 26px;
            color: white;
            font-weight: 800;
            letter-spacing: 0.3px;
        }}
        .header-title p {{
            margin: 4px 0 0 0;
            font-size: 15px;
            color: #e2e8f0;
            font-weight: 500;
        }}
        .header-contact {{
            font-size: 14px;
            text-align: right;
            line-height: 1.7;
            background: rgba(255, 255, 255, 0.12);
            padding: 12px 18px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.25);
        }}

        /* White High-Contrast Main Card Container */
        .main-card {{
            background-color: #ffffff;
            padding: 38px 42px;
            border-radius: 16px;
            box-shadow: 0 12px 35px rgba(0,0,0,0.35);
            margin-bottom: 35px;
            color: #1a202c;
        }}
        
        /* Form Section Headers */
        .section-header {{
            background-color: #f0f7f1;
            border-left: 5px solid #2e7d32;
            padding: 12px 18px;
            font-size: 16px;
            font-weight: 700;
            color: #1b5e20;
            border-radius: 0 8px 8px 0;
            margin: 25px 0 18px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        /* High-Contrast Input Field Styling */
        .stTextInput label, .stFileUploader label, .stSelectbox label {{
            color: #1a202c !important;
            font-weight: 700 !important;
            font-size: 14px !important;
        }}

        .stTextInput input {{
            background-color: #f8fafc !important;
            color: #0f172a !important;
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 8px !important;
            padding: 10px 14px !important;
            font-size: 15px !important;
        }}

        .stTextInput input:focus {{
            border-color: #2e7d32 !important;
            box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.15) !important;
        }}

        /* File Upload Helper Box */
        .stFileUploader {{
            background-color: #f8fafc;
            border: 1.5px dashed #cbd5e1;
            padding: 12px;
            border-radius: 10px;
        }}

        /* Submit Button Styling */
        div.stButton > button {{
            background-color: #2e7d32 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            padding: 14px 28px !important;
            border-radius: 10px !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(46, 125, 50, 0.3) !important;
            transition: all 0.2s ease-in-out !important;
        }}

        div.stButton > button:hover {{
            background-color: #1b5e20 !important;
            transform: translateY(-1px);
        }}
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# Header HTML with LARGER LOGO
logo_path = "logo.png"
logo_html = ""

if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        encoded_logo = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="height: 110px; width: auto; background: #ffffff; padding: 6px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">'

st.markdown(f"""
<div class="custom-header">
    <div class="header-brand">
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
menu = st.sidebar.radio("Navigatie Menu", ["Aanvraag Indienen (Burgers)", "Medewerkers Login / Dashboard"])

# ---------------------------------------------------------
# BURGERS FORMULIER
# ---------------------------------------------------------
if menu == "Aanvraag Indienen (Burgers)":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='color: #1b5e20; font-weight: 800; margin-bottom: 5px;'>📜 Aanvraag Verklaring Omtrent het Gedrag (Goedgedrag)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #4a5568; font-size: 15px; margin-bottom: 25px;'>Vul uw persoonsgegevens in en upload alle 4 verplichte documenten om uw aanvraag in te dienen.</p>", unsafe_allow_html=True)

    with st.form("public_form", clear_on_submit=True):
        st.markdown('<div class="section-header">👤 Stap 1: Persoonsgegevens</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Volledige Naam *", placeholder="Voer uw voor- en achternaam in")
            id_number = st.text_input("ID / Paspoortnummer *", placeholder="Bijv. FD000784")
        with col2:
            phone_number = st.text_input("Telefoonnummer *", placeholder="Bijv. +597 8706661")
            email = st.text_input("E-mailadres *", placeholder="naam@domein.sr")

        st.markdown('<div class="section-header">📁 Stap 2: Benodigde Documenten Uploaden</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            uitreksel = st.file_uploader("Uitreksel (PDF/Afbeelding) *", type=['pdf', 'jpg', 'jpeg', 'png'], help="Upload een recent uitreksel van CBB")
            pasfoto = st.file_uploader("Pasfoto *", type=['jpg', 'jpeg', 'png'], help="Upload een duidelijke, recente pasfoto")
        with col4:
            id_kaart = st.file_uploader("Kopie Geldig ID-kaart *", type=['pdf', 'jpg', 'jpeg', 'png'], help="Voor- en achterkant van ID-kaart")
            bankbewijs = st.file_uploader("Bewijs van Bankovermaking *", type=['pdf', 'jpg', 'jpeg', 'png'], help="Betalingsbewijs van de leges")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Aanvraag Definitief Indienen", use_container_width=True)

        if submitted:
            if not (full_name and id_number and phone_number and email and uitreksel and pasfoto and id_kaart and bankbewijs):
                st.error("⚠️ Vul alstublieft alle verplichte velden in en upload alle 4 documenten.")
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
    st.markdown("<h2 style='color: #1b5e20; font-weight: 800;'>🔒 Medewerkers Portaal Dashboard</h2>", unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.markdown('<div class="section-header">Inloggen met Beheerdersaccount</div>', unsafe_allow_html=True)
        user = st.text_input("Gebruikersnaam")
        pwd = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen"):
            if user == "admin" and pwd == "admin":  # Wachtwoord instellen
                st.session_state['logged_in'] = True
                st.session_state['username'] = user
                st.rerun()
            else:
                st.error("❌ Ongeldige gebruikersnaam of wachtwoord.")
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
            st.dataframe(df, use_container_width=True)

            st.markdown("---")
            st.markdown("### ⚙️ Beheer Aanvraag")
            app_id = st.selectbox("Selecteer Aanvraag ID", df['id'].tolist())

            col_status, col_del = st.columns(2)
            with col_status:
                new_status = st.selectbox("Status aanpassen", ["In behandeling", "Goedgekeurd", "Afgekeurd"])
                if st.button("Status Update"):
                    conn = sqlite3.connect('wanica.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
                    conn.commit()
                    conn.close()
                    st.success(f"Status voor ID #{app_id} bijgewerkt!")
                    st.rerun()

            with col_del:
                st.write("Verwijderen")
                if st.button("🗑️ Aanvraag Verwijderen", type="primary"):
                    conn = sqlite3.connect('wanica.db')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
                    conn.commit()
                    conn.close()
                    st.warning(f"Aanvraag #{app_id} verwijderd!")
                    st.rerun()
        else:
            st.info("Geen aanvragen gevonden.")

    st.markdown('</div>', unsafe_allow_html=True)
