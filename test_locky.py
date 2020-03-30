from typing import List, Optional, Tuple
import os
import pygame
import pytest
import unittest

from block import *
from blocky import *
from goal import *
from player import *

from assignments.a2.block import Block


def get_all_blocks_positions(block) -> List[Tuple[int, int]]:
    """Return a list of all blocks' position for <block> (preorder)"""
    if not block.children:
        return [block.position]
    else:
        result = [block.position]
        for child in block.children:
            result.extend(get_all_blocks_positions(child))
        return result


def get_block_num(block) -> int:
    """Return the number of the block"""
    if not block.children:
        return 1
    else:
        result = 1
        for child in block.children:
            result += get_block_num(child)
        return result


def update_max_depth(block, max_depth) -> None:
    """Update the max_depth for the block"""
    if not block.children:
        block.max_depth = max_depth
    else:
        block.max_depth = max_depth
        for child in block.children:
            update_max_depth(child, max_depth)


def smash_all_leaves(block):
    if not block.children:
        block.smash()
    else:
        for child in block.children:
            smash_all_leaves(child)


class TestBlock(unittest.TestCase):
    def setUp(self):
        """
        BlockA
        Block(position, size, colour, level, max_depth
        ------------ position (0, 0) , size = 750, colour = (255, 211, 92) level = 0, max_depth = 0
        |          |
        |          |
        |          |
        ------------

        BlockB 750
        ---------------------
        |    b2     |    b1   |  b1: (1, 128, 181)
        |          |         |   b2: (199, 44, 58)
        ---------------------
        |    b3    |     b4  |    b3: colour = (255, 211, 92)
        |         |         |    b4: colour = (138, 151, 71)
        ---------------------

        BlockC size_total = 1000
        (1398123, 1239129)
        -------------------------------------
        |                |   c01   |   c00  |  c00: (255, 211, 92)
        |                |         |        |   c01 (255, 211, 92)
        |      c1        |------------------|    c02 (138, 151, 71)
        |                |    c02  |    c03 |    c03 (1, 128, 181)
        |                |         |        |     c1   (1, 128, 181)
        -------------------------------------     c20 (199, 44, 58)
        |    c21|  c20   |                  |     c21 (123, 121, 438)
        |       |        |                  |     c22 (123, 482, 12)
        -----------------|      c3          |     c23 (89, 123, 234)
        |   c22 |   c23  |                  |
        |       |        |                  |     c3 (199, 44, 58)
        --------------------------------------

        BlockD size_total = 996
        ---------------------------------------------------   d0:(1, 128, 181)       d20 (199, 44, 58)   d330 (1, 128, 181)
        |d111| d110|           |                          |   d10 (255, 211, 92)     d21 (138, 151, 71)  d332 (1, 128, 181)
        -----------|    d10    |                          |                            d22 (1, 128, 181)   d333 (138, 151, 71)
        |d112|d113 |           |            d0            |                          d23 (199, 44, 58)
        ------------------------                          |                           d300 (255, 211,92)
        |d121| d120| d131 |d130|                          |   d110 (199, 44, 58)     d301 (138, 151, 71)
        ------------------------                          |   d111 (138, 151, 71)    d302 (199, 44, 58)
        |d122|d123 | d132|d133 |                          |   d112 (255, 211, 92)    d303 (255, 211, 92)
        |-------------------------------------------------|  d113  (199, 44, 58)    d310 (199, 44, 58)
        |           |          |   d311| d310| d301| d300 |   d120  (138, 151, 71)   d311 (138, 151, 71)
        |       d21 |    d20   | --------------------------   d121  (255, 211, 92)   d312 (1, 128, 181)
        |           |          | d312 | d313 | d302| d303 |   d122   (1, 128, 181)    d313 (199, 44, 58)
        |-------------------------------------------------|   d123   (199, 44, 58)   d321  (255, 211, 92)
        |           |          |  d321 | d320| d331| d330 |    d130   (255, 211, 92)  d320  (1, 128, 181)
        |   d22     |     d23  | -------------------------|   d131  (1, 128, 181)    d322   (255, 211, 92)
        |           |          | d322 |  d323|d332 | d333 |    d132   (199, 44, 58)   d323   (138, 151, 71)
        ---------------------------------------------------   d133   (1, 128, 182)   d331  (1, 128, 181)
        """
        BlockA = Block((0, 0), 750, (255, 211, 92), 0, 0)  # Level 0

        BlockB = Block((0, 0), 750, None, 0, 1)  # Level 1
        b2 = Block((375, 0), 375, (1, 128, 181), 1, 1)
        b1 = Block((0, 0), 375, (199, 44, 58), 1, 1)
        b3 = Block((0, 375), 375, (255, 211, 92), 1, 1)
        b4 = Block((375, 375), 375, (138, 151, 71), 1, 1)
        BlockB.children = [b2, b1, b3, b4]

        BlockC = Block((1398123, 1239129), 1000, None, 0,
                       2)  # Level 2, not at (0, 0) position
        c_child_pos = BlockC._children_positions()

        c0 = Block(c_child_pos[0], 500, None, 1, 2)
        c1 = Block(c_child_pos[1], 500, (1, 128, 181), 1, 2)
        c2 = Block(c_child_pos[2], 500, None, 1, 2)
        c3 = Block(c_child_pos[3], 500, (199, 44, 58), 1, 2)
        BlockC.children = [c0, c1, c2, c3]

        c0_child_pos = c0._children_positions()
        c00 = Block(c0_child_pos[0], 250, (255, 211, 92), 2, 2)
        c01 = Block(c0_child_pos[1], 250, (255, 211, 92), 2, 2)
        c02 = Block(c0_child_pos[2], 250, (138, 151, 71), 2, 2)
        c03 = Block(c0_child_pos[3], 250, (1, 128, 181), 2, 2)
        c0.children = [c00, c01, c02, c03]

        c2_child_pos = c2._children_positions()
        c20 = Block(c2_child_pos[0], 250, (199, 44, 58), 2, 2)
        c21 = Block(c2_child_pos[1], 250, (123, 121, 438), 2, 2)
        c22 = Block(c2_child_pos[2], 250, (123, 482, 12), 2, 2)
        c23 = Block(c2_child_pos[3], 250, (89, 123, 234), 2,
                    2)  # Color not in COLOUR_LIST
        c2.children = [c20, c21, c22, c23]

        # BlockD Level 3
        BlockD = Block((1, 1238), 996, None, 0, 3)
        d_child_pos = BlockD._children_positions()
        d0_size = BlockD._child_size()
        d0 = Block(d_child_pos[0], d0_size, (1, 128, 181), 1, 3)
        d1 = Block(d_child_pos[1], d0_size, None, 1, 3)
        d2 = Block(d_child_pos[2], d0_size, None, 1, 3)
        d3 = Block(d_child_pos[3], d0_size, None, 1, 3)
        BlockD.children = [d0, d1, d2, d3]

        d1_child_pos = d1._children_positions()
        d10_size = d0._child_size()
        d10 = Block(d1_child_pos[0], d10_size, (255, 211, 92), 2, 3)
        d11 = Block(d1_child_pos[1], d10_size, None, 2, 3)
        d12 = Block(d1_child_pos[2], d10_size, None, 2, 3)
        d13 = Block(d1_child_pos[3], d10_size, None, 2, 3)
        d1.children = [d10, d11, d12, d13]

        d2_child_pos = d2._children_positions()
        d20 = Block(d2_child_pos[0], d10_size, (199, 44, 58), 2, 3)
        d21 = Block(d2_child_pos[1], d10_size, (138, 151, 71), 2, 3)
        d22 = Block(d2_child_pos[2], d10_size, (1, 128, 181), 2, 3)
        d23 = Block(d2_child_pos[3], d10_size, (199, 44, 58), 2, 3)
        d2.children = [d20, d21, d22, d23]

        d3_child_pos = d3._children_positions()
        d30 = Block(d3_child_pos[0], d10_size, None, 2, 3)
        d31 = Block(d3_child_pos[1], d10_size, None, 2, 3)
        d32 = Block(d3_child_pos[2], d10_size, None, 2, 3)
        d33 = Block(d3_child_pos[3], d10_size, None, 2, 3)
        d3.children = [d30, d31, d32, d33]

        d11_child_pos = d11._children_positions()
        d110_size = d10._child_size()
        d110 = Block(d11_child_pos[0], d110_size, (199, 44, 58), 3, 3)
        d111 = Block(d11_child_pos[1], d110_size, (138, 151, 71), 3, 3)
        d112 = Block(d11_child_pos[2], d110_size, (255, 211, 92), 3, 3)
        d113 = Block(d11_child_pos[3], d110_size, (199, 44, 58), 3, 3)
        d11.children = [d110, d111, d112, d113]

        d12_child_pos = d12._children_positions()
        d120 = Block(d12_child_pos[0], d110_size, (138, 151, 71), 3, 3)
        d121 = Block(d12_child_pos[1], d110_size, (255, 211, 92), 3, 3)
        d122 = Block(d12_child_pos[2], d110_size, (1, 128, 181), 3, 3)
        d123 = Block(d12_child_pos[3], d110_size, (199, 44, 58), 3, 3)
        d12.children = [d120, d121, d122, d123]

        d13_child_pos = d13._children_positions()
        d130 = Block(d13_child_pos[0], d110_size, (255, 211, 92), 3, 3)
        d131 = Block(d13_child_pos[1], d110_size, (1, 128, 181), 3, 3)
        d132 = Block(d13_child_pos[2], d110_size, (199, 44, 58), 3, 3)
        d133 = Block(d13_child_pos[3], d110_size, (1, 128, 181), 3, 3)
        d13.children = [d130, d131, d132, d133]

        d30_child_pos = d30._children_positions()
        d300_size = d30._child_size()
        d300 = Block(d30_child_pos[0], d300_size, (255, 211, 92), 3, 3)
        d301 = Block(d30_child_pos[1], d300_size, (138, 151, 71), 3, 3)
        d302 = Block(d30_child_pos[2], d300_size, (199, 44, 58), 3, 3)
        d303 = Block(d30_child_pos[3], d300_size, (255, 211, 92), 3, 3)
        d30.children = [d300, d301, d302, d303]

        d31_child_pos = d31._children_positions()
        d310 = Block(d31_child_pos[0], d300_size, (199, 44, 58), 3, 3)
        d311 = Block(d31_child_pos[1], d300_size, (138, 151, 71), 3, 3)
        d312 = Block(d31_child_pos[2], d300_size, (1, 128, 181), 3, 3)
        d313 = Block(d31_child_pos[3], d300_size, (199, 44, 58), 3, 3)
        d31.children = [d310, d311, d312, d313]

        d32_child_pos = d32._children_positions()
        d320 = Block(d32_child_pos[0], d300_size, (1, 128, 181), 3, 3)
        d321 = Block(d32_child_pos[1], d300_size, (255, 211, 92), 3, 3)
        d322 = Block(d32_child_pos[2], d300_size, (255, 211, 92), 3, 3)
        d323 = Block(d32_child_pos[3], d300_size, (138, 151, 71), 3, 3)
        d32.children = [d320, d321, d322, d323]

        d33_child_pos = d33._children_positions()
        d330 = Block(d33_child_pos[0], d300_size, (1, 128, 181), 3, 3)
        d331 = Block(d33_child_pos[1], d300_size, (1, 128, 181), 3, 3)
        d332 = Block(d33_child_pos[2], d300_size, (1, 128, 181), 3, 3)
        d333 = Block(d33_child_pos[3], d300_size, (138, 151, 71), 3, 3)
        d33.children = [d330, d331, d332, d333]

        self.BlockA = BlockA
        self.BlockB = BlockB
        self.BlockC = BlockC
        self.BlockD = BlockD
        self.error_message = "Expected value for {} is {} Actual value is {}".format

    def tearDown(self) -> None:
        BlockA = Block((0, 0), 750, (255, 211, 92), 0, 0)  # Level 0
        BlockB = Block((0, 0), 750, None, 0, 1)  # Level 1
        b2 = Block((375, 0), 375, (1, 128, 181), 1, 1)
        b1 = Block((0, 0), 375, (199, 44, 58), 1, 1)
        b3 = Block((0, 375), 375, (255, 211, 92), 1, 1)
        b4 = Block((375, 375), 375, (138, 151, 71), 1, 1)
        BlockB.children = [b2, b1, b3, b4]

        BlockC = Block((1398123, 1239129), 1000, None, 0,
                       2)  # Level 2, not at (0, 0) position
        c_child_pos = BlockC._children_positions()

        c0 = Block(c_child_pos[0], 500, None, 1, 2)
        c1 = Block(c_child_pos[1], 500, (1, 128, 181), 1, 2)
        c2 = Block(c_child_pos[2], 500, None, 1, 2)
        c3 = Block(c_child_pos[3], 500, (199, 44, 58), 1, 2)
        BlockC.children = [c0, c1, c2, c3]

        c0_child_pos = c0._children_positions()
        c00 = Block(c0_child_pos[0], 250, (255, 211, 92), 2, 2)
        c01 = Block(c0_child_pos[1], 250, (255, 211, 92), 2, 2)
        c02 = Block(c0_child_pos[2], 250, (138, 151, 71), 2, 2)
        c03 = Block(c0_child_pos[3], 250, (1, 128, 181), 2, 2)
        c0.children = [c00, c01, c02, c03]

        c2_child_pos = c2._children_positions()
        c20 = Block(c2_child_pos[0], 250, (199, 44, 58), 2, 2)
        c21 = Block(c2_child_pos[1], 250, (123, 121, 438), 2, 2)
        c22 = Block(c2_child_pos[2], 250, (123, 482, 12), 2, 2)
        c23 = Block(c2_child_pos[3], 250, (89, 123, 234), 2,
                    2)  # Color not in COLOUR_LIST
        c2.children = [c20, c21, c22, c23]

        # BlockD Level 3
        BlockD = Block((1, 1238), 996, None, 0, 3)
        d_child_pos = BlockD._children_positions()
        d0_size = BlockD._child_size()
        d0 = Block(d_child_pos[0], d0_size, (1, 128, 181), 1, 3)
        d1 = Block(d_child_pos[1], d0_size, None, 1, 3)
        d2 = Block(d_child_pos[2], d0_size, None, 1, 3)
        d3 = Block(d_child_pos[3], d0_size, None, 1, 3)
        BlockD.children = [d0, d1, d2, d3]

        d1_child_pos = d1._children_positions()
        d10_size = d0._child_size()
        d10 = Block(d1_child_pos[0], d10_size, (255, 211, 92), 2, 3)
        d11 = Block(d1_child_pos[1], d10_size, None, 2, 3)
        d12 = Block(d1_child_pos[2], d10_size, None, 2, 3)
        d13 = Block(d1_child_pos[3], d10_size, None, 2, 3)
        d1.children = [d10, d11, d12, d13]

        d2_child_pos = d2._children_positions()
        d20 = Block(d2_child_pos[0], d10_size, (199, 44, 58), 2, 3)
        d21 = Block(d2_child_pos[1], d10_size, (138, 151, 71), 2, 3)
        d22 = Block(d2_child_pos[2], d10_size, (1, 128, 181), 2, 3)
        d23 = Block(d2_child_pos[3], d10_size, (199, 44, 58), 2, 3)
        d2.children = [d20, d21, d22, d23]

        d3_child_pos = d3._children_positions()
        d30 = Block(d3_child_pos[0], d10_size, None, 2, 3)
        d31 = Block(d3_child_pos[1], d10_size, None, 2, 3)
        d32 = Block(d3_child_pos[2], d10_size, None, 2, 3)
        d33 = Block(d3_child_pos[3], d10_size, None, 2, 3)
        d3.children = [d30, d31, d32, d33]

        d11_child_pos = d11._children_positions()
        d110_size = d10._child_size()
        d110 = Block(d11_child_pos[0], d110_size, (199, 44, 58), 3, 3)
        d111 = Block(d11_child_pos[1], d110_size, (138, 151, 71), 3, 3)
        d112 = Block(d11_child_pos[2], d110_size, (255, 211, 92), 3, 3)
        d113 = Block(d11_child_pos[3], d110_size, (199, 44, 58), 3, 3)
        d11.children = [d110, d111, d112, d113]

        d12_child_pos = d12._children_positions()
        d120 = Block(d12_child_pos[0], d110_size, (138, 151, 71), 3, 3)
        d121 = Block(d12_child_pos[1], d110_size, (255, 211, 92), 3, 3)
        d122 = Block(d12_child_pos[2], d110_size, (1, 128, 181), 3, 3)
        d123 = Block(d12_child_pos[3], d110_size, (199, 44, 58), 3, 3)
        d12.children = [d120, d121, d122, d123]

        d13_child_pos = d13._children_positions()
        d130 = Block(d13_child_pos[0], d110_size, (255, 211, 92), 3, 3)
        d131 = Block(d13_child_pos[1], d110_size, (1, 128, 181), 3, 3)
        d132 = Block(d13_child_pos[2], d110_size, (199, 44, 58), 3, 3)
        d133 = Block(d13_child_pos[3], d110_size, (1, 128, 181), 3, 3)
        d13.children = [d130, d131, d132, d133]

        d30_child_pos = d30._children_positions()
        d300_size = d30._child_size()
        d300 = Block(d30_child_pos[0], d300_size, (255, 211, 92), 3, 3)
        d301 = Block(d30_child_pos[1], d300_size, (138, 151, 71), 3, 3)
        d302 = Block(d30_child_pos[2], d300_size, (199, 44, 58), 3, 3)
        d303 = Block(d30_child_pos[3], d300_size, (255, 211, 92), 3, 3)
        d30.children = [d300, d301, d302, d303]

        d31_child_pos = d31._children_positions()
        d310 = Block(d31_child_pos[0], d300_size, (199, 44, 58), 3, 3)
        d311 = Block(d31_child_pos[1], d300_size, (138, 151, 71), 3, 3)
        d312 = Block(d31_child_pos[2], d300_size, (1, 128, 181), 3, 3)
        d313 = Block(d31_child_pos[3], d300_size, (199, 44, 58), 3, 3)
        d31.children = [d310, d311, d312, d313]

        d32_child_pos = d32._children_positions()
        d320 = Block(d32_child_pos[0], d300_size, (1, 128, 181), 3, 3)
        d321 = Block(d32_child_pos[1], d300_size, (255, 211, 92), 3, 3)
        d322 = Block(d32_child_pos[2], d300_size, (255, 211, 92), 3, 3)
        d323 = Block(d32_child_pos[3], d300_size, (138, 151, 71), 3, 3)
        d32.children = [d320, d321, d322, d323]

        d33_child_pos = d33._children_positions()
        d330 = Block(d33_child_pos[0], d300_size, (1, 128, 181), 3, 3)
        d331 = Block(d33_child_pos[1], d300_size, (1, 128, 181), 3, 3)
        d332 = Block(d33_child_pos[2], d300_size, (1, 128, 181), 3, 3)
        d333 = Block(d33_child_pos[3], d300_size, (138, 151, 71), 3, 3)
        d33.children = [d330, d331, d332, d333]

        self.BlockA = BlockA
        self.BlockB = BlockB
        self.BlockC = BlockC
        self.BlockD = BlockD

    def test_eq(self):
        BlockD_copy = Block((1, 1238), 996, None, 0, 3)
        d_child_pos = BlockD_copy._children_positions()
        d0_size = BlockD_copy._child_size()
        d0 = Block(d_child_pos[0], d0_size, (1, 128, 181), 1, 3)
        d1 = Block(d_child_pos[1], d0_size, None, 1, 3)
        d2 = Block(d_child_pos[2], d0_size, None, 1, 3)
        d3 = Block(d_child_pos[3], d0_size, None, 1, 3)
        BlockD_copy.children = [d0, d1, d2, d3]

        d1_child_pos = d1._children_positions()
        d10_size = d0._child_size()
        d10 = Block(d1_child_pos[0], d10_size, (255, 211, 92), 2, 3)
        d11 = Block(d1_child_pos[1], d10_size, None, 2, 3)
        d12 = Block(d1_child_pos[2], d10_size, None, 2, 3)
        d13 = Block(d1_child_pos[3], d10_size, None, 2, 3)
        d1.children = [d10, d11, d12, d13]

        d2_child_pos = d2._children_positions()
        d20 = Block(d2_child_pos[0], d10_size, (199, 44, 58), 2, 3)
        d21 = Block(d2_child_pos[1], d10_size, (138, 151, 71), 2, 3)
        d22 = Block(d2_child_pos[2], d10_size, (1, 128, 181), 2, 3)
        d23 = Block(d2_child_pos[3], d10_size, (199, 44, 58), 2, 3)
        d2.children = [d20, d21, d22, d23]

        d3_child_pos = d3._children_positions()
        d30 = Block(d3_child_pos[0], d10_size, None, 2, 3)
        d31 = Block(d3_child_pos[1], d10_size, None, 2, 3)
        d32 = Block(d3_child_pos[2], d10_size, None, 2, 3)
        d33 = Block(d3_child_pos[3], d10_size, None, 2, 3)
        d3.children = [d30, d31, d32, d33]

        d11_child_pos = d11._children_positions()
        d110_size = d10._child_size()
        d110 = Block(d11_child_pos[0], d110_size, (199, 44, 58), 3, 3)
        d111 = Block(d11_child_pos[1], d110_size, (138, 151, 71), 3, 3)
        d112 = Block(d11_child_pos[2], d110_size, (255, 211, 92), 3, 3)
        d113 = Block(d11_child_pos[3], d110_size, (199, 44, 58), 3, 3)
        d11.children = [d110, d111, d112, d113]

        d12_child_pos = d12._children_positions()
        d120 = Block(d12_child_pos[0], d110_size, (138, 151, 71), 3, 3)
        d121 = Block(d12_child_pos[1], d110_size, (255, 211, 92), 3, 3)
        d122 = Block(d12_child_pos[2], d110_size, (1, 128, 181), 3, 3)
        d123 = Block(d12_child_pos[3], d110_size, (199, 44, 58), 3, 3)
        d12.children = [d120, d121, d122, d123]

        d13_child_pos = d13._children_positions()
        d130 = Block(d13_child_pos[0], d110_size, (255, 211, 92), 3, 3)
        d131 = Block(d13_child_pos[1], d110_size, (1, 128, 181), 3, 3)
        d132 = Block(d13_child_pos[2], d110_size, (199, 44, 58), 3, 3)
        d133 = Block(d13_child_pos[3], d110_size, (1, 128, 181), 3, 3)
        d13.children = [d130, d131, d132, d133]

        d30_child_pos = d30._children_positions()
        d300_size = d30._child_size()
        d300 = Block(d30_child_pos[0], d300_size, (255, 211, 92), 3, 3)
        d301 = Block(d30_child_pos[1], d300_size, (138, 151, 71), 3, 3)
        d302 = Block(d30_child_pos[2], d300_size, (199, 44, 58), 3, 3)
        d303 = Block(d30_child_pos[3], d300_size, (255, 211, 92), 3, 3)
        d30.children = [d300, d301, d302, d303]

        d31_child_pos = d31._children_positions()
        d310 = Block(d31_child_pos[0], d300_size, (199, 44, 58), 3, 3)
        d311 = Block(d31_child_pos[1], d300_size, (138, 151, 71), 3, 3)
        d312 = Block(d31_child_pos[2], d300_size, (1, 128, 181), 3, 3)
        d313 = Block(d31_child_pos[3], d300_size, (199, 44, 58), 3, 3)
        d31.children = [d310, d311, d312, d313]

        d32_child_pos = d32._children_positions()
        d320 = Block(d32_child_pos[0], d300_size, (1, 128, 181), 3, 3)
        d321 = Block(d32_child_pos[1], d300_size, (255, 211, 92), 3, 3)
        d322 = Block(d32_child_pos[2], d300_size, (255, 211, 92), 3, 3)
        d323 = Block(d32_child_pos[3], d300_size, (138, 151, 71), 3, 3)
        d32.children = [d320, d321, d322, d323]

        d33_child_pos = d33._children_positions()
        d330 = Block(d33_child_pos[0], d300_size, (1, 128, 181), 3, 3)
        d331 = Block(d33_child_pos[1], d300_size, (1, 128, 181), 3, 3)
        d332 = Block(d33_child_pos[2], d300_size, (1, 128, 181), 3, 3)
        d333 = Block(d33_child_pos[3], d300_size, (138, 151, 71), 3, 3)
        d33.children = [d330, d331, d332, d333]

        self.assertEqual(self.BlockD, BlockD_copy,
                         "They should be equal in attributes but not in address")
        self.assertTrue(self.BlockA != None, "Check if None works")


from block import random as a2_random
import random

SEED_NUMBER = 996


class TestBlockMethods(TestBlock):
    def setUp(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().setUp()

    def tearDown(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().tearDown()

    def test_eq(self):
        BlockD_copy = Block((1, 1238), 996, None, 0, 3)
        d_child_pos = BlockD_copy._children_positions()
        d0_size = BlockD_copy._child_size()
        d0 = Block(d_child_pos[0], d0_size, (1, 128, 181), 1, 3)
        d1 = Block(d_child_pos[1], d0_size, None, 1, 3)
        d2 = Block(d_child_pos[2], d0_size, None, 1, 3)
        d3 = Block(d_child_pos[3], d0_size, None, 1, 3)
        BlockD_copy.children = [d0, d1, d2, d3]

        d1_child_pos = d1._children_positions()
        d10_size = d0._child_size()
        d10 = Block(d1_child_pos[0], d10_size, (255, 211, 92), 2, 3)
        d11 = Block(d1_child_pos[1], d10_size, None, 2, 3)
        d12 = Block(d1_child_pos[2], d10_size, None, 2, 3)
        d13 = Block(d1_child_pos[3], d10_size, None, 2, 3)
        d1.children = [d10, d11, d12, d13]

        d2_child_pos = d2._children_positions()
        d20 = Block(d2_child_pos[0], d10_size, (199, 44, 58), 2, 3)
        d21 = Block(d2_child_pos[1], d10_size, (138, 151, 71), 2, 3)
        d22 = Block(d2_child_pos[2], d10_size, (1, 128, 181), 2, 3)
        d23 = Block(d2_child_pos[3], d10_size, (199, 44, 58), 2, 3)
        d2.children = [d20, d21, d22, d23]

        d3_child_pos = d3._children_positions()
        d30 = Block(d3_child_pos[0], d10_size, None, 2, 3)
        d31 = Block(d3_child_pos[1], d10_size, None, 2, 3)
        d32 = Block(d3_child_pos[2], d10_size, None, 2, 3)
        d33 = Block(d3_child_pos[3], d10_size, None, 2, 3)
        d3.children = [d30, d31, d32, d33]

        d11_child_pos = d11._children_positions()
        d110_size = d10._child_size()
        d110 = Block(d11_child_pos[0], d110_size, (199, 44, 58), 3, 3)
        d111 = Block(d11_child_pos[1], d110_size, (138, 151, 71), 3, 3)
        d112 = Block(d11_child_pos[2], d110_size, (255, 211, 92), 3, 3)
        d113 = Block(d11_child_pos[3], d110_size, (199, 44, 58), 3, 3)
        d11.children = [d110, d111, d112, d113]

        d12_child_pos = d12._children_positions()
        d120 = Block(d12_child_pos[0], d110_size, (138, 151, 71), 3, 3)
        d121 = Block(d12_child_pos[1], d110_size, (255, 211, 92), 3, 3)
        d122 = Block(d12_child_pos[2], d110_size, (1, 128, 181), 3, 3)
        d123 = Block(d12_child_pos[3], d110_size, (199, 44, 58), 3, 3)
        d12.children = [d120, d121, d122, d123]

        d13_child_pos = d13._children_positions()
        d130 = Block(d13_child_pos[0], d110_size, (255, 211, 92), 3, 3)
        d131 = Block(d13_child_pos[1], d110_size, (1, 128, 181), 3, 3)
        d132 = Block(d13_child_pos[2], d110_size, (199, 44, 58), 3, 3)
        d133 = Block(d13_child_pos[3], d110_size, (1, 128, 181), 3, 3)
        d13.children = [d130, d131, d132, d133]

        d30_child_pos = d30._children_positions()
        d300_size = d30._child_size()
        d300 = Block(d30_child_pos[0], d300_size, (255, 211, 92), 3, 3)
        d301 = Block(d30_child_pos[1], d300_size, (138, 151, 71), 3, 3)
        d302 = Block(d30_child_pos[2], d300_size, (199, 44, 58), 3, 3)
        d303 = Block(d30_child_pos[3], d300_size, (255, 211, 92), 3, 3)
        d30.children = [d300, d301, d302, d303]

        d31_child_pos = d31._children_positions()
        d310 = Block(d31_child_pos[0], d300_size, (199, 44, 58), 3, 3)
        d311 = Block(d31_child_pos[1], d300_size, (138, 151, 71), 3, 3)
        d312 = Block(d31_child_pos[2], d300_size, (1, 128, 181), 3, 3)
        d313 = Block(d31_child_pos[3], d300_size, (199, 44, 58), 3, 3)
        d31.children = [d310, d311, d312, d313]

        d32_child_pos = d32._children_positions()
        d320 = Block(d32_child_pos[0], d300_size, (1, 128, 181), 3, 3)
        d321 = Block(d32_child_pos[1], d300_size, (255, 211, 92), 3, 3)
        d322 = Block(d32_child_pos[2], d300_size, (255, 211, 92), 3, 3)
        d323 = Block(d32_child_pos[3], d300_size, (138, 151, 71), 3, 3)
        d32.children = [d320, d321, d322, d323]

        d33_child_pos = d33._children_positions()
        d330 = Block(d33_child_pos[0], d300_size, (1, 128, 181), 3, 3)
        d331 = Block(d33_child_pos[1], d300_size, (1, 128, 181), 3, 3)
        d332 = Block(d33_child_pos[2], d300_size, (1, 128, 181), 3, 3)
        d333 = Block(d33_child_pos[3], d300_size, (138, 151, 71), 3, 3)
        d33.children = [d330, d331, d332, d333]

        self.assertTrue(self.BlockD == BlockD_copy,
                        "They should be equal in attributes but not in address")
        self.assertTrue(self.BlockA != None, "Check if None works")
        self.assertFalse(self.BlockA == self.BlockB,
                         "Check if two blocks are not equal")

    def test_create_copy(self):
        Block_B_copy = self.BlockB.create_copy()
        self.assertTrue(Block_B_copy == self.BlockB,
                        "The attributes in the copy not equal")
        self.assertFalse(Block_B_copy is self.BlockB,
                         "The address for the copy and the origin should not be True")
        Block_B_copy.rotate(3)
        self.assertFalse(Block_B_copy == self.BlockB,
                         "The mutation of BlockB deep copy affect the original one")

    def test_update_children_position(self):
        dx = random.randint(2, 129)
        dy = random.randint(5, 123)
        move_pos = (dx, dy)
        Block_A_copy = self.BlockA.create_copy()
        Block_A_copy._update_children_positions(move_pos)
        self.assertTrue(Block_A_copy.position == move_pos,
                        "Please check your base case")
        Block_B_copy = self.BlockB.create_copy()
        Block_B_copy._update_children_positions(move_pos)
        self.assertTrue(Block_B_copy.position == move_pos,
                        "You forgot to update the inner node position")
        new_positions = Block_B_copy._children_positions()
        d = Block_B_copy._child_size()
        expect = [(dx + d, dy), (dx, dy), (dx, dy + d), (dx + d, dy + d)]
        self.assertEqual(new_positions, expect,
                         "You fail to assign the children a new position")

    def test_update_children_position0(self):
        """Test if the descendents of the block can be updated
        """
        dx = random.randint(12, 12391203)
        dy = random.randint(1,1390)
        Block_C_copy = self.BlockC.create_copy()
        origC = get_all_blocks_positions(Block_C_copy)
        Block_C_copy._update_children_positions((dx, dy))
        currC = get_all_blocks_positions(Block_C_copy)
        self.assertTrue(len(origC) == len(currC), "The number of nodes of your block changes")
        for i in range(len(origC)):
            self.assertTrue(origC[i][0] != currC[i][0], "The x value of descendents' positions has not updated")
            self.assertTrue(origC[i][1] != currC[i][0], "The y value of the descendents' position has not updated")

        Block_D_copy = self.BlockD.create_copy()
        origD = get_all_blocks_positions(Block_D_copy)
        Block_D_copy._update_children_positions((dx, dy))
        currD = get_all_blocks_positions(Block_D_copy)
        self.assertTrue(len(origD) == len(currD))
        for i in range(len(origD)):
            self.assertTrue(origD[i][0] != currD[i][0])
            self.assertTrue(origD[i][1] != currD[i][1])

    def test_smash_false(self):
        """Test if smash does not work"""
        BlockA = self.BlockA.create_copy()
        a = BlockA.smash()
        self.assertFalse(a, "You fail to check smashable")
        BlockB = self.BlockB.create_copy()
        b = BlockB.smash()
        self.assertFalse(b, "Should not smash when self have children")
        c = BlockB.children[0].smash()
        self.assertFalse(c, "Should not smash when level == max_depth")

    def test_smash_true0(self):
        """Test if smash works."""
        for _ in range(10):
            BlockA = self.BlockA.create_copy()
            BlockA.max_depth = 2
            BlockA.smash()
            self.assertEqual(len(get_all_blocks_positions(BlockA)), 21, "When level == 1, math.exp(-0.25*(level-1)) is 1 > random_num generated, then the number of nodes should be 21")

        for _ in range(10):
            BlockB = self.BlockB.create_copy()
            BlockB.max_depth = 2
            for child in BlockB.children:
                child.max_depth = 2
                child.smash()
            self.assertEqual(len(get_all_blocks_positions(BlockB)),  21)

        for _ in range(10):
            BlockC = self.BlockC.create_copy()
            for child in BlockC.children:
                child.smash()
            self.assertTrue(len(get_all_blocks_positions(BlockC)) == 21)

    def test_smash_true1(self):
        """Test if smash leaf works.
        If we smash all leaves for BlockD, then the number of nodes should be at
        range"""
        num_d = []
        for _ in range(20):
            BlockD = self.BlockD.create_copy()
            smash_all_leaves(BlockD)
            num_d.append(len(get_all_blocks_positions(BlockD)))
            self.assertTrue(69 <= len(get_all_blocks_positions(BlockD)) <= 64+ 16 + 4+1, "The number of nodes should be at this range after we smash all leaves")
            self.assertEqual(len(get_all_blocks_positions(BlockD)) % 4, 1, "Every successful smash fail to get 4 new nodes")

    def test_rotate_false(self):
        """Rotation fail for non_children block
        Cite: If this Block has no children, do nothing. If <direction> is 1, rotate
        clockwise. If <direction> is 3, rotate counter-clockwise.
         """
        BlockA = self.BlockA.create_copy()
        BlockB = self.BlockB.create_copy()
        self.assertFalse(BlockA.rotate(1))
        for child in BlockB.children:
            self.assertFalse(child.rotate(random.choice([1, 3])))

    def test_rotate_true_level0_b(self):
        """ Rotation for Block B
        BlockB         clockwise, direction == 1
        ---------------------
        |    b3   |    b2   |  b1: (1, 128, 181)
        |         |         |   b2: (199, 44, 58)
        |-------------------|
        |    b4   |     b1  |    b3: colour = (255, 211, 92)
        |         |         |    b4: colour = (138, 151, 71)
        ---------------------

        BlockB      counterclockwise: direction == 3

                BlockB 750
        ---------------------
        |    b1   |    b4   |  b1: (1, 128, 181)
        |         |         |   b2: (199, 44, 58)
        |-------------------|
        |    b2   |     b3  |    b3: colour = (255, 211, 92)
        |         |         |    b4: colour = (138, 151, 71)
        ---------------------


        """
        # Clockwise
        BlockB = self.BlockB.create_copy()
        self.assertTrue(BlockB.rotate(1))
        children_pos = BlockB._children_positions()
        children_colour = [(199, 44, 58), (255, 211, 92), (138, 151, 71), (1, 128, 181)]
        for i in range(4):
            self.assertEqual(BlockB.children[i].position, children_pos[i], "Fail to uodate position or update children list")
            self.assertEqual(BlockB.children[i].colour, children_colour[i], "Fail to update colour or update children list")

        # Counter Clockwise
        BlockB = self.BlockB.create_copy()
        self.assertTrue(BlockB.rotate(3))
        children_pos = BlockB._children_positions()
        children_colour = [(138, 151, 71), (1, 128, 181), (199, 44, 58), (255, 211, 92)]
        for i in range(4):
            self.assertEqual(BlockB.children[i].position, children_pos[i], "Fail to uodate position or update children list, fail for counter clockwise")
            self.assertEqual(BlockB.children[i].colour, children_colour[i], "Fail to update colour or update children list, fail for counter clockwise")

    def test_rotate_true_level0_c(self):
        """   Original
                BlockC size_total = 1000
        -------------------------------------
        |                |   c01   |   c00  |  c00: (255, 211, 92)
        |                |         |        |   c01 (255, 211, 92)
        |      c1        |------------------|    c02 (138, 151, 71)
        |                |    c02  |    c03 |    c03 (1, 128, 181)
        |                |         |        |     c1   (1, 128, 181)
        -------------------------------------     c20 (199, 44, 58)
        |    c21|  c20   |                  |     c21 (123, 121, 438)
        |       |        |                  |     c22 (123, 482, 12)
        -----------------|      c3          |     c23 (89, 123, 234)
        |   c22 |   c23  |                  |
        |       |        |                  |     c3 (199, 44, 58)
        -------------------------------------

        Clockwise level == 0 direction == 1
                        BlockC size_total = 1000
        -------------------------------------
        |       |        |                  |  c00: (255, 211, 92)
        |   c22 |  c21   |                  |   c01 (255, 211, 92)
        |----------------|            c1    |    c02 (138, 151, 71)
        |       |        |                  |    c03 (1, 128, 181)
        |   c23 |    c20 |                  |     c1   (1, 128, 181)
        -------------------------------------     c20 (199, 44, 58)
        |                |        |         |     c21 (123, 121, 438)
        |                |   c02  |   c01   |     c22 (123, 482, 12)
        |       c3       |------------------|     c23 (89, 123, 234)
        |                |        |         |
        |                |   c03  |   c00   |     c3 (199, 44, 58)
        -------------------------------------

        """
        BlockC = self.BlockC.create_copy()
        BlockC.rotate(1)
        childrenC_pos = BlockC._children_positions()
        C0_children = BlockC.children
        self.assertEqual(C0_children[0].colour, (1, 128, 181), "Fail to rotate level 1, children 1 -> 0")
        self.assertEqual(C0_children[2].colour, (199, 44, 58), "Fail to rotate level 1, children 3 -> 2")
        for i in range(4):
            self.assertEqual(childrenC_pos[i], C0_children[i].position, "Fail to update position")

        # Check child 1
        child1 = BlockC.children[1]
        child1_pos = child1._children_positions()
        C1_children = child1.children
        color_lst = [(123, 121, 438), (123, 482, 12), (89, 123, 234), (199, 44, 58)]
        for i in range(4):
            self.assertEqual(child1_pos[i], C1_children[i].position, "Fail to update descendent position")
            self.assertEqual(C1_children[i].colour, color_lst[i], "Fail to update descendent colour")

        # check child 3
        child3 = BlockC.children[3]
        child3_pos = child3._children_positions()
        C3_children = child3.children
        color_lst = [(255, 211, 92), (138, 151, 71), (1, 128, 181), (255, 211, 92)]
        for i in range(4):
            self.assertEqual(child3_pos[i], C3_children[i].position, "Fail to update descendent position")
            self.assertEqual(C3_children[i].colour, color_lst[i], "Fail to update descendent colour")

    def test_rotate_true_level1_c(self):
        """   Original
        BlockC size_total = 1000
        -------------------------------------
        |                |   c01   |   c00  |  c00: (255, 211, 92)
        |                |         |        |   c01 (255, 211, 92)
        |      c1        |------------------|    c02 (138, 151, 71)
        |                |    c02  |    c03 |    c03 (1, 128, 181)
        |                |         |        |     c1   (1, 128, 181)
        -------------------------------------     c20 (199, 44, 58)
        |    c21|  c20   |                  |     c21 (123, 121, 438)
        |       |        |                  |     c22 (123, 482, 12)
        -----------------|      c3          |     c23 (89, 123, 234)
        |   c22 |   c23  |                  |
        |       |        |                  |     c3 (199, 44, 58)
        -------------------------------------

        c0 rotate counter clockwise
        -------------------------------------
        |                |   c00   |   c03  |  c00: (255, 211, 92)
        |                |         |        |   c01 (255, 211, 92)
        |      c1        |------------------|    c02 (138, 151, 71)
        |                |    c01  |    c02 |    c03 (1, 128, 181)
        |                |         |        |     c1   (1, 128, 181)
        -------------------------------------     c20 (199, 44, 58)
        |    c21|  c20   |                  |     c21 (123, 121, 438)
        |       |        |                  |     c22 (123, 482, 12)
        -----------------|      c3          |     c23 (89, 123, 234)
        |   c22 |   c23  |                  |
        |       |        |                  |     c3 (199, 44, 58)
        -------------------------------------



        """
        BlockC = self.BlockC.create_copy()
        c0 = BlockC.children[0].create_copy()
        c1 = BlockC.children[1].create_copy()
        c2 = BlockC.children[2].create_copy()
        c3 = BlockC.children[3].create_copy()
        BlockC.children[0].rotate(3)
        c0_r = BlockC.children[0]
        self.assertFalse(c0_r == c0, "Fail to rotate in specific level")
        self.assertTrue(c1 == BlockC.children[1], "Other block should not mutate")
        self.assertTrue(c2 == BlockC.children[2])
        self.assertTrue(c3 == BlockC.children[3])

        # check c0_r
        color_check = [(1, 128, 181), (255, 211, 92), (255, 211, 92), (138, 151, 71)]
        for i in range(4):
            self.assertEqual(color_check[i], c0_r.children[i].colour, "Fail to update the colour")
            self.assertEqual(c0_r._children_positions()[i], c0_r.children[i].position, "Fail to update children positions")

        # Rotate c2 clockwise
        #             c2 rotate clockwise
        #     -------------------------------------
        #     |                |   c00   |   c03  |  c00: (255, 211, 92)
        #     |                |         |        |   c01 (255, 211, 92)
        #     |      c1        |------------------|    c02 (138, 151, 71)
        #     |                |    c01  |    c02 |    c03 (1, 128, 181)
        #     |                |         |        |     c1   (1, 128, 181)
        #     -------------------------------------     c20 (199, 44, 58)
        #     |    c22|  c21   |                  |     c21 (123, 121, 438)
        #     |       |        |                  |     c22 (123, 482, 12)
        #     -----------------|      c3          |     c23 (89, 123, 234)
        #     |   c23 |   c20  |                  |
        #     |       |        |                  |     c3 (199, 44, 58)
        #     -------------------------------------

        BlockC.children[2].rotate(1)
        c2_r = BlockC.children[2]
        self.assertFalse(c2_r == c2, "Fail to counter clockwise in a specific level")
        self.assertTrue(c1 == BlockC.children[1])
        self.assertTrue(c3 == BlockC.children[3])
        color_check = [(123, 121, 438), (123, 482, 12), (89, 123, 234), (199, 44, 58)]
        for i in range(4):
            self.assertEqual(color_check[i], c2_r.children[i].colour, "Fail to update the colour")
            self.assertEqual(c2_r._children_positions()[i], c2_r.children[i].position, "Fail to update children positions")

    def test_rotate_true_level0_d(self):
        pass


from blocky import _block_to_squares

class TestBlocky(TestBlock):
    def setUp(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().setUp()

    def tearDown(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().tearDown()

    def test_block_to_square_A(self):
        """
        BlockA
        Block(position, size, colour, level, max_depth
        position (0, 0) , size = 750, colour = (255, 211, 92) level = 0, max_depth = 0
        ------------
        |          |
        |          |
        |          |
        ------------
        """
        BlockA = self.BlockA.create_copy()
        expect = [((255, 211, 92), (0, 0), 750)]
        self.assertEqual(expect, _block_to_squares(BlockA), "Base case for _block_to_square fail ")

    def test_block_to_square_B(self):
        """
                BlockB
        (0, 0)
        ---------------------
        |    b2   |    b1   |  b1: (1, 128, 181)
        |         |         |   b2: (199, 44, 58)
        |-------------------|
        |    b3   |     b4  |    b3: colour = (255, 211, 92)
        |         |         |    b4: colour = (138, 151, 71)
        ---------------------
        """

        BlockB = self.BlockB.create_copy()
        get_lst = _block_to_squares(BlockB)
        self.assertEqual(len(get_lst), 4, "You fail to get all blocks in list")
        expect = [((1, 128, 181), (375, 0), 375), ((199, 44, 58), (0, 0), 375), ((255, 211, 92), (0, 375), 375), ((138, 151, 71), (375, 375), 375)]
        for item in expect:
            self.assertTrue(item in get_lst, "You left some leaves")

    def test_block_to_square_C(self):
        """
                BlockC size_total = 1000
        (1398123, 1239129)
        -------------------------------------
        |                |   c01   |   c00  |  c00: (255, 211, 92)
        |                |         |        |   c01 (255, 211, 92)
        |      c1        |------------------|    c02 (138, 151, 71)
        |                |    c02  |    c03 |    c03 (1, 128, 181)
        |                |         |        |     c1   (1, 128, 181)
        -------------------------------------     c20 (199, 44, 58)
        |    c21|  c20   |                  |     c21 (123, 121, 438)
        |       |        |                  |     c22 (123, 482, 12)
        -----------------|      c3          |     c23 (89, 123, 234)
        |   c22 |   c23  |                  |
        |       |        |                  |     c3 (199, 44, 58)
        --------------------------------------

        """
        BlockC = self.BlockC.create_copy()
        c1 = ((1, 128, 181), (1398123, 1239129), BlockC._child_size())
        c3 = ((199, 44, 58), (1398123 + BlockC._child_size(), 1239129 + BlockC._child_size()), BlockC._child_size())
        pass




















































if __name__ == "__main__":
    unittest.main(exit=False)
