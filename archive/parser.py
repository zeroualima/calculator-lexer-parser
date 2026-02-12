#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : parser - requires Python version >= 3.10
"""

import sys
from math import factorial
assert sys.version_info >= (3, 10), "Use Python 3.10 or newer !"

import lexer
from definitions import V_T, str_attr_token

#####
# Variables internes (à ne pas utiliser directement)

_current_token = V_T.END
_value = None  # attribut du token renvoyé par le lexer

#####
# Fonctions génériques

class ParserError(Exception):
    pass

def unexpected_token(expected):
    return ParserError("Found token '" + str_attr_token(_current_token, _value) + "' but expected " + expected)

def get_current():
    return _current_token

def init_parser(stream):
    global _current_token, _value
    lexer.reinit(stream)
    _current_token, _value = lexer.next_token()
    # print("@ init parser on",  repr(str_attr_token(_current, _value)))  # for DEBUGGING

def consume_token(tok):
    # Vérifie que le prochain token est tok ;
    # si oui, le consomme et renvoie son attribut ; si non, lève une exception
    global _current_token, _value
    if _current_token != tok:
        raise unexpected_token(tok.name)
    if _current_token != V_T.END:
        old = _value
        _current_token, _value = lexer.next_token()
        return old

#########################
## Parsing de input et exp

def parse_input():
    if get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB] :
        parse_exp5()
        consume_token(V_T.SEQ)
        parse_input()
    else : # Donc get_current() == V_T.END
        return

def parse_exp5() :
    # Donc get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB] :
    parse_exp4()
    parse_A()

def parse_A() :
    if get_current() in [V_T.ADD, V_T.SUB] :
        parse_exp5_()
        parse_A()
    else : # Donc get_current() in [V_T.SEQ, V_T.CPAR]
        return

def parse_exp5_() :
    if get_current() ==  V_T.ADD :
        consume_token(V_T.ADD)
        parse_exp4()
    else : # Donc get_current() == V_T.SUB 
        consume_token(V_T.SUB)
        parse_exp4()

def parse_exp4() :
    #Donc get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB] :
    parse_exp3()
    parse_B()

def parse_B() :
    if get_current() in [V_T.MUL, V_T.DIV] :
        parse_exp4_()
        parse_B()
    else : # Donc get_current() in [V_T.ADD, V_T.SUB, V_T.SEQ, V_T.CPAR]
        return

def parse_exp4_() :
    if get_current() ==  V_T.MUL :
        consume_token(V_T.MUL)
        parse_exp3()
    else : # Donc get_current() == V_T.DIV
        consume_token(V_T.DIV) 
        parse_exp3()

def parse_exp3() :
    if get_current() == V_T.SUB :
        consume_token(V_T.SUB)
        parse_exp3()
    else : # Donc get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR]
        parse_exp2() 

def parse_exp2() :
    # Donc get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR] :
    parse_exp1()
    parse_C() 

def parse_C() :
    if get_current() == V_T.FACT :
        consume_token(V_T.FACT)
        parse_C()
    else : # Donc get_current() in [V_T.ADD, V_T.SUB, V_T.SEQ, V_T.MUL, V_T.DIV, V_T.CPAR] 
        return

def parse_exp1() :
    # Donc get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR] :
    parse_exp0()
    parse_exp1_()

def parse_exp1_() :
    if get_current() == V_T.POW :
        consume_token(V_T.POW)
        parse_exp1()
    else : # Donc get_current() in [V_T.FACT, V_T.ADD, V_T.SUB, V_T.SEQ, V_T.MUL, V_T.DIV, V_T.CPAR]
        return

def parse_exp0() :
    if get_current() == V_T.NUM :
        consume_token(V_T.NUM)
    elif get_current() == V_T.CALC :
        consume_token(V_T.CALC)
    else : # Donc get_current() == V_T.OPAR
        consume_token(V_T.OPAR)
        parse_exp5()
        consume_token(V_T.CPAR)


#####################################
## Fonction principale de la calculatrice
## Appelle l'analyseur grammatical et retourne
## - None sans les attributs
## - la liste des valeurs des calculs avec les attributs

def parse(stream=sys.stdin):
    init_parser(stream)
    l = parse_input()
    consume_token(V_T.END)
    return l

#####################################
## Test depuis la ligne de commande

if __name__ == "__main__":
    print("@ Testing the calculator in infix syntax.")
    result = parse()
    if result is None:
        print("@ Input OK ")
    else:
        print("@ result = ", repr(result))
