"""
A naming convention and discovery mechanism for HTTP endpoints.

Operations provide a naming convention for references between endpoints,
allowing easy construction of links or audit trails for external consumption.

"""
from collections import namedtuple

from enum import Enum, unique


# metadata for an operation
OperationInfo = namedtuple("OperationInfo", ["name", "method", "pattern", "default_code"])


NODE_PATTERN = "{}.{}"
EDGE_PATTERN = "{}.{}.{}"


@unique
class Operation(Enum):
    """
    An enumerated set of operation types, which know how to resolve themselves into
    URLs and hrefs.

    """
    # discovery operation
    Discover = OperationInfo("discover", "GET", NODE_PATTERN, 200)

    # collection operations
    Search = OperationInfo("search", "GET", NODE_PATTERN, 200)
    Create = OperationInfo("create", "POST", NODE_PATTERN, 201)
    # bulk update is possible here with PATCH

    # instance operations
    Retrieve = OperationInfo("retrieve", "GET", NODE_PATTERN, 200)
    Delete = OperationInfo("delete", "DELETE", NODE_PATTERN, 204)
    Replace = OperationInfo("replace", "PUT", NODE_PATTERN, 200)
    Update = OperationInfo("update", "PATCH", NODE_PATTERN, 200)

    # relation operations
    CreateFor = OperationInfo("create_for", "POST", EDGE_PATTERN, 201)
    RetrieveFor = OperationInfo("retrieve_for", "GET", EDGE_PATTERN, 200)
    SearchFor = OperationInfo("search_for", "GET", EDGE_PATTERN, 200)

    # ad hoc operations
    Command = OperationInfo("command", "POST", NODE_PATTERN, 200)
    Query = OperationInfo("query", "GET", NODE_PATTERN, 200)

    @classmethod
    def from_name(cls, name):
        for operation in cls:
            if operation.value.name.lower() == name.lower():
                return operation
        else:
            raise ValueError(name)
