"""REST client handling, including TikTokStream base class."""

from functools import cached_property
import json
import requests
from typing import Any, Dict, Optional

from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

from tap_tiktok.auth import ProxyTikTokAuthenticator, TikTokAuthenticator

DATE_FORMAT = "%Y-%m-%d"


class TikTokStream(RESTStream):

    url_base = "https://business-api.tiktok.com/open_api/v1.3"

    records_jsonpath = "$.data.list[*]"

    @cached_property
    def authenticator(self):
        """Return the authenticator for TikTok API requests."""
        oauth_credentials = self.config.get("oauth_credentials") or {}

        client_id = oauth_credentials.get("client_id") or self.config.get("client_key")
        client_secret = oauth_credentials.get("client_secret") or self.config.get("client_secret")
        refresh_token = oauth_credentials.get("refresh_token") or self.config.get("refresh_token")
        refresh_proxy_url = oauth_credentials.get("refresh_proxy_url") or self.config.get("refresh_proxy_url")
        token_url = (
            oauth_credentials.get("token_url")
            or self.config.get("oauth_access_token_url")
            or "https://open.tiktokapis.com/v2/oauth/token/"
        )

        if client_id and client_secret and refresh_token:
            return TikTokAuthenticator(
                stream=self,
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=refresh_token,
                auth_endpoint=token_url,
            )

        if refresh_proxy_url and refresh_token:
            return ProxyTikTokAuthenticator(
                stream=self,
                refresh_token=refresh_token,
                proxy_auth=oauth_credentials.get("refresh_proxy_url_auth") or self.config.get("refresh_proxy_url_auth"),
                auth_endpoint=refresh_proxy_url,
            )

        access_token = oauth_credentials.get("access_token") or self.config.get("access_token")
        if access_token:
            return APIKeyAuthenticator.create_for_stream(
                self,
                key="Access-Token",
                value=access_token,
                location="header",
            )

        raise ValueError(
            "Insufficient config to establish an authenticator. "
            "Provide `access_token`, `oauth_credentials.access_token`, "
            "`oauth_credentials.client_id` + `oauth_credentials.client_secret` + `oauth_credentials.refresh_token`, "
            "or `oauth_credentials.refresh_proxy_url` + `oauth_credentials.refresh_token`."
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        headers["Content-Type"] = "application/json"
        return headers

    @staticmethod
    def _get_page_info(json_path, json):
        page_matches = extract_jsonpath(json_path, json)
        return next(iter(page_matches), None)

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        current_page = self._get_page_info("$.data.page_info.page", response.json()) or 0
        total_pages = self._get_page_info("$.data.page_info.total_page", response.json()) or 0
        if current_page < total_pages:
            return current_page + 1
        return None

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        advertiser_id = context.get("advertiser_id") if context else None
        if not advertiser_id:
            raise ValueError("Missing advertiser_id in context.")
        
        params: dict = {"advertiser_id": advertiser_id}
        if next_page_token:
            params["page"] = next_page_token
        params["filtering"] = json.dumps({"primary_status": "STATUS_ALL" if self.config.get("include_deleted") else "STATUS_NOT_DELETE"})
        params["page_size"] = 1000
        return params


class TikTokReportsStream(TikTokStream):

    url_base = "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/"

    records_jsonpath = "$.data.list[*]"
    next_page_token_jsonpath = "$.page_info.page"

    def post_process(self, row: dict, context: Optional[dict] = None) -> Optional[dict]:
        return {**row['dimensions'], **row['metrics']}

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        page_matches = extract_jsonpath("$.data.page_info.page", response.json())
        page_match = next(iter(page_matches), None)
        current_page = page_match
        total_pages_matches = extract_jsonpath("$.data.page_info.total_page", response.json())
        total_pages_match = next(iter(total_pages_matches), None)
        total_pages = total_pages_match
        if current_page < total_pages:
            return current_page + 1
        return None
