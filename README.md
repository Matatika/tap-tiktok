# tap-tiktok

`tap-tiktok` is a Singer tap for TikTok Ads.

It extracts advertiser, campaign, ad group, ad, and reporting data from the
TikTok Marketing API so it can be loaded into a warehouse or downstream
analytics system.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Current Status

This tap currently supports the core TikTok entity streams plus report streams, and
it also supports config-driven custom basic reports through `custom_basic_report`.

At the moment:

- `custom_basic_report` is a list of report definitions, not a single object.
- Each custom basic report becomes its own Singer stream.
- Custom basic reports run in 1-day request windows.
- `custom_reports` is not supported.

## Installation

```bash
pipx install git+https://github.com/gthsheep/tap-tiktok
```

## Setup Guide

1. Create a TikTok developer app with access to the TikTok Marketing API.
2. Grant the app the scopes needed for account, campaign, ad group, ad, and
   reporting access.
3. Generate an `access_token` using the TikTok authentication flow.
4. Identify the TikTok `advertiser_ids` you want the tap to sync.
5. Create a JSON config file with the required settings.
6. Run discovery first to confirm the connection and inspect the catalog.

Example:

```bash
tap-tiktok --config .secrets/config.json --discover
```

## Configuration

### Accepted Config Options

- `access_token` - Bearer token used to authenticate requests to the TikTok
  Marketing API.
- `advertiser_ids` - List of TikTok advertiser account IDs to sync.
- `start_date` - Earliest timestamp to begin extracting time-based data, for
  example `2022-01-01T00:00:00Z`.
- `lookback` - Number of trailing days to refetch on each run to catch late
  arriving changes. Default: `0`.
- `include_deleted` - When `true`, includes deleted entities for endpoints that
  support deleted-status records.
- `custom_basic_report` - List of custom TikTok Basic Report definitions. Each
  object creates its own Singer stream.

Example custom Basic Report config:

```json
{
  "access_token": "...",
  "advertiser_ids": ["1234567890"],
  "start_date": "2026-01-01T00:00:00Z",
  "custom_basic_report": [
    {
      "name": "campaign_country_spend_by_day",
      "service_type": "AUCTION",
      "report_type": "BASIC",
      "data_level": "AUCTION_CAMPAIGN",
      "dimensions": ["campaign_id", "country_code", "stat_time_day"],
      "metrics": ["spend"],
      "primary_keys": ["campaign_id", "country_code", "stat_time_day"],
      "replication_key": "stat_time_day"
    }
  ]
}
```

Only `dimensions` and `metrics` are required for each report definition. Useful
optional fields are `name`, `data_level`, `primary_keys`, and `replication_key`.

Custom report notes:

- `custom_basic_report` must be passed as an array of objects.
- `data_level: AUCTION_CAMPAIGN` is the right choice when using `campaign_id`.
- The tap currently forces custom basic reports to run with 1-day steps.
- Multiple custom reports can be added by placing multiple objects in the array.


A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-tiktok --about
```

### Setting Reference

- `access_token`: Required. TikTok API access token for the authenticated app.
- `advertiser_ids`: Required. One or more advertiser accounts to query.
- `start_date`: Optional. Lower bound for incremental reporting syncs.
- `lookback`: Optional. Re-sync window in days for recent data corrections.
- `include_deleted`: Optional. Controls whether deleted entities are included
  where the endpoint supports them.
- `custom_basic_report`: Optional. Advanced configuration for additional report
  streams built from TikTok's integrated reporting endpoint.

`custom_basic_report` objects support these fields:

- `name`: Stream name to expose in Singer.
- `service_type`: TikTok service type, such as `AUCTION`.
- `report_type`: TikTok report type, such as `BASIC`.
- `data_level`: Reporting grain, such as campaign-level reporting.
- `dimensions`: Required list of report dimensions.
- `metrics`: Required list of report metrics.
- `primary_keys`: Fields to use as the Singer primary key.
- `replication_key`: Field to use for incremental replication.
- `status_field`: Status column used when filtering deleted rows.
- `include_status_filter`: Whether to apply status-based filtering.
- `step_num_days`: Request window size in days.
- `page_size`: Page size for report pagination.
- `filtering`: Additional TikTok report filters.

### Source Authentication and Authorization

To obtain an `access_token` you should follow the App creation steps described in the TikTok documentation,
[here](https://ads.tiktok.com/marketing_api/docs?id=1701890912382977), then the Authentication documentation, 
[here](https://ads.tiktok.com/marketing_api/docs?id=1701890914536450).  
As for scopes for your App, metrics streams are fed by the Reporting permission set, then data for Campaign, Ad Group,
and Ads require their respective read permissions.  

Ad Account Management -> Read
Ads Management -> Read ads/ adgroups/ campaigns
Reporting -> All
Tiktok Business -> All

## Streams

The tap exposes these built-in streams:

- `ad_accounts`: Advertiser account metadata such as account name, status,
  timezone, currency, and contact details.
- `campaigns`: Campaign entities and campaign-level configuration details.
- `ad_groups`: Ad group entities including targeting, bidding, budgeting, and
  scheduling attributes.
- `ads`: Individual ad entities and ad-level creative metadata.
- `ads_attribute_metrics`: Daily ad-level attribute reporting.
- `ads_basic_data_metrics_by_day`: Daily ad-level delivery and spend metrics.
- `ads_basic_data_metrics_by_hour`: Hourly ad-level delivery and spend metrics.
- `ads_video_play_metrics_by_day`: Daily ad-level video play metrics.
- `ads_engagement_metrics_by_day`: Daily ad-level engagement metrics.
- `ads_attribution_metrics_by_day`: Daily ad-level attributed conversion metrics.
- `ads_page_event_metrics_by_day`: Daily ad-level page event metrics.
- `ads_in_app_event_metrics_by_day`: Daily ad-level in-app event metrics.
- `ad_group_basic_data_metrics_by_hour`: Hourly ad group-level delivery and
  spend metrics.
- `campaigns_attribute_metrics`: Daily campaign-level attribute reporting.
- `campaigns_basic_data_metrics_by_day`: Daily campaign-level delivery and
  spend metrics.
- `campaigns_video_play_metrics_by_day`: Daily campaign-level video play
  metrics.
- `campaigns_engagement_metrics_by_day`: Daily campaign-level engagement
  metrics.
- `campaigns_attribution_metrics_by_day`: Daily campaign-level attributed
  conversion metrics.
- `campaigns_page_event_metrics_by_day`: Daily campaign-level page event
  metrics.
- `campaigns_in_app_event_metrics_by_day`: Daily campaign-level in-app event
  metrics.
- `campaigns_basic_data_metrics_by_hour`: Hourly campaign-level delivery and
  spend metrics.
- `custom_basic_report` streams: Optional user-defined reporting streams created
  from each object in `custom_basic_report`.

## Stream Fields

The list below provides a practical summary of the main fields exposed by each
stream family. For the complete schema for your configuration, run
`tap-tiktok --config CONFIG --discover`.

### Entity Streams

- `ad_accounts`: `advertiser_id` (account ID), `name` (account name),
  `company` (business name), `currency` (billing currency), `timezone`
  (account timezone), `status` (account status).
- `campaigns`: `campaign_id` (campaign ID), `campaign_name` (campaign name),
  `advertiser_id` (parent advertiser), `objective` (campaign objective),
  `budget` (configured budget), `status` (campaign status), `modify_time`
  (last update timestamp).
- `ad_groups`: `adgroup_id` (ad group ID), `campaign_id` (parent campaign),
  `adgroup_name` (ad group name), `budget` (budget amount), `bid` (bid value),
  `schedule_start_time` (start time), `schedule_end_time` (end time),
  `modify_time` (last update timestamp).
- `ads`: `ad_id` (ad ID), `adgroup_id` (parent ad group), `campaign_id`
  (parent campaign), `ad_name` (ad name), `creative_type` (creative type),
  `image_ids` and `video_id` (creative assets), `status` (ad status),
  `modify_time` (last update timestamp).

### Reporting Streams

- Common identifier fields: `advertiser_id`, one of `campaign_id`,
  `adgroup_id`, or `ad_id`, plus a time grain such as `stat_time_day` or
  `stat_time_hour`.
- Common delivery fields: `spend`, `impressions`, `clicks`, `cpc`, `cpm`,
  `ctr`, `reach`.
- Common video fields: video play counts, watch-through rates, and completion
  metrics.
- Common engagement fields: engagement actions such as likes, comments,
  shares, and follows where available from TikTok reporting.
- Common attribution and event fields: conversion counts, page events,
  in-app events, and other attributed outcomes depending on the report stream.

### Custom Basic Report Streams

- Fields depend on the `dimensions` and `metrics` supplied in each
  `custom_basic_report` object.
- Typical dimensions include IDs and time grains such as `campaign_id`,
  `adgroup_id`, `ad_id`, `country_code`, and `stat_time_day`.
- Typical metrics include measures such as `spend`, `impressions`, `clicks`,
  and conversion-related values.

## Usage

You can easily run `tap-tiktok` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-tiktok --version
tap-tiktok --help
tap-tiktok --config CONFIG --discover > ./catalog.json
```

To debug with the local JSON config file:

```bash
tap-tiktok --config .secrets/config.json --discover
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_tiktok/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-tiktok` CLI interface directly using `poetry run`:

```bash
poetry run tap-tiktok --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-tiktok
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-tiktok --version
# OR run a test `elt` pipeline:
meltano run tap-tiktok target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
