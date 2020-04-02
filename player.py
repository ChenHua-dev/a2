"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple, Dict
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    acc = []
    id_index = 0
    for _ in range(num_human):
        goals = generate_goals(1)
        acc.append(HumanPlayer(id_index, goals[0]))
        id_index += 1

    for _ in range(num_random):
        goals = generate_goals(1)
        acc.append(RandomPlayer(id_index, goals[0]))
        id_index += 1

    for item in smart_players:
        goals = generate_goals(1)
        acc.append(SmartPlayer(id_index, goals[0], item))
        id_index += 1

    return acc


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
        - block.level <= level <= max_depth
    """
    x = block.position[0]
    y = block.position[1]
    d = round(block.size / 2.0)
    target_x = location[0]
    target_y = location[1]

    if x <= target_x < x + block.size and y <= target_y < y + block.size:
        if len(block.children) == 0:
            return block
        elif level == 0:
            return block
        else:
            if target_x >= x + d and target_y < y + d:
                return _get_block(block.children[0], location, level - 1)
            elif target_x < x + d and target_y < y + d:
                return _get_block(block.children[1], location, level - 1)
            elif target_x < x + d and target_y >= y + d:
                return _get_block(block.children[2], location, level - 1)
            elif target_x >= x + d and target_y >= y + d:
                return _get_block(block.children[3], location, level - 1)
            else:
                return None
    else:
        return None


def _generate_random_block(board: Block) -> \
        Tuple[Block, Optional[Block], Tuple[int, int], int]:
    """Return a tuple that contains the copy of the original <board>,
    randomly generated block based on random position and random level.
    If the randomly selected position is not valid, return None instead of the
    random block.
    """
    copied = board.create_copy()

    # Random position
    x = random.randint(copied.position[0], copied.position[0] + copied.size - 1)
    y = random.randint(copied.position[1], copied.position[1] + copied.size - 1)
    random_pos = (x, y)

    # Random level
    random_level = random.randint(copied.level, copied.max_depth)
    random_block = _get_block(copied, random_pos, random_level)

    return copied, random_block, random_pos, random_level


def _generate_random_move(actions: Dict[int, Tuple[str, Optional[int]]]) -> \
        Tuple[str, Optional[int]]:
    """Return a randomly generated valid action from <actions>, except for PASS.
    """
    # Generating random move
    potential_moves = []
    for value in actions.values():
        if value[0] != PASS[0]:
            potential_moves.append(value)
    action = random.choice(potential_moves)
    return action


def _validate_move(move: Tuple[str, Optional[int]], block: Block,
                   goal: Goal) -> bool:
    """Return boolean variable to see if <move> has been successfully applied to
    <block>. True if <move> is successful, false otherwise.
    """
    if move in [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE]:
        return block.rotate(move[1])
    elif move in [SWAP_HORIZONTAL, SWAP_VERTICAL]:
        return block.swap(move[1])
    elif move == SMASH:
        return block.smash()
    elif move == PAINT:
        return block.paint(goal.colour)
    elif move == COMBINE:
        return block.combine()
    else:
        return False


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    """Return string of description of <action> and possible direction of
    <action>, and <block> that <action> will be applied to.

    Note:
        - direction located at index 1 of <action> could be None

    """
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, min(self._level, board.max_depth))

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """Generate a random player in the Blocky game.

    === Private Attributes ===
    _proceed:
        True when the player should make a move, False when the player should
        wait.
    """
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this RandomPlayer with the given <player_id>, <goal> and
        initialize <_proceed> to False
        """
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return None for random player. Block selection is through
        generate_move method
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the human player
        allowing the random player to start its move. The allowing signal is
        pressing the mouse button down 1 time.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None
        valid_move = False
        while valid_move is False:
            random_result = _generate_random_block(board)
            if random_result[1] is not None:
                action = _generate_random_move(KEY_ACTION)
                valid_move = _validate_move(action, random_result[1], self.goal)
                if valid_move:
                    block = _get_block(board, random_result[2],
                                       random_result[3])
                    move = _create_move(action, block)

                    self._proceed = False
                    return move


class SmartPlayer(Player):
    """Generate a smart player in the Blocky game.

    === Private Attributes ===
    _proceed:
        True when the player should make a move, False when the player should
        wait.
    _difficulty:
        A integer that shows the number of moves a smart player can generate for
        each turn
    """
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        """Initialize this SmartPlayer with the given <player_id>, <goal>,
        <difficulty>.
        Initialize <_proceed> to False
        """
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return None for smart player. Block selection is through
        generate_move method.
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the human player
        allowing the random player to start its move. The allowing signal is
        pressing the mouse button down 1 time.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None
        best_score, best_action, best_pos, best_level = None, None, None, None
        for _ in range(self._difficulty):
            valid_move = False
            stop_criteria = {}
            while valid_move is False and \
                    len(stop_criteria) < len(KEY_ACTION) - 1:
                random_result = _generate_random_block(board)
                action = None
                if random_result[1] is None:
                    valid_move = False
                else:
                    action = _generate_random_move(KEY_ACTION)
                    valid_move = _validate_move(action, random_result[1],
                                                self.goal)

                if valid_move and action is not None and \
                        self.goal.score(random_result[0]) > \
                        self.goal.score(board) and \
                        (best_score is None or best_score <
                         self.goal.score(random_result[0])):
                    best_score, best_action, best_pos, best_level = \
                        self.goal.score(random_result[0]), action, \
                        random_result[2], random_result[3]
                elif not valid_move and action is None:
                    pass
                elif not valid_move and action is not None \
                        and action not in stop_criteria:
                    stop_criteria[action] = 1
                elif not valid_move and action is not None \
                        and action in stop_criteria:
                    stop_criteria[action] += 1

        self._proceed = False
        if best_score is None:
            return _create_move(PASS, board)
        else:
            return _create_move(best_action,
                                _get_block(board, best_pos, best_level))


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
