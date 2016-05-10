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



class Validator(object):
    def __or__(self, other):
        return OrValidator(self, other)

    def __call__(self, snippet):
        return self.validate(snippet)


class OrValidator(Validator):
    def __init__(self, validator_a, validator_b):
        self._validator_a = validator_a
        self._validator_b = validator_b

    def validate(self, snippet):
        validation_a = self._validator_a(snippet)
        validation_b = self._validator_b(snippet)

        if validation_a is None or validation_b is None:
            return None
        else:
            if validation_a is not None:
                return validation_a
            else:
                return validation_b


class Any(Validator):
    def __call__(self, snippet):
        return None


class Scalar(Validator):
    @property
    def rule_description(self):
        return "a {0}".format(self.__class__.__name__.lower())

    def validate(self, snippet):
        if type(snippet) == CommentedSeq or type(snippet) == CommentedMap:
            return YAMLValidationError(snippet, "Not {0}".format(self.rule_description))
        else:
            return self.validate_scalar(snippet)

class Enum(Scalar):
    def __init__(self, restricted_to):
        # TODO: Validate set or list
        self._restricted_to = restricted_to

    def validate_scalar(self, snippet):
        if snippet not in self._restricted_to:
            return YAMLValidationError(snippet, "not in enum")


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


class Float(Scalar):
    def __call__(self, snippet):
        if type(snippet) == CommentedSeq or type(snippet) == CommentedMap:
            return YAMLValidationError(snippet, "Not a float")
        else:
            if re.compile("^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$").match(str(snippet)) is None:
                return YAMLValidationError(snippet, "not a float")
            else:
                return None


class Seq(Validator):
    def __init__(self, validator):
        self._validator = validator

    def validate(self, snippet):
        if type(snippet) != CommentedSeq:
            return YAMLValidationError(snippet, "Not a sequence")
        else:
            for item in snippet:
                validation = self._validator(item)
                if validation is not None:
                    return validation


class Map(Validator):
    def __init__(self, validator):
        self._validator = validator

        self._validator_dict = {
            key.key if type(key) == Optional else key: value for key, value in validator.items()
        }

    def validate(self, snippet):
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


class MapPattern(Validator):
    def __init__(self, key_validator, value_validator):
        self._key_validator = key_validator
        self._value_validator = value_validator

    def validate(self, snippet):
        if type(snippet) != CommentedMap:
            return YAMLValidationError(snippet, "Not a mapping")
        else:
            for key, value in snippet.items():
                key_validation = self._key_validator(key)
                if key_validation is not None:
                    return key_validation

                value_validation = self._value_validator(value)
                if value_validation is not None:
                    return value_validation