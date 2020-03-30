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
        |    b1     |    b2   |  b1: (1, 128, 181)
        |          |         |   b2: (199, 44, 58)
        ---------------------
        |    b3    |     b4  |    b3: colour = (255, 211, 92)
        |         |         |    b4: colour = (138, 151, 71)
        ---------------------

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
        |   c23 |   c24  |                  |
        |       |        |                  |     c3 (199, 44, 58)
        --------------------------------------

        BlockD size_total = 996
        ---------------------------------------------------   d0:(1, 128, 181)       d20 (199, 44, 58)   d330 (1, 128, 181)
        |d111| d110|            |                         |   d10 (255, 211, 92)     d21 (138, 151, 71)  d332 (1, 128, 181)
        -----------|  d10      |                          |                            d22 (1, 128, 181)   d333 (138, 151, 71)
        |d112|d113 |           |            d0            |                          d23 (199, 44, 58)
        ------------------------                          |                           d300 (255, 211,92)
        |d121| d120| d131 |d130|                          |   d110 (199, 44, 58)     d301 (138, 151, 71)
        ------------------------                          |   d111 (138, 151, 71)    d302 (199, 44, 58)
        |d122|d123 | d132|d133 |                          |   d112 (255, 211, 92)    d303 (255, 211, 92)
        --------------------------------------------------    d113  (199, 44, 58)    d310 (199, 44, 58)
        |           |          |   d311| d310| d301| d300 |   d120  (138, 151, 71)   d311 (138, 151, 71)
        |       d21 |    d20   | --------------------------   d121  (255, 211, 92)   d312 (1, 128, 181)
        |           |          | d312 | d313 | d302| d303 |   d122   (1, 128, 181)    d313 (199, 44, 58)
        ---------------------------------------------------   d123   (199, 44, 58)   d321  (255, 211, 92)
        |           |          |  d321 | d320| d331|d330 |    d130   (255, 211, 92)  d320  (1, 128, 181)
        |   d22     |     d23  | --------------------------   d131  (1, 128, 181)    d322   (255, 211, 92)
        |           |          | d322 |  d323|d332 | d333|    d132   (199, 44, 58)   d323   (138, 151, 71)
        ---------------------------------------------------   d133   (1, 128, 182)   d331  (1, 128, 181)
        """
        BlockA = Block((0, 0), 750, (255, 211, 92), 0, 0) # Level 0

        BlockB = Block((0, 0), 750, None, 0, 1)     # Level 1
        b2 = Block((375, 0), 375, (1, 128, 181), 1, 1)
        b1 = Block((0, 0), 375, (199, 44, 58), 1, 1)
        b3 = Block((0, 375), 375, (255, 211, 92), 1, 1)
        b4 = Block((375, 375), 375, (138, 151, 71), 1, 1)
        BlockB.children = [b2, b1, b3, b4]

        BlockC = Block((1398123, 1239129), 1000, None, 0, 2)   # Level 2, not at (0, 0) position
        c_child_pos = BlockC._children_positions()

        c0 = Block(c_child_pos[0], 500, None, 1, 2)
        c1 = Block(c_child_pos[1], 500, (1, 128, 181), 1, 2)
        c2 = Block(c_child_pos[2], 500, None, 1, 2)
        c3 = Block(c_child_pos[3], 500, (199, 44, 58), 1, 2)
        BlockC.children = [c0, c1, c2, c3]

        c0_child_pos = c0._children_positions()
        c00 = Block(c0_child_pos[0], 250, (255, 211, 92),2,2)
        c01 = Block(c0_child_pos[1], 250, (255, 211, 92), 2,2)
        c02 = Block(c0_child_pos[2], 250, (138, 151, 71), 2,2)
        c03 = Block(c0_child_pos[3], 250, (1, 128, 181), 2,2)
        c0.children = [c00, c01, c02, c03]

        c2_child_pos = c2._children_positions()
        c20 = Block(c2_child_pos[0], 250, (199, 44, 58), 2, 2)
        c21 = Block(c2_child_pos[1], 250, (123, 121, 438), 2, 2)
        c22 = Block(c2_child_pos[2], 250, (123,482,12), 2, 2)
        c23 = Block(c2_child_pos[3], 250, (89, 123, 234), 2, 2) # Color not in COLOUR_LIST
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

        




























