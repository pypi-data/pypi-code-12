# -*- coding: utf-8 -*-


def AST(name, val):
    """
    Helper for create AST nodes.

    :param name: AST node name
    :type name: str

    :param val: AST node value

    :returns: AST node
    :rtype: dict
    """

    return {
        'name': name,
        'val': val
    }


class ASTError(Exception):
    """
    Basic AST semantic error.
    """

    pass


class ASTSingleStatementError(ASTError):
    """
    Error raised when trying to execute statements that must be in a sequence.
    """

    def __init__(self, stmt):
        super(ASTSingleStatementError, self).__init__(
            'Single statement must be "get" or "create", got: {0}'.format(
                stmt
            )
        )


class ASTLastStatementError(ASTError):
    """
    Error raised when trying to execute a statement that must be in the end of
    the sequence.
    """

    def __init__(self, stmt, pos):
        super(ASTLastStatementError, self).__init__(
            'Statement "{0}" must be last, got position: {1}'.format(stmt, pos)
        )


class ASTInvalidStatementError(ASTError):
    """
    Error raised when trying to execute an unknown statement.
    """

    def __init__(self, stmt):
        super(ASTInvalidStatementError, self).__init__(
            'Statement not allowed in this context: {0}'.format(stmt)
        )


class ASTInvalidFormatError(ASTError):
    """
    Error raised when supplied AST is not a valid expected type.
    """

    def __init__(self):
        super(ASTInvalidFormatError, self).__init__(
            'AST must be a list or a dict'
        )
