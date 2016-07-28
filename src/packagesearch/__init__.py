#!/usr/bin/env python
"""
Base classes for the package indexer implementation
"""
import logging
import os

from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.writing import AsyncWriter

class NoInventoryError(Exception):
    """
    Exception denoting that an inventory file was not found
    """
    pass

class PackageIndexer(object):
    """
    Base class for building indexers
    """
    def __init__(self):
        self.index_name = "packages"
        self.writer = self.get_writer()

    def index(self):
        """
        Store the list of packages from the implementation in the search index
        """
        logging.debug("Indexing packages for %s" % self.name)
        try:
            for package in self.packages():
                for version in package['versions']:
                    self.writer.update_document(
                        key=unicode("%s-%s-%s-%s" % (package['title'], version, package['provider'], self.id)),
                        package=unicode(package['title']),
                        version=unicode(version),
                        provider=unicode(package['provider']),
                        container_id=unicode(self.id),
                        container_name=unicode(self.name)
                    )
            self.writer.commit()
        except NoInventoryError:
            logging.debug("No inventory found for %s" % self.name)
            self.writer.cancel()

    def get_writer(self):
        """
        Return an object which can be used to write to the search index
        The object should deal with file locking from across threads and
        processes although writes will happen asyncronously
        """
        index = self.get_index()
        return AsyncWriter(index)

    def get_index(self):
        """
        Get or create a search index on disk, including creating the required
        directory and initialising the schema if required.
        """
        if not os.path.exists(self.index_name):
            os.mkdir(self.index_name)

        if exists_in(self.index_name):
            index = open_dir(self.index_name)
        else:
            schema = Schema(
                key=ID(stored=True, unique=True),
                package=TEXT(stored=True),
                container_id=TEXT(stored=True),
                container_name=TEXT(stored=True),
                version=TEXT(stored=True),
                provider=TEXT(stored=True)
            )
            index = create_in(self.index_name, schema)
        return index
