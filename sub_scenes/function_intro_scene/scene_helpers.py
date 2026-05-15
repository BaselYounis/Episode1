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
        new_elements = m.VGroup(
            *[m.Text(text, font_size=30, font="Century") for text in elements]
        )
        dots = m.VGroup(*[m.Dot(radius=0.02) for _ in new_elements])
        for element, dot in zip(new_elements, dots):
            direction = m.RIGHT if self.is_left_set else m.LEFT
            dot.next_to(element, direction, buff=0.1)
        new_elements = m.VGroup(
            *[m.VGroup(dot, element) for dot, element in zip(dots, new_elements)]
        )
        new_elements.arrange(m.DOWN, buff=0.5)
        new_elements.move_to(self.oval.get_center())
        return new_elements

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
        elements_mobjects = self.create_elements_mobject(new_elements)
        return m.AnimationGroup(m.Transform(self.elements, elements_mobjects))


def make_arrow(
    from_elem, to_elem, buff: float = 0, stroke_width: float = 2.0, upward: bool = False
) -> m.CurvedArrow:
    angle_magnitude = m.PI / 4
    arc_angle = -angle_magnitude if upward else angle_magnitude
    arrow = m.CurvedArrow(
        from_elem[0].get_center(), to_elem[0].get_center(), angle=arc_angle
    )
    # Set the visual thickness of the arrow
    arrow.set_stroke(width=stroke_width)
    arrow.tip.scale(0.5)  # Adjust the size of the arrow tip
    return arrow
