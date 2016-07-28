#!/usr/bin/env python
import logging
import json

import tornado.web

from whoosh.qparser import QueryParser
from whoosh.index import open_dir


class SearchHandler(tornado.web.RequestHandler):
    """
    Search API for querying package resoures from the Whoosh index
    """
    def get(self):
        """
        Return a JSON document which comprises an array of hashes, each
        hash representing a package version installed on a container.
        Takes a query string argument of 'q' for tailoring searches.
        """
        index = open_dir("packages")
        query = self.get_argument("q", default="*")
        logging.debug("query for %s" % query)
        with index.searcher() as searcher:
            query = QueryParser("package", index.schema).parse(query)
            results = searcher.search(query, limit=100)
            output = []
            for result in results:
                output.append({
                    'package': result['package'],
                    'version': result['version'],
                    'provider': result['provider'],
                    'container_id': result['container_id'],
                    'container_name': result['container_name']
                })
            self.write(json.dumps(output))
