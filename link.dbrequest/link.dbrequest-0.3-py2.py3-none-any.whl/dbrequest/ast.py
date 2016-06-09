# -*- coding: utf-8 -*-


def AST(name, val):
    return {
        'name': name,
        'val': val
    }


class ASTError(Exception):
    pass


class ASTSingleStatementError(ASTError):
    def __init__(self, stmt):
        super(ASTSingleStatementError, self).__init__(
            'Signle statement must be "get" or "create", got: {0}'.format(
                stmt
            )
        )


class ASTLastStatementError(ASTError):
    def __init__(self, stmt, pos):
        super(ASTLastStatementError, self).__init__(
            'Statement "{0}" must be last, got position: {1}'.format(stmt, pos)
        )


class ASTInvalidStatementError(ASTError):
    def __init__(self, stmt):
        super(ASTInvalidStatementError, self).__init__(
            'Statement not allowed in this context: {0}'.format(stmt)
        )


class ASTInvalidFormatError(ASTError):
    def __init__(self):
        super(ASTInvalidFormatError, self).__init__(
            'AST must be a list or a dict'
        )
