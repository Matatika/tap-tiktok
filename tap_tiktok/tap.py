"""TikTok tap class."""

from typing import List

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
    CustomBasicReportStream,
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
            required=True,
            description="The token to authenticate against the API service"
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
        ),
        th.Property(
            "custom_basic_report",
            th.ObjectType(
                th.Property("name", th.StringType),
                th.Property("service_type", th.StringType),
                th.Property("report_type", th.StringType),
                th.Property("data_level", th.StringType),
                th.Property("dimensions", th.ArrayType(th.StringType), required=True),
                th.Property("metrics", th.ArrayType(th.StringType), required=True),
                th.Property("primary_keys", th.ArrayType(th.StringType)),
                th.Property("replication_key", th.StringType),
                th.Property("status_field", th.StringType),
                th.Property("include_status_filter", th.BooleanType),
                th.Property("step_num_days", th.IntegerType),
                th.Property("page_size", th.IntegerType),
                th.Property("filtering", th.ArrayType(th.ObjectType())),
            ),
            description="Single TikTok basic report definition for /report/integrated/get/."
        )
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        streams = [stream_class(tap=self) for stream_class in STREAM_TYPES]

        if self.config.get("custom_basic_report"):
            streams.append(CustomBasicReportStream(tap=self, report_config=self.config["custom_basic_report"]))

        return streams
