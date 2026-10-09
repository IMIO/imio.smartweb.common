# -*- coding: utf-8 -*-
"""Authorization header for calls between iMio applications
(smartweb, events, news, directory).

- "Use basic auth" selected in the control panel (@@sso-controlpanel):
  basic auth with the user and password of the control panel.
  The user must exist in the called site.
- Else: Keycloak (sso-apps) token of the technical user (SSO_APPS_CLIENT_ID,
  SSO_APPS_CLIENT_SECRET, SSO_APPS_URL, SSO_APPS_USER_USERNAME,
  SSO_APPS_USER_PASSWORD). pas.plugins.kimug accepts it on the called site.

Never log the secrets (password, client secret, token)."""

from plone import api

import base64
import json
import logging
import os
import requests
import time

logger = logging.getLogger("imio.smartweb.common")

REGISTRY_PREFIX = "imio.smartweb.common.sso"

SSO_TIMEOUT = 10
# Get a new token some seconds before it expires.
TOKEN_EXPIRY_MARGIN = 30

# {(sso_url, client_id, username): (header, expires_at)}
_token_cache = {}


def basic_auth_header(username, password):
    """Return a basic auth Authorization header value."""
    credentials = base64.b64encode(f"{username}:{password}".encode("utf-8"))
    return f"Basic {credentials.decode('utf-8')}"


def clear_sso_token_cache():
    _token_cache.clear()


def _get_setting(name):
    """Return a value of the control panel, or None (ex: no Plone site)."""
    try:
        return api.portal.get_registry_record(f"{REGISTRY_PREFIX}.{name}", default=None)
    except Exception:
        return None


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
    if _get_setting("force_basic_auth"):
        username = _get_setting("basic_auth_username")
        password = _get_setting("basic_auth_password")
        if not username or not password:
            logger.warning(
                "Basic auth is selected but its username or password is empty: "
                "no Authorization header"
            )
            return None
        return basic_auth_header(username, password)

    client_id = os.environ.get("SSO_APPS_CLIENT_ID", "")
    client_secret = os.environ.get("SSO_APPS_CLIENT_SECRET", "")
    sso_url = os.environ.get("SSO_APPS_URL", "")
    username = os.environ.get("SSO_APPS_USER_USERNAME", "")
    password = os.environ.get("SSO_APPS_USER_PASSWORD", "")
    if not all((client_id, client_secret, sso_url, username, password)):
        logger.warning(
            "SSO config is not complete (SSO_APPS_* env vars) and basic auth "
            "is not selected: no Authorization header"
        )
        return None

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
