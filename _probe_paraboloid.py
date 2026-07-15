import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy
import manimlib as m
from sub_scenes.function_intro_scene.scene_helpers import SceneOverlayBox
from sub_scenes.function_intro_scene.scene_globals import f_color
from helper_animated_objects.general_objects import main_background


def build(theta_deg, phi_deg):
    formula = m.Tex(r"f(x, y) = x^2 + y^2", font_size=24)
    formula.set_color(m.BLUE)
    formula.to_corner(m.UL)

    axes = m.ThreeDAxes(
        x_range=[-2, 2, 1],
        y_range=[-2, 2, 1],
        z_range=[0, 4, 1],
    )
    surface = axes.get_parametric_surface(
        lambda r, theta: [r * numpy.cos(theta), r * numpy.sin(theta), r**2],
        u_range=(0, 2),
        v_range=(0, m.TAU),
        color=f_color,
    )
    group = m.Group(axes, surface)
    group.rotate(phi_deg * m.DEGREES, axis=m.RIGHT)
    group.rotate(theta_deg * m.DEGREES, axis=m.OUT)
    scene_mobjects = m.Group(formula, group)
    overlay_box = SceneOverlayBox()
    overlay_box.put_mobject_inside(scene_mobjects)
    return overlay_box, formula, group


class Probe(m.Scene):
    def construct(self):
        self.add(main_background)
        box, formula, group = build(-110, -70)
        self.add(box.mobject, formula, group)
        self.wait(0.1)
