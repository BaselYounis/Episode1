"""The bridge to the second way of finding a function.

The derivation only reached p = 1/2 g t^2 + v_0 t + p_0 because it was handed
the physics to start from. Strip that away and all that is left of the ball is
what you can measure — a handful of heights, each one off by a little. This
section takes the very graph the derivation just drew, moves it to centre
stage, scatters those measurements over it, and then dims the curve away, so
the closing image is the one function approximation actually starts from: dots,
and no curve.

It sets the question up; it does not answer it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from helpers import mixed_tex_parser

from ..ball_thrown_section.ball_thrown_section import (
    BALL_COLOR,
    FONT,
    height_at,
)

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

import manimlib as m

# ---- staging ----
# The graph arrives from the right-hand panel and takes the whole stage. 1.4x
# leaves a clear band above the axes for the running commentary.
SCALE_UP = 1.4
STAGE_CENTER = np.array([0.0, -0.7, 0.0])
PROSE_Y = 3.05
PROSE_FONT_SIZE = 26

# ---- the measurements ----
# Sampled inside T_LAND = 2.53, over a stretch where the true curve never drops
# below 1.6 m — so three sigma of error still cannot push a dot through the
# t-axis. np.clip below is a guard in case these are ever retuned.
N_POINTS = 13
T_MIN, T_MAX = 0.12, 2.40
SIGMA_P = 0.45  # metres of measurement error
P_FLOOR, P_CEILING = 0.2, 8.6

# Drawn once, at import, from a fixed seed: the scatter has to be identical on
# every render or the scene changes between takes. This particular seed gives a
# spread with no dot escaping the plot box and a clearly visible — but not
# freakish — error on the point singled out at BELL_INDEX.
SEED = 8
T_VALUES = np.linspace(T_MIN, T_MAX, N_POINTS)
P_TRUE = height_at(T_VALUES)
P_NOISY = np.clip(
    P_TRUE + np.random.default_rng(SEED).normal(0.0, SIGMA_P, N_POINTS),
    P_FLOOR,
    P_CEILING,
)

DOT_RADIUS = 0.06
GHOST_OPACITY = 0.15

# The one measurement whose error gets drawn out. On the way down, clear of both
# the apex and the axis, so a full bell fits either side of it.
BELL_INDEX = 9
BELL_WIDTH = 0.35  # peak height of the bell, in seconds along the t-axis
ANNOTATION_COLOR = m.GREY_A


# =============================== builders ===============================


def build_measurements(axes: m.Axes) -> dict:
    """The scatter, in two positions: on the curve, and knocked off it.

    Must be called *after* the axes have been moved and scaled. Axes.c2p works
    off x_axis.number_to_point, which reads the axis's live points, so it
    reports wherever the axes currently are — meaning the dots can simply be
    placed at their final coordinates with no transform bookkeeping.

    Individual Dots rather than Axes.get_scatterplot: that returns a DotCloud,
    and these have to be animated off the curve one at a time.
    """
    dots = m.VGroup()
    for t, p in zip(T_VALUES, P_TRUE):
        dot = m.Dot(axes.c2p(t, p), radius=DOT_RADIUS)
        dot.set_color(BALL_COLOR)
        dot.set_stroke(m.BLACK, width=1)  # keeps neighbours from merging
        dots.add(dot)

    noisy_points = [axes.c2p(t, p) for t, p in zip(T_VALUES, P_NOISY)]

    return dict(dots=dots, noisy_points=noisy_points)


def build_error_bell(axes: m.Axes) -> dict:
    """A bell lying on its side at one measurement, so "Gaussian" is shown
    rather than asserted, plus the segment between where the ball actually was
    and where we recorded it."""
    t0 = T_VALUES[BELL_INDEX]
    p0 = P_TRUE[BELL_INDEX]

    def bell_point(p: float) -> np.ndarray:
        offset = BELL_WIDTH * np.exp(-((p - p0) ** 2) / (2 * SIGMA_P**2))
        return axes.c2p(t0 + offset, p)

    bell = m.ParametricCurve(
        bell_point,
        t_range=(p0 - 3.2 * SIGMA_P, p0 + 3.2 * SIGMA_P, 0.05),
    )
    bell.set_stroke(ANNOTATION_COLOR, width=2)
    # An open curve fills as if closed, and the closing chord here runs straight
    # down the t = t0 line — exactly the baseline a bell should sit on. Without
    # the fill the outline reads as a bracket rather than a distribution.
    bell.set_fill(ANNOTATION_COLOR, opacity=0.12)

    # Where the ball actually was, as opposed to what we wrote down.
    true_marker = m.Circle(radius=0.07)
    true_marker.move_to(axes.c2p(t0, p0))
    true_marker.set_stroke(ANNOTATION_COLOR, width=2)
    true_marker.set_fill(opacity=0)

    error_bar = m.DashedLine(
        axes.c2p(t0, p0),
        axes.c2p(t0, P_NOISY[BELL_INDEX]),
        dash_length=0.05,
    )
    error_bar.set_stroke(ANNOTATION_COLOR, width=3)

    sigma_label = m.Tex(r"\sigma", font_size=26).set_color(ANNOTATION_COLOR)
    sigma_label.next_to(bell, m.RIGHT, buff=0.12)

    return dict(
        bell=bell,
        true_marker=true_marker,
        error_bar=error_bar,
        sigma_label=sigma_label,
        group=m.VGroup(bell, true_marker, error_bar, sigma_label),
    )


def build_prose(text: str) -> m.VGroup:
    """A line of commentary in the band above the axes."""
    prose = mixed_tex_parser.convert_tex_to_vgroup(
        text, font=FONT, font_size=PROSE_FONT_SIZE
    )
    prose.move_to(np.array([0.0, PROSE_Y, 0.0]))
    return prose


# =============================== the section ===============================


def data_points_section(s: MainTheatreScene, graph_panel: dict) -> None:
    axes = graph_panel["axes"]
    curve_group = graph_panel["curve_group"]

    # ---------------- 1. take the stage ----------------
    # Transform onto a scaled copy rather than chaining .animate calls, so the
    # move and the scale resolve as one interpolation. curve_group's children
    # are transformed in place, so `axes` and `graph` stay the same objects —
    # and axes.c2p reports the new geometry straight afterwards.
    stage_target = curve_group.copy()
    stage_target.scale(SCALE_UP)
    stage_target.move_to(STAGE_CENTER)
    s.play(m.Transform(curve_group, stage_target), run_time=1.2)
    s.wait_for_button()

    # ---------------- 2. the catch ----------------
    prose = build_prose(
        "that only worked because we already knew the physics"
        r"\nd"
        "usually, all we can do is measure"
    )
    s.play(m.FadeIn(prose, shift=m.UP * 0.25), run_time=0.9)
    s.wait_for_button()

    # ---------------- 3. the measurements, taken perfectly ----------------
    measurements = build_measurements(axes)
    dots = measurements["dots"]

    prose_measure = build_prose(
        r"at each instant $t$, we record the ball's height $p$"
    )
    s.play(m.FadeTransform(prose, prose_measure), run_time=0.8)
    s.play(
        m.LaggedStartMap(m.FadeIn, dots, scale=0.4, lag_ratio=0.06, run_time=1.4)
    )
    s.wait_for_button()

    # ---------------- 4. ...except no measurement is perfect ----------------
    # The cascade off the curve is the error. Each dot carries its own draw from
    # a normal distribution, so the scatter widens without any of it being
    # arranged by hand.
    prose_error = build_prose("but every measurement carries error")
    s.play(m.FadeTransform(prose_measure, prose_error), run_time=0.8)
    s.play(
        m.AnimationGroup(
            *(
                dot.animate.move_to(point)
                for dot, point in zip(dots, measurements["noisy_points"])
            ),
            lag_ratio=0.04,
        ),
        run_time=1.3,
    )
    s.wait_for_button()

    # Name the distribution on one of them, while the true curve is still there
    # to measure the error against.
    bell = build_error_bell(axes)
    s.play(
        m.ShowCreation(bell["true_marker"]),
        m.ShowCreation(bell["error_bar"]),
        run_time=0.8,
    )
    s.play(
        m.ShowCreation(bell["bell"]),
        m.FadeIn(bell["sigma_label"]),
        run_time=1.1,
    )
    s.wait_for_button()

    # ---------------- 5. take the curve away ----------------
    # The whole point: the parabola was never on offer. Dimming it rather than
    # cutting it leaves a ghost, so it is legible that the dots are still
    # gathered around something — we just do not have it.
    prose_gone = build_prose("and the curve was never given to us — only the dots")
    s.play(
        m.FadeOut(bell["group"]),
        m.FadeTransform(prose_error, prose_gone),
        graph_panel["graph"].animate.set_stroke(opacity=GHOST_OPACITY),
        run_time=1.4,
    )
    s.wait_for_button()

    # ---------------- 6. name the second way ----------------
    heading = m.Text(
        "2 — Approximating the function from data",
        font=FONT,
        font_size=30,
    )
    heading.move_to(np.array([0.0, PROSE_Y, 0.0]))
    s.play(m.FadeTransform(prose_gone, heading), run_time=1.0)
    s.wait_for_button()

    # ---------------- tear down ----------------
    s.play(
        m.FadeOut(m.VGroup(heading, dots, curve_group)),
        run_time=0.6,
    )
