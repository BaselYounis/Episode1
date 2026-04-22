from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m
import numpy as np


def ann_section(s: MainTheatreScene) -> m.VGroup:
    line = m.Line(
        start=m.ORIGIN,
        end=m.ORIGIN,
        color=m.WHITE,
    )
    line.set_stroke(width=0.4, color=m.WHITE)
    line.set_opacity(0.5)
    circle_radius = 0.1
    circle = m.Circle(
        radius=circle_radius,
        color=m.WHITE,
        fill_color=m.WHITE,
        fill_opacity=0.05,
        stroke_color=m.WHITE,
        stroke_width=0.2,
    )

    net_col_config = [1, 4, 4, 4, 1]
    network = m.VGroup()
    for col in net_col_config:
        col = [circle.copy() for _ in range(col)]
        col_group = m.VGroup(*col).arrange(m.DOWN, buff=0.2)
        network.add(col_group)
    network.arrange(m.RIGHT, buff=0.5)
    line = m.Line()
    line.set_opacity(0.5)
    line.set_stroke(width=0.4, color=m.WHITE)
    lines = []
    lines_creation_anim = []
    for i, col in enumerate(network):
        next_col = network[i + 1] if i < len(network) - 1 else None
        if next_col is None:
            break
        for circle in col:
            for other_circle in network[i + 1]:
                new_line = line.copy()
                to_next_dot_vector = other_circle.get_center() - circle.get_center()
                to_next_dot_vector = to_next_dot_vector / np.linalg.norm(
                    to_next_dot_vector
                )
                to_current_dot_vector = -to_next_dot_vector
                start = circle.get_center() + to_next_dot_vector * circle_radius
                end = other_circle.get_center() + to_current_dot_vector * circle_radius

                new_line.put_start_and_end_on(start, end)
                lines.append(new_line)
                lines_creation_anim.append(m.ShowCreation(new_line))

    network_group = m.VGroup(network, *lines)
    ann_text = m.Text("Artificial Neural Network", font_size=24, font="Century")
    ann_text.next_to(network_group, m.UP, buff=0.5)
    network_with_text = m.VGroup(network_group, ann_text)
    text_anim = m.Write(ann_text)
    lines_anim_group = m.AnimationGroup(*lines_creation_anim, lag_ratio=0)
    circles_creation_anim = m.AnimationGroup(
        *[m.ShowCreation(circle) for circle in network], lag_ratio=0.2
    )
    s.wait_for_button()
    s.play(circles_creation_anim, text_anim, run_time=1.5)
    s.play(lines_anim_group, run_time=1)
    highlight = m.SurroundingRectangle(network_with_text, color=m.YELLOW)
    s.play(m.ShowPassingFlash(highlight), run_time=1.5, rate_func=m.smooth)
    return network_with_text
