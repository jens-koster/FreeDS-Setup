from freeds_setup.helpers.bao_client import BaoClient


class VaultUtil:
    """Client for reading plugin config from the Vault server."""

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        self.bao = BaoClient()


if __name__ == "__main__":
    pass
