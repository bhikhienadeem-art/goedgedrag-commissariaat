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

# Forceer lichte achtergrond via CSS
st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important;
        color: #1e293b !important;
    }
    .top-gov-bar {
        background-color: #0d5c3a;
        color: white;
        padding: 12px 24px;
        font-size: 0.9rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    .gov-title {
        color: #0d5c3a;
        font-weight: 800;
        font-size: 2rem;
    }
    .form-container {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 35px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
    }
    div.stButton > button:first-child {
        background-color: #0d5c3a !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100% !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #15803d !important;
    }
    .gov-footer {
        background-color: #053823;
        color: #ffffff;
        padding: 40px;
        border-radius: 12px;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

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

st.markdown("""
<div class="top-gov-bar">
    <div>🏛️ <b>Officieel Aanvraagportaal Verklaring van Goed Gedrag (VGG)</b></div>
    <div>📍 Tawajarieweg no.20 &nbsp;|&nbsp; 📞 366660 / 3666929 / 3666944</div>
</div>
""", unsafe_allow_html=True)

col_logo, col_menu = st.columns([2, 1])
with col_logo:
    st.markdown("<h1 class='gov-title'>Commissariaat Wanica Centrum</h1>", unsafe_allow_html=True)
    st.caption("District Commissariaat Wanica — Digitale Loketdiensten")

with col_menu:
    tab_choice = st.radio("Navigatie", ["📝 Online Aanvraag (Cliënten)", "🔐 Medewerkers Portaal"], horizontal=True, label_visibility="collapsed")

st.divider()

if tab_choice == "📝 Online Aanvraag (Cliënten)":
    st.markdown("""
    <div class="form-container">
        <h2 style='color:#0d5c3a; margin-top:0;'>Aanvraag Verklaring van Goed Gedrag (VGG)</h2>
        <p style='color:#64748b;'>Vul onderstaande velden nauwkeurig in en upload de vereiste documenten.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("client_vgg_submission", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            volledige_naam = st.text_input("VOLLEDIGE NAAM *", placeholder="Volgens CBB uittreksel")
        with col2:
            emailadres = st.text_input("E-MAILADRES *", placeholder="jouw@email.com")
            
        st.markdown("<br><b>VEREISTE DOCUMENTEN (3 BESTANDEN)</b>", unsafe_allow_html=True)
        
        c_u, c_p, c_b = st.columns(3)
        with c_u:
            st.info("🪪 **1. Uittreksel CBB**\n\n(PDF/Afbeelding, max 5MB)")
            uittreksel_file = st.file_uploader("Upload uittreksel", type=['pdf', 'jpg', 'jpeg', 'png'], key="uit")
        with c_p:
            st.info("👤 **2. Pasfoto**\n\n(Recente pasfoto, JPG/PNG)")
            pasfoto_file = st.file_uploader("Upload pasfoto", type=['jpg', 'jpeg', 'png'], key="pas")
        with c_b:
            st.info("🧾 **3. Bankbewijs**\n\n(Leges overschrijving, PDF/JPG)")
            bankbewijs_file = st.file_uploader("Upload bankbewijs", type=['pdf', 'jpg', 'jpeg', 'png'], key="ban")

        st.markdown("<br>", unsafe_allow_html=True)
        submit_clicked = st.form_submit_button("✈️ Aanvraag Veilig Verzenden")
        
        if submit_clicked:
            if not volledige_naam or not emailadres or not uittreksel_file or not pasfoto_file or not bankbewijs_file:
                st.error("⚠️ Vul alstublieft alle velden in en zorg dat alle 3 de documenten zijn geüpload.")
            else:
                try:
                    with st.spinner("Bezig met uploaden en registreren..."):
                        u_res = storage.create_file(APPWRITE_BUCKET_ID, 'unique()', InputFile.from_bytes(uittreksel_file.read(), filename=uittreksel_file.name))
                        p_res = storage.create_file(APPWRITE_BUCKET_ID, 'unique()', InputFile.from_bytes(pasfoto_file.read(), filename=pasfoto_file.name))
                        b_res = storage.create_file(APPWRITE_BUCKET_ID, 'unique()', InputFile.from_bytes(bankbewijs_file.read(), filename=bankbewijs_file.name))

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

                        st.success("✅ Uw aanvraag is succesvol ingediend bij het Commissariaat!")
                        st.info(f"**Uw unieke aanvraagnummer is:** `{aanvraagnummer}`")
                except Exception as e:
                    st.error(f"Fout bij indienen: {str(e)}")
else:
    st.markdown("### 🔐 Medewerkers Beheerdersportaal")
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        with st.form("staff_login"):
            email = st.text_input("Medewerker E-mailadres")
            password = st.text_input("Wachtwoord", type="password")
            login_btn = st.form_submit_button("Inloggen op Portaal")

            if login_btn:
                try:
                    account.create_email_password_session(email, password)
                    st.session_state['logged_in'] = True
                    st.success("Succesvol ingelogd!")
                    st.rerun()
                except Exception:
                    st.error("Inloggen mislukt. Controleer uw inloggegevens.")
    else:
        if st.button("Uitloggen"):
            st.session_state['logged_in'] = False
            st.rerun()

        st.subheader("📋 Binnengekomen Aanvragen")
        try:
            docs = databases.list_documents(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID).get('documents', [])
            if not docs:
                st.info("Geen aanvragen gevonden.")
            else:
                for doc in docs:
                    with st.expander(f"📌 {doc.get('aanvraagnummer')} — {doc.get('client_naam')} ({doc.get('status').upper()})"):
                        st.write(f"**E-mail:** {doc.get('client_email')}")
                        col_1, col_2, col_3 = st.columns(3)
                        with col_1:
                            u_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{doc.get('uittreksel_file_id')}/view?project={APPWRITE_PROJECT_ID}"
                            st.link_button("Bekijk Uittreksel", u_url)
                        with col_2:
                            p_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{doc.get('pasfoto_file_id')}/view?project={APPWRITE_PROJECT_ID}"
                            st.link_button("Bekijk Pasfoto", p_url)
                        with col_3:
                            b_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{doc.get('bankbewijs_file_id')}/view?project={APPWRITE_PROJECT_ID}"
                            st.link_button("Bekijk Bankbewijs", b_url)

                        new_status = st.selectbox(
                            "Status bijwerken",
                            ["ingediend", "in_behandeling", "goedgekeurd", "afgewezen"],
                            index=["ingediend", "in_behandeling", "goedgekeurd", "afgewezen"].index(doc.get('status', 'ingediend')),
                            key=f"status_{doc['$id']}"
                        )
                        if st.button("Status Opslaan", key=f"save_{doc['$id']}"):
                            databases.update_document(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, doc['$id'], {'status': new_status})
                            st.success("Status bijgewerkt!")
                            st.rerun()
        except Exception as e:
            st.error(f"Fout bij ophalen: {str(e)}")

st.markdown("""
<div class="gov-footer">
    <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
        <div style="flex: 1; min-width: 250px;">
            <b>🏛️ Commissariaat Wanica Centrum</b><br>Officiële digitale dienstverlening.
        </div>
        <div style="flex: 1; min-width: 250px;">
            <b>ADRES & CONTACT</b><br>📍 Tawajarieweg no.20<br>📞 366660 / 3666929
        </div>
        <div style="flex: 1; min-width: 250px;">
            <b>OPENINGSTIJDEN</b><br>Ma-Do: 07:00 - 15:00<br>Vrijdag: 07:00 - 14:30
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
