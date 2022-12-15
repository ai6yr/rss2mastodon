# rss2mastodon

A quick set of python scripts for auto-posting an RSS or Atom feed to Mastodon. Created by AI6YR (Ben)

## Mastodon setup

In order to have this script work, you need the following:
1. A dedicated Mastodon user account created on a server.
2. An "access key" for your app created for that user account. (under yourserver/settings/applications)

## Script setup

All configuration for the script will ultimately reside in config.ini

### Mastodon configuration
* access_token = Mastodon access token
* app_url = Mastodon server
* max_image_size = max image size accepted by server

### Feed configuration
* feed_url = URL of the RSS feed you want to query
* feed_name = What you want to name this feed
* feed_visibility = public, unlisted, etc. (per Mastodon.py)
* feed_tags = #your #additional #tags here will be appended to the toot
* feed_delay = delay in seconds between checking on the RSS/Atom feed

