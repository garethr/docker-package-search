# Docker Package Search

[puppet-inventory](https://github.com/puppetlabs/puppetlabs-inventory) provides a simple way of inventorying a host, and by
using that as part of a container build process we can generate a
list of resources (like packages, users and groups) at build-time and
store that as part of the resulting image.

Package Indexer is a simple example of what we can do with that
inventory. The indexer process will check for running containers every
60 seconds (by default), and for each running container it will check for the
`inventory.json` file using the Docker exec API. If found it will store the
results in a local search index. The running process also exposes a simple
HTTP search interface for querying the index.

You can use this to solve a number of management problems, but a common
example might be:

> Tell me which of my containers are running a specific version of
> OpenSSH

Note that because Puppet is cross-platform, `puppet-inventory` is too.
Which means this gives you a unified interface for package search across
all your linux-based containers (and maybe later Windows containers),
whatever base operating system they are running.


## Usage

The simplest way of running the indexer is from a Docker container.

    docker run --rm --name indexer -P -v /var/run/docker.sock:/var/run/docker.sock garethr/package-indexer

Note that we mount the docker socket from the host. You can also connect
to a TCP socket by passing the standard DOCKER environment variables if
you would prefer.

Alternatively you can run from source if you have a Python environment
setup:

    pip install -r requirements.txt
    cd src
    python package-indexer.py


## Search

With the container running above we first find the port on which the
search API is listening:

```
docker port indexer
8888/tcp -> 0.0.0.0:32770
```

The search engine will by default return the first 100 packages, or you
can pass a text query using the `q` query string parameter.

````
curl -s localhost:32779\?q=rake | jq
[
  {
    "container_name": "sleepy_jones",
    "version": "2.3.1-r0",
    "provider": "apk",
    "container_id":
"39276441516b1d7b1550bc25a29f71010cd592ae0da44a3459c1eb039948081c",
    "package": "ruby"
  },
  {
    "container_name": "sleepy_jones",
    "version": "2.3.1-r0",
    "provider": "apk",
    "container_id":
"39276441516b1d7b1550bc25a29f71010cd592ae0da44a3459c1eb039948081c",
    "package": "ruby-libs"
  },
  ...
```

You can also match on specific properties:

```
curl -s localhost:32779\?q=package:rake | jq
[
  {
    "container_name": "sleepy_jones",
    "version": "10.4.2",
    "provider": "gem",
    "container_id":
"39276441516b1d7b1550bc25a29f71010cd592ae0da44a3459c1eb039948081c",
    "package": "rake"
  }
]
```

See the Whoosh documentation for all the different search types.


## Points of interest

The examples use a static inventory compiled at build time. The
advantages of taking that approach include speed (reading a
pre-formatted file on disk should be much quicker than running apt
or yum), not requiring a package cache in the image (which takes up
space and tends to be removed as part of the build process) and not
requiring `puppet-inventory` (or a similar tool) at runtime. This works
particularly well for images which are run with read-only file systems
(ie. immutable containers) as these should not be able to be changed at
runtime anyway.

Nothing about `puppet-inventory` is container specific. The example here
uses the Docker API to retrieve a list of containers, and the same API
to execute commands in the context of the container to get the
inventory. It would be simple enough to use a different API (for
instance from AWS or vSphere) and SSH to return the inventory.

This example focuses on packages, but other resources from the inventory
could also be indexed and searched.

As this is a simple proof-of-concept the interface is left as HTTP.
Expert users can use `curl` and `jq`. Building a rich CLI or GUI on that
API would be an obvious path to take to making a more powerful tool.
