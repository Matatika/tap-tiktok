"""TikTok authentication helpers."""

import json
from typing import Optional

import requests
from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta, utc_now


class TikTokAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator for TikTok OAuth token refresh."""

    def __init__(
        self,
        *args,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.refresh_token = refresh_token
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def auth_headers(self) -> dict:
        """Return auth headers for API requests."""
        if not self.is_token_valid():
            self.update_access_token()
        return {"Access-Token": str(self.access_token)}

    @property
    def oauth_request_headers(self) -> dict:
        """Return headers for OAuth token requests."""
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @property
    def oauth_request_body(self) -> dict:
        """Return the OAuth refresh request payload."""
        return {
            "client_key": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

    def update_access_token(self) -> None:
        """Refresh the OAuth access token."""
        request_time = utc_now()
        headers = self.oauth_request_headers or {}
        body = self.oauth_request_body

        # Choose json= vs data= based on Content-Type header
        content_type = headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            token_response = requests.post(self.auth_endpoint, json=body, headers=headers)
        else:
            token_response = requests.post(self.auth_endpoint, data=body, headers=headers)

        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            # Try to surface raw response text to aid debugging (may not be JSON)
            resp_text = None
            try:
                resp_text = token_response.text
            except Exception:
                resp_text = "<unable to read response body>"
            raise RuntimeError(
                f"Failed OAuth login (status={token_response.status_code}), response was: {resp_text}. {ex}"
            )

        # Parse JSON response, failing with a clear message if not JSON
        try:
            token_json = token_response.json()
        except Exception as ex:
            raise RuntimeError(
                f"OAuth refresh response is not valid JSON: {token_response.text}. {ex}"
            )
        if "access_token" not in token_json:
            raise RuntimeError(
                "OAuth refresh response did not include 'access_token'. "
                f"Response was: {token_json}"
            )

        self.access_token = token_json["access_token"]
        self.refresh_token = token_json.get("refresh_token", self.refresh_token)
        self.expires_in = token_json.get("expires_in", self._default_expiration)
        self.last_refreshed = request_time


class ProxyTikTokAuthenticator(TikTokAuthenticator, metaclass=SingletonMeta):
    """Authenticator for proxy-backed TikTok OAuth refresh."""

    def __init__(self, *args, proxy_auth: Optional[str] = None, **kwargs) -> None:
        self._proxy_auth = proxy_auth
        super().__init__(*args, **kwargs)

    @property
    def oauth_request_headers(self) -> dict:
        """Return headers for proxy refresh requests."""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self._proxy_auth:
            headers["Authorization"] = self._proxy_auth
        return headers

    @property
    def oauth_request_body(self) -> dict:
        """Return the proxy refresh request payload."""
        body: dict = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        # Include client credentials when available so they're sent in the body
        if getattr(self, "_client_id", None):
            body["client_key"] = self._client_id
        if getattr(self, "_client_secret", None):
            body["client_secret"] = self._client_secret
        return body
