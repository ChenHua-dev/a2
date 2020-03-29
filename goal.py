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
from typing import List, Tuple
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
    # TODO: Implement Me
    # Choosing between Perimeter and Blob goal
    # 0 represents PerimeterGoal; 1 represents BlobGoal
    rn = random.randint(0, 1)

    length_colour_list = len(COLOUR_LIST)
    index_list = list(range(0, length_colour_list))

    if rn == 0:
        s = []
        for _ in range(num_goals):
            temp = random.choice(index_list)
            s.append(PerimeterGoal(COLOUR_LIST[temp]))
            index_list.remove(temp)
        return s
    else:  # elif rn == 1:
        s = []
        for _ in range(num_goals):
            temp = random.choice(index_list)
            s.append(BlobGoal(COLOUR_LIST[temp]))
            index_list.remove(temp)
        return s


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
    # TODO: Implement me
    # Base case: when there is no children
    if len(block.children) == 0:
        lst = []
        for _ in range(int(math.pow(2, block.max_depth - block.level))):
            column = []
            for _ in range(int(math.pow(2, block.max_depth - block.level))):
                column.append(block.colour)
            lst.append(column)
        return lst
    # Recursive case: where there are children under tree node (internal node)
    else:
        # List for return in the recursive case
        # Parent block
        acc = []
        for _ in range(int(math.pow(2, block.max_depth - block.level))):
            column = []
            for _ in range(int(math.pow(2, block.max_depth - block.level))):
                column.append(None)
            acc.append(column)

        child_size = round((math.pow(2, block.max_depth - block.level)) / 2.0)
        # Gather flattened block from child 0
        flattened_child_0 = _flatten(block.children[0])
        for i in range(child_size):
            for j in range(child_size):
                acc[i + child_size][j] = flattened_child_0[i][j]

        # Gather flattened block from child 1
        flattened_child_1 = _flatten(block.children[1])
        for i in range(child_size):
            for j in range(child_size):
                acc[i][j] = flattened_child_1[i][j]

        # Gather flattened block from child 2
        flattened_child_2 = _flatten(block.children[2])
        for i in range(child_size):
            for j in range(child_size):
                acc[i][j + child_size] = flattened_child_2[i][j]

        # Gather flattened block from child 3
        flattened_child_3 = _flatten(block.children[3])
        for i in range(child_size):
            for j in range(child_size):
                acc[i + child_size][j + child_size] = flattened_child_3[i][j]

        return acc
    # board = Block((0, 0), 750, None, 0, 2)
    #
    # # Level 1
    # colours = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    # set_children(board, colours)
    #
    # # Level 2
    # colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3]]
    # set_children(board.children[0], colours)
    #
    # [
    #     [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]],
    #     [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]],
    #     [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3]],
    #     [COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]]
    # ]


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
        # TODO: Implement me
        s = 0
        flat_board = _flatten(board)
        board_size = len(flat_board)
        for i in range(board_size):
            # score upper
            if flat_board[i][0] == self.colour:
                s += 1
            # score lower
            if flat_board[i][-1] == self.colour:
                s += 1
            # score left
            if flat_board[0][i] == self.colour:
                s += 1
            # score right
            if flat_board[-1][i] == self.colour:
                s += 1
        return s

    def description(self) -> str:
        # TODO: Implement me
        return 'Player creates the largest possible ' \
               'perimeter of the board using the target colour'


class BlobGoal(Goal):
    def score(self, board: Block) -> int:
        # TODO: Implement me
        # # flattening the tree/block
        flat_board = _flatten(board)
        col_size = len(flat_board)
        row_size = len(flat_board)

        matrix = []
        for _ in range(col_size):
            column = []
            for _ in range(row_size):
                column.append(-1)
            matrix.append(column)

        max_score = None
        for i in range(col_size):
            for j in range(row_size):
                pos = (i, j)
                temp = self._undiscovered_blob_size(pos, flat_board, matrix)
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
        # TODO: Implement me
        i = pos[0]
        j = pos[1]
        board_size = len(board)

        # out of bound
        if not (0 <= i < board_size and 0 <= j < board_size):
            return 0
        if visited[i][j] == 0 or visited[i][j] == 1:
            return 0
        else:  # within bound and the current cell hasn't been visited
            # if current cell's colour is not the same as target colour
            if board[i][j] != self.colour:
                visited[i][j] = 0
                return 0
            else:  # if current cell's colour is the same as target colour
                visited[i][j] = 1
                # # upper, lower, left, right connected unit cells, respectively
                upper = self._undiscovered_blob_size((i-1, j), board, visited)
                lower = self._undiscovered_blob_size((i+1, j), board, visited)
                left = self._undiscovered_blob_size((i, j-1), board, visited)
                right = self._undiscovered_blob_size((i, j+1), board, visited)
                return 1 + upper + lower + left + right

    def description(self) -> str:
        # TODO: Implement me
        return 'Player creates the largest possible ' \
               'blob of blocks using the target colour'


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
