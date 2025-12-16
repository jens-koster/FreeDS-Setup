import os
import requests
from pathlib import Path
from typing import Optional

class VaultUtil:
    """Client for reading plugin config from the Vault server.
    """
    def __init__(self, plugin_name: str):
        self.env_prefix = "FDS"
        self.name = plugin_name
        self.uri = os.environ.get("FDS_VAULT_URI")
        if not self.uri:
            raise RuntimeError("FDS_VAULT_URI is not set")

        self.token = self.get_plugin_env('VAULT_TOKEN')
        self.session = requests.Session()

    def header(self):
        """Return headers for vault requests."""
        h = {"Content-Type": "application/json"}
        if self.root_token:
            h["X-Vault-Token"] = self.root_token
        return h


    def env_name(self, key:str)->str:
        """Format an env variable name fomr plugin and value name (key)."""
        return f"{self.env_prefix}_{self.name.upper()}_{key.upper()}"

    def get_env(self, env_name:str)->Optional[str]:
            """Get an env variable, raise if not set."""
            env_value = os.environ.get(env_name)
            if not env_value:
                raise RuntimeError(f"Env variable not set: {env_name}")
            return env_value

    def get_plugin_env(self, key:str)->Optional[str]:
        """Get an env variable for this plugin, raise if not set."""
        return self.get_env(self.env_name(key))

    def sen_envs(self, envs:dict)->None:
        """read all env config from vault and set envs for this plugin."""
        path = self.paths.plugin_path(self.name)
        data = {"data": envs}
        result = self.session.post(
            path,
            headers=self.header(),
            json=data,
            timeout=5)
        result.raise_for_status()

    def vault_path(self)->str:
        v1_path = f"{self.uri}/v1"
        path =f"{v1_path}/config/data/{self.name}"
        return path


    def read_vault_entry(self)->dict:
        """Read plugin config from vault."""
        result = self.session.get(
            self.vault_path(),
            headers=self.header(),
            timeout=self.timeout)
        if result.status_code == 404:
            return {}
        return result.json()

    def read_plugin_config(self, plugin: str = None)->dict:
        """Read plugin config from vault."""
        data = self.read_plugin_vault_entry(plugin)
        return data.get("data", {}).get("data", {})


    def post_raw(self, path: str, body=None)->dict:
        """POST to vault, return response json or raise."""
        result = self.session.post(path, headers=self.header(), json=body, timeout=self.timeout)
        if result.status_code == 204:
            return {}
        if not result.ok:
            raise RuntimeError(f"POST failed: {result.status_code} {result.text}")
        return result.json()

    def close(self):
        self.session.close()

if __name__ == '__main__':
    pass