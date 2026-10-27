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

# Initialize Database & Tables
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO staff (username, password) VALUES (?, ?)", ("admin", "admin@123"))
    conn.commit()
    conn.close()

init_db()

# Uploads Directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_file(uploaded_file):
    if uploaded_file is not None:
        new_name = f"{hashlib.md5(uploaded_file.name.encode()).hexdigest()}_{uploaded_file.name}"
        path = os.path.join(UPLOAD_DIR, new_name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return new_name
    return None

# Custom CSS for High Contrast and Clear Containers
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
        
        /* SIDEBAR FIX: Light Background & Dark Readable Text */
        [data-testid="stSidebar"] {{
            background-color: #f8fafc !important;
            border-right: 2px solid #cbd5e1 !important;
        }}
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div {{
            color: #0f172a !important;
            font-weight: 700 !important;
        }}
        [data-testid="stSidebar"] .stRadio label {{
            color: #0f172a !important;
            font-size: 15px !important;
            font-weight: 700 !important;
        }}

        /* Modern Header Layout */
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

        /* SOLID WHITE CONTAINER FOR FORMS */
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

        /* FORCE ALL LABELS INSIDE FORMS & WIDGETS TO BE DARK & BOLD */
        div[data-testid="stForm"] label, 
        div[data-testid="stForm"] div[data-testid="stWidgetLabel"] p,
        div[data-testid="stForm"] span,
        div[data-testid="stForm"] small,
        label, div[data-testid="stWidgetLabel"] p {{
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

# Header HTML with Logo & Contact Info
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
    
    st.markdown("""
    <div style="background-color: rgba(255, 255, 255, 0.95); padding: 20px 25px; border-radius: 14px; margin-bottom: 25px; border-left: 6px solid #1b5e20; box-shadow: 0 8px 20px rgba(0,0,0,0.3);">
        <h3 style="color: #1b5e20; margin-top: 0; font-weight: 800; font-size: 18px;">Welkom bij het Online Aanvraagportaal</h3>
        <p style="color: #0f172a; font-size: 14.5px; line-height: 1.6; margin-bottom: 0;">
            Via dit portaal kunt u als burger van Wanica Centrum eenvoudig online uw <b>Verklaring Omtrent het Gedrag (Goedgedrag)</b> aanvragen en de benodigde documenten uploaden. Vul het onderstaande formulier volledig en correct in om uw aanvraag in behandeling te nemen.
        </p>
    </div>
    """, unsafe_allow_html=True)

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

                # Vriendelijke bevestigingsmail weergave voor de burger op het scherm
                st.success("✅ Uw aanvraag is succesvol ingediend!")
                st.markdown(f"""
                <div style="background-color: #f8fafc; border: 2px solid #2e7d32; padding: 20px; border-radius: 12px; color: #0f172a; margin-top: 20px;">
                    <h4 style="color: #1b5e20; margin-top: 0;">✉️ Bevestigingsmail verzonden naar: {email}</h4>
                    <p>Beste <b>{full_name}</b>,</p>
                    <p>Hartelijk dank voor uw aanvraag voor een <b>Verklaring Omtrent het Gedrag (Goedgedrag)</b> bij het Districtscommissariaat Wanica Centrum.</p>
                    <p>Wij hebben uw aanvraag in goede orde ontvangen en in behandeling genomen. Zodra uw aanvraag is beoordeeld, nemen wij contact met u op via dit e-mailadres of uw telefoonnummer ({phone_number}).</p>
                    <p style="margin-bottom: 0;">Met vriendelijke groet,<br><b>Districtscommissariaat Wanica Centrum</b></p>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MEDEWERKERS DASHBOARD
# ---------------------------------------------------------
else:
    st.markdown("<h2 style='color: #ffffff; font-weight: 800;'>🔒 Medewerkers Portaal Dashboard</h2>", unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""

    if not st.session_state['logged_in']:
        with st.form("login_form"):
            st.markdown('<div class="section-header">Inloggen met Beheerders- of Medewerkersaccount</div>', unsafe_allow_html=True)
            user_input = st.text_input("Gebruikersnaam", placeholder="Voer gebruikersnaam in")
            pwd_input = st.text_input("Wachtwoord", type="password", placeholder="Voer wachtwoord in")
            login_submitted = st.form_submit_button("🔑 Inloggen")
            
            if login_submitted:
                if user_input == "admin" and pwd_input == "admin@123":
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = "admin"
                    st.rerun()
                else:
                    conn = sqlite3.connect('wanica.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM staff WHERE username = ? AND password = ?", (user_input, pwd_input))
                    staff_member = cursor.fetchone()
                    conn.close()
                    
                    if staff_member:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = user_input
                        st.rerun()
                    else:
                        st.error("❌ Ongeldige gebruikersnaam of wachtwoord.")
    else:
        col_user, col_logout = st.columns([4, 1])
        with col_user:
            st.markdown(f"<h3 style='color: #ffffff; margin-top: 10px;'>👋 Ingelogd als: <b>{st.session_state['username']}</b></h3>", unsafe_allow_html=True)
        with col_logout:
            if st.button("🚪 Uitloggen", use_container_width=True):
                st.session_state['logged_in'] = False
                st.session_state['username'] = ""
                st.rerun()

        st.divider()

        # ---------------------------------------------------------
        # ADMIN PANEL: Beheer Medewerkers
        # ---------------------------------------------------------
        if st.session_state['username'] == "admin":
            st.markdown("<h3 style='color: #ffffff;'>👥 Medewerkers Beheren (Admin Optie)</h3>", unsafe_allow_html=True)
            with st.expander("➕ Nieuwe Medewerker Toevoegen of Verwijderen"):
                with st.form("add_staff_form"):
                    new_staff_user = st.text_input("Nieuwe Medewerker Gebruikersnaam")
                    new_staff_pwd = st.text_input("Nieuw Wachtwoord", type="password")
                    add_staff_btn = st.form_submit_button("Medewerker Aanmaken")
                    
                    if add_staff_btn:
                        if new_staff_user and new_staff_pwd:
                            try:
                                conn = sqlite3.connect('wanica.db')
                                cursor = conn.cursor()
                                cursor.execute("INSERT INTO staff (username, password) VALUES (?, ?)", (new_staff_user, new_staff_pwd))
                                conn.commit()
                                conn.close()
                                st.success(f"Medewerker '{new_staff_user}' succesvol toegevoegd!")
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("❌ Deze gebruikersnaam bestaat al.")
                        else:
                            st.warning("Vul zowel gebruikersnaam als wachtwoord in.")

                conn = sqlite3.connect('wanica.db')
                staff_df = pd.read_sql_query("SELECT id, username, created_at FROM staff WHERE username != 'admin'", conn)
                conn.close()

                if not staff_df.empty:
                    st.markdown("<b>Bestaande medewerkers:</b>", unsafe_allow_html=True)
                    st.dataframe(staff_df, use_container_width=True)
                    
                    del_staff_id = st.selectbox("Selecteer Medewerker ID om te verwijderen", staff_df['id'].tolist(), key="del_staff")
                    if st.button("🗑️ Geselecteerde Medewerker Verwijderen"):
                        conn = sqlite3.connect('wanica.db')
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM staff WHERE id = ?", (del_staff_id,))
                        conn.commit()
                        conn.close()
                        st.warning(f"Medewerker #{del_staff_id} verwijderd!")
                        st.rerun()
                else:
                    st.info("Geen extra medewerkers gevonden.")
            st.divider()

        # ---------------------------------------------------------
        # DASHBOARD: Binnengekomen Aanvragen
        # ---------------------------------------------------------
        conn = sqlite3.connect('wanica.db')
        df = pd.read_sql_query("SELECT id, full_name, id_number, phone_number, email, uitreksel_file, pasfoto_file, id_kaart_file, bankbewijs_file, status, created_at FROM applications ORDER BY id DESC", conn)
        conn.close()

        st.markdown("<h3 style='color: #ffffff;'>📋 Binnengekomen Aanvragen & Documenten</h3>", unsafe_allow_html=True)
        
        if not df.empty:
            display_df = df[['id', 'full_name', 'id_number', 'phone_number', 'email', 'status', 'created_at']]
            st.dataframe(display_df, use_container_width=True)

            st.markdown("---")
            st.markdown("<h3 style='color: #ffffff;'>⚙️ Beheer & Documenten Downloaden</h3>", unsafe_allow_html=True)
            
            # Duidelijke en goed leesbare selectie container
            st.markdown("""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 14px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); color: #0f172a; margin-bottom: 25px;">
                <h4 style="color: #1b5e20; margin-top: 0; font-weight: 800;">🔍 Aanvraag Selecteren voor Beheer</h4>
            </div>
            """, unsafe_allow_html=True)
            
            selected_app_id = st.selectbox("Kies hier het Aanvraag ID uit de lijst:", df['id'].tolist())
            selected_row = df[df['id'] == selected_app_id].iloc[0]
            
            st.markdown(f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 10px; color: #0f172a; margin-bottom: 20px;">
                <b>Geselecteerde Aanvraag #{selected_row['id']}</b><br>
                <b>Naam:</b> {selected_row['full_name']} | <b>ID-Nr:</b> {selected_row['id_number']}<br>
                <b>Telefoon:</b> {selected_row['phone_number']} | <b>E-mail:</b> {selected_row['email']}<br>
                <b>Huidige Status:</b> <span style="color: #1b5e20; font-weight: bold;">{selected_row['status']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Documenten downloaden & automatisch verwijderen uit database
            st.markdown("<b>📁 Geüploade Bestanden (Download verwijdert het bestand automatisch uit de database/server):</b>", unsafe_allow_html=True)
            
            files_dict = {
                "Uitreksel": selected_row['uitreksel_file'],
                "Pasfoto": selected_row['pasfoto_file'],
                "ID-Kaart": selected_row['id_kaart_file'],
                "Bankbewijs": selected_row['bankbewijs_file']
            }

            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
            cols = [col_d1, col_d2, col_d3, col_d4]

            for idx, (label, fname) in enumerate(files_dict.items()):
                with cols[idx]:
                    if fname:
                        fpath = os.path.join(UPLOAD_DIR, fname)
                        if os.path.exists(fpath):
                            with open(fpath, "rb") as f:
                                file_bytes = f.read()
                            
                            if st.download_button(label=f"📥 Download {label}", data=file_bytes, file_name=fname, key=f"dl_{selected_app_id}_{label}"):
                                conn = sqlite3.connect('wanica.db')
                                cursor = conn.cursor()
                                col_map = {
                                    "Uitreksel": "uitreksel_file",
                                    "Pasfoto": "pasfoto_file",
                                    "ID-Kaart": "id_kaart_file",
                                    "Bankbewijs": "bankbewijs_file"
                                }
                                cursor.execute(f"UPDATE applications SET {col_map[label]} = NULL WHERE id = ?", (selected_app_id,))
                                conn.commit()
                                conn.close()
                                
                                try:
                                    os.remove(fpath)
                                except OSError:
                                    pass
                                
                                st.success(f"{label} gedownload en automatisch uit het systeem verwijderd!")
                                st.rerun()
                        else:
                            st.caption(f"❌ {label}: Reeds gedownload / verwijderd")
                    else:
                        st.caption(f"⚠️ {label}: Niet beschikbaar")

            st.markdown("<br>", unsafe_allow_html=True)

            with st.form("manage_form"):
                new_status = st.selectbox("Status aanpassen", ["In behandeling", "Goedgekeurd", "Afgekeurd"], index=["In behandeling", "Goedgekeurd", "Afgekeurd"].index(selected_row['status']))
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    update_submitted = st.form_submit_button("💾 Status Bijwerken")
                with col_btn2:
                    delete_submitted = st.form_submit_button("🗑️ Volledige Aanvraag Verwijderen")

                if update_submitted:
                    conn = sqlite3.connect('wanica.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, selected_app_id))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"Status voor ID #{selected_app_id} bijgewerkt naar '{new_status}'!")
                    st.rerun()

                if delete_submitted:
                    conn = sqlite3.connect('wanica.db')
                    cursor = conn.cursor()
                    for f in [selected_row['uitreksel_file'], selected_row['pasfoto_file'], selected_row['id_kaart_file'], selected_row['bankbewijs_file']]:
                        if f:
                            fp = os.path.join(UPLOAD_DIR, f)
                            if os.path.exists(fp):
                                try:
                                    os.remove(fp)
                                except OSError:
                                    pass
                    cursor.execute("DELETE FROM applications WHERE id = ?", (selected_app_id,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.warning(f"Aanvraag #{selected_app_id} en alle bijbehorende bestanden zijn volledig verwijderd!")
                    st.rerun()
        else:
            st.info("Geen aanvragen gevonden in het systeem.")
