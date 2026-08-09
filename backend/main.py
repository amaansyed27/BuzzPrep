"""Vercel-recognized ASGI entrypoint; local development still uses app.main:app."""

from app.main import app

__all__ = ["app"]
