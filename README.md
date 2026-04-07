# tap-tiktok

`tap-tiktok` is a Singer tap for TikTok.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

```bash
pipx install git+https://github.com/gthsheep/tap-tiktok
```

## Configuration

### Accepted Config Options

`access_token` - Static access token for the API. If you use OAuth settings below, this can be omitted.  
`client_key` - TikTok OAuth client key.  
`client_secret` - TikTok OAuth client secret.  
`auth_code` - One-time OAuth authorization code for the initial token exchange.  
`refresh_token` - OAuth refresh token for subsequent runs.  
`redirect_uri` - Redirect URI registered in your TikTok app. Required with `auth_code`.  
`oauth_access_token_url` - Token endpoint, defaulting to `https://open.tiktokapis.com/v2/oauth/token/`.  
`advertiser_id` - Advertiser ID for your TikTok account.  
`start_date` - Start date as of when to start collecting metrics, e.g. `2022-01-01T00:00:00Z`  
`lookback` - Number of days prior to the current date for which data should be refetched (default `0`)

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-tiktok --about
```

### Source Authentication and Authorization

To obtain an `access_token` you can either paste a static token into `access_token`, or configure OAuth and let the tap exchange or refresh tokens at runtime.
The tap supports:

1. `auth_code` + `client_key` + `client_secret` + `redirect_uri` for the initial OAuth token exchange.
2. `refresh_token` + `client_key` + `client_secret` for later refreshes.

The default token endpoint is TikTok OAuth v2 at `https://open.tiktokapis.com/v2/oauth/token/`, which expects
`application/x-www-form-urlencoded` requests for both `authorization_code` and `refresh_token` grants. After the first
successful exchange, you should persist the returned `refresh_token` in your Meltano secrets or environment so future
runs can refresh without reusing the one-time `auth_code`.

TikTok app creation and scope setup still need to follow TikTok's developer and business documentation for the
permissions your streams require.  
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
meltano elt tap-tiktok target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
