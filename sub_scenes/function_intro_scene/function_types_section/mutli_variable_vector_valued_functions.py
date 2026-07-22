from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

from helpers import mixed_tex_parser
import manimlib as m

# A multivariable vector-valued function takes a *vector* in and hands a
# *vector* back. Fluid flow is the cleanest picture of this: feed it a point
# (x, y) in the plane and it returns the velocity (u, v) of the fluid there.
#
#   F(x, y) = ( u(x, y) , v(x, y) )
#           = ( sin x cos y , -cos x sin y )
#
# This particular field is the Taylor-Green vortex, an exact solution of the
# incompressible Navier-Stokes equations. It is divergence-free (du/dx + dv/dy
# = 0), so it reads as a genuine, mass-conserving fluid: a tidy lattice of
# counter-rotating swirls. The wavenumber K just sets how many swirls land in
# the frame.
K = 0.6


def flow_field(coords: np.ndarray) -> np.ndarray:
    """The velocity (u, v) of the fluid at each input point (x, y).

    Written to swallow whatever the field/stream-line machinery hands it: a
    single (2,) point during ODE integration, or a batched (N, 2) array of
    sample points for the arrow grid. The trailing axis always holds (x, y),
    so the same indexing covers both.
    """
    coords = np.asarray(coords, dtype=float)
    x, y = coords[..., 0], coords[..., 1]
    u = np.sin(K * x) * np.cos(K * y)
    v = -np.cos(K * x) * np.sin(K * y)
    return np.stack([u, v], axis=-1)


FONT = "Century"

IN_COLOR = m.TEAL_B  # the input vector: a position (x, y)
OUT_COLOR = m.YELLOW_B  # the output vector: the velocity F(x, y)
U_COLOR = m.RED_B  # first output component
V_COLOR = m.BLUE_B  # second output component

# The plane is sized so its coordinate ranges fill most of the frame at one
# screen-unit per coordinate-unit (13.0 x 7.2), leaving room for the header.
X_RANGE = (-6.5, 6.5, 1)
Y_RANGE = (-3.6, 3.6, 1)

# How densely the plane is sampled. Turn these up for more arrows / more flow
# lines (denser but busier and slower to build), down for a sparser picture.
FIELD_DENSITY = 2.6  # arrows per coordinate-unit in the vector grid
FLOW_DENSITY = 2.2  # seed density for the animated stream lines

# One point to probe. The position points up-and-right while the velocity there
# points down-and-right, so the picture makes plain that the output vector is
# nothing like the input vector.
PROBE = (1.3, 1.3)
VEL_SCALE = 2.0  # lengthen the lone velocity arrow so its direction reads


def build_header() -> m.VGroup:
    title = m.Text("Vector Fields", font=FONT, font_size=32)
    subtitle = mixed_tex_parser.convert_tex_to_vgroup(
        r"a vector $(x, y) \in \mathbb{R}^2$ maps to a vector "
        r"$\mathbf{F}(x, y) \in \mathbb{R}^2$",
        font=FONT,
        font_size=20,
    )
    subtitle.set_color(m.GREY_A)
    header = m.VGroup(title, subtitle).arrange(m.DOWN, buff=0.14)
    header.to_edge(m.UP, buff=0.2)
    header.fix_in_frame()
    return header


def build_formula() -> m.Tex:
    """The flow's formula, pinned to a corner, one colour per output component."""
    parts = {
        r"\mathbf{F}(x, y)": OUT_COLOR,
        r"\sin x \cos y": U_COLOR,
        r"-\cos x \sin y": V_COLOR,
    }
    formula = m.Tex(
        r"\mathbf{F}(x, y) = (\, \sin x \cos y \,,\, -\cos x \sin y \,)",
        isolate=list(parts.keys()),
        font_size=26,
    )
    for sub, color in parts.items():
        formula.select_parts(sub).set_color(color)
    formula.to_corner(m.UL, buff=0.35).shift(m.DOWN * 1.05)
    formula.add_background_rectangle(opacity=0.6, buff=0.12)
    formula.fix_in_frame()
    return formula


def build_probe(plane: m.NumberPlane) -> dict:
    """Pick one input point and trace it to its output vector.

    A faint arrow from the origin is the input vector (a position); a bold
    arrow rooted at that point is the output vector (the velocity the fluid
    has there). Returns the pieces plus enough structure to reveal them in
    order: point in, vector out.
    """
    x0, y0 = PROBE
    u0, v0 = flow_field(np.array([x0, y0]))

    origin = plane.get_origin()
    base = plane.c2p(x0, y0)
    # The velocity in screen coordinates, then stretched for legibility.
    vel = (plane.c2p(x0 + u0, y0 + v0) - base) * VEL_SCALE
    tip = base + vel

    input_arrow = m.Arrow(origin, base, buff=0, thickness=3)
    input_arrow.set_color(IN_COLOR)
    input_arrow.set_opacity(0.85)
    input_dot = m.Dot(base, radius=0.06).set_color(IN_COLOR)
    input_dot.set_stroke(m.WHITE, width=1)

    input_label = m.Tex("(x, y)", font_size=30).set_color(IN_COLOR)
    input_label.next_to(base, m.UR, buff=0.1)

    output_arrow = m.Arrow(base, tip, buff=0, thickness=4)
    output_arrow.set_color(OUT_COLOR)
    output_label = m.Tex(r"\mathbf{F}(x, y)", font_size=30).set_color(OUT_COLOR)
    output_label.next_to(tip, m.DR, buff=0.1)

    return dict(
        input_arrow=input_arrow,
        input_dot=input_dot,
        input_label=input_label,
        output_arrow=output_arrow,
        output_label=output_label,
    )


# Built once, at import time, before the presentation window opens. The stream
# lines integrate an ODE from every seed point, which is the one genuinely slow
# step here; doing it now keeps the scene from stalling when it is reached.
PLANE = m.NumberPlane(
    x_range=X_RANGE,
    y_range=Y_RANGE,
    background_line_style=dict(
        stroke_color=m.BLUE_E, stroke_width=1, stroke_opacity=0.35
    ),
    faded_line_ratio=1,
)

FIELD = m.VectorField(
    flow_field,
    PLANE,
    density=FIELD_DENSITY,
    magnitude_range=(0, 1.0),
    stroke_width=3,
)

STREAM_LINES = m.StreamLines(
    flow_field,
    PLANE,
    density=FLOW_DENSITY,
    stroke_width=2.0,
    color_by_magnitude=False,
    stroke_color=m.BLUE_B,
    stroke_opacity=0.9,
)
FLOW = m.AnimatedStreamLines(STREAM_LINES)


def vector_fields(s: MainTheatreScene) -> None:
    header = build_header()
    formula = build_formula()
    probe = build_probe(PLANE)

    # ================= ANIMATE =================
    s.play(m.FadeIn(header, shift=m.DOWN * 0.3))
    s.play(
        m.ShowCreation(PLANE, lag_ratio=0.0),
        m.FadeIn(formula, shift=m.DOWN * 0.2),
        run_time=1.5,
    )

    s.wait_for_button("Press SPACE to reveal the field ")

    # The whole field at once: at every point (x, y) in the plane sits an
    # output vector, coloured by how fast the fluid moves there. Every arrow is
    # *created together*, each growing from its own base point to full length
    # (rather than fading in as a block). The field is one mesh of many arrows,
    # so a plain ShowCreation would sweep across them in order; instead we drive
    # a single grow factor that collapses every vector back onto its base at 0
    # and lets them all extend simultaneously as it climbs to 1.
    grow = m.ValueTracker(0.0)

    def grow_vectors(mob):
        mob.update_vectors()
        points = mob.get_points()
        bases = np.repeat(mob.sample_points, 8, axis=0)[: len(points)]
        points[:] = bases + grow.get_value() * (points - bases)
        mob.note_changed_data()

    FIELD.add_updater(grow_vectors)
    s.add(FIELD)
    s.play(grow.animate.set_value(1.0), run_time=1.5)
    FIELD.remove_updater(grow_vectors)
    FIELD.update_vectors()

    s.wait_for_button("Press SPACE to probe a point ")

    # One input point in, one output vector out.
    s.play(
        m.GrowArrow(probe["input_arrow"]),
        m.FadeIn(probe["input_dot"]),
        m.Write(probe["input_label"]),
        run_time=0.9,
    )
    s.play(
        m.GrowArrow(probe["output_arrow"]),
        m.Write(probe["output_label"]),
        run_time=0.9,
    )

    s.wait_for_button("Press SPACE to release the flow ")

    # Turn the static arrows into moving fluid: dim the field, clear the probe,
    # and let stream lines drift along it so the swirls read as real flow.
    probe_group = m.VGroup(*probe.values())
    s.play(
        m.FadeOut(probe_group),
        FIELD.animate.set_stroke(opacity=0.25),
        run_time=0.8,
    )
    s.add(FLOW)

    s.wait_for_button()

    # ---- tear down ----
    FLOW.clear_updaters()
    s.remove(FLOW)
    everything = m.Group(header, formula, PLANE, FIELD)
    s.play(m.FadeOut(everything), run_time=0.6)
