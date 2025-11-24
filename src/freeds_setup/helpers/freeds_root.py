from pathlib import Path

def freeds_file_path() -> Path:
    return Path.home() / ".freeds"

def get_freeds_root()->Path:
    with open(freeds_file_path(), "r") as f:
        return Path(f.read())

def set_freeds_root(freeds_root_path:Path)->Path:
    with open(freeds_file_path(), "r") as f:
        f.write(str(freeds_root_path))

def vault_file_path() -> Path:
    return Path.home() / ".vault"

def get_vault_uri()->str:
    with open(freeds_file_path(), "r") as f:
        return f.read()

def set_vault_uri(vault_uri)->str:
    with open(vault_file_path(), "r") as f:
        f.write(vault_uri)
