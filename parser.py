# -*- coding: utf-8 -*-

import lexer

from nodes import *

class ParserException(Exception): pass
class ParserSyntaxError(ParserException): pass

# Parse helpers

tokens = []

def LA(n, safe=True):
    if n > len(tokens):
        # Safe makes sure that there is a token tokens[n]
        # If there is not and safe is True, raise an error to interrupt execution
        if not safe:
            return None
        else:
            error("Unexpected EOF (expected at least %d more token(s))" % n)
    
    return tokens[n-1] 

def consume():
    global tokens
    t = tokens[0]
    tokens = tokens[1:]
    return t

def look(typ, *contents):
    t = LA(1, safe=False)
    fail = (t is None)
        
    if not fail and typ != t.type:
        fail = True
    
    if not fail and len(contents) > 0:
        for content in contents:
            if content == t.content:
                break
        else:
            fail = True
                
    if fail:
        error("Expected %(exp_typ)s%(exp_content)s, got %(got_typ)s ('%(got_content)s')" % {
            "exp_typ": lexer.tokens_natural[typ],
            "exp_content":
                (len(contents) > 0) 
                and " (%s)" % " or ".join(map(lambda s: "'%s'" % s, contents)) 
                or "",
            "got_typ": t and t.get_type_string() or "EOF",
            "got_content": t and t.content or ""
        }, t)

    return t

def match(typ, *contents):
    t = look(typ, *contents)
    consume()
    return t

def error(msg, token=None):
    if token:
        loc = "Line %d Col %d" % (token.line, token.col)
    else:
        loc = "near EOF"
    
    raise ParserSyntaxError("[Syntaxerror %s] %s" % (loc, msg))

# Productions

# Statement -> VarDecl | Lambda | FuncCall 
def parse_statement():
    t = LA(1)
    if t.type == lexer.TOKEN_KEYWORD:
        if t.content == "var":
            return parse_var_decl()
        elif t.content == "lambda":
            return parse_lambda()
        else:
            error("Unknown keyword '%s'" % LA(1).content, t)
    elif t.type == lexer.TOKEN_IDENTIFIER:
        return parse_func_call()
    else:
        error("Expected either keyword or function call, got %s" % t.get_type_string(), t)

# VarDecl -> "var" IDENTIFIER "=" Expression
def parse_var_decl():
    match(lexer.TOKEN_KEYWORD, "var")
    name = match(lexer.TOKEN_IDENTIFIER)
    match(lexer.TOKEN_ASSIGN)
    expr = parse_expression()
    
    return VarDecl(name, expr)

# Lambda -> "lambda" IDENTIFIER "(" LambdaParams ")" "=" Expression
def parse_lambda():
    match(lexer.TOKEN_KEYWORD, "lambda")
    name = match(lexer.TOKEN_IDENTIFIER)
    match(lexer.TOKEN_BRACEOPEN)
    params = parse_lambda_params()
    match(lexer.TOKEN_BRACECLOSE)
    match(lexer.TOKEN_ASSIGN)
    expr = parse_expression()
    
    return Lambda(name, params, expr)

# LambdaParams -> LambdaParam | e
# LambdaParam -> IDENTIFIER "," LambdaParam | IDENTIFIER
def parse_lambda_params():
    params = []
    
    if LA(1).content == ")":
        # No params
        return params
    
    params.append(match(lexer.TOKEN_IDENTIFIER))
    while LA(1).content == ",":
        match(lexer.TOKEN_COMMA)
        params.append(match(lexer.TOKEN_IDENTIFIER))
    
    return params

# Expression -> Term + Expr | Term - Expr | Term
def parse_expression():
    t = parse_term()
    
    if LA(1).content in ["+", "-"]:
        op = match(lexer.TOKEN_OPERATION, "+", "-")
        e = parse_expression()
        return Expression(t, op, e)
    
    return t

# Term -> Power * Expr | Power / Expr | Power
def parse_term():
    p = parse_power()
    
    if LA(1).content in ["*", "/"]:
        op = match(lexer.TOKEN_OPERATION, "*", "/")
        e = parse_expression()
        return Term(p, op, e)
    
    return p

# Power -> Factor ^ Expr | Factor
def parse_power():
    f = parse_factor()
    
    if LA(1).content == "^":
        match(lexer.TOKEN_OPERATION, "^")
        e = parse_expression()
        return Power(f, e)
    
    return f

# Factor -> IDENTIFIER | FuncCall | "(" Expression ")"
def parse_factor():
    t = LA(1)
    if t.type == lexer.TOKEN_IDENTIFIER:
        if LA(2).type == lexer.TOKEN_BRACEOPEN:
            return parse_func_call()
        else:
            name = match(lexer.TOKEN_IDENTIFIER)
            return Identifier(name)
    elif t.type == lexer.TOKEN_NUMBER:
        val = match(lexer.TOKEN_NUMBER)
        return Number(val)
    elif t.type == lexer.TOKEN_BRACEOPEN:
        match(lexer.TOKEN_BRACEOPEN)
        res = parse_expression()
        match(lexer.TOKEN_BRACECLOSE)
        return res
    else:
        error("Expected either an identifier, a function call or a number (got %s)" % 
              t.get_type_string(), t)

# FuncCall -> IDENTIFIER "(" FuncParams ")"
def parse_func_call():
    name = match(lexer.TOKEN_IDENTIFIER)
    match(lexer.TOKEN_BRACEOPEN)
    params = parse_func_params()
    match(lexer.TOKEN_BRACECLOSE)
    
    return FuncCall(name, params)

# FuncParams -> FuncParam | e
# FuncParam -> Expression | Expression "," FuncParam 
def parse_func_params():
    params = []
    
    if LA(1).content == ")":
        # No params
        return params
    
    params.append(parse_expression())
    while LA(1).content == ",":
        match(lexer.TOKEN_COMMA)
        params.append(parse_expression())
    
    return params

# Statements -> { Statement ";" }
def parse_statements():
    stmts = []
    
    while len(tokens) > 0:
        stmts.append(parse_statement())
        match(lexer.TOKEN_SEMICOLON)

    return stmts

# Returns statements list
def parse(src):
    global tokens
    tokens = lexer.tokenize(src)  
    return parse_statements()

if __name__ == "__main__":
    def main():
        stmts = parse("""
        var c = 2; // Exponent
        var s = 0.5;
    
        // Funktion zur Potenzierung
        lambda pow(a) = a^c;
        
        // Funktion zum Wurzelziehen
        lambda sqrt(a) = a^s;
    
        // Ergebnis berechnen von 5^2
        var result = pow(5);
        
        // Ergebnis berechnen von 25^0.5
        var result2 = sqrt(result);
    
        // Ergebnis ausgeben
        print(result);   // Gibt 25 aus
        print(result2);  // Gibt 5 aus
        
        lambda get_sqrt_const() = 1 * s + 10 ^ d+f;
        print(100^get_sqrt_const());
        get_sqrt_const();
        """.strip())
        
        for stmt in stmts:
            print stmt
    main()