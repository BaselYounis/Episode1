from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m

from .ball_thrown_section.ball_thrown_section import ball_thrown_section
from .data_points_section.data_points_section import data_points_section

def function_approx_scene(s: MainTheatreScene) -> None:
    what_is_a_function_text = m.Text(
            "How to find the function?", font_size=36, font="Century"
        )
    s.play(m.Write(what_is_a_function_text), run_time=1)
    s.wait_for_button()
    s.play(m.FadeOut(what_is_a_function_text), run_time=0.5)
    # The graph the derivation ends on stays up — the next section keeps working
    # on that same one.
    graph_panel = ball_thrown_section(s)
    data_points_section(s, graph_panel)