"""
Push resource definitions to an output destination.

"""
from json import dumps
from logging import getLogger
from sys import stdout

import requests
from requests.exceptions import ConnectionError
from six.moves.urllib.parse import urlparse, urlunparse
from yaml import safe_dump_all


logger = getLogger("sync.push")


def push_yaml(inputs, destination):
    """
    Write inputs to destination as YAML.

    :param inputs: an iterable of (href, resource) pairs
    :param destination: a writable file-like object

    """
    safe_dump_all(({href: resource} for href, resource in inputs), destination)


def push_json(inputs, base_url, batch_size, enable_sessions=False,  max_attempts=2):
    """
    Write inputs to remote URL as JSON.

    Future implementations could perform paginated PATCH requests to a collection URI
    if our conventions support it.

    """
    # either use a session or use plain requests
    session_factory = requests.Session if enable_sessions else lambda: requests

    session = session_factory()
    for uri, resources in iter_json_batches(inputs, base_url, batch_size):
        # retry on connection failures
        for attempt in range(max_attempts):
            try:
                if batch_size == 1:
                    push_resource_json(session, uri, resources[0])
                else:
                    push_resource_json_batch(session, uri, resources)
            except ConnectionError as error:
                logger.info("Connection error for uri: {}: {}".format(uri, error))
                # on connection failure, recreate the session
                session = session_factory()
                continue
            else:
                break
        else:
            raise error


def iter_json_batches(inputs, base_url, batch_size):
    parsed_base_url = urlparse(base_url)

    current_uri = None
    current_batch = []

    for href, resource in inputs:
        # Skip over links-only (discovery) resources
        if resource.keys() == ["_links"]:
            continue

        # Inject the base URL's scheme and netloc; `urljoin` should do exactly this operation,
        # but actually won't if the right-hand-side term defines its own netloc
        parsed_href = urlparse(href)
        uri = urlunparse(parsed_href._replace(
            scheme=parsed_base_url.scheme,
            netloc=parsed_base_url.netloc,
        ))

        if batch_size == 1:
            yield (uri, [resource])
        else:
            # batch handling
            collection_uri = uri.rsplit("/", 1)[0]

            if any((
                    current_uri is not None and current_uri != collection_uri,
                    len(current_batch) >= batch_size,
            )):
                yield (current_uri, current_batch)
                current_batch = []

            current_uri = collection_uri
            current_batch.append(resource)

    if current_batch:
        yield (current_uri, current_batch)


def push_resource_json(session, uri, resource):
    """
    Push a single resource as JSON to a URI.

    Assumes that the backend supports a replace/put convention.

    """
    logger.debug("Pushing resource for {}".format(uri))

    response = session.put(
        uri,
        data=dumps(resource),
        headers={"Content-Type": "application/json"},
    )
    try:
        response.raise_for_status()
    except:
        logger.warn("Unable to replace {}".format(
            uri,
        ))
        raise


def push_resource_json_batch(session, uri, resources):
    """
    Push a single resource as JSON to a URI.

    Assumes that the backend supports a replace/put convention.

    """
    logger.debug("Pushing resource batch of size {} for {}".format(len(resources), uri))

    response = session.patch(
        uri,
        data=dumps(dict(
            items=resources,
        )),
        headers={"Content-Type": "application/json"},
    )
    try:
        response.raise_for_status()
    except:
        logger.warn("Unable to replace {}".format(
            uri,
        ))
        raise


def push(args, inputs):
    """
    Push content to a destination.

    If the destination is "-", YAML is written to stdout.
    If the destination has a http prefix, JSON is written to a URL.
    Otherwise, YAML is written to a local file.

    """
    logger.info("Pushing resources to: {}".format(args.output))

    if args.output == "-":
        push_yaml(inputs, stdout)
    elif args.output.startswith("http"):
        push_json(inputs, args.output, args.batch_size, args.enable_sessions)
    else:
        with open(args.output, "w") as file_:
            push_yaml(inputs, file_)
