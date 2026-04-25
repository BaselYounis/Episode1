from __future__ import annotations
from typing import TYPE_CHECKING

from helpers import mixed_tex_parser

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


class Set:
    def __init__(
        self, elements: list[str], set_name: str, is_left_set: bool = True
    ) -> None:
        self.oval = self.create_oval_mobject()
        self.is_left_set = is_left_set
        self.elements = self.create_elements_mobject(elements)
        self.set_name = self.create_set_name_mobject(set_name)
        self.mobject = m.VGroup(self.oval, self.elements, self.set_name)

    def create_oval_mobject(self) -> m.Ellipse:
        new_oval = m.Ellipse(
            width=4,
            height=2,
            color=m.BLUE,
            fill_color=m.BLUE,
            fill_opacity=0.5,
            stroke_color=m.BLUE,
        )
        new_oval.rotate(m.PI / 2)
        return new_oval

    def create_elements_mobject(self, elements: list[str]) -> m.VGroup:
        elements = m.VGroup(
            *[m.Text(text, font_size=30, font="Century") for text in elements]
        )
        dots = m.VGroup(*[m.Dot(radius=0.02) for _ in elements])
        for element, dot in zip(elements, dots):
            direction = m.RIGHT if self.is_left_set else m.LEFT
            dot.next_to(element, direction, buff=0.1)
        elements = m.VGroup(
            *[m.VGroup(dot, element) for dot, element in zip(dots, elements)]
        )
        elements.arrange(m.DOWN, buff=0.5)
        elements.move_to(self.oval.get_center())
        return elements

    def create_set_name_mobject(self, set_name: str) -> m.Text:
        set_oval_text = m.Text(set_name, font_size=24, font="Century")
        set_oval_text.next_to(self.oval, m.UP)
        return set_oval_text

    def get_creation_animation(self) -> m.AnimationGroup:
        text_creation_anim = m.AnimationGroup(
            *[m.Write(text) for text in self.elements],
            m.Write(self.set_name),
            lag_ratio=0.5,
        )
        oval_creation_anim = m.FadeIn(self.oval)
        return m.AnimationGroup(oval_creation_anim, text_creation_anim, lag_ratio=0.5)

    def transform_elements(self, new_elements: list[str]) -> m.AnimationGroup:
        new_elements = self.create_elements_mobject(new_elements)
        return m.Transform(self.elements, new_elements)


# a function from a set X to a set Y assigns to each element of X exactly one element of Y The set X is called the domain of the function and the set Y is called the codomain of the function
def set_to_set_section(s: MainTheatreScene) -> None:
    font = "Century"
    narrative_text = m.Text("Formal definition of a function", font=font, font_size=36)
    narrative_text.to_edge(m.UP, buff=0.2)
    function_def = mixed_tex_parser.parse_tex_text(
        text=r"""
        A function $f$ from a set $X$ to set $Y$ assigns exactly one element of $Y$ to each element of $X$\nd
        We denote a function $f$ from $X$ to $Y$ as $f: X \to Y$\nd
        and we write $f(x) = y$ if $y$ is the unique element of $Y$ that is assigned to element $x \in X$
        """,
    )
    mixed_tex_parser.map_tex_to_color(
        function_def, {"f": m.PINK, "X": m.BLUE, "x": m.BLUE, "y": m.RED, "Y": m.RED}
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
    set_group.arrange(m.RIGHT, buff=1.5)
    set_group.next_to(function_def, m.DOWN, buff=0.6)
    set_group.shift(m.RIGHT * 1.25)
    s.play(m.Write(narrative_text), m.FadeIn(line), m.Write(function_def))
    s.play(x_set.get_creation_animation(), y_set.get_creation_animation())
