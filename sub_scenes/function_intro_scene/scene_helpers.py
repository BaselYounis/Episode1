import numpy as np
import manimlib as m


class SceneOverlayBox:
    def __init__(self, FRAME_WIDTH: float = 5, FRAME_HEIGHT: float = 5) -> None:
        self.FRAME_WIDTH = FRAME_WIDTH
        self.FRAME_HEIGHT = FRAME_HEIGHT
        self.color = m.BLACK
        self.box = m.Rectangle(
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            color=self.color,
            fill_color=self.color,
            fill_opacity=1,
        )
        self.mobjects_z_index = 10
        self.box.set_z_index(self.mobjects_z_index)
        vertical_displacement_vector = m.UP * (
            m.FRAME_HEIGHT / 2 - self.FRAME_WIDTH / 2
        )
        horizontal_displacement_vector = m.RIGHT * (
            m.FRAME_WIDTH / 2 - self.FRAME_WIDTH / 2
        )
        displacement_vector = (
            vertical_displacement_vector + horizontal_displacement_vector
        )
        self.box.shift(displacement_vector)

        self.box.set_stroke(width=2, color=m.WHITE)
        self.mobject = self.box
        self.origin = np.array([self.box.get_x(), self.box.get_y(), 0])
        self.horizontal_scaling_factor = self.FRAME_WIDTH / m.FRAME_WIDTH
        self.vertical_scaling_factor = self.FRAME_HEIGHT / m.FRAME_HEIGHT
    def put_mobject_inside(self, mobject: m.Mobject) -> None:
        mobject_delta_vector = mobject.get_center() - m.ORIGIN
        mobject_delta_vector_normalized = mobject_delta_vector / m.FRAME_WIDTH
        scaled_delta_vector = mobject_delta_vector_normalized * self.FRAME_WIDTH
        mobject_new_position = self.origin + scaled_delta_vector
        mobject.scale(self.horizontal_scaling_factor)
        mobject.move_to(mobject_new_position)
        self.z_index = self.mobjects_z_index + 1
        mobject.set_z_index(self.z_index)


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
        old_elements = self.elements
        self.elements = elements_mobjects
        return m.AnimationGroup(m.ReplacementTransform(old_elements, self.elements))


def make_arrow(
    from_elem,
    to_elem,
    color=m.YELLOW_A,
    buff: float = 0.1,
    stroke_width: float = 2.0,
    upward: bool = False,
    scaling_factor: float = 1.0,
) -> m.CurvedArrow:
    angle = m.PI / 4
    arc_angle = -angle if upward else angle
    angle_direction_vector = np.array(
        [np.cos(arc_angle / 2), -1 * np.sin(arc_angle / 2), 0]
    )
    start = from_elem[0].get_center() + angle_direction_vector * buff * scaling_factor
    end = to_elem[0].get_center()
    arrow = m.CurvedArrow(start, end, angle=arc_angle)
    # Set the visual thickness of the arrow
    arrow.set_color(color)
    arrow.set_stroke(width=stroke_width * scaling_factor)
    arrow.tip.scale(0.5)  # Adjust the size of the arrow tip
    arrow.tip.shift(angle_direction_vector * buff * np.array([-1, 1, 1]))
    return arrow
