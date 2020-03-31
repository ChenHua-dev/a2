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

import random
from typing import List, Optional, Tuple

import pygame
from actions import COMBINE, KEY_ACTION, PAINT, PASS, ROTATE_CLOCKWISE, \
    ROTATE_COUNTER_CLOCKWISE, SMASH, SWAP_HORIZONTAL, SWAP_VERTICAL
from block import Block
from goal import Goal, generate_goals


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
    goals = generate_goals(num_human + num_random + len(smart_players))
    players = []
    for i in range(num_human):
        players.append(HumanPlayer(i, goals[i]))
    for i in range(num_human, num_human + num_random):
        players.append(RandomPlayer(i, goals[i]))
    for i in range(len(smart_players)):
        players.append(
            SmartPlayer(i + num_human + num_random,
                        goals[i + num_human + num_random], smart_players[i]))
    return players


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

     === Private Attributes ===
     _level:
         The level of the Block that the user selected most recently.
     _desired_action:
         The most recent action that the user is attempting to do.

     == Representation Invariants concerning the private attributes ==
         _level >= 0
    """
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
        block = _get_block(board, mouse_pos, self._level)

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
    """ Generate a random player
     === Private Attributes ===
     _proceed:
       True when the player should make a move, False when the player should
       wait.
    """
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None
        valid_move = False
        while not valid_move:
            x = random.randint(board.position[0],
                               board.position[0] + board.size - 1)
            y = random.randint(board.position[1],
                               board.position[1] + board.size - 1)
            ran_level = random.randint(board.level, board.max_depth)
            ran_block = _get_block(board.create_copy(), (x, y), ran_level)
            block_return = _get_block(board, (x, y), ran_level)
            action = random.choice(list(KEY_ACTION.values()))
            if ran_block is None:
                valid_move = False
            elif action in [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE]:
                valid_move = ran_block.rotate(action[1])
            elif action in [SWAP_HORIZONTAL, SWAP_VERTICAL]:
                valid_move = ran_block.swap(action[1])
            elif action == SMASH:
                valid_move = ran_block.smash()
            elif action == PAINT:
                valid_move = ran_block.paint(self.goal.colour)
            elif action == COMBINE:
                valid_move = ran_block.combine()
            if valid_move:
                move = _create_move(action, block_return)
                self._proceed = False
                return move


class SmartPlayer(Player):
    """ Generate a smart player
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
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
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
        actions = list(KEY_ACTION.values())
        mark_to_action = {}
        for _ in range(self._difficulty):
            board_copy = board.create_copy()
            original_mark = self.goal.score(board_copy)
            random_action = random.choice(actions)  # (str_action, direction)
            x = random.randint(board.position[0],
                               board.position[0] + board.size - 1)
            y = random.randint(board.position[1],
                               board.position[1] + board.size - 1)
            get_level = random.randint(0, board.max_depth)
            random_block = _get_block(board_copy, (x, y), get_level)
            block_return = _get_block(board, (x, y), get_level)
            if random_block is None:
                mark_to_action[
                    self.goal.score(board_copy) - original_mark] = \
                    _create_move(PASS, board)
            elif (random_action in [ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE]
                  and random_block.rotate(random_action[1])) \
                    or (random_action in [SWAP_HORIZONTAL, SWAP_VERTICAL]
                        and random_block.rotate(random_action[1])) \
                    or (random_action == SMASH and random_block.smash()) or \
                    (random_action == PAINT and random_block.paint(
                        self.goal.colour)) \
                    or (random_action == COMBINE or random_block.combine()):
                mark_to_action[self.goal.score(board_copy) - original_mark] \
                    = _create_move(random_action, block_return)
        marks = list(mark_to_action.keys())
        self._proceed = False  # Must set to False before returning!
        if len(marks) != 0 and max(marks) > 0:
            return mark_to_action[max(marks)]
        return _create_move(PASS, board)


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
