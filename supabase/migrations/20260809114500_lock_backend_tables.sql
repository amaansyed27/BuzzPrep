drop index if exists public.ix_interview_sessions_session_id;
drop index if exists public.ix_interview_sessions_owner_id;
drop index if exists public.ix_interview_sessions_status;
drop index if exists public.ix_interview_turns_session_id;

create policy "deny direct client access"
    on public.interview_sessions
    for all
    to anon, authenticated
    using (false)
    with check (false);

create policy "deny direct client access"
    on public.interview_turns
    for all
    to anon, authenticated
    using (false)
    with check (false);
