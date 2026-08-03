"""The bridge to the second way of finding a function.

The derivation only reached p = 1/2 g t^2 + v_0 t + p_0 because it was handed
the physics to start from. Strip that away and all that is left of the ball is
what you can measure — a handful of heights, each one off by a little. This
section takes the very graph the derivation just drew, moves it to centre
stage, scatters those measurements over it, and then dims the curve away, so
what is left is the one thing function approximation actually starts from: dots,
and no curve.

It closes by naming the new goal. The real function is not on the table any
more, so the search is for one that runs close to the dots instead — and when
the true curve is brought back to check, the fit is beside it, not on it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..ball_thrown_section.ball_thrown_section import (
    BALL_COLOR,
    FONT,
    MOTION_COLOR,
    height_at,
)

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

import manimlib as m

# ---- staging ----
# The graph arrives from the right-hand panel and takes the whole stage. 1.4x
# leaves a clear band above the axes for the section heading.
SCALE_UP = 1.4
STAGE_CENTER = np.array([0.0, -0.7, 0.0])
HEADING_Y = 3.05

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
# spread with no dot escaping the plot box and errors that read clearly without
# any of them looking freakish.
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
# The true curve comes back up this far at the end — enough to see the
# approximation lying almost, but not quite, on top of it.
COMPARE_OPACITY = 0.5

# ---- the approximation ----
# The answer the section closes on: not p, but something near it. Fitted to the
# noisy dots, since those are all the search ever gets to see — which is why it
# lands beside the true curve rather than on it (visibly so at the left end,
# where the first measurement came in low).
FIT_COLOR = m.TEAL_B
FIT_COEFFS = np.polyfit(T_VALUES, P_NOISY, 2)

# Two candidates tried before it, so the fit reads as something searched for
# rather than handed over. The line is the least-squares line — wrong shape.
LINE_COEFFS = np.polyfit(T_VALUES, P_NOISY, 1)
# Hand-picked: right shape, too sharp, and it hits the ground well before the
# last measurements do. Drawn only to its own root, so it stays in the box.
STEEP_COEFFS = np.array([-7.5, 16.0, 0.3])
STEEP_T_END = float(max(np.roots(STEEP_COEFFS)))

FIT_T_RANGE = (0.0, 2.53, 0.02)
RESIDUAL_COLOR = m.GREY_B


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


def build_approximation(axes: m.Axes) -> dict:
    """The candidates, the fit, and the gap that is left over.

    Same rule as build_measurements: call it after the axes have been staged.
    """

    def curve(coeffs: np.ndarray, t_range: tuple) -> m.VMobject:
        graph = axes.get_graph(lambda t: float(np.polyval(coeffs, t)), x_range=t_range)
        graph.set_stroke(FIT_COLOR, width=3)
        return graph

    # The one that gets transformed along the search; the other two are only
    # ever Transform targets, so they never enter the scene themselves.
    candidate = curve(LINE_COEFFS, FIT_T_RANGE)
    steep = curve(STEEP_COEFFS, (0.0, STEEP_T_END, 0.02))
    fit = curve(FIT_COEFFS, FIT_T_RANGE)

    # What "close" costs, per measurement: the leftover between the dot and the
    # curve the search settled on.
    residuals = m.VGroup()
    for t, p in zip(T_VALUES, P_NOISY):
        segment = m.Line(axes.c2p(t, p), axes.c2p(t, float(np.polyval(FIT_COEFFS, t))))
        segment.set_stroke(RESIDUAL_COLOR, width=2)
        residuals.add(segment)

    return dict(candidate=candidate, steep=steep, fit=fit, residuals=residuals)


def build_legend(axes: m.Axes) -> m.VGroup:
    """Which curve is which, in the empty corner above the rising branch.

    Nothing but the two symbols: the real function we never get, and the one we
    settle for.
    """
    rows = m.VGroup()
    for color, opacity, tex in (
        (MOTION_COLOR, COMPARE_OPACITY, "p(t)"),
        (FIT_COLOR, 1.0, r"\hat p(t)"),
    ):
        swatch = m.Line(m.LEFT * 0.16, m.RIGHT * 0.16)
        swatch.set_stroke(color, width=3, opacity=opacity)
        label = m.Tex(tex, font_size=24).set_color(color)
        label.set_opacity(opacity)
        rows.add(m.VGroup(swatch, label).arrange(m.RIGHT, buff=0.14))

    rows.arrange(m.DOWN, buff=0.18, aligned_edge=m.LEFT)
    rows.move_to(axes.c2p(0.12, 8.7), aligned_edge=m.UL)
    return rows


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

    # ---------------- 2. the measurements, taken perfectly ----------------
    measurements = build_measurements(axes)
    dots = measurements["dots"]

    s.play(
        m.LaggedStartMap(m.FadeIn, dots, scale=0.4, lag_ratio=0.06, run_time=1.4)
    )
    s.wait_for_button()

    # ---------------- 3. ...except no measurement is perfect ----------------
    # The cascade off the curve is the error. Each dot carries its own draw from
    # a normal distribution, so the scatter widens without any of it being
    # arranged by hand.
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

    # ---------------- 4. take the curve away ----------------
    # The whole point: the parabola was never on offer. Dimming it rather than
    # cutting it leaves a ghost, so it is legible that the dots are still
    # gathered around something — we just do not have it.
    s.play(
        graph_panel["graph"].animate.set_stroke(opacity=GHOST_OPACITY),
        run_time=1.4,
    )
    s.wait_for_button()

    # ---------------- 5. name the second way ----------------
    heading = m.Text(
        "2 — Approximating the function from data",
        font=FONT,
        font_size=30,
    )
    heading.move_to(np.array([0.0, HEADING_Y, 0.0]))
    s.play(m.FadeIn(heading, shift=m.UP * 0.25), run_time=1.0)
    s.wait_for_button()

    # ---------------- 6. what we go looking for instead ----------------
    # Not p — that one is gone with the physics. Something we can build out of
    # the dots and then check against them. The search is shown as a search: two
    # candidates that miss before the one that does not.
    approx = build_approximation(axes)
    candidate = approx["candidate"]
    s.play(m.ShowCreation(candidate), run_time=1.0)
    s.wait_for_button()

    s.play(m.Transform(candidate, approx["steep"]), run_time=0.9)
    s.play(m.Transform(candidate, approx["fit"]), run_time=1.1)
    s.wait_for_button()

    # It threads the dots, but it does not hit them — and it was never asked to.
    # The residuals are what "close" means here, and they are what any of this
    # can actually be measured against.
    s.play(
        m.LaggedStartMap(m.ShowCreation, approx["residuals"], lag_ratio=0.06),
        run_time=1.2,
    )
    s.wait_for_button()

    # Bring the true curve back up to see the whole point: the fit is beside it,
    # not on it — and it got there without ever being shown it.
    legend = build_legend(axes)
    s.play(
        m.FadeOut(approx["residuals"]),
        graph_panel["graph"].animate.set_stroke(opacity=COMPARE_OPACITY),
        m.FadeIn(legend),
        run_time=1.2,
    )
    s.wait_for_button()

    closeness = m.Tex(r"\hat p(t) \approx p(t)", font_size=30)
    closeness.set_color(FIT_COLOR)
    closeness.move_to(axes.c2p(2.45, 8.0))
    s.play(m.Write(closeness), run_time=1.0)
    s.play(m.FlashAround(closeness), run_time=1.0)
    s.wait_for_button()

    # ---------------- tear down ----------------
    s.play(
        m.FadeOut(m.VGroup(heading, dots, curve_group, candidate, legend, closeness)),
        run_time=0.6,
    )
