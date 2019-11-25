from typing import List, Tuple, Optional
from enum import Enum, auto
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

        self.token = token
        self.line_info = line_info

    def __repr__(self):
        return f"({self.token.token_id}, \"{self.token.value}\")"

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
        return self.matchers.__repr__()

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

                if not token:
                    raise BadTokenException(line_number, line_pos, line)

                # token found! populate line information
                line_info = LineInfo(line_number, line_pos, line_pos + width)
                line_pos += width

                # append to list
                output.append(Token(token, line_info))




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
        return f"({self.symbol}: {self.token})"

class SymbolMatcher(TokenMatcher):
    """
    A type of matcher that will match simple symbols. This is so you can forgo regex
    in the case of easy symbols, like '>' or '=='.
    """
    symbols: List[Symbol]

    def __init__(self, symbols: str = None):
        """
        Creates a SymbolMatcher.

        :param symbols: A set of symbols to match with by default. Must be of the form "SYMBOL TOKEN\nSYMBOL TOKEN" or
        ValueError will be raised.
        """
        self.symbols = []
        if symbols:
            for line in symbols.splitlines():
                # generate split
                split = [x.strip() for x in line.strip().split(" ") if len(x) > 0 and not x.isspace()]

                if len(split) != 2:
                    raise ValueError(f'Couldn\'t find valid split for line "{line}"')

                self.symbols.append(Symbol(split[0], split[1]))

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
                if token.token.token_id == self.ml_start.token:
                    raise NoEndException(token.line_info.line_number, token.line_info.line_start)


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

if __name__ == "__main__":


    symb_match = SymbolMatcher(""" ?     SYMB_TERNARY_START
                                   :     SYMB_COLON
                                   !==   SYMB_XOR
                                   !=    SYMB_XOR
                                   !     SYMB_NOT
                                   ~^    SYMB_XNOR
                                   ~     SYMB_NOT
                                   &&    SYMB_AND
                                   &     SYMB_AND
                                   ||    SYMB_OR
                                   |     SYMB_OR
                                   ^~    SYMB_XNOR
                                   ^     SYMB_XOR
                                   ===   SYMB_XNOR
                                   ==    SYMB_XNOR
                                   =     SYMB_EQ
                                   <->   SYMB_XNOR
                                   ->    SYMB_ARROW
                                   ;     SYMB_SEMICOLON
                                   (     SYMB_LEFT_PAREN
                                   )     SYMB_RIGHT_PAREN
                                   ,     SYMB_COMMA
                                   *     SYMB_STAR
                                   begin SYMB_BEGIN
                                   end   SYMB_END
                                   0     SYMB_ZERO
                                   1     SYMB_ONE""")
    comm_match = CommentMatcher(Symbol("/*", "MULTILINE_START"),
                                Symbol("*/", "MULTILINE_END"),
                                Symbol("//", "SINGLE_COMMENT"))

    key_match = RegexMatcher(r'\$([A-Za-z_][A-Za-z0-9_]*)\b', "KEYWORD")
    var_match = RegexMatcher(r'([A-Za-z_][A-Za-z0-9_]*)\b', "VARIABLE")

    tokenizer = Tokenizer()
    tokenizer.add_matcher(comm_match)
    tokenizer.add_matcher(symb_match)
    tokenizer.add_matcher(key_match)
    tokenizer.add_matcher(var_match)

    print(var_match.match_token("input  logic in"))

    tokens = tokenizer.match_tokens(r"""
/* * * * * * * * * * *
 *      testFSM      *
 * * * * * * * * * * *
 *
 * Here is a sample module to highlight the syntax 
 * of our FSM HDL.
 */
$fsm testFSM (
  input  logic in1, in2, in3,
  output logic out1, out2);

  /* Declares all possible states in the FSM */
  $states init, read1, read2, read3,
        read4, read5, read6$;

  /* Define all possible transitions */
  $transitions begin
    init -> read1: in1 & in2;
    init -> read2: in1 & ~in2;
    read1 -> read1: in3;
    read1 -> init: in2 & ~in3;
    read2 -> read3: in1 | in2 | in3;
    read3 -> init: 1;
  end

  /* Define asserted outputs if the FSM is a moore machine. */
  $moore_out begin
    init: out1;
    read1: out2;
    read2: out2, out1;
    read3: out2, out1;

    /* Specify default output values (optional) */
    default: begin
      //out1 = 0;
      //out2 = 0;
      ~out1, ~out2;
    end
  end

  /* Define asserted outputs if the FSM is a mealy machine */
  $mealy_out begin
    init -> read1: out1;
    init -> read2: out2 = in1; // There might be a nicer way of doing something
                               // like this. 
    read1 -> read1: out1, out2;
    read3 -> init: out1 = in1, out2;
  end
$endfsm""")

    for token in tokens:
        if token.token.token_id in ["MULTILINE_START", "MULTILINE_END", "SINGLE_COMMENT"]: continue
        print(f"{token.token.token_id:15} {token.token.value}")

#                    ^

# KEYWORD="control" VARIABLE [SYMB_COMMA VARIABLE] SYMB_SEMICOLON