# Goedgedrag – starterproject (Streamlit + Supabase)

Dit is een startproject, geen reeds gekoppelde/live applicatie. Het bevat:
- Streamlit-medewerkersdashboard (`app.py`)
- FastAPI-downloadendpoint (`download_api.py`) dat biedt een eenmalige downloadlink en probeert na het verzenden van de response het geselecteerde bestand uit Supabase Storage te verwijderen
- SQL-schema (`supabase_schema.sql`)
- voorbeeldconfiguratie (`.env.example`)

## Belangrijke beperking
Een server kan detecteren dat de HTTP-response is verzonden, maar kan niet garanderen dat een medewerker het bestand daadwerkelijk heeft geopend of lokaal heeft opgeslagen. Dit project verwijdert na het verzenden van de response; test dit eerst met fictieve bestanden. Voor officieel gebruik moet het commissariaat deze bewaartermijn en werkwijze formeel goedkeuren.

## Installatie
1. Maak een Supabase-project aan.
2. Open SQL Editor en voer `supabase_schema.sql` uit.
3. Maak in Supabase Storage een **private** bucket met naam `aanvraag-documenten`.
4. Maak een `.env` op basis van `.env.example`.
5. Installeer Python-pakketten:
   `pip install -r requirements.txt`
6. Start de download-API in terminal 1:
   `uvicorn download_api:app --host 127.0.0.1 --port 8001`
7. Start Streamlit in terminal 2:
   `streamlit run app.py`

## Configuratie
- `SUPABASE_URL`: project-URL
- `SUPABASE_ANON_KEY`: anon/publishable key
- `SUPABASE_SERVICE_ROLE_KEY`: server-only secret. Zet deze nooit in GitHub, browsercode of Streamlit UI.
- `DOWNLOAD_API_URL`: bijvoorbeeld `http://127.0.0.1:8001` (interne API vanuit Streamlit)
- `PUBLIC_DOWNLOAD_API_URL`: URL die de browser van de medewerker kan bereiken, bijvoorbeeld `http://127.0.0.1:8001` lokaal of de publieke HTTPS-URL na deployment

## Beveiliging vóór productie
- Gebruik HTTPS en een betrouwbare hostingomgeving.
- Zet secrets in de hostingprovider, niet in Git.
- Stel medewerkers in via Supabase Auth en `profiles`; alleen `role='staff'` of `role='admin'` mag downloaden.
- Configureer Supabase Row Level Security (RLS) en test alle policies.
- Voeg rate limiting, limieten voor bestandsgrootte, malwarecontrole en back-ups toe.
- Test verwijdering en foutafhandeling met niet-gevoelige testbestanden.
- Auditlogs bevatten metadata, nooit documentinhoud of publieke bestandslinks.


## Handmatig aanvraagnummer
Het officiële aanvraagnummer wordt niet automatisch gegenereerd. De medewerker voert dit in via het dashboard wanneer de ontvangst wordt geregistreerd. De database voorkomt dubbele aanvraagnummers. Het moment van ontvangst en de medewerker worden vastgelegd.
