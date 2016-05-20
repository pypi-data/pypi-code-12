__author__ = 'schlitzer'


SAMPLE = {
  "type": "object",
  "additionalProperties": False,
  "properties": {
    "_id": {
      "type": "string",
      "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}"
    },
    "description": {
      "type": "string",
      "required": False
    },
    "users": {
      "type": "array",
      "required": False,
      "items": {
        "type": "string",
        "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        "uniqueItems": True,
        "enum": [
          "blargggg1",
          "blargggg2"
        ]
      }
    }
  }
}


PERMISSIONS_CREATE = {
    "type": "object",
    "additionalProperties": False,
    "required":  ["_id", "scope"],
    "properties": {
        "_id": {
            "type": "string",
            "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        },
        "description": {
            "type": "string",
        },
        "permissions": {
            "type": "array",
            "items": {
                "type": "string",
                "uniqueItems": True,
                "enum": [
                    ':',
                    ':cluster:',
                    ':cluster:monitor',
                    ':index:',
                    ':index:crud:',
                    ':index:crud:create',
                    ':index:crud:read',
                    ':index:crud:update',
                    ':index:crud:delete',
                    ':index:crud:search',
                    ':index:manage:',
                    ':index:manage:monitor',
                ]
            }
        },
        "roles": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
                "minItems": 0
            }
        },
        "scope": {
            "type": "string"
        }
    }
}

PERMISSIONS_UPDATE = {
    "type": "object",
    "additionalProperties": False,
    "anyOf": [
        {"required": ["description"]},
        {"required": ["permissions"]},
        {"required": ["roles"]},
        {"required": ["scope"]}
    ],
    "properties": {
        "description": {
            "type": "string",
        },
        "permissions": {
            "type": "array",
            "items": {
                "type": "string",
                "uniqueItems": True,
                "enum": [
                    ':',
                    ':cluster:',
                    ':cluster:monitor',
                    ':index:',
                    ':index:crud:',
                    ':index:crud:create',
                    ':index:crud:read',
                    ':index:crud:update',
                    ':index:crud:delete',
                    ':index:crud:search',
                    ':index:manage:',
                    ':index:manage:monitor',
                ]
            }
        },
        "roles": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
                "minItems": 0
            }
        },
        "scope": {
            "type": "string"
        }
    }
}

ROLES_CREATE = {
    "type": "object",
    "additionalProperties": False,
    "required":  ["_id"],
    "properties": {
        "_id": {
            "type": "string",
            "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        },
        "description": {
            "type": "string",
        },
        "users": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
                "minItems": 0
            }
        }
    }
}

ROLES_UPDATE = {
    "type": "object",
    "additionalProperties": False,
    "anyOf": [
        {"required": ["description"]},
        {"required": ["users"]}
    ],
    "properties": {
        "description": {
            "type": "string",
        },
        "users": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
                "minItems": 0
            }
        }
    }
}

SESSIONS_TOKEN = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "_id",
        "_token"
    ],
    "properties": {
        "_id": {
            "type": "string"
        },
        "token": {
            "type": "string"
        }
    }
}

USERS_CREATE = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "_id",
        "admin",
        "email",
        "name",
        "password"
    ],
    "properties": {
        "_id": {
            "type": "string",
            "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        },
        "admin": {
            "type": "boolean",
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "name": {
            "type": "string",
        },
        "password": {
            "type": "string",
        }
    }
}

USERS_CREDENTIALS = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "password",
        "user"
    ],
    "properties": {
        "password": {
            "type": "string"
        },
        "user": {
            "type": "string",
            "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        }
    }
}

USERS_UPDATE = {
    "type": "object",
    "additionalProperties": False,
    "anyOf": [
        {"required": ["admin"]},
        {"required": ["email"]},
        {"required": ["name"]},
        {"required": ["password"]},
    ],
    "properties": {
        "admin": {
            "type": "boolean",
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "name": {
            "type": "string",
        },
        "password": {
            "type": "string",
        }
    }
}

LOSTPW_REQUEST = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "_id",
    ],
    "properties": {
        "_id": {
            "type": "string"
        }
    }
}

LOSTPW_RESET = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "token",
        "password"
    ],
    "properties": {
        "token": {
            "type": "string",
        },
        "password": {
            "type": "string",
        }
    }
}

CHECK_CONFIG_MAIN = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "dlog",
        "port",
        "static_path"
    ],
    "properties": {
        "dlog": {
            "type": "string",
        },
        "port": {
            "type": "integer",
            "maximum": 65535,
            "minimum": 1
        },
        "static_path": {
            "type": "string",
        },
    }
}

CHECK_CONFIG_MONGOPOOL = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "hosts",
        "db"
    ],
    "optional": [
        "pass",
        "user"
    ],
    "properties": {
        "hosts": {
            "type": "string",
        },
        "db": {
            "type": "string",
        },
        "pass": {
            "type": "string",
        },
        "user": {
            "type": "string",
        },
    }
}

CHECK_CONFIG_MONGOCOLL = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "coll",
        "pool"
    ],
    "properties": {
        "coll": {
            "type": "string",
        },
        "pool": {
            "type": "string",
        }
    }
}

CHECK_CONFIG_PW_RECOVERY = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "api_url",
        "www_url",
        "from",
        "subject",
        "text_tmpl",
        "html_tmpl",
        "smtp_host",
        "smtp_port"
    ],
    "properties": {
        "api_url": {
            "type": "string",
            "format": "uri"
        },
        "www_url": {
            "type": "string",
            "format": "uri"
        },
        "from": {
            "type": "string",
            "format": "email"
        },
        "subject": {
            "type": "string",
        },
        "text_tmpl": {
            "type": "string",
        },
        "html_tmpl": {
            "type": "string",
        },
        "smtp_host": {
            "type": "string"
        },
        "smtp_port": {
            "type": "integer",
            "maximum": 65535,
            "minimum": 1
        },
    }
}
