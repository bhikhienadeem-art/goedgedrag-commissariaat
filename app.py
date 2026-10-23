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

# Appwrite Configuratie
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

# Forceer witte achtergrond en strakke overheidsstijl
st.markdown("""
<style>
    /* Force Light Theme Base */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    
    /* Top Bar */
    .top-bar {
        background-color: #0d5c3a;
        color: white;
        padding: 10px 24px;
        font-size: 0.88rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 6px;
        margin-bottom: 20px;
    }
    
    /* Main Container */
    .main-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
    }
    
    .brand-title {
        color: #0d5c3a;
        font-weight: 800;
        font-size: 1.8rem;
        margin: 0;
    }
    
    /* Document Cards */
    .doc-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 10px;
        min-height: 110px;
    }
    
    .doc-icon {
        background-color: #d1fae5;
        color: #0d5c3a;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        margin-bottom: 8px;
    }

    /* Groene Verzendknop */
    div.stButton > button:first-child {
        background-color: #0d5c3a !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        padding: 12px 28px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100% !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #15803d !important;
    }
    
    /* Footer Styling */
    .footer-container {
        background-color: #053823;
        color: #ffffff;
        padding: 35px 40px;
        border-radius: 16px;
        margin-top: 40px;
    }
    .footer-header {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 12px;
        color: #ffffff;
    }
    .footer-text {
        color: #cbd5e1;
        font-size: 0.88rem;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Appwrite Client
@st.cache_resource
def get_appwrite_clients():
    client = Client()
    client.set_endpoint(APPWRITE_ENDPOINT)
    client.set_project(APPWRITE_PROJECT_ID)
    return client, Databases(client), Storage(client), Account(client)

client, databases, storage, account = get_appwrite_clients()

def generate_aanvraagnummer():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"VGG-WAN-2026-{suffix}"

# 🏛️ Bovenbalk
st.markdown("""
<div class="top-bar">
    <div>🏛️ <b>Officieel Aanvraagportaal Verklaring van Goed Gedrag (VGG)</b></div>
    <div>📍 Tawajarieweg no.20 &nbsp;|&nbsp; 📞 366660 / 3666929 / 3666944</div>
</div>
""", unsafe_allow_html=True)

# Header met Navigatie
col_brand, col_nav = st.columns([2, 1])
with col_brand:
    st.markdown("<h1 class='brand-title'>🏛️ Commissariaat Wanica Centrum</h1>", unsafe_allow_html=True)

with col_nav:
    tab_choice = st.radio("", ["📝 Online Aanvraag (Cliënten)", "🔐 Medewerkers Portaal"], horizontal=True)

st.divider()

# ---------------------------------------------------------
# TAB 1: ONLINE AANVRAAG
# ---------------------------------------------------------
if tab_choice == "📝 Online Aanvraag (Cliënten)":
    st.markdown("""
    <div class="main-card">
        <h2 style='color:#0d5c3a; margin-top:0;'>🟢 Aanvraag Verklaring van Goed Gedrag (VGG)</h2>
        <p style='color:#475569;'>Vul onderstaande gegevens nauwkeurig in en voeg uw documenten toe om uw aanvraag in te dienen bij het Commissariaat Wanica Centrum.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("vgg_client_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            volledige_naam = st.text_input("VOLLEDIGE NAAM *", placeholder="bijv. Jan van Sichem")
        with col_f2:
            emailadres = st.text_input("E-MAILADRES *", placeholder="naam@voorbeeld.com")
            
        st.markdown("<br><b>VEREISTE DOCUMENTEN (3 BESTANDEN)</b>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div class="doc-box">
                <div class="doc-icon">🪪</div>
                <b>1. Uittreksel CBB *</b><br>
                <small style='color:#64748b;'>PDF of Afbeelding (Max 5MB)</small>
            </div>
            """, unsafe_allow_html=True)
            uittreksel_file = st.file_uploader("", type=['pdf', 'jpg', 'jpeg', 'png'], key="uittreksel")
            
        with c2:
            st.markdown("""
            <div class="doc-box">
                <div class="doc-icon">👤</div>
                <b>2. Pasfoto *</b><br>
                <small style='color:#64748b;'>Recente pasfoto (JPG/PNG)</small>
            </div>
            """, unsafe_allow_html=True)
            pasfoto_file = st.file_uploader("", type=['jpg', 'jpeg', 'png'], key="pasfoto")
            
        with c3:
            st.markdown("""
            <div class="doc-box">
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
                    with st.spinner("Documenten uploaden naar Appwrite..."):
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

                        st.success("✅ Uw aanvraag is succesvol geregistreerd!")
                        st.info(f"**Uw Aanvraagnummer:** `{aanvraagnummer}`")
                except Exception as e:
                    st.error(f"Fout bij opslaan: {str(e)}")

# ---------------------------------------------------------
# TAB 2: MEDEWERKERS PORTAAL
# ---------------------------------------------------------
else:
    st.markdown("### 🔐 Medewerkers Beheerdersportaal")
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        with st.form("login_form"):
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

        st.subheader("📋 Binnengekomen Aanvragen (Appwrite Database)")
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
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            u_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{doc.get('uittreksel_file_id')}/view?project={APPWRITE_PROJECT_ID}"
                            st.link_button("Bekijk Uittreksel", u_url)
                        with col2:
                            p_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{doc.get('pasfoto_file_id')}/view?project={APPWRITE_PROJECT_ID}"
                            st.link_button("Bekijk Pasfoto", p_url)
                        with col3:
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
# FOOTER
# ---------------------------------------------------------
st.markdown("""
<div class="footer-container">
    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 250px; margin-bottom: 20px;">
            <div class="footer-header">🏛️ Commissariaat Wanica Centrum</div>
            <div class="footer-text">Officiële digitale dienstverlening voor burgers in het district Wanica Centrum.</div>
        </div>
        <div style="flex: 1; min-width: 250px; margin-bottom: 20px;">
            <div class="footer-header">ADRES & CONTACT</div>
            <div class="footer-text">📍 Tawajarieweg no.20, Wanica, Suriname</div>
            <div class="footer-text">📞 366660 / 3666929 / 3666944</div>
        </div>
        <div style="flex: 1; min-width: 250px; margin-bottom: 20px;">
            <div class="footer-header">OPENINGSTIJDEN</div>
            <div class="footer-text">Maandag - Donderdag: 07:00 - 15:00 uur</div>
            <div class="footer-text">Vrijdag: 07:00 - 14:30 uur</div>
            <div class="footer-text">Zaterdag & Zondag: Gesloten</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
