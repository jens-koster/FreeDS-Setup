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



The repo is scanned for plugins and the plugin info and config are stored in the vault.
