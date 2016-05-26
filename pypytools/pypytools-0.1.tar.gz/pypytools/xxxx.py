    
    
    
class Unroller(ast.NodeTransformer):
    def __init__(self, freevars):
        self.freevars = freevars

    def visit_FunctionDef(self, node):
        self.unroll_name = node.args.args[0].id
        return self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.iter, ast.Name) and node.iter.id == self.unroll_name:
            return self.unroll(node)
        return node

    def unroll(self, fornode):
        assert fornode.orelse == []
        body = []
        for i in range(self.n):
            item = ast.Subscript(value=ast.Name(id=self.unroll_name, ctx=ast.Load()),
                                 slice=ast.Index(value=ast.Num(n=i)),
                                 ctx=ast.Load())
            assign = ast.Assign(targets=[fornode.target],
                                value=item)
            body.append(assign)
            body.extend(fornode.body)
        return body


## ITEMS = [1, 2, 3, 4]

## @unroll(ITEMS)
## def foo(items):
##     for i in items:
##         print i

## foo() # the ``items`` arg is automatically bound by @unroll

# alternative syntax

## @unroll(items=ITEMS)
## def foo(items):
##     for i in items:
##         print i

## @unroll
## def foo(items=unroll(ITEMS)):
##     for i in items:
##         print i


## @unroll(items=ITEMS)
## def foo():
##     for i in unroll(items):
##         print i
