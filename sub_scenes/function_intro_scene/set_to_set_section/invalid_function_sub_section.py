from __future__ import annotations
from typing import TYPE_CHECKING

from helpers import mixed_tex_parser
from sub_scenes.function_intro_scene.scene_helpers import Set, make_arrow

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


def invalid_function_sub_section(s: MainTheatreScene, x_set: Set, y_set: Set) -> None:
    #the second 0 index to point to the dot now the actual text
    arrow_a_to_1 = make_arrow(
        x_set.elements[0][0], y_set.elements[0][0], upward=True
    )  # a → 1
    arrow_a_to_2 = make_arrow(
        x_set.elements[0][0], y_set.elements[1][0], upward=False
    )  # a → 2
    arrow_b_to_2 = make_arrow(
        x_set.elements[1][0], y_set.elements[1][0], upward=True
    )  # b → 2
    arrow_c_to_3 = make_arrow(
        x_set.elements[2][0], y_set.elements[2][0], upward=False
    )  # c → 3 
    invalid_function_text = mixed_tex_parser.convert_tex_to_vgroup(
        r"""invalid function $\times$"""
    )
    mixed_tex_parser.map_tex_to_color(invalid_function_text, {r"\times": m.RED})  # type: ignore
    sets_center = (x_set.mobject.get_center() + y_set.mobject.get_center()) / 2
    invalid_function_text.next_to(sets_center, m.UP, buff=2)

    s.play(
        m.ShowCreation(arrow_a_to_2),
        m.ShowCreation(arrow_a_to_1),
        m.ShowCreation(arrow_b_to_2),
        m.ShowCreation(arrow_c_to_3),
    )
    s.play(m.FadeIn(invalid_function_text, shift=m.UP * 0.5))
    s.wait_for_button()
    s.play(
        m.FadeOut(invalid_function_text, shift=m.UP * 0.5),
        m.FadeOut(arrow_a_to_2),
        m.FadeOut(arrow_a_to_1),
        m.FadeOut(arrow_b_to_2),
        m.FadeOut(arrow_c_to_3),
    )
