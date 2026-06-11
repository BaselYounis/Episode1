from __future__ import annotations
from typing import TYPE_CHECKING

from sub_scenes.function_intro_scene.scene_helpers import Set, make_arrow

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m

 


def numbers_to_numbers_sub_section(s: MainTheatreScene, x_set: Set, y_set: Set) -> None:
    x_set_anim = x_set.transform_elements(["1", "2", "3", "4"])
    y_set_anim = y_set.transform_elements(["1", "4", "9", "16"])
    arrow_1_to_1 = make_arrow(
        x_set.elements[0], y_set.elements[0], upward=True
    )  # 1 → 1
    arrow_2_to_4 = make_arrow(
        x_set.elements[1], y_set.elements[1], upward=True
    )  # 2 → 4
    arrow_3_to_9 = make_arrow(
        x_set.elements[2], y_set.elements[2], upward=False
    )  # 3 → 9
    arrow_4_to_16 = make_arrow(
        x_set.elements[3], y_set.elements[3], upward=False
    )  # 4 → 16
    s.play(x_set_anim, y_set_anim)
    s.play(
        m.ShowCreation(arrow_1_to_1),
        m.ShowCreation(arrow_2_to_4),
        m.ShowCreation(arrow_3_to_9),
        m.ShowCreation(arrow_4_to_16),
    )
