import os
import streamlit as st
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.services.account import Account

load_dotenv()

# Appwrite Configuratie
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://fra.cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", "6adb474d000b3faf4ab8")
APPWRITE_DB_ID = os.getenv("APPWRITE_DB_ID", "6adb48b70023ab8bd572")
APPWRITE_COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_ID", "aanvragen")
APPWRITE_BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID", "documenten")

st.set_page_config(
    page_title="Goedgedrag | Commissariaat Wanica Centrum",
    layout="wide"
)

# Groen-witte overheidsstijl
st.markdown("""
<style>
    .main-header {
        background-color: #0d5c3a;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-header h1, .main-header p {
        color: white !important;
    }
</style>
<div class="main-header">
    <h1>Commissariaat Wanica Centrum</h1>
    <p>Verklaring van Goed Gedrag (VGG) — Medewerkersdashboard</p>
</div>
""", unsafe_allow_html=True)

# Appwrite Client
@st.cache_resource
def get_appwrite_clients():
    client = Client()
    client.set_endpoint(APPWRITE_ENDPOINT)
    client.set_project(APPWRITE_PROJECT_ID)
    return client, Databases(client), Storage(client), Account(client)

client, databases, storage, account = get_appwrite_clients()

if "session" not in st.session_state:
    st.session_state.session = None

# Medewerker Login via Appwrite Auth
if not st.session_state.session:
    st.subheader("Medewerker Inloggen")
    email = st.text_input("E-mailadres")
    password = st.text_input("Wachtwoord", type="password")
    
    if st.button("Inloggen", type="primary"):
        try:
            session = account.create_email_password_session(email, password)
            st.session_state.session = session
            st.success("Succesvol ingelogd!")
            st.rerun()
        except Exception as e:
            st.error("Inloggen mislukt. Controleer uw e-mailadres en wachtwoord.")
    st.stop()

if st.button("Uitloggen"):
    try:
        account.delete_session('current')
    except Exception:
        pass
    st.session_state.session = None
    st.rerun()

st.divider()
st.subheader("Binnengekomen Aanvragen")

try:
    response = databases.list_documents(
        database_id=APPWRITE_DB_ID,
        collection_id=APPWRITE_COLLECTION_ID
    )
    applications = response.get("documents", [])
except Exception as e:
    st.error(f"Fout bij het ophalen van aanvragen uit Appwrite: {e}")
    applications = []

if not applications:
    st.info("Er zijn momenteel geen aanvragen gevonden in de Appwrite database.")
    st.stop()

for app_doc in applications:
    app_id = app_doc.get("$id")
    aanvraagnummer = app_doc.get("aanvraagnummer", "Geen nummer")
    client_naam = app_doc.get("client_naam", "Onbekend")
    status = app_doc.get("status", "ingediend")

    with st.expander(f"📌 {aanvraagnummer} — {client_naam} ({status.upper()})"):
        st.write(f"**E-mailadres:** {app_doc.get('client_email', '—')}")
        st.write(f"**Huidige Status:** `{status}`")

        statuses = ["ingediend", "in_behandeling", "goedgekeurd", "afgewezen"]
        current_index = statuses.index(status) if status in statuses else 0
        new_status = st.selectbox("Status wijzigen", statuses, index=current_index, key=f"status_{app_id}")
        
        if st.button("Status opslaan", key=f"save_{app_id}"):
            try:
                databases.update_document(
                    database_id=APPWRITE_DB_ID,
                    collection_id=APPWRITE_COLLECTION_ID,
                    document_id=app_id,
                    data={"status": new_status}
                )
                st.success("Status succesvol bijgewerkt in Appwrite!")
                st.rerun()
            except Exception as e:
                st.error(f"Kon status niet bijwerken: {e}")

        st.markdown("---")
        st.markdown("**Gekoppelde Documenten:**")

        file_keys = [
            ("Uittreksel", app_doc.get("uittreksel_file_id")),
            ("Pasfoto", app_doc.get("pasfoto_file_id")),
            ("Bankbewijs", app_doc.get("bankbewijs_file_id"))
        ]

        col1, col2, col3 = st.columns(3)
        for i, (doc_label, file_id) in enumerate(file_keys):
            col = [col1, col2, col3][i]
            if file_id:
                file_url = f"{APPWRITE_ENDPOINT}/storage/buckets/{APPWRITE_BUCKET_ID}/files/{file_id}/view?project={APPWRITE_PROJECT_ID}"
                col.markdown(f"**{doc_label}:**")
                col.link_button(f"Bekijk {doc_label}", file_url)
            else:
                col.write(f"**{doc_label}:** Niet beschikbaar")
