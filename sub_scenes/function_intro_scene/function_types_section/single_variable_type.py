from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

from helpers import mixed_tex_parser
import manimlib as m

# Shared with the multivariable scene so the "input -> output" probe reads
# the same across both: teal marks the input scalar, yellow the output scalar.
INPUT_COLOR = m.TEAL_B
OUTPUT_COLOR = m.YELLOW_B

examples = [
    {
        "name": "Car velocity",
        "label": r"$v(t)$",
        "formula": r"$v(t) = 60\,t\,e^{-0.5t}$",
        "func": lambda t: 60 * t * np.exp(-0.5 * t),
        "color": m.BLUE_B,
        # One input value to probe, tracing t -> f(t) on the first curve.
        "probe": 3.0,
    },
    {
        "name": "Population (÷10)",
        "label": r"$P(t)$",
        "formula": r"$P(t) = \frac{1000}{1 + 9e^{-0.8t}}$",
        "func": lambda t: 100 / (1 + 9 * np.exp(-0.8 * t)),
        "color": m.GREEN_B,
    },
    {
        "name": "Battery charge",
        "label": r"$C(t)$",
        "formula": r"$C(t) = 100\,e^{-0.25t}$",
        "func": lambda t: 100 * np.exp(-0.25 * t),
        "color": m.YELLOW_B,
    },
    {
        "name": "Stock price",
        "label": r"$S(t)$",
        "formula": r"$S(t) = 50 + 3t + 6\sin(2t) + 3\sin(5t)$",
        "func": lambda t: 50 + 3 * t + 6 * np.sin(2 * t) + 3 * np.sin(5 * t),
        "color": m.RED_B,
    },
]


def build_probe(axes: m.Axes, func, t0: float) -> dict:
    """Build the mobjects that pick one input scalar and trace it to its output.

    A dot on the x-axis marks the input scalar t0; a dashed riser climbs to
    the curve, and a dashed crossbar carries that height back to a dot on the
    y-axis — the output scalar f(t0). The whole path reads left-to-right,
    bottom-to-top: number in, climb, across, number out.
    """
    y0 = float(func(t0))
    base = axes.c2p(t0, 0)      # input scalar, on the x-axis
    top = axes.c2p(t0, y0)      # the point it lands on, on the curve
    out = axes.c2p(0, y0)       # output scalar, on the y-axis

    input_dot = m.Dot(base, radius=0.06).set_color(INPUT_COLOR)
    input_label = m.Tex("t_0", font_size=30).set_color(INPUT_COLOR)
    input_label.next_to(base, m.DOWN, buff=0.15)

    riser = m.DashedLine(base, top, dash_length=0.1)
    riser.set_stroke(INPUT_COLOR, width=2, opacity=0.9)

    graph_dot = m.Dot(top, radius=0.06).set_color(m.WHITE)

    crossbar = m.DashedLine(top, out, dash_length=0.1)
    crossbar.set_stroke(OUTPUT_COLOR, width=2, opacity=0.9)

    output_dot = m.Dot(out, radius=0.07).set_color(OUTPUT_COLOR)
    output_dot.set_stroke(m.WHITE, width=1)
    output_label = m.Tex("f(t_0)", font_size=30).set_color(OUTPUT_COLOR)
    output_label.next_to(out, m.LEFT, buff=0.15)

    return dict(
        input_dot=input_dot, input_label=input_label, riser=riser,
        graph_dot=graph_dot, crossbar=crossbar,
        output_dot=output_dot, output_label=output_label,
    )


def reveal_probe(s: MainTheatreScene, probe: dict) -> None:
    """Walk the mapping one beat at a time: scalar in, climb, across, scalar out."""
    s.wait_for_button("Press SPACE to probe a point ")
    # The input: one scalar t0 on the x-axis.
    s.play(
        m.FadeIn(probe["input_dot"], scale=0.5),
        m.Write(probe["input_label"]),
        run_time=0.7,
    )
    # Climb straight up to the curve it lands on.
    s.play(m.ShowCreation(probe["riser"]), m.FadeIn(probe["graph_dot"], scale=0.5), run_time=0.8)
    # Carry that height across to the y-axis.
    s.play(m.ShowCreation(probe["crossbar"]), run_time=0.8)
    # The output: one scalar f(t0), the height of the curve there.
    s.play(
        m.FadeIn(probe["output_dot"], scale=0.5),
        m.Write(probe["output_label"]),
        run_time=0.7,
    )


def single_variable_type(s: MainTheatreScene) -> None:
    font = "Century"
    title = m.Text("Single Variable Functions Examples", font=font, font_size=32)
    title.to_edge(m.UP, buff=0.2)

    # State the mapping's arity up front: one scalar in, one scalar out. This
    # mirrors the subtitle the multivariable scene carries for (x, y) -> z.
    subtitle = mixed_tex_parser.convert_tex_to_vgroup(
        r"a scalar $t \in \mathbb{R}$ maps to a single scalar $f(t) \in \mathbb{R}$",
        font=font, font_size=20,
    )
    subtitle.set_color(m.GREY_A)
    subtitle.next_to(title, m.DOWN, buff=0.15)

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

    s.play(m.FadeIn(title, shift=m.DOWN * 0.3), m.FadeIn(subtitle, shift=m.DOWN * 0.3))
    s.play(m.ShowCreation(axes), m.FadeIn(x_label), m.FadeIn(y_label), run_time=1.5)

    def attach_to_tail(label, graph):
        # Ride the drawing head of the curve while ShowCreation truncates it.
        label.add_updater(
            lambda mob: mob.next_to(graph.get_end(), m.UR, buff=0.08)
        )

    graphs = m.VGroup()
    tail_labels = m.VGroup()
    legend = m.VGroup()
    for example in examples:
        graph = axes.get_graph(example["func"], color=example["color"])
        graphs.add(graph)

        tail_label = mixed_tex_parser.convert_tex_to_vgroup(
            example["label"], font=font, font_size=20
        )
        tail_label.set_color(example["color"])
        attach_to_tail(tail_label, graph)
        tail_labels.add(tail_label)

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
    for i, (graph, tail_label, entry) in enumerate(zip(graphs, tail_labels, legend)):
        s.play(
            m.ShowCreation(graph),
            m.FadeIn(tail_label),
            m.FadeIn(entry, shift=m.LEFT * 0.3),
            run_time=1.5,
        )
        # Freeze the label at the curve's end once drawing finishes.
        tail_label.clear_updaters()

        # On the first curve, make the scalar -> scalar mapping explicit before
        # moving on to the rest of the examples.
        if i == 0:
            probe = build_probe(axes, examples[0]["func"], examples[0]["probe"])
            reveal_probe(s, probe)
            s.wait_for_button()
            s.play(m.FadeOut(m.VGroup(*probe.values())), run_time=0.5)

        if i < len(graphs) - 1:
            s.wait_for_button()

    s.wait_for_button()

    scene_mobjects = [title, subtitle, axes, x_label, y_label, graphs, tail_labels, legend]
    s.play(
        m.FadeOut(m.VGroup(*scene_mobjects)),
        run_time=0.5,
    )
