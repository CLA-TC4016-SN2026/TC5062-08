import os

# The contract tests import src.main/src.auth, which build a Settings() at module
# level. Settings.jwt_secret now rejects anything under 32 characters (see
# src/settings.py) so a weak secret can't accidentally run in production — but that
# means a fresh checkout with no .env would fail to even collect these tests. This
# is a pytest-only placeholder, long enough to pass validation, never used to sign
# a real token.
os.environ.setdefault("JWT_SECRET", "pytest-only-secret-not-for-production-1234567890")
