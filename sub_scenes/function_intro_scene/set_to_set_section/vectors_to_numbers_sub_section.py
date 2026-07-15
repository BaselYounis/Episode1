from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
from sub_scenes.function_intro_scene.scene_helpers import (
    Set,
    get_vertical_number_list_mobject,
)

import manimlib as m

element_1 = get_vertical_number_list_mobject(numbers=[1, 1])
element_2 = get_vertical_number_list_mobject(numbers=[2, 2])
element_3 = get_vertical_number_list_mobject(numbers=[3, 3])
element_4 = get_vertical_number_list_mobject(numbers=[4, 4])


def vectors_to_numbers_sub_section(s: MainTheatreScene, x_set: Set, y_set: Set):
    x_set_anim = x_set.transform_elements([element_1, element_2, element_3, element_4])
    y_set_anim = y_set.transform_elements(["2", "8", "18", "32"])
    s.play(x_set_anim, y_set_anim)
