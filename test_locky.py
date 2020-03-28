from typing import List, Optional, Tuple
import os
import pygame
import pytest

from block import Block
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten
from player import _get_block
from renderer import Renderer
from settings import COLOUR_LIST


class TestBlock:
    def setup_class(self):
        block_0 = Block((0, 0), 750, None, 0, 3)
        children_positions = block_0._children_positions()
        child_size1 = block_0._child_size()
        block_1_0 = Block(children_positions[0], child_size1, )



