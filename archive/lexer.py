#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet TL : lexer de la calculatrice
"""

import sys
import enum
import definitions as defs


# Pour lever une erreur, utiliser: raise LexerError("message décrivant l'erreur dans le lexer")
class LexerError(Exception):
    pass


#################################
# Variables et fonctions internes (privées)

# Variables privées : les trois prochains caractères de l'entrée
current_char1 = ''
current_char2 = ''
current_char3 = ''

# Initialisation: on vérifie que EOI n'est pas dans V_C et on initialise les prochains caractères
def init_char():
    global current_char1, current_char2, current_char3
    # Vérification de cohérence: EOI n'est pas dans V_C ni dans SEP
    if defs.EOI in defs.V_C:
        raise LexerError('character ' + repr(defs.EOI) + ' in V_C')
    defs.SEP = {' ', '\n', '\t'} - set(defs.EOI)
    defs.V = set(tuple(defs.V_C) + (defs.EOI,) + tuple(defs.SEP))
    current_char1 = defs.INPUT_STREAM.read(1)
    # print("@", repr(current_char1))  # decomment this line may help debugging
    if current_char1 not in defs.V:
        raise LexerError('Character ' + repr(current_char1) + ' unsupported')
    if current_char1 == defs.EOI:
        current_char2 = defs.EOI
        current_char3 = defs.EOI
    else:
        current_char2 = defs.INPUT_STREAM.read(1)
        # print("@", repr(current_char2))  # decomment this line may help debugging
        if current_char2 not in defs.V:
            raise LexerError('Character ' + repr(current_char2) + ' unsupported')
        if current_char2 == defs.EOI:
            current_char3 = defs.EOI
        else:
            current_char3 = defs.INPUT_STREAM.read(1)
            # print("@", repr(current_char3))  # decomment this line may help debugging
            if current_char3 not in defs.V:
                raise LexerError('Character ' + repr(current_char3) + ' unsupported')

    return

# Accès aux caractères de prévision
def peek_char3():
    global current_char1, current_char2, current_char3
    return (current_char1 + current_char2 + current_char3)

def peek_char1():
    global current_char1
    return current_char1

# Avancée d'un caractère dans l'entrée
def consume_char():
    global current_char1, current_char2, current_char3
    if current_char2 == defs.EOI: # pour ne pas lire au delà du dernier caractère
        current_char1 = defs.EOI
        return
    if current_char3 == defs.EOI: # pour ne pas lire au delà du dernier caractère
        current_char1 = current_char2
        current_char2 = defs.EOI
        return
    next_char = defs.INPUT_STREAM.read(1)
    # print("@", repr(next_char))  # decommenting this line may help debugging
    if next_char in defs.V:
        current_char1 = current_char2
        current_char2 = current_char3
        current_char3 = next_char
        return
    raise LexerError('Character ' + repr(next_char) + ' unsupported')

def expected_digit_error(char):
    return LexerError('Expected a digit, but found ' + repr(char))

def unknown_token_error(char):
    return LexerError('Unknown start of token ' + repr(char))

# Initialisation de l'entrée
def reinit(stream=sys.stdin):
    global input_stream, current_char1, current_char2, current_char3
    assert stream.readable()
    defs.INPUT_STREAM = stream
    current_char1 = ''
    current_char2 = ''
    current_char3 = ''
    init_char()


#################################
## Automates pour les entiers et les flottants


def read_INT_to_EOI():
    accepted = True
    if peek_char1() not in defs.DIGITS :
        accepted = False
    while peek_char1() in defs.DIGITS :
        consume_char()
    if peek_char1() != defs.EOI :
        accepted = False
        while peek_char1() != defs.EOI :
            consume_char()
    consume_char()
    return accepted
    
    
def read_FLOAT_to_EOI():
    if peek_char1() == '.' :
        consume_char()
        if peek_char1() in defs.DIGITS :
            while peek_char1() in defs.DIGITS :
                consume_char()
            if peek_char1() == defs.EOI :
                return True
        return False
    while peek_char1() in defs.DIGITS :
        consume_char()
    if peek_char1() == '.' :
        consume_char()
        while peek_char1() in defs.DIGITS :
            consume_char()
        if peek_char1() == defs.EOI :
            return True
        return False
    return False


#################################
## Lecture de l'entrée: entiers, nombres, tokens


# Lecture d'un chiffre, puis avancée et renvoi de sa valeur
def read_digit():
    current_char = peek_char1()
    if current_char not in defs.DIGITS:
        raise expected_digit_error(current_char)
    value = eval(current_char)
    consume_char()
    return value


# Lecture d'un entier en renvoyant sa valeur
def read_INT():
    value = 0
    if peek_char1() not in defs.DIGITS:
        raise expected_digit_error(peek_char1())
    while peek_char1() in defs.DIGITS :
        value = 10 * value + int(peek_char1())
        consume_char()
    return value


global int_value
global exp_value
global sign_value

# Lecture d'un nombre en renvoyant sa valeur
def read_NUM():
    global int_value, exp_value
    exp_value = 0
    if peek_char1() == '.' :
        consume_char()
        frac = read_INT()
        nb_ap_virgule = len(str(frac))
        exp_value -= nb_ap_virgule
        int_value = frac
        if current_char1 in ['e', 'E'] :
            if current_char2 in defs.DIGITS :
                consume_char()
                exp_value += read_INT()
            elif (current_char2 in ['+', '-']) & (current_char3 in defs.DIGITS) :
                if current_char2 == '+' :
                    consume_char()
                    consume_char()
                    exp_value += read_INT()
                elif current_char2 == '-' :
                    consume_char()
                    consume_char()
                    exp_value -= read_INT()
        return int_value * 10**exp_value
    
    elif peek_char1() in defs.DIGITS :
        int_value = read_INT()
        if peek_char1() == '.' :
            consume_char()
        if peek_char1() in defs.DIGITS :
            frac = read_INT()
            nb_ap_virgule = len(str(frac))
            exp_value -= nb_ap_virgule
            int_value = int_value * 10**nb_ap_virgule + frac
        if current_char1 in ['e', 'E'] :
            if current_char2 in defs.DIGITS :
                consume_char()
                exp_value += read_INT()
            elif (current_char2 in ['+', '-']) & (current_char3 in defs.DIGITS) :
                if current_char2 == '+' :
                    consume_char()
                    consume_char()
                    exp_value += read_INT()
                elif current_char2 == '-' :
                    consume_char()
                    consume_char()
                    exp_value -= read_INT()
        return int_value * 10**exp_value


# Parse un lexème (sans séparateurs) de l'entrée et renvoie son token.
# Cela consomme tous les caractères du lexème lu.
def read_token_after_separators():
    c = peek_char1()
    if c in defs.DIGITS or c == '.':
        return (defs.V_T.NUM, read_NUM())
    if c == defs.EOI:
        consume_char()
        return (defs.V_T.END, None)
    if c in defs.TOKEN_MAP:
        token = defs.TOKEN_MAP[c]
        consume_char()
        if token == defs.V_T.CALC:        # CAS SPECIAL : #
            return (token, read_INT())
        return (token, None)
    print("@", repr(c))  # decommenting this line may help debugging
    raise unknown_token_error(f"Caractère inattendu : {c}")


# Donne le prochain token de l'entrée, en sautant les séparateurs éventuels en tête
# et en consommant les caractères du lexème reconnu.
def next_token():
    while peek_char1() in defs.SEP :
        consume_char()
    return read_token_after_separators()


#################################
## Fonctions de tests

def test_INT_to_EOI():
    print("@ Testing read_INT_to_EOI. Type a word to recognize.")
    reinit()
    if read_INT_to_EOI():
        print("Recognized")
    else:
        print("Not recognized")

def test_FLOAT_to_EOI():
    print("@ Testing read_FLOAT_to_EOI. Type a word to recognize.")
    reinit()
    if read_FLOAT_to_EOI():
        print("Recognized")
    else:
        print("Not recognized")

def test_lexer():
    print("@ Testing the lexer. Just type tokens and separators on one line")
    reinit()
    token, value = next_token()
    while token != defs.V_T.END:
        print("@", defs.str_attr_token(token, value))
        token, value = next_token()

if __name__ == "__main__":
    ## Choisir une seule ligne à décommenter
    # test_INT_to_EOI()
    # test_FLOAT_to_EOI()
    test_lexer()
