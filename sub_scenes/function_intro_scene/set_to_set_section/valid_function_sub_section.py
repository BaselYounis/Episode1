from __future__ import annotations
from typing import TYPE_CHECKING
from helpers import mixed_tex_parser
from sub_scenes.function_intro_scene.scene_helpers import  Set, make_arrow

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


def valid_function_sub_section(s: MainTheatreScene, x_set: Set, y_set: Set) -> None:
    valid_function_text = mixed_tex_parser.convert_tex_to_vgroup(
        r"""valid function $\checkmark$"""
    )
    mixed_tex_parser.map_tex_to_color(valid_function_text, {r"\checkmark": m.GREEN})  # type: ignore
    sets_center = (x_set.mobject.get_center() + y_set.mobject.get_center()) / 2
    valid_function_text.next_to(sets_center, m.UP, buff=2)
    #the second 0 index to point to the dot now the actual text
    arrow_a_to_1 = make_arrow(
        x_set.elements[0], y_set.elements[0], upward=True
    )  # a → 1
    arrow_b_to_2 = make_arrow(
        x_set.elements[1], y_set.elements[1], upward=True
    )  # b → 2

    arrow_c_to_2 = make_arrow(
        x_set.elements[2], y_set.elements[1], upward=False
    )  # c → 2
    arrow_d_to_3 = make_arrow(
        x_set.elements[3], y_set.elements[2], upward=False
    )  # d → 3
    valid_function_text = mixed_tex_parser.convert_tex_to_vgroup(
        r"""valid function $\checkmark$"""
    )
    mixed_tex_parser.map_tex_to_color(valid_function_text, {r"\checkmark": m.GREEN})  # type: ignore
    sets_center = (x_set.mobject.get_center() + y_set.mobject.get_center()) / 2
    valid_function_text.next_to(sets_center, m.UP, buff=2)
    
    
    s.play(

        m.ShowCreation(arrow_a_to_1),
        m.ShowCreation(arrow_b_to_2),
        m.ShowCreation(arrow_c_to_2),
        m.ShowCreation(arrow_d_to_3),
    )
    s.wait_for_button()
    s.play(m.FadeIn(valid_function_text, shift=m.UP * 0.5))
    s.wait_for_button()
    s.play(
        m.FadeOut(valid_function_text, shift=m.UP * 0.5),
        m.FadeOut(arrow_a_to_1),
        m.FadeOut(arrow_b_to_2),
        m.FadeOut(arrow_c_to_2),
        m.FadeOut(arrow_d_to_3),
    )
    
    