#!/usr/bin/env python3

import lexer
import runtime

import rich

with open('test.dice', 'r') as file:
    tokens = lexer.Lexer(file.read()).lex()
runtime.run(tokens)
