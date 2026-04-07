"""TikTok tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_tiktok.streams import (
    UserInfoStream,
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
    UserInfoStream,
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
            description="Access Token for Tiktok API authentication. Not required if using OAuth configuration.",
        ),
        th.Property(
            "authorization_url",
            th.StringType,
            description="OAuth authorization endpoint.",
        ),
        th.Property(
            "scope",
            th.StringType,
            description="OAuth scopes requested for TikTok API access.",
        ),
        th.Property(
            "client_key",
            th.StringType,
            description="OAuth client key used to refresh access tokens.",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            description="OAuth client secret used to refresh access tokens.",
        ),
        th.Property(
            "auth_code",
            th.StringType,
            description="One-time authorization code for the initial OAuth exchange.",
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            description="OAuth refresh token used to renew the access token.",
        ),
        th.Property(
            "redirect_uri",
            th.StringType,
            description="Redirect URI registered for the OAuth client.",
        ),
        th.Property(
            "oauth_access_token_url",
            th.StringType,
            default="https://open.tiktokapis.com/v2/oauth/token/",
            description="OAuth endpoint used to refresh access tokens.",
        ),
        th.Property(
            "oauth_credentials",
            th.ObjectType(
                th.Property(
                    "authorization_url",
                    th.StringType,
                    default="https://www.tiktok.com/v2/auth/authorize/",
                    description="OAuth identity provider authorization endpoint used to create and refresh tokens.",
                ),
                th.Property(
                    "scope",
                    th.StringType,
                    default="user.info.basic ad.read",
                    description="OAuth scopes requested for TikTok API access.",
                ),
                th.Property(
                    "access_token",
                    th.StringType,
                    description="Token used to authenticate and authorize API requests.",
                ),
                th.Property(
                    "client_id",
                    th.StringType,
                    description="OAuth client ID used to refresh access tokens.",
                ),
                th.Property(
                    "client_secret",
                    th.StringType,
                    description="OAuth client secret used to refresh access tokens.",
                ),
                th.Property(
                    "refresh_token",
                    th.StringType,
                    description="OAuth refresh token used to renew the access token.",
                ),
                th.Property(
                    "refresh_proxy_url",
                    th.StringType,
                    description="Optional proxy URL used to refresh the access token.",
                ),
                th.Property(
                    "refresh_proxy_url_auth",
                    th.StringType,
                    description="Optional Authorization header value for refresh proxy requests.",
                ),
                th.Property(
                    "token_url",
                    th.StringType,
                    default="https://open.tiktokapis.com/v2/oauth/token/",
                    description="OAuth endpoint used to refresh access tokens.",
                ),
            ),
            description="TikTok OAuth credentials and token configuration.",
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

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
