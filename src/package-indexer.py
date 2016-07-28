#!/usr/bin/env python
"""
The main entry point for package-indexer. Running this file will
run a Tornado server which runs a periodic job and exposes an HTTP
interface. Running --help on this script will provide a full list of
available options.
"""
from datetime import datetime
import logging
import json

import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.options
import tornado.web

from apscheduler.schedulers.tornado import TornadoScheduler

from docker import Client
from docker.utils import kwargs_from_env

from whoosh.qparser import QueryParser
from whoosh.index import open_dir

from packagesearch.docker import DockerPackageIndexer
from packagesearch.api import SearchHandler

from requests.exceptions import ConnectionError

tornado.options.define("port", default=8888, help="run on the given port", type=int)
tornado.options.define("reload", default=False, help="Whether or not to reload when the source changes", type=bool)
tornado.options.define("interval", default=60, help="Interval for reindexing operations", type=int)


def index_container_packages(docker_client):
    """
    Scheduled job to be run periodically. Iterates over all running containers
    and stores the list of packages from the inventory in a search index
    """
    for container in docker_client.containers():
        indexer = DockerPackageIndexer(container, docker_client)
        indexer.index()

if __name__ == '__main__':
    tornado.log.enable_pretty_logging()
    tornado.options.parse_command_line()

    try:
        docker_client = Client(**kwargs_from_env(assert_hostname=False))
        docker_client.ping()
    except ConnectionError:
        logging.error("Unable to connect to Docker. Ensure Docker is running and environment variables are set.")
        exit(1)

    scheduler = TornadoScheduler()
    scheduler.add_job(lambda: index_container_packages(docker_client), 'interval', seconds=tornado.options.options.interval)
    scheduler.start()

    app = tornado.web.Application([
        (r"/", SearchHandler),
    ], debug=tornado.options.options.reload)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)

    try:
        tornado.ioloop.IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        pass
