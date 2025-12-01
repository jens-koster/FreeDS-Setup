# FreeDS-Setup

## Setup sequence
The initial operations require a specific order.

    freeds-setup init freeds
Clones a few hard coded repos to get things going
* the-free-data-stack
* FreeDS CLI and packages
* install freeds CLI in editable mode using pip
*

This includes the vault plugin, which needs separate initialisation before we can do anything else.

    freeds-setup init vault

Starts the vault plugin

Bootstraps the vault

    freeds-setup scan the-free-datastack

The repo is scanned for plugins and the plugins are imported.
I looked at terraform (OpenTofu) but it's overkill for our needs and custom functionality serves plugin development better.

    freeds-setup import <plugin folder>

The plugin config is processed, resources are setup and the resulting config is stored in the vault.


Most plugins provide config for all dependent plugins, like KAFKA_BOOTSTRAP_SERVERS, S3_URL, POSTGRES_URL these are used by all plugins.
A few resources are allocated on per plugin basis. Currently that's Postgres databses and S3 buckets.
Plugin config processing consists of:

Folder creation, there are a few hardcoded locations where a plugin can configure folders, which are created at import time.

plugin_files/<plugin name> misc stuff the plugin needs to work. Airflow dags and stuff like that
data/<plugin_name>: data files never touched by users

if a key named <something>_USER exists, a key named <something>_PASSWORD is created and filled with a random value.

if POSTGRES_DB key exists as config for a plugin we create the database and set all three.
* POSTGRES_DB*
* POSTGRES_USER
* POSTGRES_PASSWORD
-----------
if S3_BUCKET is defined we setup S3 credentials and a bucket, optionally the folders in that bucket.

* S3_BUCKET*
* S3_FOLDERS (no folder)
* S3_ACCESS_KEY
* S3_SECRET_KEY
-----------



