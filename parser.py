from typing import List, Optional
import re
from tokenizer import Token, Tuple

class ExistsException(Exception):
    pass


class ExpectsException(Exception):
    pass

class Transition(object):
    def __init__(self, to: str, condition: str):
        self.to: str = to
        self.condition: str = condition

    def __eq__(self, other):
        return self.to == other.to

class State(object):
    def __init__(self, name: str):
        self.name: str = name
        self.transitions: List[Transition] = []

    def add_transition(self, transition: Transition):
        if transition in self.transitions:
            raise ExistsException()

        self.transitions.append(transition)

class FSMData(object):
    def __init__(self):
        self.inputs: List[str] = []
        self.outputs: List[str] = []
        self.states: List[State] = []
        self.name: str = ""

    def set_name(self, name: str):
        if self.name != "":
            raise ExistsException()

        self.name = name

    def add_input(self, input: str):
        if input in self.inputs:
            raise ExistsException()

        self.inputs.append(input)

    def add_output(self, output: str):
        if output in self.outputs:
            raise ExistsException()

        self.outputs.append(output)

    def add_state(self, state: State):
        if state in self.states:
            raise ExistsException()

        self.states.append(state)


class TokenHolder(object):

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def find_match(self, pos: int, token_id: str, value: Optional[str] = None) -> Tuple[bool, Optional[Token]]:
        if pos >= len(self.tokens):
            return False, None

        token = self.tokens[pos]

        if (token.token_id != token_id):
            return False, token

        if value and value != token.value:
            return False, token

        return True, token

    def expect_match(self, pos: int, token_id: str, value: Optional[str] = None) -> None:
        if pos >= len(self.tokens):
            raise ExpectsException(f"Expected {token_id}, got EOF")

        token = self.tokens[pos]

        if (token.token_id != token_id):
            raise ExpectsException(f"Expected {token_id}, got {token.token_id}")

        if value and value != token.value:
            raise ExpectsException(f"Expected {value}, got {token.value}")

def parse_header(tokens: TokenHolder, pos: int,
                 data: FSMData) -> int:

    success, name = tokens.find_match(pos, "VARIABLE")
    if not success:
        raise ExpectsException("Name expected")

    data.set_name(name.value)
    pos += 1

    success, _ = tokens.find_match(pos, "SYMB_LEFT_PAREN")
    if not success:
        raise ExpectsException("( expected")
    pos += 1

    got_input = False
    got_output = False
    while True:

        # get first declarator
        success, declarator = tokens.find_match(pos, "LOGIC_DECLARATOR")
        if not success:
            # we want a different error if we don't end on a SYMB_RIGHT_PAREN
            tokens.expect_match(pos, "SYMB_RIGHT_PAREN")
            break

        pos += 1
        is_output = declarator.value == "output"

        if is_output:
            got_output = True
        else:
            got_input = True

        got_var = False
        while True:

            success, var = tokens.find_match(pos, "VARIABLE")
            if not success:
                # if we don't get a variable here, we expect a new "input logic" or "output logic",
                # not a final parenthesis
                tokens.expect_match(pos, "LOGIC_DECLARATOR")
                break

            if is_output:
                data.add_output(var.value)
            else:
                data.add_input(var.value)

            pos += 1
            got_var = True
            success, _ = tokens.find_match(pos, "SYMB_COMMA")
            if not success:
                # if we don't get a comma here, we expect the end parenthesis, not a new logic declarator
                tokens.expect_match(pos, "SYMB_RIGHT_PAREN")
                break

            pos += 1

        if not got_var:
            raise ExpectsException("No variables defined after input/output logic")

    if not got_input:
        raise ExpectsException("FSM has no input variables")

    if not got_output:
        raise ExpectsException("FSM has not output variables")

    tokens.expect_match(pos, "SYMB_RIGHT_PAREN")
    pos += 1
    tokens.expect_match(pos, "SYMB_SEMICOLON")
    pos += 1

    return pos








def parse_fsm(stream: List[Token]):
    """
    Parses a full $fsm block, from starting $fsm to $endfsm, generating a structure with all the fsm data.
    This will then need to be interpreted.

    :param stream: the stream, starting with $fsm and ending with $endfsm, to parse.
    :return:
    """

    tokens = TokenHolder(stream)
    data = FSMData()
    pos = parse_header(tokens, 0, data)

    print(data.inputs)
    print(data.outputs)
    print(data.name)