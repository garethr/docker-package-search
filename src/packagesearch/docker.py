#!/usr/bin/env python
import json

from packagesearch import PackageIndexer, NoInventoryError

class DockerPackageIndexer(PackageIndexer):
    """
    Package Indexer specific to the Docker API.
    """
    def __init__(self, container, docker_client):
        self.container = container
        self.id = container['Id']
        self.name = container['Names'][0].strip('/')
        self.docker_client = docker_client
        super(DockerPackageIndexer, self).__init__()

    def packages(self):
        """
        List the packages from the inventory file, or raise a NoInventoryError
        if no inventory file is found
        """
        executor = self.docker_client.exec_create(
            container = self.container['Id'],
            cmd = "cat /inventory.json",
        )
        try:
            data = json.loads(self.docker_client.exec_start(exec_id=executor['Id']))
        except ValueError:
            raise NoInventoryError
        packages = [x for x in data['resources'] if x['resource'] == 'package']
        return packages


