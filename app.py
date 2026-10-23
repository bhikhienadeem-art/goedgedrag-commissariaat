import os, requests
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
DOWNLOAD_API_URL = os.getenv("DOWNLOAD_API_URL", "http://127.0.0.1:8001")

st.set_page_config(page_title="Goedgedrag | Commissariaat Wanica Centrum", layout="wide")
st.title("Goedgedrag – Medewerkersdashboard")
st.caption("Commissariaat Wanica Centrum")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    st.error("Vul SUPABASE_URL en SUPABASE_ANON_KEY in het .env-bestand in.")
    st.stop()

if "session" not in st.session_state:
    st.session_state.session = None
if "supabase" not in st.session_state:
    st.session_state.supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
client = st.session_state.supabase

if not st.session_state.session:
    st.subheader("Medewerker login")
    email = st.text_input("E-mailadres")
    password = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen", type="primary"):
        try:
            result = client.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.session = result.session
            st.rerun()
        except Exception:
            st.error("Inloggen mislukt. Controleer uw gegevens of neem contact op met de beheerder.")
    st.info("Medewerkersaccounts moeten vooraf door een beheerder worden aangemaakt.")
    st.stop()

session = st.session_state.session
access_token = session.access_token
user_id = session.user.id

try:
    profile = client.table("profiles").select("display_name,role").eq("id", user_id).single().execute().data
except Exception:
    profile = None
if not profile or profile.get("role") not in ("staff", "admin"):
    st.error("Uw account heeft geen bevoegde medewerkersrol.")
    if st.button("Uitloggen"):
        client.auth.sign_out()
        st.session_state.session = None
        st.rerun()
    st.stop()

st.write(f"Ingelogd als **{profile.get('display_name') or session.user.email}**")
if st.button("Uitloggen"):
    client.auth.sign_out()
    st.session_state.session = None
    st.rerun()

st.divider()
st.subheader("Aanvragen")
try:
    applications = client.table("applications").select(
        "id,application_number,full_name,email,phone,status,created_at"
    ).order("created_at", desc=True).limit(200).execute().data or []
except Exception:
    applications = []

if not applications:
    st.info("Er zijn nog geen aanvragen, of de database is nog niet ingericht.")
    st.stop()

for application in applications:
    shown_number = application.get("application_number") or "Nog niet genummerd"
    with st.expander(f"{shown_number} — {application['full_name']} — {application['status']}"):
        st.write(f"E-mail: {application.get('email') or '—'}")
        if not application.get("application_number"):
            st.info("Deze aanvraag heeft nog geen officieel aanvraagnummer.")
            with st.form(key=f"receipt_form_{application['id']}"):
                manual_number = st.text_input(
                    "Officieel aanvraagnummer (handmatig invoeren)",
                    key=f"manual_number_{application['id']}",
                    placeholder="Bijv. GG/2026/015"
                )
                confirm_receipt = st.form_submit_button("Ontvangst registreren")
            if confirm_receipt:
                cleaned_number = manual_number.strip()
                if not cleaned_number:
                    st.error("Vul eerst het aanvraagnummer in.")
                else:
                    try:
                        existing = client.table("applications").select("id").eq(
                            "application_number", cleaned_number
                        ).execute().data or []
                        if existing:
                            st.error("Dit aanvraagnummer is al in gebruik. Controleer het nummer.")
                        else:
                            client.table("applications").update({
                                "application_number": cleaned_number,
                                "received_at": __import__("datetime").datetime.now(
                                    __import__("datetime").timezone.utc
                                ).isoformat(),
                                "received_by": user_id,
                                "status": "Stukken controleren"
                            }).eq("id", application["id"]).execute()
                            client.table("audit_log").insert({
                                "actor_user_id": user_id,
                                "application_id": application["id"],
                                "action": "receipt_registered",
                                "outcome": "success",
                                "details": {"application_number": cleaned_number}
                            }).execute()
                            st.success("Ontvangst en aanvraagnummer geregistreerd.")
                            st.rerun()
                    except Exception:
                        st.error("Ontvangst kon niet worden geregistreerd. Controleer databasebeleid.")
        else:
            st.write(f"Officieel aanvraagnummer: **{application['application_number']}**")
            st.write(f"Ontvangen op: {application.get('received_at') or '—'}")
        st.write(f"Telefoon: {application.get('phone') or '—'}")
        st.write(f"Aangemaakt: {application.get('created_at') or '—'}")
        statuses = ["Nieuw", "Stukken controleren", "In behandeling", "Afgegeven"]
        new_status = st.selectbox("Status", statuses, index=statuses.index(application["status"]), key=f"status_{application['id']}")
        if st.button("Status opslaan", key=f"save_{application['id']}"):
            try:
                client.table("applications").update({"status": new_status}).eq("id", application["id"]).execute()
                client.table("audit_log").insert({
                    "actor_user_id": user_id, "application_id": application["id"],
                    "action": "status_changed", "outcome": "success",
                    "details": {"new_status": new_status}
                }).execute()
                st.success("Status bijgewerkt.")
                st.rerun()
            except Exception:
                st.error("Status kon niet worden bijgewerkt. Controleer databasebeleid en rechten.")

        docs = client.table("application_documents").select(
            "id,document_type,original_filename,uploaded_at,downloaded_at,deleted_at,download_status"
        ).eq("application_id", application["id"]).order("uploaded_at").execute().data or []
        st.markdown("**Documenten**")
        for doc in docs:
            cols = st.columns([3, 2, 2])
            cols[0].write(f"{doc['document_type']}: {doc['original_filename']}")
            cols[1].write(doc["download_status"])
            if doc["download_status"] == "available":
                if cols[2].button("Downloadlink maken", key=f"prepare_{doc['id']}"):
                    try:
                        result = requests.post(
                            f"{DOWNLOAD_API_URL.rstrip('/')}/prepare-download",
                            json={"document_id": doc["id"]},
                            headers={"Authorization": f"Bearer {access_token}"},
                            timeout=20
                        )
                        if result.ok:
                            link = result.json()["download_url"]
                            st.link_button("Download document (eenmalige link)", link)
                            st.warning(
                                "Na openen van deze link wordt het bestand via de download-API verzonden. "
                                "Daarna probeert de server het bestand uit Supabase Storage te verwijderen. "
                                "Dit bewijst niet dat het bestand lokaal is opgeslagen."
                            )
                        else:
                            st.error("Downloadlink kon niet worden gemaakt; het bestand is niet verwijderd.")
                    except Exception:
                        st.error("Downloadlink kon niet worden gemaakt; het bestand is niet verwijderd.")
            elif doc["download_status"] == "deleted":
                cols[2].write("Verwijderd")
