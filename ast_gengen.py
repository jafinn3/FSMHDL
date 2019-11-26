"""
Code to implement a recursive descent parser.
Supports:
optional parameters as []
repeating parameters as {}
alternative parameters with |
saving parameters when preceded by *
recognizing all caps as terminal symbols

Doesn't support:
nested [] or {} (use
"""
from typing import Callable, Tuple, List
import tokenizer as tkn
from functools import partial

def optional(subexpr: Callable[[int], Tuple[int, bool]], pos: int) -> Tuple[int, bool]:
    newpos, success = subexpr(pos)
    if success:
        return newpos, True
    else:
        return pos, True

def concat(subexprs: List[Callable[[int], Tuple[int, bool]]], pos: int) -> Tuple[int, bool]:
    newpos = pos
    for subexpr in subexprs:
        newpos, success = subexpr(newpos)
        if not success:
            return pos, False
    return newpos, True

def altern(subexprs: List[Callable[[int], Tuple[int, bool]]], pos: int) -> Tuple[int, bool]:
    for subexpr in subexprs:
        newpos, success = subexpr(pos)
        if success:
            return newpos, True
    return pos, False

def kleene(subexpr: Callable[[int], Tuple[int, bool]], pos: int) -> Tuple[int, bool]:
    retpos = pos
    while True:
        newpos, success = subexpr(retpos)
        if not success:
            return retpos, True
        retpos = newpos

def terminal_match(tokens: List[tkn.Token], id: str, val: str, pos: int) -> Tuple[int, bool]:
    if pos >= len(tokens):
        return pos, False

    if tokens[pos].token.token_id != id:
        return pos, False
    if not val:
        return pos + 1, True
    if tokens[pos].token.value == val:
        return pos + 1, True
    return pos, False


def variable_list(tokens: List[tkn.Token], pos: int) -> Tuple[int, bool]:
    return partial(concat, [
        partial(terminal_match, tokens, "VARIABLE", None),
        partial(kleene, partial(concat, [
            partial(terminal_match, tokens, "SYMB_COMMA", None),
            partial(terminal_match, tokens, "VARIABLE", None)
        ]))
    ])(pos)