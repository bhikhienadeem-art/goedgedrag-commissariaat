-- Starter schema. Test eerst in een nieuw Supabase-project.
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null default '',
  role text not null check (role in ('staff','admin')),
  created_at timestamptz not null default now()
);

create table if not exists public.applications (
  id uuid primary key default gen_random_uuid(),
  -- Official number is entered by staff when receipt is registered.
  application_number text unique,
  received_at timestamptz,
  received_by uuid references auth.users(id) on delete set null,
  full_name text not null,
  email text,
  phone text,
  status text not null default 'Nieuw'
    check (status in ('Nieuw','Stukken controleren','In behandeling','Afgegeven')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.application_documents (
  id uuid primary key default gen_random_uuid(),
  application_id uuid not null references public.applications(id) on delete restrict,
  document_type text not null check (document_type in ('uittreksel','pasfoto','betalingsbewijs')),
  bucket_name text not null default 'aanvraag-documenten',
  object_path text not null,
  original_filename text not null,
  uploaded_at timestamptz not null default now(),
  downloaded_at timestamptz,
  deleted_at timestamptz,
  download_status text not null default 'available'
    check (download_status in ('available','deleting','deleted','delete_failed')),
  unique(bucket_name, object_path)
);

create table if not exists public.audit_log (
  id bigint generated always as identity primary key,
  actor_user_id uuid references auth.users(id) on delete set null,
  application_id uuid references public.applications(id) on delete set null,
  document_id uuid references public.application_documents(id) on delete set null,
  action text not null,
  outcome text not null,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.applications enable row level security;
alter table public.application_documents enable row level security;
alter table public.audit_log enable row level security;

-- Do not add broad public policies. This starter performs privileged reads/writes
-- server-side after checking the logged-in user's role. Configure tighter policies
-- before production if clients will access Supabase directly.


-- One-time tokens used by the browser to download a document directly.
create table if not exists public.document_download_tokens (
  token_hash text primary key,
  document_id uuid not null references public.application_documents(id) on delete cascade,
  actor_user_id uuid not null references auth.users(id) on delete cascade,
  expires_at timestamptz not null,
  used_at timestamptz,
  created_at timestamptz not null default now()
);
alter table public.document_download_tokens enable row level security;
