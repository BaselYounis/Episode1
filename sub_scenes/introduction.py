from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import random
import manimlib as manim
from helper_animated_objects.backgrounds import bg
import numpy as np




def introduction_scene(manim_scene: MainTheatreScene) -> None:
    manim_scene.add(bg)
    random.seed(42)
    n_dots = 30
    positions = [
        np.array([random.uniform(-7, 7), random.uniform(-4, 4), 0])
        for _ in range(n_dots)
    ]

    dots = manim.VGroup()
    for pos in positions:
        dot = manim.Dot(pos, radius=0.04, color=manim.BLUE_E)
        dot.set_opacity(0.4)
        dots.add(dot)

    lines = manim.VGroup()
    for i in range(n_dots):
        for j in range(i + 1, n_dots):
            if np.linalg.norm(positions[i] - positions[j]) < 2.5:
                line = manim.Line(
                    positions[i],
                    positions[j],
                    stroke_width=0.5,
                    stroke_color=manim.BLUE_E,
                )
                line.set_opacity(0.2)
                lines.add(line)

    network = manim.VGroup(lines, dots)

    manim_scene.play(manim.FadeIn(network, run_time=2))
    manim_scene.wait_for_button("This is a network of 30 random points. ")

    manim_scene.play(manim.FadeOut(network, run_time=2))
