from __future__ import annotations

from typing import TYPE_CHECKING

import numpy

from sub_scenes.function_intro_scene.scene_helpers import (
    SceneOverlayBox,
    Set,
    make_arrow,
)

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m
from ..scene_globals import f_color


def quadratic_function_overlay(s: MainTheatreScene) -> None:
    formula = m.Tex(r"f(x) = x^2", font_size=24)
    formula.set_color(m.BLUE)
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
    overlay_box = SceneOverlayBox()
    overlay_box.put_mobject_inside(scene_mobjects)
    s.play(m.FadeIn(overlay_box.mobject))
    s.play(m.Write(formula))
    s.play(m.ShowCreation(plane))
    s.play(m.ShowCreation(graph))


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
    quadratic_function_overlay(s)
