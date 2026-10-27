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

# Custom CSS with Larger Header Logo and Larger Contact Info
def add_custom_css():
    bg_image_path = "achtergrond.jpg"
    bg_css = ""
    if os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as f:
            encoded_bg = base64.b64encode(f.read()).decode()
        bg_css = f"""
            background: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), url("data:image/jpg;base64,{encoded_bg}") no-repeat center center fixed;
            background-size: cover;
        """

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

        html, body, [class*="css"], .stApp {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            {bg_css}
        }}
        
        /* Modern Header Layout with Larger, Prominent Elements */
        .custom-header {{
            background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
            border-bottom: 6px solid #144517;
            padding: 28px 35px;
            border-radius: 16px;
            color: #ffffff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.45);
            flex-wrap: wrap;
            gap: 25px;
        }}
        .header-brand {{
            display: flex;
            align-items: center;
            gap: 24px;
        }}
        .header-title h1 {{
            margin: 0;
            font-size: 28px;
            color: #ffffff !important;
            font-weight: 800;
            letter-spacing: 0.3px;
        }}
        .header-title p {{
            margin: 6px 0 0 0;
            font-size: 16px;
            color: #e2e8f0 !important;
            font-weight: 600;
        }}
        /* BIGGER AND CLEARER CONTACT INFO */
        .header-contact {{
            font-size: 16px;
            text-align: right;
            line-height: 1.8;
            background: rgba(255, 255, 255, 0.18);
            padding: 14px 22px;
            border-radius: 12px;
            color: #ffffff !important;
            border: 1.5px solid rgba(255, 255, 255, 0.35);
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}

        /* SOLID WHITE CONTAINER FOR FORM */
        div[data-testid="stForm"] {{
            background-color: #ffffff !important;
            padding: 40px !important;
            border-radius: 16px !important;
            box-shadow: 0 15px 40px rgba(0,0,0,0.5) !important;
            border: 1px solid #cbd5e1 !important;
        }}
        
        /* Form Section Headers */
        .section-header {{
            background-color: #e8f5e9;
            border-left: 6px solid #2e7d32;
            padding: 12px 18px;
            font-size: 16px;
            font-weight: 800;
            color: #1b5e20 !important;
            border-radius: 0 8px 8px 0;
            margin: 25px 0 18px 0;
        }}

        /* FORCE ALL LABELS INSIDE FORM TO BE DARK & BOLD */
        div[data-testid="stForm"] label, 
        div[data-testid="stForm"] div[data-testid="stWidgetLabel"] p,
        div[data-testid="stForm"] span,
        div[data-testid="stForm"] small {{
            color: #0f172a !important;
            font-weight: 700 !important;
            font-size: 15px !important;
        }}

        /* Text Input Styling */
        .stTextInput input {{
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 2px solid #64748b !important;
            border-radius: 8px !important;
            padding: 12px 15px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
        }}

        /* FILE UPLOADER VISIBILITY FIX */
        [data-testid="stFileUploader"] {{
            background-color: #f1f5f9 !important;
            border: 2px dashed #475569 !important;
            border-radius: 12px !important;
            padding: 16px !important;
        }}
        [data-testid="stFileUploaderDropzone"] {{
            background-color: #ffffff !important;
            border: 1.5px solid #cbd5e1 !important;
        }}
        [data-testid="stFileUploaderDropzone"] * {{
            color: #0f172a !important;
            fill: #0f172a !important;
        }}
        [data-testid="stFileUploaderDropzone"] button {{
            background-color: #1b5e20 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
        }}
        [data-testid="stFileUploaderDropzone"] button * {{
            color: #ffffff !important;
            fill: #ffffff !important;
        }}
        [data-testid="stFileUploaderDropzoneInstructions"] span {{
            color: #0f172a !important;
            font-weight: 700 !important;
        }}

        /* SUBMIT BUTTON VISIBILITY FIX */
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {{
            background-color: #1b5e20 !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            font-size: 18px !important;
            padding: 16px 30px !important;
            border-radius: 10px !important;
            border: none !important;
            box-shadow: 0 5px 15px rgba(27, 94, 32, 0.4) !important;
            width: 100% !important;
        }}
        div.stButton > button *, div[data-testid="stFormSubmitButton"] > button * {{
            color: #ffffff !important;
        }}
        div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {{
            background-color: #2e7d32 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# Header HTML with MUCH LARGER LOGO (135px) and Prominent Contact Info
logo_path = "logo.png"
logo_html = ""

if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        encoded_logo = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="height: 135px; width: auto; background: #ffffff; padding: 8px; border-radius: 14px; box-shadow: 0 6px 18px rgba(0,0,0,0.35);">'

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
    
    st.markdown("<h2 style='color: #ffffff; font-weight: 800; margin-bottom: 5px;'>📜 Aanvraag Verklaring Omtrent het Gedrag (Goedgedrag)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #f1f5f9; font-size: 15px; margin-bottom: 25px;'>Vul uw persoonsgegevens in en upload alle 4 verplichte documenten om uw aanvraag in te dienen.</p>", unsafe_allow_html=True)

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
        submitted = st.form_submit_button("🚀 Aanvraag Definitief Indienen")

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

# ---------------------------------------------------------
# MEDEWERKERS DASHBOARD
# ---------------------------------------------------------
else:
    st.markdown("<h2 style='color: #ffffff; font-weight: 800;'>🔒 Medewerkers Portaal Dashboard</h2>", unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        with st.form("login_form"):
            st.markdown('<div class="section-header">Inloggen met Beheerdersaccount</div>', unsafe_allow_html=True)
            user = st.text_input("Gebruikersnaam")
            pwd = st.text_input("Wachtwoord", type="password")
            login_submitted = st.form_submit_button("🔑 Inloggen")
            if login_submitted:
                if user == "admin" and pwd == "admin":
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
                    cursor.close()
                    st.success(f"Status voor ID #{app_id} bijgewerkt!")
                    st.rerun()

            with col_del:
                st.write("Verwijderen")
                if st.button("🗑️ Aanvraag Verwijderen", type="primary"):
                    conn = sqlite3.connect('wanica.db')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
                    conn.commit()
                    cursor.close()
                    st.warning(f"Aanvraag #{app_id} verwijderd!")
                    st.rerun()
        else:
            st.info("Geen aanvragen gevonden.")
