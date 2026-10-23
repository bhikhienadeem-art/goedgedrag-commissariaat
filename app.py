import os
import random
import string
import streamlit as st
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.services.account import Account
from appwrite.input_file import InputFile

load_dotenv()

# Appwrite Configurations
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://fra.cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", "6adb474d000b3faf4ab8")
APPWRITE_DB_ID = os.getenv("APPWRITE_DB_ID", "6adb48b70023ab8bd572")
APPWRITE_COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_ID", "aanvragen")
APPWRITE_BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID", "documenten")

st.set_page_config(
    page_title="Commissariaat Wanica Centrum | VGG",
    page_icon="🏛️",
    layout="wide"
)

# Custom Styling (Commissariaat Wanica Centrum Groen/Wit Thema)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f8fafc;
    }
    
    /* Top Utility Bar */
    .top-bar {
        background-color: #0d5c3a;
        color: white;
        padding: 8px 30px;
        font-size: 0.85rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    
    /* Header Brand */
    .brand-title {
        color: #0d5c3a;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.1;
    }
    
    /* Document Cards Styling */
    .doc-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .doc-icon {
        background-color: #d1fae5;
        color: #0d5c3a;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* Primary Buttons */
    .stButton > button {
        background-color: #0d5c3a !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 10px 24px !important;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #15803d !important;
    }
    
    /* Footer */
    .custom-footer {
        background-color: #053823;
        color: white;
        padding: 30px;
        border-radius: 12px 12px 0 0;
        margin-top: 50px;
    }
    .footer-title {
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .footer-text {
        color: #cbd5e1;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# Appwrite Initialization
@st.cache_resource
def get_appwrite_clients():
    client = Client()
    client.set_endpoint(APPWRITE_ENDPOINT)
    client.set_project(APPWRITE_PROJECT_ID)
    return client, Databases(client), Storage(client), Account(client)

client, databases, storage, account = get_appwrite_clients()

# Helper for Unique ID
def generate_aanvraagnummer():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"VGG-WAN-2026-{suffix}"

# 🏛️ Top Header Bar
st.markdown("""
<div class="top-bar">
    <div>🏛️ <b>Officieel Aanvraagportaal Verklaring van Goed Gedrag (VGG)</b></div>
    <div>📍 Tawajarieweg no.20 &nbsp;|&nbsp; 📞 366660 / 3666929 / 3666944</div>
</div>
""", unsafe_allow_html=True)

# Header Navigation Tabs
col_logo, col_tabs = st.columns([2, 1])
with col_logo:
    st.markdown("<h2 class='brand-title'>🏛️ Commissariaat Wanica Centrum</h2>", unsafe_allow_html=True)

with col_tabs:
    active_tab = st.radio("", ["📝 Online Aanvraag (Cliënten)", "🔐 Medewerkers Portaal"], horizontal=True)

st.divider()

# ---------------------------------------------------------
# TAB 1: ONLINE AANVRAAG (CLIËNTEN)
# ---------------------------------------------------------
if active_tab == "📝 Online Aanvraag (Cliënten)":
    st.markdown("### 📄 Aanvraag Verklaring van Goed Gedrag (VGG)")
    st.caption("Vul onderstaande gegevens nauwkeurig in en voeg uw documenten toe om uw aanvraag in te dienen bij het Commissariaat Wanica Centrum.")
    
    with st.form("client_vgg_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            volledige_naam = st.text_input("VOLLEDIGE NAAM *", placeholder="bijv. Jan van Sichem")
        with col_b:
            emailadres = st.text_input("E-MAILADRES *", placeholder="naam@voorbeeld.com")
            
        st.markdown("<br><b>VEREISTE DOCUMENTEN (3 BESTANDEN)</b>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div class="doc-card">
                <div class="doc-icon">🪪</div>
                <b>1. Uittreksel CBB *</b><br>
                <small style='color:#64748b;'>PDF of Afbeelding (Max 5MB)</small>
            </div>
            """, unsafe_allow_html=True)
            uittreksel_file = st.file_uploader("", type=['pdf', 'jpg', 'jpeg', 'png'], key="uittreksel")
            
        with c2:
            st.markdown("""
            <div class="doc-card">
                <div class="doc-icon">👤</div>
                <b>2. Pasfoto *</b><br>
                <small style='color:#64748b;'>Recente pasfoto (JPG/PNG)</small>
            </div>
            """, unsafe_allow_html=True)
            pasfoto_file = st.file_uploader("", type=['jpg', 'jpeg', 'png'], key="pasfoto")
            
        with c3:
            st.markdown("""
            <div class="doc-card">
                <div class="doc-icon">🧾</div>
                <b>3. Bankbewijs *</b><br>
                <small style='color:#64748b;'>Leges overschrijving (PDF/JPG)</small>
            </div>
            """, unsafe_allow_html=True)
            bankbewijs_file = st.file_uploader("", type=['pdf', 'jpg', 'jpeg', 'png'], key="bankbewijs")

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("✈️ Aanvraag Verzenden")
        
        if submit_btn:
            if not volledige_naam or not emailadres or not uittreksel_file or not pasfoto_file or not bankbewijs_file:
                st.error("Vul alstublieft alle verplichte velden in en voeg alle 3 documenten toe.")
            else:
                try:
                    with st.spinner("Uw documenten worden geüpload en geregistreerd..."):
                        u_res = storage.create_file(
                            bucket_id=APPWRITE_BUCKET_ID,
                            file_id='unique()',
                            file=InputFile.from_bytes(uittreksel_file.read(), filename=uittreksel_file.name)
                        )
                        p_res = storage.create_file(
                            bucket_id=APPWRITE_BUCKET_ID,
                            file_id='unique()',
                            file=InputFile.from_bytes(pasfoto_file.read(), filename=pasfoto_file.name)
                        )
                        b_res = storage.create_file(
                            bucket_id=APPWRITE_BUCKET_ID,
                            file_id='unique()',
                            file=InputFile.from_bytes(bankbewijs_file.read(), filename=bankbewijs_file.name)
                        )

                        aanvraagnummer = generate_aanvraagnummer()
                        databases.create_document(
                            database_id=APPWRITE_DB_ID,
                            collection_id=APPWRITE_COLLECTION_ID,
                            document_id='unique()',
                            data={
                                'aanvraagnummer': aanvraagnummer,
                                'client_naam': volledige_naam,
                                'client_email': emailadres,
                                'status': 'ingediend',
                                'uittreksel_file_id': u_res['$id'],
                                'pasfoto_file_id': p_res['$id'],
                                'bankbewijs_file_id': b_res['$id']
                            }
                        )

                        st.success("✅ Uw aanvraag is succesvol verzonden!")
                        st.info(f"**Uw Unieke Aanvraagnummer:** `{aanvraagnummer}`\n\nBewaar dit nummer goed.")
                except Exception as e:
                    st.error(f"Fout bij verzenden: {str(e)}")

# ---------------------------------------------------------
# TAB 2: MEDEWERKERS PORTAAL
# ---------------------------------------------------------
else:
    st.markdown("### 🔐 Medewerkers Beheerdersportaal")
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        with st.form("staff_login"):
            email = st.text_input("E-mailadres")
            password = st.text_input("Wachtwoord", type="password")
            login_btn = st.form_submit_button("Inloggen")

            if login_btn:
                try:
                    session = account.create_email_password_session(email, password)
                    st.session_state['logged_in'] = True
                    st.success("Succesvol ingelogd!")
                    st.rerun()
                except Exception:
                    st.error("Inloggen mislukt. Controleer uw e-mailadres en wachtwoord.")
    else:
        if st.button("Uitloggen"):
            st.session_state['logged_in'] = False
            st.rerun()

        st.subheader("📋 Binnengekomen Aanvragen")
        try:
            docs = databases.list_documents(
                database_id=APPWRITE_DB_ID,
                collection_id=APPWRITE_COLLECTION_ID
            ).get('documents', [])

            if not docs:
                st.info("Geen aanvragen gevonden.")
            else:
                for doc in docs:
                    with st.expander(f"📌 {doc.get('aanvraagnummer')} — {doc.get('client_naam')} ({doc.get('status').upper()})"):
                        st.write(f"**E-mail:** {doc.get('client_email')}")
                        
                        col_u, col_p, col_b = st.columns(3)
                        with col_u:
                            u_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{doc.get('uittreksel_file_id')}/view?project={APPWRITE_PROJECT_ID}"
                            st.link_button("Bekijk Uittreksel", u_url)
                        with col_p:
                            p_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{doc.get('pasfoto_file_id')}/view?project={APPWRITE_PROJECT_ID}"
                            st.link_button("Bekijk Pasfoto", p_url)
                        with col_b:
                            b_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{doc.get('bankbewijs_file_id')}/view?project={APPWRITE_PROJECT_ID}"
                            st.link_button("Bekijk Bankbewijs", b_url)

                        new_status = st.selectbox(
                            "Status wijzigen",
                            ["ingediend", "in_behandeling", "goedgekeurd", "afgewezen"],
                            index=["ingediend", "in_behandeling", "goedgekeurd", "afgewezen"].index(doc.get('status', 'ingediend')),
                            key=doc['$id']
                        )
                        if st.button("Status Opslaan", key=f"btn_{doc['$id']}"):
                            databases.update_document(
                                database_id=APPWRITE_DB_ID,
                                collection_id=APPWRITE_COLLECTION_ID,
                                document_id=doc['$id'],
                                data={'status': new_status}
                            )
                            st.success("Status bijgewerkt!")
                            st.rerun()
        except Exception as e:
            st.error(f"Fout bij ophalen van gegevens: {str(e)}")

# ---------------------------------------------------------
# FOOTER (Samen met Contact & Openingstijden)
# ---------------------------------------------------------
st.markdown("""
<div class="custom-footer">
    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 250px; margin-bottom: 20px;">
            <div class="footer-title">🏛️ Commissariaat Wanica Centrum</div>
            <div class="footer-text">Officiële digitale dienstverlening voor burgers in het district Wanica Centrum.</div>
        </div>
        <div style="flex: 1; min-width: 250px; margin-bottom: 20px;">
            <div class="footer-title">ADRES & CONTACT</div>
            <div class="footer-text">📍 Tawajarieweg no.20, Wanica, Suriname</div>
            <div class="footer-text">📞 366660 / 3666929 / 3666944</div>
        </div>
        <div style="flex: 1; min-width: 250px; margin-bottom: 20px;">
            <div class="footer-title">OPENINGSTIJDEN</div>
            <div class="footer-text">Maandag - Donderdag: 07:00 - 15:00 uur</div>
            <div class="footer-text">Vrijdag: 07:00 - 14:30 uur</div>
            <div class="footer-text">Zaterdag & Zondag: Gesloten</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
