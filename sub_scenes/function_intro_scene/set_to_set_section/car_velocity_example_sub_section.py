from __future__ import annotations
from typing import TYPE_CHECKING

from helpers import mixed_tex_parser
from sub_scenes.function_intro_scene.scene_helpers import Set, make_arrow

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


def car_velocity_example_sub_section(
    s: MainTheatreScene, x_set: Set, y_set: Set
) -> None:
    f_of_0s = mixed_tex_parser.convert_tex_to_vgroup(r"$f(0s)=0km/h$")
    f_of_5s = mixed_tex_parser.convert_tex_to_vgroup(r"$f(5s)=0km/h$")
    f_of_10s = mixed_tex_parser.convert_tex_to_vgroup(r"$f(10s)=20km/h$")
    checkmark_1 = mixed_tex_parser.convert_tex_to_vgroup(r"$\checkmark$")
    mixed_tex_parser.map_tex_to_color(checkmark_1, {r"\checkmark": m.GREEN})
    checkmark_2 = checkmark_1.copy()

    mixed_tex_parser.map_tex_to_color(f_of_0s, {"f": m.YELLOW_A, "0s": m.BLUE, "0km/h": m.RED})  # type: ignore
    mixed_tex_parser.map_tex_to_color(f_of_5s, {"f": m.YELLOW_A, "5s": m.BLUE, "0km/h": m.RED})  # type: ignore
    mixed_tex_parser.map_tex_to_color(f_of_10s, {"f": m.YELLOW_A, "10s": m.BLUE, "20km/h": m.RED})  # type: ignore
    x_set_anim = x_set.transform_elements(["0s", "5s", "10s", "15s"])
    y_set_anim = y_set.transform_elements(["0km/h", "20km/h", "40km/h"])
    set_anim_group = m.AnimationGroup(x_set_anim, y_set_anim)
    arrow_a_to_1 = make_arrow(x_set.elements[0], y_set.elements[0], upward=True)
    arrow_b_to_2 = make_arrow(x_set.elements[1], y_set.elements[0], upward=False)
    arrow_c_to_2 = make_arrow(x_set.elements[2], y_set.elements[1], upward=False)
    arrow_d_to_3 = make_arrow(x_set.elements[3], y_set.elements[2], upward=False)
    sets_center = (x_set.mobject.get_center() + y_set.mobject.get_center()) / 2
    f_of_0s.next_to(sets_center, m.UP, buff=2)
    f_of_5s.next_to(f_of_0s, m.DOWN, buff=0.1)
    checkmark_1.next_to(f_of_0s, m.RIGHT, buff=0.5)
    checkmark_2.next_to(f_of_5s, m.RIGHT, buff=0.5)

    s.play(set_anim_group)
    s.play(
        m.ShowCreation(arrow_a_to_1),
        m.ShowCreation(arrow_b_to_2),
        m.ShowCreation(arrow_c_to_2),
        m.ShowCreation(arrow_d_to_3),
    )
    s.play(
        m.FadeIn(f_of_0s, shift=m.UP * 0.5),
    )
    s.wait_for_button()
    s.play(m.FadeIn(f_of_5s, shift=m.UP * 0.5))
    s.wait_for_button()
    s.play(m.Write(checkmark_1), m.Write(checkmark_2))
