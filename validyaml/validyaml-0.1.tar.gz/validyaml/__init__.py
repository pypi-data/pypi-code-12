from ruamel.yaml.comments import CommentedSeq, CommentedMap
import re


class YAMLValidationError(Exception):
    def __init__(self, message, snippet):
        self._message = message
        self._snippet = snippet

    @property
    def lineno(self):
        return self._snippet.lc.line + 1


class Optional(object):
    def __init__(self, key):
        self.key = key


class Any(object):
    def __call__(self, snippet):
        return None


class Scalar(object):
    @property
    def rule_description(self):
        return "a {0}".format(self.__class__.__name__.lower())

    def __call__(self, snippet):
        if type(snippet) == CommentedSeq or type(snippet) == CommentedMap:
            return YAMLValidationError(snippet, "Not {0}".format(self.rule_description))
        else:
            return self.validate_scalar(snippet)


class Str(Scalar):
    def validate_scalar(self, snippet):
        return None


class Int(Scalar):
    def validate_scalar(self, snippet):
        if re.compile("^[-+]?\d+$").match(str(snippet)) is None:
            return YAMLValidationError(snippet, "not an integer")


class Bool(Scalar):
    def validate_scalar(self, snippet):
        if str(snippet).lower() not in ["yes", "true", "no", "false", ]:
            return YAMLValidationError(snippet, "not a bool")


class Float(object):
    def __call__(self, snippet):
        if type(snippet) == CommentedSeq or type(snippet) == CommentedMap:
            return YAMLValidationError(snippet, "Not a float")
        else:
            if re.compile("^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$").match(str(snippet)) is None:
                return YAMLValidationError(snippet, "not a float")
            else:
                return None


class Seq(object):
    def __init__(self, validator):
        self._validator = validator

    def __call__(self, snippet):
        if type(snippet) != CommentedSeq:
            return YAMLValidationError(snippet, "Not a sequence")
        else:
            for item in snippet:
                validation = self._validator(item)
                if validation is not None:
                    return validation


class Map(object):
    def __init__(self, validator):
        self._validator = validator

        self._validator_dict = {
            key.key if type(key) == Optional else key: value for key, value in validator.items()
        }

    def __call__(self, snippet):
        if type(snippet) != CommentedMap:
            return YAMLValidationError(snippet, "Not a mapping")
        else:
            if not set(snippet.keys()).issubset(set(self._validator_dict.keys())):
                return YAMLValidationError(
                    snippet, "Invalid keys found {}".format(list(self._validator_dict))
                )

            for key, value in snippet.items():
                validation = self._validator_dict[key](value)
                if validation is not None:
                    return validation
