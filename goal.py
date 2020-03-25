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
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations

import random
from typing import Dict, List, Tuple

from block import Block
from settings import COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    num_choose = random.randint(1, 2)
    if num_choose == 1:
        return [PerimeterGoal(random.choice(COLOUR_LIST)) for _ in
                range(num_goals)]
    else:
        return [BlobGoal(random.choice(COLOUR_LIST)) for _ in range(num_goals)]


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    new_copy = block.create_copy()
    final_block = _get_block_to_max_depth(new_copy)
    p2c = _get_positions_and_color_of_leaves(final_block)
    positions = list(p2c.keys())
    x_values = list(set([position[0] for position in positions]))
    y_values = list(set([position[1] for position in positions]))
    x_values.sort()
    y_values.sort()
    result = []
    for y in y_values:
        x_lst = []
        for x in x_values:
            x_lst.append(p2c[(y, x)])
        result.append(x_lst)
    return result


def _get_block_to_max_depth(block: Block) -> Block:
    """Return a Block that makes all colored blocks in the original blocks
    to a level of block.max_depth. That is, if a block is not at max_depth,
    smash it into children with 4 same color as the original block"""
    if not block.children and block.level < block.max_depth:
        target_color = block.colour
        block.smash()
        for child in block.children:
            child.colour = target_color
        return block
    else:
        block.children = [_get_block_to_max_depth(child)
                          for child in block.children]
        return block


def _get_positions_and_color_of_leaves(block: Block) -> Dict[
    Tuple[int, int], Tuple[int, int, int]]:
    """Return a dictionary that get map to the positions of all leaves of the
    block to its corresponding colour. The key is the position of the block as
    a (int, int) tuple while the value is the corresponding
    colour of this block
    """
    if not block.children:
        return {block.position: block.colour}
    else:
        result = {}
        for child in block.children:
            new_dict = _get_positions_and_color_of_leaves(child)
            for key in new_dict:
                result[key] = new_dict[key]
        return result


def _get_position_block(block: Block) -> Dict[Tuple[int, int], Block]:
    """ Return a dictionary that maps the positions of all colored blocks in
    <block> to the related block. The key is the position tuple and the value is
    the related block
    """
    if not block.children:
        return {block.position: block}
    else:
        result = {}
        for child in block.children:
            to_add = _get_position_block(child)
            for key in to_add:
                result[key] = to_add[key]
        return result


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    def score(self, board: Block) -> int:
        result = 0
        block_flatten = _flatten(board)
        length = len(block_flatten) - 1
        left_side = [block_flatten[i][0] for i in range(length)]
        right_side = [block_flatten[i][length] for i in range(length)]
        result += (left_side.count(self.colour) + right_side.count(self.colour)
                   + block_flatten[0].count(self.colour) +
                   block_flatten[length].count(self.colour))
        return result

    def description(self) -> str:
        return 'PerimeterGoal: the current score is, targeting color: {0}'.\
            format(self.colour)


class BlobGoal(Goal):
    def score(self, board: Block) -> int:
        lst_scores = []
        flatten_block = _flatten(board)
        visited = [[-1 for _ in range(len(flatten_block))] for _ in
                   range(len(flatten_block))]
        for x in range(len(flatten_block)):
            for y in range(len(flatten_block)):
                lst_scores.append(
                    self._undiscovered_blob_size((x, y), flatten_block,
                                                 visited))
        return max(lst_scores)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        if pos[0] < len(board) and pos[1] < len(board):
            return 0
        self._update_visited(pos, board, visited)
        result = 0
        for row in visited:
            for cell in row:
                result += cell
        return result

    def _update_visited(self, pos: Tuple[int, int],
                        board: List[List[Tuple[int, int, int]]],
                        visited: List[List[int]]) -> None:
        """
        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        surround_lst = [(pos[0] + 1, pos[1]), (pos[0] - 1, pos[1]),
                        (pos[0], pos[1] + 1), (pos[0], pos[1] - 1)]
        for position in surround_lst:
            x, y = position
            if (x >= len(board) or y >= len(board)) and visited[x][y] != -1:
                surround_lst.remove(position)
        if not surround_lst:
            return None
        for surround in surround_lst:
            cell_color = board[surround[0]][surround[1]]
            if cell_color == self.colour:
                visited[surround[0]][surround[1]] = 1
            else:
                visited[surround[0]][surround[1]] = 0
            self._update_visited(surround, board, visited)

    def description(self) -> str:
        # TODO: Implement me
        return 'DESCRIPTION'  # FIXME


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
