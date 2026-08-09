from __future__ import annotations

import os

from app.auth.base import AuthService, UnconfiguredAuthService
from app.auth.supabase import SupabaseAuthService


def build_auth_service() -> AuthService:
    url = os.getenv("SUPABASE_URL", "").strip()
    publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()
    if not url or not publishable_key:
        return UnconfiguredAuthService()
    return SupabaseAuthService(url=url, publishable_key=publishable_key)
