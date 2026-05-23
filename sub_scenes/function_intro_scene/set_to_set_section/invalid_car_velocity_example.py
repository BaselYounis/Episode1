from __future__ import annotations
from typing import TYPE_CHECKING
from ..scene_globals import f_color, x_color, y_color

from helpers import mixed_tex_parser
from sub_scenes.function_intro_scene.scene_helpers import Set, make_arrow

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


def invalid_car_velocity_example(s: MainTheatreScene, x_set: Set, y_set: Set) -> None:
    x_set_anim = x_set.transform_elements(["0s", "5s"])
    x_mark_1 = mixed_tex_parser.convert_tex_to_vgroup(r"$\times$")
    mixed_tex_parser.map_tex_to_color(x_mark_1, {r"\times": m.RED})
    x_mark_2 = x_mark_1.copy()
    arrow_a_to_1 = make_arrow(x_set.elements[0], y_set.elements[0], upward=True)
    arrow_a_to_2 = make_arrow(x_set.elements[0], y_set.elements[1], upward=False)
    arrow_b_to_3 = make_arrow(x_set.elements[1], y_set.elements[2], upward=False)
    f_of_0s_to_1 = mixed_tex_parser.convert_tex_to_vgroup(r"$f(0s)=0km/h$")
    f_of_0s_to_2 = mixed_tex_parser.convert_tex_to_vgroup(r"$f(0s)=20km/h$")
    mixed_tex_parser.map_tex_to_color(f_of_0s_to_1, {"f": f_color, "0s": x_color, "0km/h": y_color})  # type: ignore
    mixed_tex_parser.map_tex_to_color(f_of_0s_to_2, {"f": f_color, "0s": x_color, "20km/h": y_color})  # type: ignore

    sets_center = (x_set.mobject.get_center() + y_set.mobject.get_center()) / 2
    f_of_0s_to_1.next_to(sets_center, m.UP, buff=2)
    f_of_0s_to_2.next_to(f_of_0s_to_1, m.DOWN, buff=0.1)
    x_mark_1.next_to(f_of_0s_to_1, m.RIGHT, buff=0.5)
    x_mark_2.next_to(f_of_0s_to_2, m.RIGHT, buff=0.5)
    s.play(x_set_anim)
    s.play(
        m.ShowCreation(arrow_a_to_2),
        m.ShowCreation(arrow_a_to_1),
        m.ShowCreation(arrow_b_to_3),
    )
    s.wait_for_button()
    s.play(
        m.FadeIn(f_of_0s_to_1, shift=m.UP * 0.5),
    )
    s.wait_for_button()
    s.play(
        m.FadeIn(f_of_0s_to_2, shift=m.UP * 0.5),
    )
    s.wait_for_button()
    s.play(m.Write(x_mark_1), m.Write(x_mark_2))
    s.wait_for_button()
    s.play(
        m.FadeOut(x_mark_1),
        m.FadeOut(x_mark_2),
        m.FadeOut(f_of_0s_to_1),
        m.FadeOut(f_of_0s_to_2),
        m.FadeOut(arrow_a_to_1),
        m.FadeOut(arrow_a_to_2),
        m.FadeOut(arrow_b_to_3),
    )
