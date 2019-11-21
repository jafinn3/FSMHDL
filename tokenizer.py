from typing import List, Tuple, Optional
from enum import Enum, auto
import re

class TokenID(Enum):
    """
    An enum representing all valid token types.
    """

    # Symbols
    SYMBOL_TERNARY_START = auto()   # ?
    SYMBOL_COLON = auto()           # :
    SYMBOL_NOT = auto()             # ! ~
    SYMBOL_AND = auto()             # & &&
    SYMBOL_OR = auto()              # | ||
    SYMBOL_XOR = auto()             # ^ != !==
    SYMBOL_XNOR = auto()            # ^~ ~^ == === <->
    SYMBOL_ARROW = auto()           # ->
    SYMBOL_SEMICOLON = auto()       # ;
    SYMBOL_LEFT_PAREN = auto()      # (
    SYMBOL_RIGHT_PAREN = auto()     # )
    SYMBOL_COMMA = auto()           # ,
    SYMBOL_STAR = auto()            # *

    # words
    KEYWORD_BEGIN = auto()          # begin
    KEYWORD_END = auto()            # end
    KEYWORD_GENERAL = auto()        # \$[a-zA-Z][a-zA-Z0-9_]*
    VARIABLE_OR_STATE = auto()      # [a-zA-Z][a-zA-Z0-9_]





class LineInfo(object):
    """
    Stores information about the line of a token/AST node. Used to generate error messages.
    """

    def __init__(self, line_number: int, line_start: int, line_end: Optional[int] = None):
        """
        :param line_number: The line number.
        :param line_start: The start of the relevant piece of text we're referencing.
        :param line_end: The end of the relevant piece of text we're referencing.
        """
        self.line_number = line_number
        self.line_start = line_start
        self.line_end = line_end

class FloatingToken(object):
    """
    A string with a defined meaning, given by the string ID. Unlike Tokens, FloatingTokens do not have line information
    stored about them.
    """
    def __init__(self, token_id: TokenID, value: Optional[str] = None):
        self.token_id = token_id
        self.value = value


class Token(object):
    def __init__(self, token: FloatingToken, line_info: LineInfo):
        """
        Creates a Token.

        :param token: The FloatingToken that stores syntax about the token itself.
        :param line_info: Information about where that token is in the input stream.
        """

        self.token = token
        self.line_info = line_info


class TokenMatcher(object):
    """
    A base class that will parse an input stream into a token.
    """
    def match_token(self, stream: str) -> Optional[Tuple[FloatingToken, int]]:
        """
        Gets a token from an input stream.

        :param stream: The stream to parse
        :param line_number: The line number that we are currently on.
        :param line_start: The current position in the line.
        :return: Either None, or a tuple containing the found token and its length in the input stream.
        """
        pass


class FloatingTokenizer(object):
    """
    A wrapper for a list of matchers that will parse an input stream into tokens. This does not give line information.
    """
    matchers: List[TokenMatcher] = []

    def add_matcher(self, matcher: TokenMatcher) -> None:
        """
        Adds a TokenMatcher to the list of matchers that the tokenizer uses.

        :param matcher: The TokenMatcher to add.
        """
        self.matchers.append(matcher)

    def match_token(self, stream: str) -> Optional[Tuple[FloatingToken, int]]:
        """
        Matches a token from an input stream.

        :param stream: The stream to match against.
        :return: Either None or the
        """
        for i in self.matchers:
            match = i.match_token(stream)
            if match:
                return match
        return None


class BadTokenException(Exception):
    """Raised when a matching token did not exist in the given tokenizer."""

    def __init__(self, line_number: int, line_position: int, line: str):
        """
        :param line_number: The line number where this error was found.
        :param line_position: The position in the line where this error was found.
        :param line: A copy of the erroring line itself, for error printing.
        """
        self.line_number = line_number
        self.line_position = line_position
        self.line = line


class Tokenizer(object):
    tokenizer: FloatingTokenizer

    def __init__(self):
        self.tokenizer = FloatingTokenizer()

    def add_matcher(self, matcher: TokenMatcher) -> None:
        self.tokenizer.add_matcher(matcher)

    def match_tokens(self, stream: str) -> List[Token]:
        lines = stream.splitlines()
        for line_number, line in enumerate(lines):
            pass #TODO

class Symbol(object):
    """
    Represents a symbol to be matched by the symbol matcher.
    """

    def __init__(self, symbol: str, token: TokenID):
        """
        Initializes a symbol.

        :param symbol: The symbol to match.
        :param token: The TokenID to give the matched symbol.
        """
        self.symbol = symbol
        self.token = token

class SymbolMatcher(TokenMatcher):
    """
    A type of matcher that will match simple symbols. This is so you can forgo regex
    in the case of easy symbols, like '>' or '=='.
    """
    symbols: List[Symbol]

    def __init__(self, symbols: Optional[List[Symbol]] = None):
        """
        Creates a SymbolMatcher.

        :param symbols: A set of symbols to match with by default.
        """
        if symbols:
            self.symbols = symbols
        else:
            self.symbols = []

    def add_symbol(self, symbol: str, token: TokenID) -> None:
        """
        Adds a symbol to the list of symbols the matcher will attempt to match.

        :param symbol: The symbol to match.
        :param token: The TokenID to give the Token of the matched symbol.
        """
        self.symbols.append(Symbol(symbol, token))

    def add_symbols(self, symbols: List[Symbol]) -> None:
        """
        Adds a list of symbols to match.

        :param symbols: The symbols to match.
        """
        self.symbols.extend(symbols)

    def match_token(self, stream: str) -> Optional[Tuple[FloatingToken, int]]:
        """
        Matches the first symbol in the list against a character stream.

        :param stream: The character stream to match against
        :returns: None if the stream doesn't match, or both the generated token and line position where the token ends.
        """

        for symbol in self.symbols:
            if stream.startswith(symbol.symbol):
                return FloatingToken(symbol.token, symbol.symbol), len(symbol.symbol)
