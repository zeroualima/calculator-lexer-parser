#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : parser - requires Python version >= 3.10
"""

import math

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
    
def recover(suiv) :
    while (get_current() not in suiv) and (get_current() != V_T.END) :
        consume_token(get_current())
    return
 
#########################
## Parsing de input et exp

def parse_input(Li = []):
    try :
        if get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB] :
            n = parse_exp5(Li)
            consume_token(V_T.SEQ)
            L0 = parse_input(Li + [n])
            return L0
        elif get_current() == V_T.END :
            return Li
        else :
            raise unexpected_token("NUM, CALC, OPAR, SUB, or END")
    except ParserError :
        recover([V_T.END])
        return

def parse_exp5(L) :
    try :
        if get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB] :
            n0 = parse_exp4(L)
            n = parse_A(L, n0)
            return n
        else :
            raise unexpected_token("NUM, CALC, OPAR, or SUB")
    except ParserError :
        recover([V_T.SEQ, V_T.CPAR])
        return

def parse_A(L, n0) :
    try :
        if get_current() in [V_T.ADD, V_T.SUB] :
            n1 = parse_exp5_(L, n0)
            n = parse_A(L, n1)
            return n
        elif get_current() in [V_T.SEQ, V_T.CPAR] :
            return n0
        else :
            raise unexpected_token("ADD, SUB, SEQ, or CPAR")
    except ParserError :
        recover([V_T.SEQ, V_T.CPAR])
        return

def parse_exp5_(L, n0) :
    try :
        if get_current() ==  V_T.ADD :
            consume_token(V_T.ADD)
            n1 = parse_exp4(L)
            return n0 + n1
        elif get_current() == V_T.SUB :
            consume_token(V_T.SUB)
            n1 = parse_exp4(L)
            return n0 - n1
        else :
            raise unexpected_token("ADD or SUB")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.CPAR])
        return

def parse_exp4(L) :
    try :
        if get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR, V_T.SUB] :
            n0 = parse_exp3(L)
            n = parse_B(L, n0)
            return n
        else :
            raise unexpected_token("NUM, CALC, OPAR or SUB")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.CPAR])
        return

def parse_B(L, n0) :
    try :
        if get_current() in [V_T.MUL, V_T.DIV] :
            n1 = parse_exp4_(L, n0)
            n = parse_B(L, n1)
            return n
        elif get_current() in [V_T.ADD, V_T.SUB, V_T.SEQ, V_T.CPAR] :
            return n0
        else :
            raise unexpected_token("MUL, DIV, ADD, SUB, SEQ, or CPAR")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.CPAR])
        return

def parse_exp4_(L, n0) :
    try :
        if get_current() ==  V_T.MUL :
            consume_token(V_T.MUL)
            n1 = parse_exp3(L)
            return n0 * n1
        elif get_current() == V_T.DIV :
            consume_token(V_T.DIV) 
            n1 = parse_exp3(L)
            return n0 / n1
        else :
            raise unexpected_token("MUL or DIV")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.MUL, V_T.DIV, V_T.CPAR])
        return

def parse_exp3(L) :
    try :
        if get_current() == V_T.SUB :
            consume_token(V_T.SUB)
            n0 = parse_exp3(L)
            return - n0
        elif get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR] :
            n = parse_exp2(L) 
            return n
        else :
            raise unexpected_token("NUM, SUB, CALC, or OPAR")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.MUL, V_T.DIV, V_T.CPAR])
        return

def parse_exp2(L) :
    try :
        if get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR] :
            n0 = parse_exp1(L)
            n = parse_C(n0) 
            return n
        else :
            raise unexpected_token("NUM, CALC or OPAR")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.MUL, V_T.DIV, V_T.CPAR])
        return

def parse_C(n0) :
    try :
        if get_current() == V_T.FACT :
            consume_token(V_T.FACT)
            n1 = parse_C(math.factorial(n0))
            return n1
        elif get_current() in [V_T.ADD, V_T.SUB, V_T.SEQ, V_T.MUL, V_T.DIV, V_T.CPAR] :
            return n0
        else :
            raise unexpected_token("ADD, SUB, SEQ, MUL, DIV, FACT, or CPAR")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.MUL, V_T.DIV, V_T.CPAR])
        return

def parse_exp1(L) :
    try :
        if get_current() in [V_T.NUM, V_T.CALC, V_T.OPAR] :
            n1 = parse_exp0(L)
            n = parse_exp1_(L, n1)
            return n
        else :
            raise unexpected_token("NUM, CALC or OPAR")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.MUL, V_T.DIV, V_T.FACT, V_T.CPAR])
        return

def parse_exp1_(L, n1) :
    try :
        if get_current() == V_T.POW :
            consume_token(V_T.POW)
            n2 = parse_exp1(L)
            return math.pow(n1, n2)
        elif get_current() in [V_T.FACT, V_T.ADD, V_T.SUB, V_T.SEQ, V_T.MUL, V_T.DIV, V_T.CPAR] :
            return n1
        else :
            raise unexpected_token("FACT, MUL, DIV, ADD, SUB, SEQ, or CPAR")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.MUL, V_T.DIV, V_T.FACT, V_T.CPAR])
        return

def parse_exp0(L) :
    try :
        if get_current() == V_T.NUM :
            n = consume_token(V_T.NUM)
            return n
        elif get_current() == V_T.CALC :
            i = consume_token(V_T.CALC)
            return L[i - 1]
        elif get_current() == V_T.OPAR :
            consume_token(V_T.OPAR)
            n = parse_exp5(L)
            consume_token(V_T.CPAR)
            return n
        else :
            raise unexpected_token("NUM, CALC or OPAR")
    except ParserError :
        recover([V_T.SEQ, V_T.ADD, V_T.SUB, V_T.MUL, V_T.DIV, V_T.FACT, V_T.POW, V_T.CPAR])
        return


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
