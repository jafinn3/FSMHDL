import tokenizer as tkn
from tokenizer import Symbol
import json
import ast_gengen

from typing import List, Dict


def parse_to_symbols(input: List[Dict]) -> List[Symbol]:
    return [Symbol(x["symbol"], x["token"]) for x in input]

def build_tokenizer(file: str) -> tkn.Tokenizer:

    with open(file, "rb") as f:
        f_json = json.load(f)

        symbols = parse_to_symbols(f_json["symbols"])
        comments = parse_to_symbols(f_json["comment"])

        symbol_matcher = tkn.SymbolMatcher(symbols)
        comment_matcher = tkn.CommentMatcher(*comments)

        regex_matchers = [tkn.RegexMatcher(x["match"], x["token"]) for x in f_json["regex"]]

        tokenizer = tkn.Tokenizer()
        tokenizer.add_matcher(comment_matcher)
        tokenizer.add_matcher(symbol_matcher)
        for regex_matcher in regex_matchers:
            tokenizer.add_matcher(regex_matcher)

        return tokenizer


def main():

    # with open("sample1.sv", "r") as sample:
    #     text = sample.read()
    # tokenizer = build_tokenizer("symbols.json")
    # tokens = tokenizer.match_tokens(text)
    # for token in tokens:
    #     #if token.token.token_id.startswith("COMMENT"): continue
    #     print(f"{token.token.token_id:20} {token.token.value}")

    tokenizer = build_tokenizer("symbols.json")
    print(ast_gengen.variable_list(tokenizer.match_tokens("$in1, $in2, in3, in4"), 0))

if __name__ == "__main__":
    main()