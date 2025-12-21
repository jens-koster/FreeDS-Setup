"""Deployments are actions that sets up the environment for the plugin to run.

Examples:
    copy the airflow dags from the repo to the airflow dags folder
    copy notebooks to the plugin bucket in s3 for use in the jupyter plugin
    execute a folder of sql files on the plugin postgres database
"""

from abc import ABC, abstractmethod


class Deployment(ABC):
    """
    Base class for resources (which include dependencies)
    """

    def __init__(self, plugin_name, description, name, params: dict = None):
        self.plugin_name = plugin_name
        self.description = description
        self.name = name
        self.params = params or {}

    @abstractmethod
    def deploy(self) -> dict[str:str]:
        """Provision the resource and return a dict of env values for the plugin to use."""
        pass


class AirflowDags(Deployment):
    """Copy dags from a folder in the plugin repo to the airflow dags folder"""

    pass


class Notebooks(Deployment):
    """Copy notebooks to the plugin s3 bucket for running in jupyter plugin"""

    pass


class Sql(Deployment):
    """Execute a folder of sql files on the plugin postgres database"""

    pass


class FileCopy(Deployment):
    """Copy files from the plugin repo to the plugin data folder"""

    pass


deployment_classes = {
    "AirflowDags": AirflowDags,
}
