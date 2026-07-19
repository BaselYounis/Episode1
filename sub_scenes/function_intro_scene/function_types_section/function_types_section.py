from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m

examples = [
    {
        "name": "Car velocity",
        "formula": "v(t) = 60·t·e^(-0.5t)",
        "func": lambda t: 60 * t * np.exp(-0.5 * t),
        "color": m.BLUE_B,
    },
    {
        "name": "Population (÷10)",
        "formula": "P(t) = 1000/(1+9·e^(-0.8t))",
        "func": lambda t: 100 / (1 + 9 * np.exp(-0.8 * t)),
        "color": m.GREEN_B,
    },
    {
        "name": "Battery charge",
        "formula": "C(t) = 100·e^(-0.25t)",
        "func": lambda t: 100 * np.exp(-0.25 * t),
        "color": m.YELLOW_B,
    },
    {
        "name": "Stock price",
        "formula": "S(t) = 50+3t+6·sin(2t)+3·sin(5t)",
        "func": lambda t: 50 + 3 * t + 6 * np.sin(2 * t) + 3 * np.sin(5 * t),
        "color": m.RED_B,
    },
]


def function_types_section(s: MainTheatreScene) -> None:
    axes = m.Axes(
            x_range=[0, 10, 1],
            y_range=[0, 110, 20],
            width=9,
            height=4.6,
            axis_config=dict(
                include_tip=True,
                tip_config=dict(width=0.12, length=0.12),
            ),
        )
    s.play(m.ShowCreation(axes))

    graphs = [
        axes.get_graph(example["func"], color=example["color"])
        for example in examples
    ]
    creation_animations = [m.ShowCreation(graph) for graph in graphs]
    for i,animation in enumerate(creation_animations):
        s.play(animation, run_time=2)
        if i < len(examples) - 1:
            s.wait_for_button()
        