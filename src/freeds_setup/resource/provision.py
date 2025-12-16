from freeds_setup.resource.resource_classes import resource_classes
from freeds_setup.helpers.flog import logger
from pathlib import Path
from freeds_setup.importing.plugin_config import PluginConfig
import typing




def provision_resource(self, type, description:str, name:str, params:dict)->dict[str:str]:
        """Create the requeated resource and provide the env variables to use it"""
        resource_class = resource_classes.get(type.lower())
        if not resource_class:
            raise ValueError(f"Unknown resource type: {type} found in plugin {self.name}")
        resource = resource_class(
            plugin_name=self.name,
            description=description,
            name=name,
            params=params
        )
        return resource.provision()



def provision_dependencies(plugin_config:PluginConfig)->dict[str, typing.Any]:
    """
    Provision the resources.
    """

    for name, config in plugin_config.dependencies.items():
        type = config.get("type")
        description = config.get("description", f"{type} {name} for plugin {plugin_config.name}")
        provision_resource(
            type= type,
            description=description,
            name=name,
            params=config.get("params", {}),
        )
