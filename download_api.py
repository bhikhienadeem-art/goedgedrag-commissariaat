import os, hashlib, secrets
from datetime import datetime, timezone, timedelta
from io import BytesIO

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from pydantic import BaseModel
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET = os.getenv("SUPABASE_BUCKET", "aanvraag-documenten")
PUBLIC_DOWNLOAD_API_URL = os.getenv("PUBLIC_DOWNLOAD_API_URL", "http://127.0.0.1:8001")

app = FastAPI(title="Goedgedrag secure download API")

class PrepareRequest(BaseModel):
    document_id: str

def clients():
    if not all([SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY]):
        raise HTTPException(status_code=500, detail="Serverconfiguratie ontbreekt.")
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY), create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def audit(admin, actor_id, application_id, document_id, action, outcome, details=None):
    admin.table("audit_log").insert({
        "actor_user_id": actor_id, "application_id": application_id,
        "document_id": document_id, "action": action, "outcome": outcome,
        "details": details or {}
    }).execute()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/prepare-download")
def prepare_download(body: PrepareRequest, authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ").strip()
    if not token or token == authorization:
        raise HTTPException(status_code=401, detail="Authenticatie vereist.")
    auth_client, admin = clients()
    try:
        user = auth_client.auth.get_user(token).user
        if not user:
            raise HTTPException(status_code=401, detail="Ongeldige sessie.")
        profile = admin.table("profiles").select("role").eq("id", user.id).single().execute().data
        if not profile or profile.get("role") not in ("staff", "admin"):
            raise HTTPException(status_code=403, detail="Geen downloadrechten.")
        doc = admin.table("application_documents").select(
            "id,application_id,bucket_name,object_path,original_filename,download_status"
        ).eq("id", body.document_id).single().execute().data
        if not doc or doc["download_status"] != "available":
            raise HTTPException(status_code=404, detail="Document niet beschikbaar.")
        if doc["bucket_name"] != BUCKET:
            raise HTTPException(status_code=400, detail="Ongeldige opslaglocatie.")

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        admin.table("document_download_tokens").insert({
            "token_hash": token_hash,
            "document_id": doc["id"],
            "actor_user_id": user.id,
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        }).execute()
        return {
            "download_url": f"{PUBLIC_DOWNLOAD_API_URL.rstrip('/')}/download/{raw_token}",
            "expires_in_seconds": 300
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Downloadlink kon niet worden gemaakt.")

def cleanup_after_response(document_id, actor_id, application_id, bucket, path):
    """Runs after response transmission; this is not proof the recipient saved/opened the file."""
    _, admin = clients()
    try:
        # Remove actual object first; only then mark the metadata as deleted.
        admin.storage.from_(bucket).remove([path])
        now = datetime.now(timezone.utc).isoformat()
        admin.table("application_documents").update({
            "downloaded_at": now,
            "deleted_at": now,
            "download_status": "deleted",
            "object_path": f"deleted/{document_id}"
        }).eq("id", document_id).execute()
        audit(admin, actor_id, application_id, document_id,
              "document_download_and_delete", "success",
              {"bucket": bucket, "storage_object_removed": True})
    except Exception as exc:
        try:
            admin.table("application_documents").update({
                "download_status": "delete_failed"
            }).eq("id", document_id).execute()
            audit(admin, actor_id, application_id, document_id,
                  "document_download_and_delete", "failure",
                  {"error_type": type(exc).__name__})
        except Exception:
            pass

@app.get("/download/{raw_token}")
def download_by_token(raw_token: str):
    _, admin = clients()
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    try:
        token_row = admin.table("document_download_tokens").select(
            "token_hash,document_id,actor_user_id,expires_at,used_at"
        ).eq("token_hash", token_hash).single().execute().data
        if not token_row or token_row.get("used_at"):
            raise HTTPException(status_code=404, detail="Downloadlink ongeldig of al gebruikt.")
        expires = datetime.fromisoformat(token_row["expires_at"].replace("Z", "+00:00"))
        if expires < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="Downloadlink verlopen.")

        doc = admin.table("application_documents").select(
            "id,application_id,bucket_name,object_path,original_filename,download_status"
        ).eq("id", token_row["document_id"]).single().execute().data
        if not doc or doc["download_status"] != "available" or doc["bucket_name"] != BUCKET:
            raise HTTPException(status_code=409, detail="Document niet beschikbaar.")

        # Retrieve file first. If this fails, no cleanup task is scheduled.
        blob = admin.storage.from_(doc["bucket_name"]).download(doc["object_path"])
        if not blob:
            raise HTTPException(status_code=502, detail="Bestand kon niet worden opgehaald.")

        # Mark token used before serving, to reduce replay/race risk.
        admin.table("document_download_tokens").update({
            "used_at": datetime.now(timezone.utc).isoformat()
        }).eq("token_hash", token_hash).is_("used_at", "null").execute()
        audit(admin, token_row["actor_user_id"], doc["application_id"], doc["id"],
              "document_download_started", "success", {"filename": doc["original_filename"]})

        safe_name = doc["original_filename"].replace('"', "").replace("\r", "").replace("\n", "")
        return StreamingResponse(
            BytesIO(blob),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}"',
                     "Cache-Control": "no-store"},
            background=BackgroundTask(
                cleanup_after_response, doc["id"], token_row["actor_user_id"],
                doc["application_id"], doc["bucket_name"], doc["object_path"]
            ),
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Download kon niet worden verwerkt.")
