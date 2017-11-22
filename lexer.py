"""Lexer

Lexical analyzator for discovering states
"""
__author__ = 'ales lerch'

import re
from sys import stdin
from enum import Enum
from sys import exit
import itertools

class LexerState(Enum):
    Q_S = 0
    Q_A1 = 1
    Q_AF = 2
    Q_B1 = 3
    Q_B2 = 4
    Q_B1F = 5
    Q_B2F = 6
    Q_C1 = 7
    Q_D1 = 8
    Q_D2 = 9
    Q_F = 10


class TokenType(Enum):
    identifier = 0
    integer = 1
    string = 2
    left_paren = 3 #(
    right_paren = 4 #)
    left_braces = 5 #{
    right_braces = 6 #}
    left_closed_braces = 7 #[
    right_closed_braces = 8 #]
    line_feed = 9 #\n
    tab = 10
    space = 11
    comma = 12 #,
    arg_sep = 13 #:
    fn_conj = 14 # >
    assigment_op = 15 #=
    dot = 16 #.
    semicolon = 17 #;
    real = 18
    end_of_file = 19


class Token:

    def __init__(self, line, value, token_type):
        self.line = line
        self.value = value
        self.token_type = token_type
        #think about splitting input text for parts

    def __repr__(self):
        return f"[line: {self.line+1}, type: {self.token_type}] {self.value}"

    def check_input(self, input_file):
        if input_file:
            with open(input_file) as f:
                input_file = f.read()
            return input_file
        else:
            return stdin

    def lexer(self, input_file = ""):
        last_line_number = 0
        id_number_free = re.compile("[a-zA-Z+-\/\*]+")
        id_complex = re.compile("[a-zA-Z0-9_+-\/\*']+")
        universal = re.compile("[,:>=\.\[\]]+")
        input_file = self.check_input(input_file)
        with input_file as content:
            for line, line_number in zip(content, itertools.count()):
                value = ""
                state = LexerState.Q_S
                last_line_number = line_number
                while line != "":
                    if state == LexerState.Q_S:
                        if id_number_free.match(line[0]):
                            value += line[0]
                            line = line[1:]
                            state = LexerState.Q_A1
                        elif line[0] == '"':
                            line = line[1:]
                            state = LexerState.Q_D1
                        elif line[0] in ('+','-') or line[0].isdigit():
                            value += line[0]
                            line = line[1:]
                            state = LexerState.Q_B1
                        elif line[0] == '#':
                            line = line[1:]
                            state  = LexerState.Q_C1
                        elif line[0] == '(':
                            line = line[1:]
                            yield Token(last_line_number,'(',TokenType.left_paren)
                        elif line[0] == ')':
                            line = line[1:]
                            yield Token(last_line_number,')',TokenType.right_paren)
                        elif line[0] == '{':
                            line = line[1:]
                            yield Token(last_line_number,'{',TokenType.left_braces)
                        elif line[0] == '}':
                            line = line[1:]
                            yield Token(last_line_number,'}',TokenType.right_braces)
                        elif line[0] == ',':
                            line = line[1:]
                            yield Token(last_line_number,',',TokenType.comma)
                        elif line[0] == ':':
                            line = line[1:]
                            yield Token(last_line_number,':',TokenType.arg_sep)
                        elif line[0] == '>':
                            line = line[1:]
                            yield Token(last_line_number,'>',TokenType.fn_conj)
                        elif line[0] == '=':
                            line = line[1:]
                            yield Token(last_line_number,'=',TokenType.assigment_op)
                        elif line[0] == ';':
                            line = line[1:]
                            yield Token(last_line_number,';',TokenType.semicolon)
                        elif line[0] == '\n':
                            line = line[1:]
                            yield Token(last_line_number,'\n',TokenType.line_feed)
                        elif line[0] == ' ':
                            line = line[1:]
                            yield Token(last_line_number,' ',TokenType.space)
                        elif line[0] == '.':
                            line = line[1:]
                            yield Token(last_line_number,'.',TokenType.dot)
                        else:
                            print(f"[Error][LA] found uknown character {line[0]}, {state}")
                            exit(1)

                    elif state == LexerState.Q_A1:
                        if id_number_free.match(line[0]) or id_complex.match(line[0]):
                            value += line[0]
                            line = line[1:]
                            state = LexerState.Q_AF
                        else:
                            yield Token(last_line_number,value,TokenType.identifier)
                            value = ""
                            state = LexerState.Q_S
                            #print(f"[Error][LA] found uknown character {line[0]} {state}")
                            #exit(1)

                    elif state == LexerState.Q_AF:
                        if id_number_free.match(line[0]) or id_complex.match(line[0]):
                            value += line[0]
                            line = line[1:]
                        else:
                            yield Token(last_line_number,value,TokenType.identifier)
                            value = ""
                            state = LexerState.Q_S

                    elif state == LexerState.Q_B1:
                        if line[0].isdigit():
                            value += line[0]
                            line = line[1:]
                            state = LexerState.Q_B1F
                        elif line[0] in ('e','E','.'):
                            value += line[0]
                            line = line[1:]
                            state = LexerState.Q_B2
                        else:
                            yield Token(last_line_number,float(value),TokenType.integer)
                            value = ""
                            state = LexerState.Q_S
                            #print(f"[Error][LA] found uknown character {line[0]} {state}")
                            #exit(1)

                    elif state == LexerState.Q_B1F:
                        if line[0].isdigit():
                            value += line[0]
                            line = line[1:]
                        elif line[0] in ('e','E','.'):
                            value += line[0]
                            line = line[1:]
                            state = LexerState.Q_B2
                        else:
                            yield Token(last_line_number,float(value),TokenType.integer)
                            value = ""
                            state = LexerState.Q_S

                    elif state == LexerState.Q_B2:
                        if line[0].isdigit():
                            value += line[0]
                            line = line[1:]
                            state = LexerState.Q_B2F
                        else:
                            print(f"[Error][LA] found uknown character {line[0]} {state}")
                            exit(1)

                    elif state == Q_B2F:
                        if line[0].isdigit():
                            value += line[0]
                            line = line[1:]
                        else:
                            yield Token(last_line_number,float(value),TokenType.real)
                            value = ""
                            state = LexerState.Q_S

                    elif state == LexerState.Q_C1:
                        if line[0] in ('\t',' ') or universal.match(line[0]) or\
                                id_complex.match(line[0]):
                            value += line[0]#do i need to save commentary content?
                            line = line[1:]
                        elif line[0] == '\n':
                            value = ""
                            state = LexerState.Q_S
                        else:
                            print(f"[Error][LA] found uknown character {line[0]} {state}")
                            exit(1)

                    elif state == LexerState.Q_D1:
                        if line[0] in ('\\','\t',' ') or universal.match(line[0]) or\
                                id_complex.match(line[0]):
                            value += line[0]
                            line = line[1:]
                            status = LexerState.Q_D2
                        elif line[0] == '"':
                            yield Token(last_line_number,value,TokenType.string)
                            value = ""
                            state = LexerState.Q_S
                        else:
                            print(f"[Error][LA] found uknown character {line[0]} {state}")
                            exit(1)

                    elif state == LexerState.Q_D2:
                        if line[0] in ('\\','"','\t',' ') or universal.match(line[0]) or\
                                id_complex.match(line[0]):
                            value += line[0]
                            line = line[1:]
                            state = LexerState.Q_D1
                        else:
                            print(f"[Error][LA] found uknown character {line[0]} {state}")
                            exit(1)
                if value != "":
                    print("[Warning][LA] Some data has not been checked by LA:")
                    print(value)
        yield Token(last_line_number, "EOF", TokenType.end_of_file)

if __name__ == "__main__":
    t = Token(0,'',TokenType.space)
    for i in t.lexer():
        print(i)