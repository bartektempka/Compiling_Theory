#!/usr/bin/python

import scanner
import ply.yacc as yacc
import scanner
import AST

tokens = scanner.tokens

precedence = ( 
    ('right', ':'),
    ('nonassoc', 'IFX'),
    ('nonassoc', 'ELSE'),
    ("left", '<', '>', "NE", "GE", "LE", "EQ"),
    ("left", 'DOTADD', 'DOTSUB'),
    ("left", '+', '-'),
    ("left", 'DOTMUL', 'DOTDIV'),
    ("left", '*', '/'),
    ('nonassoc', '!'),
    ("right", 'ID', '['),
    ('right', 'UMINUS'),
    ('left', '\'') ,
)
operators = set(['+', '-', '*', '/', '==', '<', '>', '!=', '>=', '<=', '+=', '-=', '*=', '/=', '\'','.+','.-','.*','./'])

def p_error(p):
    if p:
        print("Syntax error at line {0}: LexToken({1}, '{2}')".format(p.lexer.lineno, p.type, p.value))
    else:
        print("Unexpected end of input")

def p_program(p):
    """program : instructions_opt"""
    p[0] = p[1]

def p_instructions_opt_1(p):
    """instructions_opt : instructions """
    p[0] = p[1]

def p_instructions_opt_2(p):
    """instructions_opt : """
    p[0] = AST.ListInstr(None, p.lexer.lineno)
    

def p_instructions_1(p):
    """instructions : instructions instruction
                    | instruction"""
    if len(p) == 2:
        p[0] = AST.ListInstr(p[1], p.lexer.lineno)
    else:
        p[1].add(p[2])
        p[0] = p[1]

def p_instruction(p):
    """instruction : expression ';'
                   | assignment ';'
                   | break_statement ';'
                   | continue_statement ';'
                   | return_statement ';'
                   | print_statement ';'
                   | for_statement
                   | compound_statement
                   | if_statement 
                   | while_statement"""
    p[0] = p[1]

def p_compound_statement(p):
   """compound_statement : '{' instructions_opt '}'"""
   p[0]=p[2]
    
def p_expression(p):
    """expression : expression '+' expression
                  | expression '*' expression 
                  | expression '-' expression
                  | expression '/' expression
                  | expression DOTADD expression
                  | expression DOTSUB expression
                  | expression DOTMUL expression
                  | expression DOTDIV expression
                  | expression LE expression
                  | expression GE expression
                  | expression NE expression
                  | expression EQ expression
                  | expression '<' expression
                  | expression '>' expression
                  | '(' expression ')'
                  | '[' expression_list ']'
                  | ZEROS '(' expression_list ')'
                  | ONES '(' expression_list ')'
                  | EYE '(' expression_list ')'
                  | '!' expression
                  | '-' expression %prec UMINUS
                  | ID
                  | ID '[' expression_list ']'
                  | expression ':' expression 
                  | string
                  | INTNUM
                  | FLOATNUM
                  | expression '\\'' 
                  """
    if len(p) == 2:
        if type(p[1]) == float:
            p[0] = AST.FloatNum(p[1], p.lexer.lineno)
        elif type(p[1]) == int:
            p[0] = AST.IntNum(p[1], p.lexer.lineno)
        elif type(p[1]) == AST.String:
            p[0] = p[1] #obrzydliwe ale nie mam pomysłu
        else:
            p[0] = AST.Variable(p[1], p.lexer.lineno)    
    elif len(p) == 3:
        if p[1] == '!' or p[1] == '-':
            p[0] = AST.UnaryExpr(p[2], p[1], p.lexer.lineno)
        elif p[2] == '\'':
             p[0] = AST.Transposition(p[1], p.lexer.lineno)
        else:
            p[0] = AST.UnaryExpr(p[1], p[2], p.lexer.lineno)
    elif len(p) == 4:
        if p[1] == '(':
            p[0] = p[2]
        elif p[1] == '[':
            p[0] = AST.List(p[2], p.lexer.lineno)
        elif p[2] == ':':
            p[0] = AST.RangeExpr(p[1], p[3], p.lexer.lineno)

        else:
            p[0] = AST.BinExpr(p[2], p[1], p[3], p.lexer.lineno)
    elif len(p) == 5:
        if p[4] == ']':
            p[0] = AST.ArrayElement(p[1], AST.List(p[3], p.lexer.lineno), p.lexer.lineno)
        else:
            p[0] = AST.MatrixCreate(p[1], AST.List(p[3], p.lexer.lineno), p.lexer.lineno)

def p_string (p):
    """string : STRING
              """
    if len(p) == 2:
        p[0] = AST.String(p[1], p.lexer.lineno)

def p_assigment(p):
    """assignment : lvalue '=' expression
                  | lvalue ADDASSIGN expression
                  | lvalue SUBASSIGN expression
                  | lvalue MULASSIGN expression
                  | lvalue DIVASSIGN expression"""
    p[0] = AST.AssignExpr(p[2], p[1], p[3], p.lexer.lineno)

def p_lvalue(p):
    """lvalue : ID
              | ID '[' expression_list ']' 
              """
    p[0] = AST.Variable(p[1], p.lexer.lineno) if len(p) == 2 else AST.ArrayElement(p[1], AST.List(p[3], p.lexer.lineno), p.lexer.lineno)

def p_expression_list(p):
    """expression_list : expression
                       | expression_list ',' expression
                        """ 
    if len(p) == 2:
        p[0] = AST.ListExpr(p[1], p.lexer.lineno)
    else:
        p[1].add(p[3])
        p[0] = p[1]
   
def p_if_statement(p):
    """if_statement : IF '(' expression ')' instruction %prec IFX
                   | IF '(' expression ')' instruction ELSE instruction"""
    if len(p) > 6:
         p[0] = AST.IfElseExpr(p[3], p[5], p[7], p.lexer.lineno)
    else:
         p[0] = AST.IfExpr(p[3], p[5], p.lexer.lineno)
   
   
def p_while_statement(p):
   """while_statement : WHILE '(' expression ')' instruction"""
   p[0] = AST.WhileExpr(p[3], p[5], p.lexer.lineno)


def p_for_statement(p):
   """for_statement : FOR ID '=' expression instruction""" 
   p[0] = AST.ForExpr(p[2], p[4], p[5], p.lexer.lineno)

def p_break_statement(p):
   """break_statement : BREAK"""
   p[0] = AST.BreakStmt(p.lexer.lineno)

def p_continue_statement(p):
   """continue_statement : CONTINUE"""
   p[0] = AST.ContinueStmt(p.lexer.lineno)

def p_return_statement(p):
   """return_statement : RETURN expression
                       | RETURN"""
   p[0] = AST.ReturnStmt(p[2], p.lexer.lineno) if len(p) > 2 else AST.ReturnStmt(None, p.lexer.lineno)
   
def p_print_statement(p):
   """print_statement : PRINT expression_list
                      """
   p[0] = AST.PrintStmt(p[2], p.lexer.lineno)

parser = yacc.yacc()