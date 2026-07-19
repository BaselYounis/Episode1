from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

from helpers import mixed_tex_parser
import manimlib as m

# Each colorscale is a list of (color, z-value) stops, ordered by z.
examples = [
    {
        "name": "Temperature",
        "description": "Heat spreading across a metal plate",
        "formula": r"$T(x, y) = 2.5\,e^{-(x^2 + y^2)/3}$",
        "legend": r"$x, y$ : position on the plate $\quad$ $T$ : temperature",
        "func": lambda x, y: 2.5 * np.exp(-(x**2 + y**2) / 3),
        "z_range": (0, 3, 1),
        "colorscale": [(m.BLUE_D, 0.0), (m.YELLOW, 1.2), (m.RED, 2.4)],
    },
    {
        "name": "Terrain",
        "description": "A mountain landscape — every point on the map has an altitude",
        "formula": r"$h(x, y) = 2.2\,e^{-((x-1.5)^2 + (y-1)^2)/2}"
        r" + 1.6\,e^{-((x+1.5)^2 + (y+1.5)^2)/1.5}$",
        "legend": r"$x, y$ : map coordinates $\quad$ $h$ : altitude",
        "func": lambda x, y: (
            2.2 * np.exp(-((x - 1.5) ** 2 + (y - 1) ** 2) / 2)
            + 1.6 * np.exp(-((x + 1.5) ** 2 + (y + 1.5) ** 2) / 1.5)
        ),
        "z_range": (0, 3, 1),
        "colorscale": [
            (m.GREEN_E, 0.05),
            (m.GREEN_C, 0.8),
            (m.LIGHT_BROWN, 1.5),
            (m.WHITE, 2.2),
        ],
    },
    {
        # Real seas are a superposition of waves: a dominant swell, a weaker
        # crossing swell, and small ripples — each with its own direction.
        "name": "Ocean waves",
        "description": "The sea is a sum of waves — swell, a crossing sea, and ripples",
        "formula": r"$H(x, y) = 0.5\sin(x + 0.6y)"
        r" + 0.25\sin(0.6x - 1.1y + 2) + 0.12\sin(2.2x + 1.6y)$",
        "legend": r"$x, y$ : position at sea $\quad$ $H$ : wave height",
        "func": lambda x, y: (
            0.50 * np.sin(1.0 * x + 0.6 * y)
            + 0.25 * np.sin(0.6 * x - 1.1 * y + 2)
            + 0.12 * np.sin(2.2 * x + 1.6 * y)
        ),
        "z_range": (-1.5, 1.5, 0.5),
        "colorscale": [
            (m.BLUE_E, -0.85),
            (m.BLUE_D, -0.2),
            (m.BLUE_B, 0.4),
            (m.WHITE, 0.9),
        ],
        "xy_range": 4.0,
    },
]

THETA = -50  # camera azimuth, degrees
PHI = 68  # camera tilt, degrees
ROTATION_RATE = 0.15  # radians per second of ambient rotation


def multi_variable_type(s: MainTheatreScene) -> None:
    font = "Century"
    title = m.Text("Multivariable Functions Examples", font=font, font_size=32)
    subtitle = mixed_tex_parser.convert_tex_to_vgroup(
        r"one rule $z = f(x, y)$ — many meanings", font=font, font_size=24
    )
    subtitle.set_color(m.GREY_B)
    header = m.VGroup(title, subtitle).arrange(m.DOWN, buff=0.2)
    header.to_edge(m.UP, buff=0.2)
    header.fix_in_frame()

    s.play(m.FadeIn(header, shift=m.DOWN * 0.3))

    for i, example in enumerate(examples):
        show_example(s, font, example, header)
        if i < len(examples) - 1:
            s.wait_for_button()

    s.wait_for_button()
    s.play(m.FadeOut(header), run_time=0.5)


def show_example(
    s: MainTheatreScene, font: str, example: dict, header: m.VGroup
) -> None:
    xy_range = example.get("xy_range", 3.5)
    resolution = example.get("resolution", 42)

    # Captions are pinned to the screen so they always face the viewer.
    name = m.Text(example["name"], font=font, font_size=28, color=m.YELLOW_B)
    description = m.Text(example["description"], font=font, font_size=20, color=m.GREY_A)
    formula = mixed_tex_parser.convert_tex_to_vgroup(
        example["formula"], font=font, font_size=20
    )
    formula.set_color(m.BLUE_B)
    caption = m.VGroup(name, description, formula).arrange(
        m.DOWN, aligned_edge=m.LEFT, buff=0.15
    )

    legend = mixed_tex_parser.convert_tex_to_vgroup(
        example["legend"], font=font, font_size=20
    )
    legend.set_color(m.GREY_B)
    legend.to_edge(m.DOWN, buff=0.3)

    for part in (caption, legend):
        if part.get_width() > 12:
            part.set_width(12)
        part.fix_in_frame()

    # Tuck the caption under the section header so the two never overlap.
    caption.to_edge(m.LEFT, buff=0.3)
    caption.next_to(header, m.DOWN, buff=0.35, coor_mask=m.UP)

    axes = m.ThreeDAxes(
        x_range=(-xy_range, xy_range, 1),
        y_range=(-xy_range, xy_range, 1),
        z_range=example["z_range"],
        width=7.0,
        height=7.0,
        depth=3.6,
    )
    surface = m.ParametricSurface(
        lambda u, v: axes.c2p(u, v, example["func"](u, v)),
        u_range=(-xy_range, xy_range),
        v_range=(-xy_range, xy_range),
        resolution=(resolution, resolution),
    )
    color_surface_by_height(surface, axes, example["colorscale"])
    mesh = m.SurfaceMesh(surface, resolution=(21, 21))
    mesh.set_stroke(m.WHITE, width=0.5, opacity=0.3)

    frame = s.camera.frame
    frame.reorient(THETA, PHI)

    s.play(m.FadeIn(caption, shift=m.DOWN * 0.2))
    s.play(m.ShowCreation(axes), run_time=1.0)
    s.play(m.ShowCreation(surface), run_time=1.8)
    s.play(m.FadeIn(mesh), m.FadeIn(legend), run_time=0.6)

    def rotate(mob, dt):
        mob.increment_theta(ROTATION_RATE * dt)

    frame.add_updater(rotate)
    s.wait_for_button()
    frame.remove_updater(rotate)

    s.play(
        m.FadeOut(m.Group(axes, surface, mesh)),
        m.FadeOut(caption),
        m.FadeOut(legend),
        run_time=0.6,
    )
    frame.to_default_state()


def color_surface_by_height(
    surface: m.Surface,
    axes: m.ThreeDAxes,
    colorscale: list[tuple[str, float]],
) -> None:
    """Tint every point of the surface by the graph value it sits at."""
    stops = sorted(colorscale, key=lambda stop: stop[1])
    values = np.array([value for _, value in stops])
    rgbs = np.array([m.color_to_rgb(color) for color, _ in stops])

    def rgb_at(point: np.ndarray) -> np.ndarray:
        z = axes.z_axis.p2n(point)
        return np.array([np.interp(z, values, rgbs[:, channel]) for channel in range(3)])

    surface.set_color_by_rgb_func(rgb_at, opacity=0.95)
