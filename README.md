# rss2mastodon

A quick python script for auto-posting an RSS feed to Mastodon. Created by AI6YR (Ben)

## Mastodon setup

In order to have this script work, you need the following:
1. A dedicated Mastodon user account created on a server.
2. An "access key" for your app created for that user account. (under yourserver/settings/applications)

## Script setup

All configuration for the script will ultimately reside in config.ini

* feed_url = URL of the RSS feed you want to query
* feed_name = What you want to name this feed
* feed_visibility = public, unlisted, etc. (per Mastodon.py)
* feed_tags = #your #additional #tags here will be appended to the toot

