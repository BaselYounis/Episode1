from __future__ import annotations
from pdb import run
from typing import TYPE_CHECKING
from venv import create

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


class Set:
    def __init__(self, elements: list[str], set_name: str):
        self.oval = self.create_oval()
        self.elements = self.create_elements(elements)
        self.set_name = self.create_set_name(set_name)
        self.mobject = m.VGroup(self.oval, self.elements, self.set_name)

    def create_oval(self) -> m.Ellipse:
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

    def create_elements(self, elements: list[str]) -> m.VGroup:
        elements = m.VGroup(
            *[m.Text(text, font_size=30, font="Century") for text in elements]
        )
        elements.arrange(m.DOWN, buff=0.5)
        elements.move_to(self.oval.get_center())
        return elements

    def create_set_name(self, set_name: str) -> m.Text:
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
        new_elements = self.create_elements(new_elements)
        return m.Transform(self.elements, new_elements)


def set_to_set_section(s: MainTheatreScene) -> None:
    set_a = Set(["1", "2", "3"], "A")
    set_b = Set(["4", "5", "6"], "B")
    sets_group = m.VGroup(set_a.mobject, set_b.mobject)
    sets_group.arrange(m.RIGHT, buff=2.0)
    s.play(
        m.AnimationGroup(
            set_a.get_creation_animation(),
            set_b.get_creation_animation(),
            lag_ratio=0.5,
        ),
        run_time=2,
    )
    s.wait_for_button()
    s.play(set_a.transform_elements(["4", "5", "6"]), run_time=1)
    s.wait_for_button()
    s.play(set_a.transform_elements(["7", "8", "9"]), run_time=1)
    s.wait_for_button()
    s.play(set_a.transform_elements(["10", "11", "12"]), run_time=1)
    s.wait_for_button()
    s.play(set_a.transform_elements(["13", "14", "15"]), run_time=1)
