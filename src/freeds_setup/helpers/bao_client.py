import os
import re
from pathlib import Path
import requests
import subprocess
from typing import Optional
from freeds_setup.helpers.root_config import root_config
from freeds_setup.helpers.flog import logger
import pyperclip


class BaoPaths:
    def __init__(self):
        self.mount = "config"
        addr = os.environ.get("FDS_VAULT_URI")
        if not addr:
            raise RuntimeError("FDS_VAULT_URI is not set")
        self.uri = addr.rstrip("/")

        self.v1_path = f"{self.uri}/v1"
        self.init_path = f"{self.v1_path}/sys/init"
        self.sys_mount_path = f"{self.v1_path}/sys/mounts/{self.mount}"
        self.data_path = f"{self.v1_path}/{self.mount}/data"
        self.metadata_path = f"{self.v1_path}/{self.mount}/metadata"
        self.token_path = f"{self.v1_path}/auth/token"

    def plugin_path(self, plugin: str) -> str:
        """Return the full vault path for a plugin's config (no trailing slash)."""
        return f"{self.data_path}/{plugin}"

    def plugin_meta_path(self, plugin: str) -> str:
        """Return the full vault path for a plugin's config (no trailing slash)."""
        return f"{self.metadata_path}/{plugin}"


class BaoClient:
    """Client for interacting with Bao (Vault) server.
    unseal method seems lost, but npone of that is used since I discvovered auto-unseal.
    """

    def __init__(self):
        self.root_token_file = root_config.known_location / ".bao_root"
        self.unseal_token_file = root_config.known_location / ".bao_unseal"

        self.root_token: Optional[str] = self._get_content(self.root_token_file)
        self.unseal_token: Optional[str] = self._get_content(self.unseal_token_file)

        self.timeout = 5
        self.session = requests.Session()
        self.paths = BaoPaths()

    def _get_content(self, file_path: Path) -> Optional[str]:
        if file_path.exists():
            with open(file_path, "r") as f:
                return f.read().strip()
        return None

    def header(self):
        """Return headers for vault requests."""
        h = {"Content-Type": "application/json"}
        if self.root_token:
            h["X-Vault-Token"] = self.root_token
        return h

    def read_plugin_vault_entry(self, plugin: str = None) -> dict:
        """Read plugin config from vault."""
        if not plugin:
            raise ValueError("plugin required")

        result = self.session.get(
            self.paths.plugin_path(plugin), headers=self.header(), timeout=self.timeout
        )
        if result.status_code == 404:
            return {}
        return result.json()

    def read_plugin_config(self, plugin: str = None) -> dict:
        """Read plugin config from vault."""
        data = self.read_plugin_vault_entry(plugin)
        return data.get("data", {}).get("data", {})

    def delete_plugin_config(self, plugin: str) -> None:
        """Hard delete plugin config from vault."""
        result = self.session.delete(
            self.paths.plugin_meta_path(plugin),
            headers=self.header(),
            timeout=self.timeout,
        )
        if result.status_code == 404:
            return
        result.raise_for_status()

    def write_plugin_config(self, plugin: str, config: dict) -> None:
        """Write plugin config to vault."""
        if plugin is None:
            raise ValueError("plugin required")
        existing = self.read_plugin_config(plugin)
        existing.update(config)
        data = {"data": existing}
        result = self.session.post(
            self.paths.plugin_path(plugin),
            headers=self.header(),
            json=data,
            timeout=self.timeout,
        )
        result.raise_for_status()

    def post_raw(self, path: str, body=None) -> dict:
        """POST to vault, return response json or raise."""
        result = self.session.post(
            path, headers=self.header(), json=body, timeout=self.timeout
        )
        if result.status_code == 204:
            return {}
        if not result.ok:
            raise RuntimeError(f"POST failed: {result.status_code} {result.text}")
        return result.json()

    def is_initialized(self) -> bool:
        """Check if vault is initialized."""
        r = self.session.get(
            self.paths.init_path, headers=self.header(), timeout=self.timeout
        )
        if not r.ok:
            raise RuntimeError(
                f"is_initialized failed, is vault running?: {r.status_code} {r.text}"
            )
        return bool(r.json().get("initialized"))

    def initialize(self):
        """Initialize vault and store tokens."""
        mounts = self.session.get(
            f"{self.paths.v1_path}/sys/mounts",
            headers=self.header(),
            timeout=self.timeout,
        )
        # Check if the 'config/' path is already in the mounts
        if f"{self.paths.mount}/" in mounts.json():
            logger.info(f"Vault mount already enabled: '{self.paths.mount}'")
            return

        self.post_raw(
            self.paths.sys_mount_path, {"type": "kv", "options": {"version": "2"}}
        )
        self.retrieve_tokens_from_logs()

    def retrieve_tokens_from_logs(self):
        """Retrieve tokens from vault logs and store them in the well-known location."""

        log_command = ["docker", "logs", "vault"]

        # Retrieve the logs from the Vault container
        logs = subprocess.check_output(log_command, stderr=subprocess.STDOUT, text=True)

        # Find the last occurrence of the Unseal Key and Root Token
        unseal_key_match = re.findall(r"Unseal Key: (\S+)", logs)
        root_token_match = re.findall(r"Root Token: (\S+)", logs)

        if not unseal_key_match or not root_token_match:
            raise RuntimeError("Unseal Key or Root Token not found in logs.")

        # Get the last occurrences
        self.unseal_key = unseal_key_match[-1]
        self.root_token = root_token_match[-1]

        # Store the tokens in the well-known location
        with open(self.root_token_file, "w") as f:
            f.write(self.root_token)
        with open(self.root_token_file, "w") as f:
            f.write(self.root_token)

    def close(self):
        self.session.close()


if __name__ == "__main__":
    bao = BaoClient()
    bao.retrieve_tokens_from_logs()
    print(f"Root Token: {bao.root_token}")
    pyperclip.copy(bao.root_token)
    # root_config.set_env()
    # bao = BaoClient()
    # logger.start("Initializing Vault for testing")
    # bao.retrieve_tokens_from_logs()
    # print(f"Root Token: {bao.root_token}")
    # bao.initialize()
    # logger.succeed()
    # logger.start("Writing plugin config")
    # bao.write_plugin_config("test_plugin", {"key1": "value"})
    # bao.write_plugin_config("test_plugin", {"key2": "value"})
    # logger.succeed()
    # import json

    # logger.start("Writing plugin config")
    # print(json.dumps(bao.read_plugin_config("test_plugin"), indent=4))
    # logger.succeed()

    # logger.start("Deleting plugin config")
    # #    bao.delete_plugin_config("test_plugin")
    # cfg = bao.read_plugin_config("test_plugin")
    # print(f"Config after deletion: {cfg}")
    # logger.succeed()
