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
import math
import random
from typing import List, Tuple, Optional
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    num_choose = random.randint(1, 2)
    color_copy = COLOUR_LIST[:]
    result = []
    for _ in range(num_goals):
        get_color = random.choice(color_copy)
        color_copy.remove(get_color)
        if num_choose == 1:
            result.append(PerimeterGoal(get_color))
        else:
            result.append(BlobGoal(get_color))
    return result


def _distribute_colours(acc: List[List[Optional[Tuple[int, int, int]]]],
                        flat_colour: List[List[Tuple[int, int, int]]],
                        size: int, child_index: int) -> None:
    """Assign every tuple from <flat_colour> two-dimensional list to <acc>.
    <acc> a two-dimensional list, each list in <acc> represents a column of
    colours at unit cell level or None. <size> is the size of the unit cell.
    <child_index> is the index position of the children in a Block object if
    the Block object has children.
    """
    for i in range(size):
        for j in range(size):
            if child_index == 0:
                acc[i+size][j] = flat_colour[i][j]
            if child_index == 1:
                acc[i][j] = flat_colour[i][j]
            if child_index == 2:
                acc[i][j+size] = flat_colour[i][j]
            if child_index == 3:
                acc[i+size][j+size] = flat_colour[i][j]


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
    if len(block.children) == 0:
        size = int(math.pow(2, block.max_depth - block.level))
        return [[block.colour for _ in range(size)] for _ in range(size)]
    else:
        size = int(math.pow(2, block.max_depth - block.level))
        acc = [[(0, 0, 0) for _ in range(size)] for _ in range(size)]
        for i in range(len(block.children)):
            flattened_child = _flatten(block.children[i])
            _distribute_colours(acc, flattened_child, round(size / 2.0), i)
        return acc


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
    """A perimeter goal in the game of Blocky.

    Calculate the score of the unit cells of target colour in the side of
    the block.

    === Public Attributes ===
    colour: The target colour of the block
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        """Return the score that is the edge length of the unit cells with the
        target colour in the board. Corner cells are counted twice.
        """
        flat_board = _flatten(board)
        upper = [flat_board[i][0] for i in range(len(flat_board))]
        lower = [flat_board[i][-1] for i in range(len(flat_board))]
        left = flat_board[0]
        right = flat_board[-1]
        return upper.count(self.colour) + lower.count(self.colour) + left.count(
            self.colour) + right.count(self.colour)

    def description(self) -> str:
        """Return a string that describes the perimeter goal with target colour.
        """
        colour = colour_name(self.colour)
        return 'Goal is to calculate the total number of unit cells ' \
               'with colour {0}'.format(colour)


class BlobGoal(Goal):
    """A blob goal in the game of Blocky.

    Calculate the score of the target colour by the largest blob.

    === Public Attributes ===
    colour: The target colour of the block
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        """Return the score of blob goal, which is the maximum size of blob of
        the <board> given the target colour.
        """
        flat_board = _flatten(board)  # flatten the board
        size = len(flat_board)
        unvisited_cells = [[-1 for _ in range(size)] for _ in range(size)]

        max_score = None
        for i in range(size):
            for j in range(size):
                pos = (i, j)
                temp = self._undiscovered_blob_size(pos, flat_board,
                                                    unvisited_cells)
                if max_score is None or max_score < temp:
                    max_score = temp
        return max_score

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that
            (a) is of this Goal's target colour
            (b) includes the cell at <pos>
            (c) involves only cells that have never been visited

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
        i = pos[0]
        j = pos[1]
        board_size = len(board)

        if not (0 <= i < board_size and 0 <= j < board_size):
            return 0
        if visited[i][j] == 0 or visited[i][j] == 1:
            return 0
        else:
            if board[i][j] != self.colour:
                visited[i][j] = 0
                return 0
            else:
                visited[i][j] = 1
                upper = self._undiscovered_blob_size((i-1, j), board, visited)
                lower = self._undiscovered_blob_size((i+1, j), board, visited)
                left = self._undiscovered_blob_size((i, j-1), board, visited)
                right = self._undiscovered_blob_size((i, j+1), board, visited)
                return 1 + upper + lower + left + right

    def description(self) -> str:
        """Return a string that describes the blob goal with target colour.
        """
        colour = colour_name(self.colour)
        return 'Player creates the largest possible ' \
               'blob of blocks using colour {0}'.format(colour)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
