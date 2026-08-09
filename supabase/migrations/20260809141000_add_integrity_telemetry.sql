alter table public.interview_sessions
    add column if not exists integrity_telemetry jsonb not null default '[]'::jsonb;

comment on column public.interview_sessions.integrity_telemetry is
    'Transparent focus/fullscreen/connectivity events. Separate from semantic workspace evidence.';
