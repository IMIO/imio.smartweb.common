# -*- coding: utf-8 -*-
"""Authorization header for calls between iMio applications
(smartweb, events, news, directory).

- SSO config complete (SSO_APPS_CLIENT_ID, SSO_APPS_CLIENT_SECRET,
  SSO_APPS_URL): Keycloak (sso-apps) token of the technical user.
  pas.plugins.kimug accepts it on the called application.
- Else, SSO_APPS_USER_USERNAME and SSO_APPS_USER_PASSWORD set: basic auth
  with this user (local development: the user must exist in the called site).
- Else: no header.

Never log the secrets (password, client secret, token)."""

import base64
import json
import logging
import os
import requests
import time

logger = logging.getLogger("imio.smartweb.common")

SSO_TIMEOUT = 10
# Get a new token some seconds before it expires.
TOKEN_EXPIRY_MARGIN = 30

# {(sso_url, client_id, username): (header, expires_at)}
_token_cache = {}
_fallback_logged = False


def basic_auth_header(username, password):
    """Return a basic auth Authorization header value."""
    credentials = base64.b64encode(f"{username}:{password}".encode("utf-8"))
    return f"Basic {credentials.decode('utf-8')}"


def clear_sso_token_cache():
    global _fallback_logged
    _token_cache.clear()
    _fallback_logged = False


def _get_token_expiry(token):
    """Return the 'exp' claim of a JWT, or None.
    The signature is not checked: the value is only used for the cache."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        exp = json.loads(base64.urlsafe_b64decode(payload)).get("exp")
        return float(exp)
    except Exception:
        return None


def get_sso_auth_header():
    """Return the Authorization header value to call another iMio
    application: "Bearer ...", "Basic ..." or None."""
    global _fallback_logged
    client_id = os.environ.get("SSO_APPS_CLIENT_ID", "")
    client_secret = os.environ.get("SSO_APPS_CLIENT_SECRET", "")
    sso_url = os.environ.get("SSO_APPS_URL", "")
    username = os.environ.get("SSO_APPS_USER_USERNAME", "")
    password = os.environ.get("SSO_APPS_USER_PASSWORD", "")

    if not client_id or not client_secret or not sso_url:
        if not username or not password:
            logger.warning(
                "No SSO config and no SSO_APPS_USER_USERNAME / "
                "SSO_APPS_USER_PASSWORD: no Authorization header"
            )
            return None
        if not _fallback_logged:
            logger.warning(
                f"SSO config is not complete: use basic auth for user {username}"
            )
            _fallback_logged = True
        return basic_auth_header(username, password)

    key = (sso_url, client_id, username)
    cached = _token_cache.get(key)
    if cached is not None and cached[1] > time.time():
        return cached[0]

    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password,
        "scope": ["openid"],
    }
    try:
        response = requests.post(sso_url, data=payload, timeout=SSO_TIMEOUT)
    except Exception:
        logger.exception(f"Can not get a SSO token from {sso_url}")
        return None
    try:
        id_token = response.json().get("id_token")
    except Exception:
        id_token = None
    if not id_token:
        logger.warning(
            f"No SSO token for user {username} "
            f"(client {client_id}, status {response.status_code})"
        )
        return None

    header = f"Bearer {id_token}"
    exp = _get_token_expiry(id_token)
    if exp is not None:
        _token_cache[key] = (header, exp - TOKEN_EXPIRY_MARGIN)
    return header
