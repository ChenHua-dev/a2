from test_block_and_blocky import TestBlock
from block import random as a2_random
from goal import generate_goals, PerimeterGoal, BlobGoal, _flatten
import random
from settings import COLOUR_LIST, colour_name

import unittest

from block import *
from player import *

from assignments.a2.block import Block
SEED_NUMBER = 996


def get_size_lst(block):
    if not block.children:
        return [block.size]
    else:
        result = []
        for child in block.children:
            result.append(child.size)
        return result


class TestGenerateGoal(TestBlock):
    def setUp(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().setUp()

    def tearDown(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().tearDown()

    def test_generate_goal(self):
        for _ in range(10):
            lst_goals = generate_goals(4)
            self.assertEqual(len(COLOUR_LIST), 4, "You should not mutate the COLOUR_List")
            colour_dict = {}
            type_dict = {}
            for item in lst_goals:
                self.assertTrue(isinstance(item, PerimeterGoal) or isinstance(item, BlobGoal), "The instance should be goal")
                if isinstance(item, PerimeterGoal):
                    type_dict[1] = 2
                else:
                    type_dict[2] = 1

                if item.colour in colour_dict:
                    colour_dict[item.colour] += 1
                else:
                    colour_dict[item.colour] = 1
            self.assertEqual(len(type_dict), 1, "The instance of the list should be the same")
            get_values = list(colour_dict.values())
            for num in get_values:
                self.assertEqual(num, 1, "The colour should be different for each")

class TestFlatten(TestBlock):
    def setUp(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().setUp()

    def tearDown(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().tearDown()

    def test_flatten_a(self):
        """Test flatten Block A when Block A is assigned different levels

        Expected to return
        [[(255, 211, 92)] * 2^{max depth}] * 2 ^ {max depth})
        """
        for i in range(5):
            BlockA = self.BlockA.create_copy()
            BlockA.max_depth = i
            get_A = _flatten(BlockA)
            expect = [[(255, 211, 92)] * pow(2, i)] * pow(2, i)
            self.assertEqual(expect, get_A)

    def test_flatten_B(self):
        """Test flatten Block B"""
        BlockB = self.BlockB.create_copy()
        expect = [[(199, 44, 58), (255, 211, 92)], [(1, 128, 181), (138, 151, 71)]]
        actual = _flatten(BlockB)
        self.assertEqual(actual, expect, "Fail to flatten for unrecursive block, check the docstring again")

    def test_faltten_C(self):
        """Test flatten Block C"""
        BlockC = self.BlockC.create_copy()
        expect = [[(1, 128, 181), (1, 128, 181), (123, 121, 438), (123, 482, 12)],
                  [(1, 128, 181), (1, 128, 181), (199, 44, 58), (89, 123, 234)],
                  [(255, 211, 92), (138, 151, 71), (199, 44, 58), (199, 44, 58)],
                  [(255, 211, 92), (1, 128, 181), (199, 44, 58), (199, 44, 58)]]
        actual = _flatten(BlockC)
        self.assertEqual(actual, expect, "Fail to flatten from level 1--> level 2")

    def test_flatten_D(self):
        BlockD = self.BlockD.create_copy()
        expect = [[(138, 151, 71), (255, 211, 92), (255, 211, 92), (1, 128, 181), (138, 151, 71), (138, 151, 71), (1, 128, 181), (1, 128, 181)],
                  [(199, 44, 58), (199, 44, 58), (138, 151, 71), (199, 44, 58), (138, 151, 71),  (138, 151, 71), (1, 128, 181), (1, 128, 181)],
                  [(255, 211, 92), (255, 211, 92), (1, 128, 181), (199, 44, 58), (199, 44, 58), (199, 44, 58), (199, 44, 58), (199, 44, 58)],
                  [(255, 211, 92), (255, 211, 92), (255, 211, 92), (1, 128, 181), (199, 44, 58), (199, 44, 58), (199, 44, 58), (199, 44, 58)],
                  [(1, 128, 181), (1, 128, 181),(1, 128, 181),(1, 128, 181),(138, 151, 71), (1, 128, 181), (255, 211, 92), (255, 211, 92)],
                  [(1, 128, 181),(1, 128, 181),(1, 128, 181),(1, 128, 181),(199, 44, 58), (199, 44, 58), (1, 128, 181), (138, 151, 71)],
                  [(1, 128, 181),(1, 128, 181),(1, 128, 181),(1, 128, 181),(138, 151, 71), (199, 44, 58), (1, 128, 181), (1, 128, 181)],
                  [(1, 128, 181),(1, 128, 181),(1, 128, 181),(1, 128, 181),(255, 211, 92), (255, 211, 92), (1, 128, 181), (138, 151, 71)]]
        actual = _flatten(BlockD)
        self.assertEqual(actual, expect, "Fail to flatten among trees")


class TestPerimeterGoal(TestBlock):
    def setUp(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().setUp()

    def tearDown(self) -> None:
        random.seed(SEED_NUMBER)
        a2_random.seed(SEED_NUMBER)
        super().tearDown()

    def test_peri_description(self):
        a = PerimeterGoal((255, 211, 92))
        get_name = colour_name((255, 211, 92))
        self.assertTrue(get_name in a.description(), "You should use colour name in description")

    def test_peri_score_A(self):
        """Test score Block A when Block A is assigned different levels

        Expect values: 4 * 2^i

        """
        for i in range(5):
            BlockA = self.BlockA.create_copy()
            BlockA.max_depth = i
            goal = PerimeterGoal(BlockA.colour)
            actual = goal.score(BlockA)
            expect = 4 * pow(2, i)
            self.assertEqual(expect, actual)

    def test_peri_score_B(self):
        """Test perimeter score for B"""
        BlockB = self.BlockB.create_copy()
        expect = 4
        colour_lst = [(1, 128, 181), (199, 44, 58), (255, 211, 92), (138, 151, 71)]
        for colour in colour_lst:
            goal = PerimeterGoal(colour)
            actual = goal.score(BlockB)
            self.assertEqual(expect, actual, "Fail to get perimeter score when level == 1")

    def test_peri_score_C(self):
        """Test perimeter score for C"""
        colour_lst = [(255, 211, 92), ()]
        expects = [3, ]























if __name__ == '__main__':
    unittest.main(exit = False)
