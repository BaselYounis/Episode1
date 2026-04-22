from __future__ import annotations
from typing import TYPE_CHECKING

from .set_to_set_section import set_to_set_section

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


def function_intro_scene(s: MainTheatreScene) -> None:
    what_is_a_function_text = m.Text(
        "But what is a function?", font_size=36, font="Century"
    )
    s.play(m.Write(what_is_a_function_text), run_time=1)
    s.wait_for_button()
    s.play(m.FadeOut(what_is_a_function_text))
    set_to_set_section(s)