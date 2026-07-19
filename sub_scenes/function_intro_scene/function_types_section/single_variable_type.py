from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

from helpers import mixed_tex_parser
import manimlib as m

examples = [
    {
        "name": "Car velocity",
        "formula": r"$v(t) = 60\,t\,e^{-0.5t}$",
        "func": lambda t: 60 * t * np.exp(-0.5 * t),
        "color": m.BLUE_B,
    },
    {
        "name": "Population (÷10)",
        "formula": r"$P(t) = \frac{1000}{1 + 9e^{-0.8t}}$",
        "func": lambda t: 100 / (1 + 9 * np.exp(-0.8 * t)),
        "color": m.GREEN_B,
    },
    {
        "name": "Battery charge",
        "formula": r"$C(t) = 100\,e^{-0.25t}$",
        "func": lambda t: 100 * np.exp(-0.25 * t),
        "color": m.YELLOW_B,
    },
    {
        "name": "Stock price",
        "formula": r"$S(t) = 50 + 3t + 6\sin(2t) + 3\sin(5t)$",
        "func": lambda t: 50 + 3 * t + 6 * np.sin(2 * t) + 3 * np.sin(5 * t),
        "color": m.RED_B,
    },
]


def single_variable_type(s: MainTheatreScene) -> None:
    font = "Century"
    title = m.Text("Single Variable Functions Examples", font=font, font_size=32)
    title.to_edge(m.UP, buff=0.2)

    axes = m.Axes(
        x_range=[0, 10, 1],
        y_range=[0, 110, 20],
        width=8,
        height=4.6,
        axis_config=dict(
            include_tip=True,
            tip_config=dict(width=0.12, length=0.12),
        ),
    )
    axes.shift(m.DOWN * 0.8 + m.LEFT * 1.4)

    x_label = m.Text("t (time)", font=font, font_size=22)
    x_label.next_to(axes.x_axis, m.DR, buff=0.1)
    y_label = m.Text("f(t)", font=font, font_size=22)
    y_label.next_to(axes.y_axis, m.UL, buff=0.1)

    s.play(m.FadeIn(title, shift=m.DOWN * 0.3))
    s.play(m.ShowCreation(axes), m.FadeIn(x_label), m.FadeIn(y_label), run_time=1.5)

    graphs = m.VGroup()
    legend = m.VGroup()
    for example in examples:
        graph = axes.get_graph(example["func"], color=example["color"])
        graphs.add(graph)

        swatch = m.Line(m.ORIGIN, m.RIGHT * 0.45, color=example["color"])
        swatch.set_stroke(width=6)
        name = m.Text(example["name"], font=font, font_size=20, color=example["color"])
        formula = mixed_tex_parser.convert_tex_to_vgroup(
            example["formula"], font=font, font_size=16
        )
        formula.set_color(m.GREY_B)
        entry = m.VGroup(
            m.VGroup(swatch, name).arrange(m.RIGHT, buff=0.15),
            formula,
        ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.12)
        legend.add(entry)

    legend.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.4)
    legend.to_edge(m.RIGHT, buff=0.25)
    legend.shift(m.DOWN * 0.5)

    # Draw each curve alongside its legend entry, one by one.
    for i, (graph, entry) in enumerate(zip(graphs, legend)):
        s.play(
            m.ShowCreation(graph),
            m.FadeIn(entry, shift=m.LEFT * 0.3),
            run_time=1.5,
        )

        if i < len(graphs) - 1:
            s.wait_for_button()

    s.wait_for_button()

    scene_mobjects = [title, axes, x_label, y_label, graphs, legend]
    s.play(
        m.FadeOut(m.VGroup(*scene_mobjects)),
        run_time=0.5,
    )
