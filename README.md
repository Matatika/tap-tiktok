# tap-tiktok

`tap-tiktok` is a Singer tap for TikTok.

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

## Configuration

### Accepted Config Options

- `access_token` - Access Token for the API as obtained via the authentication process described below.
- `advertiser_ids` - Advertiser IDs for your TikTok accounts.
- `start_date` - Start date as of when to start collecting metrics, e.g. `2022-01-01T00:00:00Z`.
- `lookback` - Number of days prior to the current date for which data should be refetched (default `0`).
- `include_deleted` - Include deleted-status entities when supported by the endpoint.
- `custom_basic_report` - A list of TikTok Basic Report definitions to expose as streams.

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
