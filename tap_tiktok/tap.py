"""TikTok tap class."""

import datetime
from typing import Any, Dict, List, Optional

import requests

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_tiktok.streams import (
    AdAccountsStream,
    CampaignsStream,
    AdGroupsStream,
    AdsStream,
    AdsAttributeMetricsStream,
    AdsBasicDataMetricsByDayStream,
    AdsVideoPlayMetricsByDayStream,
    AdsEngagementMetricsByDayStream,
    AdsAttributionMetricsByDayStream,
    AdsPageEventMetricsByDayStream,
    AdsInAppEventMetricsByDayStream,
    AdsBasicDataMetricsByHourStream,
    AdGroupBasicDataMetricsByHourStream,
    CampaignsAttributeMetricsStream,
    CampaignsBasicDataMetricsByDayStream,
    CampaignsVideoPlayMetricsByDayStream,
    CampaignsEngagementMetricsByDayStream,
    CampaignsAttributionMetricsByDayStream,
    CampaignsPageEventMetricsByDayStream,
    CampaignsInAppEventMetricsByDayStream,
    CampaignsBasicDataMetricsByHourStream,
)
STREAM_TYPES = [
    AdAccountsStream,
    CampaignsStream,
    AdGroupsStream,
    AdsStream,
    AdsAttributeMetricsStream,
    AdsBasicDataMetricsByDayStream,
    AdsBasicDataMetricsByHourStream,
    AdsVideoPlayMetricsByDayStream,
    AdsEngagementMetricsByDayStream,
    AdsAttributionMetricsByDayStream,
    AdsPageEventMetricsByDayStream,
    AdsInAppEventMetricsByDayStream,
    AdGroupBasicDataMetricsByHourStream,
    CampaignsAttributeMetricsStream,
    CampaignsBasicDataMetricsByDayStream,
    CampaignsVideoPlayMetricsByDayStream,
    CampaignsEngagementMetricsByDayStream,
    CampaignsAttributionMetricsByDayStream,
    CampaignsPageEventMetricsByDayStream,
    CampaignsInAppEventMetricsByDayStream,
    CampaignsBasicDataMetricsByHourStream,
]


class TapTikTok(Tap):
    """TikTok tap class."""
    name = "tap-tiktok"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "access_token",
            th.StringType,
            description="Static TikTok API access token. Optional when OAuth settings are provided."
        ),
        th.Property(
            "client_key",
            th.StringType,
            description="TikTok OAuth client key used to exchange or refresh access tokens."
        ),
        th.Property(
            "client_secret",
            th.StringType,
            secret=True,
            description="TikTok OAuth client secret used to exchange or refresh access tokens."
        ),
        th.Property(
            "auth_code",
            th.StringType,
            secret=True,
            description="OAuth authorization code used for the initial token exchange."
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            secret=True,
            description="OAuth refresh token used to renew the access token."
        ),
        th.Property(
            "redirect_uri",
            th.StringType,
            description="OAuth redirect URI registered with TikTok. Required when exchanging an auth code."
        ),
        th.Property(
            "oauth_access_token_url",
            th.StringType,
            default="https://open.tiktokapis.com/v2/oauth/token/",
            description="OAuth endpoint used to exchange auth codes and refresh tokens."
        ),
        th.Property(
            "advertiser_ids",
            th.ArrayType(th.StringType),
            required=True,
            description="List of advertiser ids"
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync"
        ),
        th.Property(
            "include_deleted",
            th.BooleanType,
            default=True,
            description="If true then deleted status entities will also be returned"
        ),
        th.Property(
            "lookback",
            th.IntegerType,
            default=0,
            description="The number of days of data to reload from the current date (ignored if current state of the extractor has a start date earlier than the current date minus number of lookback days)"
        )
    ).to_dict()

    _oauth_token_bundle: Optional[Dict[str, Any]] = None
    _oauth_refresh_token: Optional[str] = None

    def get_access_token(self) -> str:
        """Return a usable access token from either static config or OAuth."""
        if self._oauth_token_bundle:
            if not self._token_expired(self._oauth_token_bundle):
                return str(self._oauth_token_bundle["access_token"])

            token_bundle = self._refresh_access_token() if self._get_refresh_token() else self._exchange_auth_code()
            self._oauth_token_bundle = token_bundle
            refresh_token = token_bundle.get("refresh_token")
            if refresh_token:
                self._oauth_refresh_token = str(refresh_token)
            return str(token_bundle["access_token"])

        access_token = self.config.get("access_token")
        if access_token:
            return str(access_token)

        if not self._has_oauth_config():
            raise ValueError(
                "Missing authentication configuration. Provide `access_token` or TikTok OAuth settings."
            )

        token_bundle = self._refresh_access_token() if self._get_refresh_token() else self._exchange_auth_code()
        self._oauth_token_bundle = token_bundle

        refresh_token = token_bundle.get("refresh_token")
        if refresh_token:
            self._oauth_refresh_token = str(refresh_token)

        return str(token_bundle["access_token"])

    def _has_oauth_config(self) -> bool:
        return bool(self.config.get("client_key") and self.config.get("client_secret"))

    @staticmethod
    def _token_expired(token_bundle: Dict[str, Any]) -> bool:
        expires_at = token_bundle.get("expires_at")
        if not expires_at:
            return True
        return datetime.datetime.now(datetime.timezone.utc) >= expires_at

    def _exchange_auth_code(self) -> Dict[str, Any]:
        auth_code = self.config.get("auth_code")
        redirect_uri = self.config.get("redirect_uri")
        if not auth_code or not redirect_uri:
            raise ValueError(
                "OAuth auth code flow requires both `auth_code` and `redirect_uri`."
            )

        payload = {
            "client_key": self.config["client_key"],
            "client_secret": self.config["client_secret"],
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        return self._request_oauth_token(payload)

    def _refresh_access_token(self) -> Dict[str, Any]:
        refresh_token = self._get_refresh_token()
        if not refresh_token:
            raise ValueError("OAuth refresh flow requires `refresh_token`.")

        payload = {
            "client_key": self.config["client_key"],
            "client_secret": self.config["client_secret"],
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        return self._request_oauth_token(payload)

    def _get_refresh_token(self) -> Optional[str]:
        return self._oauth_refresh_token or self.config.get("refresh_token")

    def _request_oauth_token(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            self.config["oauth_access_token_url"],
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=60,
        )
        response.raise_for_status()
        token_bundle = response.json()

        access_token = token_bundle.get("access_token")
        if not access_token:
            raise ValueError(f"OAuth token response did not include `access_token`: {token_bundle}")

        expires_in = token_bundle.get("expires_in")
        if expires_in is not None:
            token_bundle["expires_at"] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                seconds=max(int(expires_in) - 300, 0)
            )

        return token_bundle

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
