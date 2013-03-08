# -*- coding: utf-8 -*-

class ExecutionException(Exception): pass

class Node(object):
    
    def execute(self, context):
        raise NotImplementedError()
    
    def error(self, msg, token):
        raise ExecutionException("[Execution error in Line %d Col %d in %s] %s" %
                                 (token.line, token.col, self.__class__.__name__, msg))

class VarDecl(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def __str__(self):
        return "<VarDecl name=%s expr=%s>" % (self.name, self.expr)
    
    def execute(self, context):
        if context.has_var(self.name.content):
            self.error("'%s' already declared" % self.name.content, self.name)
        
        context.set_var(self.name.content, self.expr.execute(context))

class Lambda(Node):
    def __init__(self, name, params, expr):
        self.name = name
        self.params = params
        self.expr = expr
    
    def __str__(self):
        return "<Lambda name=%s params=%s expr=%s>" % (self.name, self.params, self.expr)

    def execute(self, context):
        if context.has_func(self.name.content):
            self.error("Function '%s' already declared." % self.name.content, self.name)
        
        context.add_func(self.name.content, self)
    
    def run(self, context, paramexprs):
        context.enter_scope()
        try:
            if len(self.params) != len(paramexprs):
                self.error("Expected %d parameters, got %d" % (len(self.params), len(paramexprs)), self.name)
        
            # Populate the parameters in the scope
            for idx, param in enumerate(self.params):
                context.set_var(param.content, paramexprs[idx])
            
            return self.expr.execute(context) 
        finally:
            context.leave_scope()

class Identifier(Node):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return "<Identifier name=%s>" % self.name

    def execute(self, context):
        if not context.has_var(self.name.content):
            self.error("Identifier '%s' not found" % self.name.content, self.name)
        
        return context.get_var(self.name.content)

class Number(Node):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return "<Number value=%s>" % self.value
    
    def execute(self, context):
        return float(self.value.content)

class Term(Node):
    def __init__(self, power, op, expr):
        self.power = power
        self.op = op
        self.expr = expr
    
    def __str__(self):
        return "<Term power=%s op=%s expr=%s>" % (self.power, self.op, self.expr)
    
    def execute(self, context):
        if self.op.content == "*":
            return self.power.execute(context) * self.expr.execute(context)
        elif self.op.content == "/":
            return self.power.execute(context) / self.expr.execute(context)
        
        raise ExecutionException("Unhandled operator (%s)" % self.op)

class Power(Node):
    def __init__(self, factor, expr):
        self.factor = factor
        self.expr = expr
    
    def __str__(self):
        return "<Power factor=%s expr=%s>" % (self.factor, self.expr)
    
    def execute(self, context):
        return pow(self.factor.execute(context), self.expr.execute(context))

class Expression(Node):
    def __init__(self, term, op, expr):
        self.term = term
        self.op = op
        self.expr = expr
    
    def __str__(self):
        return "<Expression term=%s op=%s expr=%s>" % (self.term, self.op, self.expr)

    def execute(self, context):
        if self.op.content == "+":
            return self.term.execute(context) + self.expr.execute(context)
        elif self.op.content == "-":
            return self.term.execute(context) - self.expr.execute(context)
        
        raise ExecutionException("Unhandled operator (%s)" % self.op)

class FuncCall(Node):
    def __init__(self, name, params):
        self.name = name
        self.params = params
    
    def __str__(self):
        return "<FuncCall name=%s params=%s>" % (self.name, self.params)

    def execute(self, context):
        if not context.has_func(self.name.content):
            self.error("Function '%s' not found" % self.name.content, self.name)
        
        return context.get_func(self.name.content).run(context, map(lambda s: s.execute(context), self.params))