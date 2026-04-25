from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


class Set:
    def __init__(self, elements: list[str], set_name: str):
        self.oval = self.create_oval_mobject()
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
    fs = 28
    narrative_text = m.Text("Formal definition of a function", font=font, font_size=36)
    narrative_text.to_edge(m.UP, buff=0.2)
    formal_def_of_function = (
        m.VGroup(
            m.Text("A function", font=font, font_size=fs),
            m.Tex(r"\mathrm{f}", font_size=fs + 4).set_color(m.YELLOW),
            m.Text("from a set", font=font, font_size=fs),
            m.Tex(r"\mathrm{X}", font_size=fs + 4).set_color(m.BLUE),
            m.Text("to a set", font=font, font_size=fs),
            m.Tex(r"\mathrm{Y}", font_size=fs + 4).set_color(m.RED),
            m.Text("assigns to each element of", font=font, font_size=fs),
            m.Tex(r"\mathrm{X}", font_size=fs + 4).set_color(m.BLUE),
            m.Text("exactly one element of", font=font, font_size=fs),
            m.Tex(r"\mathrm{Y}", font_size=fs + 4).set_color(m.RED),
        )
        .arrange(m.RIGHT, buff=0.15)
        .next_to(narrative_text, m.DOWN, buff=0.5)
        .to_edge(m.LEFT, buff=0.05)
    )
    denoted_as = (
        m.VGroup(
            m.Text("We denote this by writing", font=font, font_size=fs),
            m.VGroup(
                m.Tex(r"\mathrm{f}", font_size=fs + 4).set_color(m.YELLOW),
                m.Tex(r":", font_size=fs + 4),
                m.Tex(r"\mathrm{X}", font_size=fs + 4).set_color(m.BLUE),
                m.Tex(r"\to", font_size=fs + 4),
                m.Tex(r"\mathrm{Y}", font_size=fs + 4).set_color(m.RED),
            ).arrange(m.RIGHT, buff=0.15),
        )
        .arrange(m.RIGHT, buff=0.15)
        .next_to(formal_def_of_function, m.DOWN, buff=0.15)
        .to_edge(m.LEFT, buff=0.05)
    )
    and_we_write = (
        m.VGroup(
            m.Text("and we write", font=font, font_size=fs),
            m.Tex(r"f(x)=y", font_size=fs + 4).set_color_by_tex_to_color_map(
                {"f": m.YELLOW, "x": m.BLUE, "y": m.RED}
            ),
        )
        .arrange(m.RIGHT, buff=0.15)
        .next_to(denoted_as, m.DOWN, buff=0.15)
        .to_edge(m.LEFT, buff=0.05)
    )
    some_random_text = m.Tex("x^2","\  and \ +","1", font_size=fs + 4).set_color_by_tex_to_color_map(
        {"x": m.BLUE}
    ).next_to(and_we_write, m.DOWN, buff=0.15).to_edge(m.LEFT, buff=0.05)
    some_random_text[0].scale(2)
    line = m.Line(m.LEFT_SIDE, m.RIGHT_SIDE)
    line.next_to(narrative_text, m.DOWN, buff=0.1)
    s.play(m.FadeIn(narrative_text), m.FadeIn(line), lag_ratio=0.1)
    s.play(m.Write(formal_def_of_function))
    s.play(m.Write(denoted_as))
    s.play(m.Write(and_we_write))
    s.play(m.Write(some_random_text))
