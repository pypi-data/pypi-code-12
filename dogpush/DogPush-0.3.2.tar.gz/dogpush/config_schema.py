CONFIG_SCHEMA = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "id": "http://trueaccord.com/dogpush",
  "type": "object",
  "properties": {
    "datadog": {
      "id": "http://trueaccord.com/dogpush/datadog",
      "type": "object",
      "properties": {
        "api_key": {
          "id": "http://trueaccord.com/dogpush/datadog/api_key",
          "type": "string"
        },
        "app_key": {
          "id": "http://trueaccord.com/dogpush/datadog/app_key",
          "type": "string"
        }
      }
    },
    "teams": {
      "id": "http://trueaccord.com/dogpush/teams",
      "type": "object",
      "additionalProperties": {
        "id": "http://trueaccord.com/dogpush/teams/eng",
        "type": "object",
        "properties": {
          "notifications": {
            "id": "http://trueaccord.com/dogpush/teams/eng/notifications",
            "type": "object",
            "properties": {
              "CRITICAL": {
                "id": "http://trueaccord.com/dogpush/teams/eng/notifications/CRITICAL",
                "type": "string"
              },
              "INFO": {
                "id": "http://trueaccord.com/dogpush/teams/eng/notifications/INFO",
                "type": "string"
              },
              "WARNING": {
                "id": "http://trueaccord.com/dogpush/teams/eng/notifications/WARNING",
                "type": "string"
              }
            },
            "additionalProperties": False,
          }
        },
        "additionalProperties": False,
      }
    },
    "mute_tags": {
      "id": "http://trueaccord.com/dogpush/mute_tags",
      "type": "object",
      "additionalProperties": {
        "id": "http://trueaccord.com/dogpush/mute_tags/not_business_hours",
        "type": "object",
        "properties": {
          "timezone": {
            "id": "http://trueaccord.com/dogpush/mute_tags/not_business_hours/timezone",
            "type": "string"
          },
          "expr": {
            "id": "http://trueaccord.com/dogpush/mute_tags/not_business_hours/expr",
            "type": "string"
          }
        },
        "required": [
            "timezone",
            "expr",
        ]
      }
    },
    "rule_files": {
      "id": "http://trueaccord.com/dogpush/rule_files",
      "type": "array",
      "items": {
        "id": "http://trueaccord.com/dogpush/rule_files/0",
        "type": "string"
      }
    }
  },
  "additional_properties": False
}
