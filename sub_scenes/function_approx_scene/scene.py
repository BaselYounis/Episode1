from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m

from .ball_thrown_section.ball_thrown_section import ball_thrown_section

def function_approx_scene(s: MainTheatreScene) -> None:
    what_is_a_function_text = m.Text(
            "How to find the function?", font_size=36, font="Century"
        )
    s.play(m.Write(what_is_a_function_text), run_time=1)
    s.wait_for_button()
    s.play(m.FadeOut(what_is_a_function_text), run_time=0.5)
    ball_thrown_section(s)