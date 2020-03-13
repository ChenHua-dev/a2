from block import *
import unittest
from settings import colour_name, COLOUR_LIST


class TestBlock(unittest.TestCase):
    def test__update_children_positions1(self):
        board = Block((1, 1), 2, None, 0, 10)
        c1 = Block((2, 1), 1, random.choice(COLOUR_LIST), 1, 10)
        c2 = Block((1, 1), 1, random.choice(COLOUR_LIST), 1, 10)
        c3 = Block((1, 2), 1, random.choice(COLOUR_LIST), 1, 10)
        c4 = Block((2, 2), 1, random.choice(COLOUR_LIST), 1, 10)
        board.children.append(c1)
        board.children.append(c2)
        board.children.append(c3)
        board.children.append(c4)
        # update with only one extra level of children
        board._update_children_positions((3, 4))
        expect = [(4, 4), (3, 4), (3, 5), (4, 5)]
        actual = board._children_positions()
        self.assertEqual(expect, actual)

    def test__update_children_positions2(self):
        board = Block((2, 2), 4, None, 0, 10)
        c1 = Block((4, 2), 2, random.choice(COLOUR_LIST), 1, 10)
        c2 = Block((2, 2), 2, random.choice(COLOUR_LIST), 1, 10)
        c2_1 = Block((3, 2), 1, random.choice(COLOUR_LIST), 1, 10)
        c2_2 = Block((2, 2), 1, random.choice(COLOUR_LIST), 1, 10)
        c2_3 = Block((2, 3), 1, random.choice(COLOUR_LIST), 1, 10)
        c2_4 = Block((3, 3), 1, random.choice(COLOUR_LIST), 1, 10)
        c2.children.append(c2_1)
        c2.children.append(c2_2)
        c2.children.append(c2_3)
        c2.children.append(c2_4)
        c3 = Block((2, 4), 2, random.choice(COLOUR_LIST), 1, 10)
        c4 = Block((4, 4), 2, random.choice(COLOUR_LIST), 1, 10)
        c4_1 = Block((5, 4), 1, random.choice(COLOUR_LIST), 1, 10)
        c4_2 = Block((4, 4), 1, random.choice(COLOUR_LIST), 1, 10)
        c4_3 = Block((4, 5), 1, random.choice(COLOUR_LIST), 1, 10)
        c4_4 = Block((5, 5), 1, random.choice(COLOUR_LIST), 1, 10)
        c4.children.append(c4_1)
        c4.children.append(c4_2)
        c4.children.append(c4_3)
        c4.children.append(c4_4)
        board.children.append(c1)
        board.children.append(c2)
        board.children.append(c3)
        board.children.append(c4)
        # update with only one extra level of children
        board._update_children_positions((8, 5))
        exp_upleft = [(9, 5), (8, 5), (8, 6), (9, 6)]
        exp_lowright = [(11, 7), (10, 7), (10, 8), (11, 8)]
        # board.children[0]._children_positions()
        act_upleft = board.children[1]._children_positions()
        # board.children[2]._children_positions()
        act_lowright = board.children[3]._children_positions()
        self.assertEqual(exp_upleft + exp_lowright,
                         act_upleft + act_lowright)

    def test_smash(self):


if __name__ == "__main__":
    unittest.main(exit=False)
