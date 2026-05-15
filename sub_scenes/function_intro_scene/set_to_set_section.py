from __future__ import annotations
from typing import TYPE_CHECKING


from helpers import mixed_tex_parser
from sub_scenes.function_intro_scene.scene_helpers import Set, make_arrow

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
    arrow_a_to_1 = make_arrow(
        x_set.elements[0], y_set.elements[0], upward=True
    )  # a → 1
    arrow_a_to_2 = make_arrow(
        x_set.elements[0], y_set.elements[1], upward=False
    )  # a → 2
    arrow_b_to_2 = make_arrow(
        x_set.elements[1], y_set.elements[1], upward=True
    )  # b → 2

    arrow_c_to_2 = make_arrow(
        x_set.elements[2], y_set.elements[1], upward=False
    )  # c → 2
    arrow_c_to_3 = make_arrow(
        x_set.elements[2], y_set.elements[2], upward=False
    )  # c → 3
    valid_function_text = mixed_tex_parser.convert_tex_to_vgroup(
        r"""valid function $\checkmark$"""
    )
    invalid_function_text = mixed_tex_parser.convert_tex_to_vgroup(
        r"""invalid function $\times$"""
    )
    mixed_tex_parser.map_tex_to_color(invalid_function_text, {r"\times": m.RED})  # type: ignore
    mixed_tex_parser.map_tex_to_color(valid_function_text, {r"\checkmark": m.GREEN})  # type: ignore
    sets_center = (x_set.mobject.get_center() + y_set.mobject.get_center()) / 2
    valid_function_text.next_to(sets_center, m.UP, buff=2)
    invalid_function_text.next_to(sets_center, m.UP, buff=2)

    s.play(
        m.ShowCreation(arrow_a_to_1),
        m.ShowCreation(arrow_b_to_2),
        m.ShowCreation(arrow_c_to_2),
    )
    s.play(m.FadeIn(valid_function_text, shift=m.UP * 0.5))
    s.wait_for_button()
    s.play(
        m.FadeOut(valid_function_text, shift=m.UP * 0.5),
        m.FadeOut(arrow_a_to_1),
        m.FadeOut(arrow_b_to_2),
        m.FadeOut(arrow_c_to_2),
    )
    s.play(
        m.ShowCreation(arrow_a_to_2),
        m.ShowCreation(arrow_a_to_1),
        m.ShowCreation(arrow_b_to_2),
        m.ShowCreation(arrow_c_to_3),
    )
    s.play(m.FadeIn(invalid_function_text, shift=m.UP * 0.5))
    s.wait_for_button()
