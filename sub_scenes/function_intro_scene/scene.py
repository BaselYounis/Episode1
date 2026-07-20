from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m

from sub_scenes.function_intro_scene.function_types_section.function_types_section import function_types_section



from .set_to_set_section.set_to_set_section import set_to_set_section



def function_intro_scene(s: MainTheatreScene) -> None:
    what_is_a_function_text = m.Text(
        "But what is a function?", font_size=36, font="Century"
    )
    s.play(m.Write(what_is_a_function_text), run_time=1)
    s.wait_for_button()
    s.play(m.FadeOut(what_is_a_function_text))
    # set_to_set_section(s)
    what_is_a_function_text = m.Text(
        "Functions & Real Life Examples...", font_size=36, font="Century"
    )
    s.play(m.Write(what_is_a_function_text), run_time=1)
    s.wait_for_button()
    s.play(m.FadeOut(what_is_a_function_text))
    function_types_section(s)
