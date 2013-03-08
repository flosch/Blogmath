# -*- coding: utf-8 -*-

import parser
import lexer
import nodes

class ContextException(Exception): pass

# Internal print method
class PrintMethod(object):
    def run(self, context, paramexprs):
        print " ".join(map(lambda s: str(s), paramexprs))

class Context(object):
    def __init__(self):
        self._funcs = {}
        self._vars = []
        self.enter_scope() # Create initial scope
        self.add_func("print", PrintMethod()) # Register internal 'print' method
        
    def has_var(self, name):
        for _vars in self._vars[::-1]:
            if _vars.has_key(name):
                return True
        
        return False

    def enter_scope(self):
        self._vars.append({})
    
    def leave_scope(self):
        self._vars = self._vars[:-1]

    def set_var(self, name, content):
        self._vars[len(self._vars)-1][name] = content
    
    def get_var(self, name):
        for _vars in self._vars[::-1]:
            if _vars.has_key(name):
                return _vars[name]
        raise ContextException("Variable not found: %s" % name)

    def add_func(self, name, fn):
        self._funcs[name] = fn
    
    def get_func(self, name):
        return self._funcs[name]
        
    def has_func(self, name):
        return self._funcs.has_key(name)

def evaluate(src, context):
    try:
        stmts = parser.parse(src)
    except (parser.ParserSyntaxError, lexer.LexerSyntaxException), msg:
        print msg
        return
    
    for stmt in stmts:
        try:
            res = stmt.execute(context)
            if res is not None:
                yield res
        except nodes.ExecutionException, msg:
            print msg
            return