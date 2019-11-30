from typing import List
import re

class ExistsException(Exception):
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


def parse_fsm(stream: str):
    """
    Parses a full $fsm block, from starting $fsm to $endfsm, generating a structure with all the fsm data.
    This will then need to be interpreted.

    :param stream: the stream, starting with $fsm and ending with $endfsm, to parse.
    :return:
    """

    pass