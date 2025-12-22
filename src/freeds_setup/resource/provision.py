from freeds_setup.resource.resource_classes import resource_classes
from freeds_setup.helpers.flog import logger
from freeds_setup.importing.plugin_config import PluginConfig


def set_if_not_exists(target: dict, name: str, value: dict) -> None:
    if name in target:
        logger.info(f"Resource {name} already set")
        return
    target[name] = value


def process_dependencies(plugin_config: PluginConfig) -> None:

    plugin = plugin_config.name
    logger.info(
        f"processing {len(plugin_config.dependencies)} dependencies for plugin {plugin}"
    )
    for dependency, _ in plugin_config.dependencies.items():
        logger.info(f"Dependency {dependency}")
        if dependency == "postgres":
            resource = {
                "type": "PostgresUser",
                "description": "Default user account + password in postgres for {plugin}",
            }
            set_if_not_exists(
                target=plugin_config.resources, name=f"{plugin}_pguser", value=resource
            )
            resource = {
                "type": "PostgresDatabase",
                "description": "Default postgres database for {plugin}",
            }
            set_if_not_exists(
                target=plugin_config.resources, name=f"{plugin}_pgdb", value=resource
            )


def provision_all(plugin_config: PluginConfig) -> None:
    """Provision resources and update config."""
    plugin = plugin_config.name
    process_dependencies(plugin_config)
    for name, resource in plugin_config.resources.items():
        type = resource["type"]
        description = resource["description"]
        params = resource.get("params", {})
        resource_class = resource_classes.get(type.lower())
        if not resource_class:
            raise ValueError(f"Unknown resource type: {type} found in plugin {plugin}")
        resource = resource_class(
            plugin_name=plugin, name=name, description=description, params=params
        )
        resource.provision()
        plugin_config.config.update(resource.config)
