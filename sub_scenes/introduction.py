from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import random
import manimlib as manim
import numpy as np





def introduction_scene(manim_scene: MainTheatreScene) -> None:
    title = manim.Text("The Mathematics of the Universe", font_size=48, color=manim.WHITE)
    title.to_edge(manim.UP)
    manim_scene.play(manim.Write(title))
    manim_scene.wait_for_button()
