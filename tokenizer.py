from typing import List, Tuple, Optional
import re

######################################################################################################################
# TOKEN STRUCT STUFF
######################################################################################################################

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

    def __repr__(self):
        return f"[LineInfo - line {self.line_number}:{self.line_start}-{self.line_end}]"

class FloatingToken(object):
    """
    A string with a defined meaning, given by the token_id. Unlike Tokens, FloatingTokens do not have line information
    stored about them.
    """
    def __init__(self, token_id: str, value: Optional[str] = None):
        self.token_id = token_id
        self.value = value

    def __repr__(self):
        return f"[FloatingToken - id \"{self.token_id}\", value \"{self.value}\"]"

class Token(object):
    def __init__(self, token: FloatingToken, line_info: LineInfo):
        """
        Creates a Token.

        :param token: The FloatingToken that stores syntax about the token itself.
        :param line_info: Information about where that token is in the input stream.
        """

        self.token_id = token.token_id
        self.value = token.value
        self.line_number = line_info.line_number
        self.line_start = line_info.line_start
        self.line_end = line_info.line_end

    def __repr__(self):
        return f"({self.token_id}, \"{self.value}\")"

######################################################################################################################
# EXCEPTIONS
######################################################################################################################

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

    def __repr__(self):
        return f'Could not find matching token for substring "{self.line[self.line_position:]}" ' + \
               f'({self.line_number}:{self.line_position})'

    def __str__(self):
        return self.__repr__()

class NoEndException(Exception):

    def __init__(self, line_number: int, line_position: int):
        self.line_number = line_number
        self.line_position = line_position

    def __repr__(self):
        return f'Could not find matching end comment for comment at ({self.line_number}:{self.line_position})'

    def __str__(self):
        return self.__repr__()

######################################################################################################################
# TOKENIZER STUFF
######################################################################################################################

class TokenMatcher(object):
    """
    A base class that will parse an input stream into a token.
    """

    def match_token(self, stream: str) -> Tuple[Optional[FloatingToken], int]:
        """
        Gets a token from an input stream.

        :param stream: The stream to parse
        :param line_number: The line number that we are currently on.
        :param line_start: The current position in the line.
        :return: Either None, or a tuple containing the found token and its length in the input stream.
        """
        pass

    def end_matching(self, tokens: List[Token]) -> None:
        """
        Gives opportunity for TokenMatchers to finish execution when the stream ends.
        For example, if CommentMatcher does not find a matching '*/', it should error here.
        """
        return None


class Tokenizer(object):
    matchers: List[TokenMatcher]

    def __init__(self):
        self.matchers = []
        self.whitespace_matcher = re.compile(r"^\s*")

    def __repr__(self):
        return ", ".join([i.__repr__() for i in self.matchers])

    def add_matcher(self, matcher: TokenMatcher) -> None:
        self.matchers.append(matcher)

    def match_tokens(self, stream: str) -> List[Token]:
        lines = stream.splitlines()

        output = []

        for line_number, line in enumerate(lines):
            line_pos = 0
            while line_pos < len(line):

                # remove leading whitespace
                whitespace_match = self.whitespace_matcher.match(line[line_pos:])
                line_pos += whitespace_match.end(0)
                if line_pos == len(line): break


                token, width = None, -1

                # find token
                for i in self.matchers:
                    token, width = i.match_token(line[line_pos:])
                    if token: break
                else:
                    raise BadTokenException(line_number, line_pos, line)

                # token found! populate line information
                line_info = LineInfo(line_number, line_pos, line_pos + width)
                line_pos += width

                # append to list
                output.append(Token(token, line_info))

        for i in self.matchers:
            i.end_matching(output)




        return output

######################################################################################################################
# SPECIAL TOKENMATCHERS
######################################################################################################################

class Symbol(object):
    """
    Represents a symbol to be matched by the symbol matcher.
    """

    def __init__(self, symbol: str, token: str):
        """
        Initializes a symbol.

        :param symbol: The symbol to match.
        :param token: The token id to give the matched symbol.
        """
        self.symbol = symbol
        self.token = token

    def __repr__(self):
        return f"(\"{self.symbol}\": {self.token})"

class SymbolMatcher(TokenMatcher):
    """
    A type of matcher that will match simple symbols. This is so you can forgo regex
    in the case of easy symbols, like '>' or '=='.
    """
    symbols: List[Symbol]

    def __init__(self, symbols: List[Symbol] = None):
        """
        Creates a SymbolMatcher.

        :param symbols: A set of symbols to match with by default. Must be of the form "SYMBOL TOKEN\nSYMBOL TOKEN" or
        ValueError will be raised.
        """
        self.symbols = []
        if symbols:
            self.symbols = symbols

    def add_symbol(self, symbol: str, token: str) -> None:
        """
        Adds a symbol to the list of symbols the matcher will attempt to match.

        :param symbol: The symbol to match.
        :param token: The token id to give the Token of the matched symbol.
        """
        self.symbols.append(Symbol(symbol, token))


    def __repr__(self):
        print(self.symbols)

    def add_symbols(self, symbols: List[Symbol]) -> None:
        """
        Adds a list of symbols to match.

        :param symbols: The symbols to match.
        """
        self.symbols.extend(symbols)

    def match_token(self, stream: str) -> Tuple[Optional[FloatingToken], int]:
        """
        Matches the first symbol in the list against a character stream.

        :param stream: The character stream to match against
        :returns: None if the stream doesn't match, or both the generated token and line position where the token ends.
        """

        for symbol in self.symbols:
            if stream.startswith(symbol.symbol):
                return FloatingToken(symbol.token, symbol.symbol), len(symbol.symbol)

        # no matches
        return None, -1


class CommentMatcher(TokenMatcher):
    is_multiline: bool
    ml_start: Symbol
    ml_end: Symbol
    comment: Symbol

    def __init__(self, multiline_start: Symbol, multiline_end: Symbol, comment: Symbol):
        self.is_multiline = False
        self.ml_start = multiline_start
        self.ml_end = multiline_end
        self.comment = comment

    def match_token(self, stream: str) -> Tuple[Optional[FloatingToken], int]:
        """
        Matches a comment in the character stream. If we are currently in a multiline comment, marks the comment
        as a character stream.

        :param stream: The character stream to match against
        :return: None if the stream doesn't match, or both the generated token and line position where the token ends.
        """

        # check end of multiline
        if (self.is_multiline):
            if (self.ml_end.symbol in stream):
                comment_end = stream.index(self.ml_end.symbol)

                self.is_multiline = False
                return FloatingToken(self.ml_end.token), comment_end + 2
            else:
                return FloatingToken(self.ml_end.token), len(stream)

        # check regular comment
        if (stream.startswith(self.comment.symbol)):
            return FloatingToken(self.comment.token), len(stream)

        # check multiline comment
        if (stream.startswith(self.ml_start.symbol)):
            # check ending on same line
            self.is_multiline = True
            return FloatingToken(self.ml_start.token), len(self.ml_start.token)

        return None, -1

    def end_matching(self, tokens: List[Token]) -> None:
        if (self.is_multiline):
            for token in tokens[::-1]:
                if token.token_id == self.ml_start.token:
                    raise NoEndException(token.line_number, token.line_start)


class RegexMatcher(TokenMatcher):
    token: str

    def __init__(self, regex: str, token: str):
        self.pattern = re.compile(regex)
        self.token = token

    def match_token(self, stream: str) -> Tuple[Optional[FloatingToken], int]:
        match = self.pattern.match(stream)
        if match:
            return FloatingToken(self.token, match.group(1)), len(match.group(0))
        return None, -1
