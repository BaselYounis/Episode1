from __future__ import annotations

from typing import TYPE_CHECKING


import numpy

from helpers import mixed_tex_parser
from sub_scenes.function_intro_scene.scene_helpers import (
    SceneOverlayBox,
    Set,
    make_arrow,
)

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m
from ..scene_globals import f_color, x_color, y_color


def quadratic_function_overlay(s: MainTheatreScene) -> list[m.Mobject]:
    formula = mixed_tex_parser.convert_tex_to_vgroup(r"$f(x)=x^2$")
    mixed_tex_parser.map_tex_to_color(
        formula, tex_to_color_map={"x": x_color, "f": f_color, "x^2": y_color}
    )
    formula.scale(2.5)
    formula.to_corner(m.UL)
    width = m.FRAME_WIDTH
    height = m.FRAME_HEIGHT

    x_edge_number_to_exclude = int(width / 2)
    y_edge_number_to_exclude = int(height / 2)
    plane = m.NumberPlane(
        x_range=[-int(width / 2), int(width / 2), 1],
        y_range=[-int(height / 2), int(height / 2), 1],
        background_line_style={
            "stroke_color": m.WHITE,
            "stroke_width": 0.5,
            "stroke_opacity": 0.25,
        },
        x_axis_config={
            "include_numbers": True,
            "numbers_to_exclude": [
                0,
                x_edge_number_to_exclude,
                -x_edge_number_to_exclude,
            ],
        },
        y_axis_config={
            "include_numbers": True,
            "numbers_to_exclude": [
                0,
                y_edge_number_to_exclude,
                -y_edge_number_to_exclude,
            ],
        },
    )
    graph_x_limit = numpy.sqrt(height / 2)
    graph = plane.get_graph(
        lambda x: x**2,
        x_range=[-graph_x_limit, graph_x_limit],
        color=f_color,
        stroke_width=1.5,
    )
    scene_mobjects = m.VGroup(formula, plane, graph)
    overlay_box = SceneOverlayBox(size=0.45)
    overlay_box.put_mobject_inside(scene_mobjects)
    scene_mobjects.add(overlay_box.mobject)
    s.play(m.FadeIn(overlay_box.mobject))
    s.play(m.Write(formula))
    s.play(m.ShowCreation(plane))
    s.play(m.ShowCreation(graph))
    return [overlay_box.mobject, formula, plane, graph]


def numbers_to_numbers_sub_section(s: MainTheatreScene, x_set: Set, y_set: Set) -> None:
    x_set_anim = x_set.transform_elements(["-2", "-1", "1", "2"])
    y_set_anim = y_set.transform_elements(["4", "1", "1", "4"])

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
    quad_scene_mobjects = quadratic_function_overlay(s)
    fade_out_anims = [
        m.FadeOut(quad_scene_mobjects[0]),
        m.FadeOut(quad_scene_mobjects[1]),
        m.FadeOut(quad_scene_mobjects[2]),
        m.FadeOut(quad_scene_mobjects[3]),
    ]
    s.wait_for_button()
    s.play(
        m.FadeOut(arrow_1_to_1),
        m.FadeOut(arrow_2_to_4),
        m.FadeOut(arrow_3_to_9),
        m.FadeOut(arrow_4_to_16),
        *fade_out_anims,
    )
