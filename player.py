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
from typing import List, Optional, Tuple
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
    # TODO: Implement Me
    acc = []
    # Generate human player
    id_index = 0
    for _ in range(num_human):
        goals = generate_goals(1)
        acc.append(HumanPlayer(id_index, goals[0]))
        id_index += 1

    # Generate random player
    for _ in range(num_random):
        goals = generate_goals(1)
        acc.append(RandomPlayer(id_index, goals[0]))
        id_index += 1

    # Generate smart player
    for i in range(len(smart_players)):
        goals = generate_goals(1)
        acc.append(SmartPlayer(id_index, goals[0], smart_players[i]))
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
    # TODO: Implement me
    # block attributes
    x = block.position[0]
    y = block.position[1]
    d = round(block.size / 2.0)
    # target location
    target_x = location[0]
    target_y = location[1]

    if x <= target_x < x + 2 * d and y <= target_y < y + 2 * d:
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
            else:
            # elif target_x >= x + d and target_y >= y + d:
                return _get_block(block.children[3], location, level - 1)
    else:
        return None


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
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        # TODO: Implement Me
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        # if proceed is False, then return None
        if not self._proceed:
            return None  # Do not remove
        # if proceed is True
        else:
            # TODO: Implement Me
            # 1. Make deep copy of the board
            copied_board = board.create_copy()

            # Random position
            random_x = random.randint(0, copied_board.size)
            random_y = random.randint(0, copied_board.size)
            random_pos = (random_x, random_y)

            # Random level
            # where does the random level start? board.level or 0 or 1?
            random_level = random.randint(copied_board.level,
                                          copied_board.max_depth)
            # Extract the temporary board
            temp_block = _get_block(copied_board, random_pos, random_level)
            if temp_block is None:
                return None

            potential_moves = []
            for value in KEY_ACTION.values():
                if value[0] != PASS[0]:
                    potential_moves.append(value)

            # Generating random move
            action = random.choice(potential_moves)  # this is a tuple
            direction = action[1]

            if action in [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE]:
                temp_block.rotate(direction)
            elif action in [SWAP_HORIZONTAL, SWAP_VERTICAL]:
                temp_block.swap(direction)
            elif action == SMASH:
                temp_block.smash()
            elif action == PAINT:
                temp_block.paint(self.goal.colour)
            elif action == COMBINE:
                temp_block.combine()
            else:
                pass

            move = _create_move(action, temp_block)

            self._proceed = False  # Must set to False before returning!
            return move


class SmartPlayer(Player):
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _difficulty: int
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        # TODO: Implement Me
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
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
            return None  # Do not remove
        else:
            # TODO: Implement Me
            # calculate current score
            curr_score = self.goal.score(board)
            best_score = None  # curr_score

            best_move = None  # _create_move(PASS, block: Block)
            for _ in range(self._difficulty):
                # 1. Make deep copy of the board
                copied_board = board.create_copy()

                # 2. Generate a random block
                # Random position
                random_x = random.randint(0, copied_board.size)
                random_y = random.randint(0, copied_board.size)
                random_pos = (random_x, random_y)

                # Random level
                # where does the random level start? board.level or 0 or 1?
                random_level = random.randint(copied_board.level,
                                              copied_board.max_depth)
                # Extract the temporary board
                temp_block = _get_block(copied_board, random_pos, random_level)
                if temp_block is None:
                    return None

                potential_moves = []
                for value in KEY_ACTION.values():
                    if value[0] != PASS[0]:
                        potential_moves.append(value)

                # Generating random move
                action = random.choice(potential_moves)  # this is a tuple
                direction = action[1]

                if action in [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE]:
                    temp_block.rotate(direction)
                elif action in [SWAP_HORIZONTAL, SWAP_VERTICAL]:
                    temp_block.swap(direction)
                elif action == SMASH:
                    temp_block.smash()
                elif action == PAINT:
                    temp_block.paint(self.goal.colour)
                elif action == COMBINE:
                    temp_block.combine()
                else:
                    pass

                # calculate new score
                new_score = self.goal.score(copied_board)
                if new_score > curr_score:
                    if best_score is None or best_score < new_score:
                        best_score = new_score
                        best_move = _create_move(action, temp_block)

            self._proceed = False  # Must set to False before returning!
            if best_score is None:
                return None
            else:
                return best_move


# if __name__ == '__main__':
#     import python_ta
#
#     python_ta.check_all(config={
#         'allowed-io': ['process_event'],
#         'allowed-import-modules': [
#             'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
#             'goal', 'pygame', '__future__'
#         ],
#         'max-attributes': 10,
#         'generated-members': 'pygame.*'
#     })
