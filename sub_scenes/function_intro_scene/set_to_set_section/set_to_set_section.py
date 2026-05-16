from __future__ import annotations
from typing import TYPE_CHECKING


from helpers import mixed_tex_parser
from sub_scenes.function_intro_scene.scene_helpers import Set 
from sub_scenes.function_intro_scene.set_to_set_section.invalid_function_sub_section import (
    invalid_function_sub_section,
)
from sub_scenes.function_intro_scene.set_to_set_section.valid_function_sub_section import (
    valid_function_sub_section,
)

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


# a function from a set X to a set Y assigns to each element of X exactly one element of Y The set X is called the domain of the function and the set Y is called the codomain of the function
def set_to_set_section(s: MainTheatreScene) -> None:
    font = "Century"
    narrative_text = m.Text("Formal definition of a function", font=font, font_size=36)
    narrative_text.to_edge(m.UP, buff=0.2)
    function_def = mixed_tex_parser.convert_tex_to_vgroup(
        text=r"""
        A function $f$ from a set $X$ to set $Y$ assigns exactly one element of $Y$ to each element of $X$\nd
        We denote a function $f$ from $X$ to $Y$ as $f: X \to Y$\nd
        and we write $f(x) = y$ if $y$ is the unique element of $Y$ that is assigned to element $x \in X$
        """,
    )
    mixed_tex_parser.map_tex_to_color(
        function_def, {"f": m.PINK, "X": m.BLUE, "x": m.BLUE, "y": m.RED, "Y": m.RED}  # type: ignore
    )
    line = m.Line(m.LEFT_SIDE, m.RIGHT_SIDE)
    line.next_to(narrative_text, m.DOWN, buff=0.2)
    function_def.next_to(line, m.DOWN, buff=0.5)
    function_def.to_edge(m.LEFT, buff=0.1)
    x_set = Set(["a", "b", "c"], "X")
    x_set.oval.set_color(m.BLUE)
    x_set.set_name.set_color(m.BLUE)
    y_set = Set(["1", "2", "3"], "Y", is_left_set=False)
    y_set.oval.set_color(m.RED)
    y_set.set_name.set_color(m.RED)
    set_group = m.VGroup(x_set.mobject, y_set.mobject)
    set_group.arrange(m.RIGHT, buff=2.5)
    set_group.next_to(function_def, m.DOWN, buff=0.6)
    set_group.shift(m.RIGHT * 1.25)  # pyright: ignore[reportOperatorIssue]
    s.play(m.Write(narrative_text), m.FadeIn(line), m.Write(function_def))
    s.play(x_set.get_creation_animation(), y_set.get_creation_animation())
    valid_function_sub_section(s, x_set, y_set)
    invalid_function_sub_section(s, x_set, y_set)
    