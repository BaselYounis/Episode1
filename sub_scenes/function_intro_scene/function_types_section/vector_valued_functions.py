from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

from helpers import mixed_tex_parser
import manimlib as m

# A vector-valued function r(t) takes a single scalar t (time) and returns a
# vector (a point in space). The projectile makes this concrete: at every
# instant the ball is somewhere, and stringing those positions together in
# order traces its flight path through 3D space.
#
#   r(t) = ( x(t), y(t), z(t) )
#          (  3.6 t ,  2.0 t ,  5.0 t - 2.5 t^2  )
#
# The numbers are chosen so the flight reads cleanly: launch at t = 0, land at
# t = 2 s, peak height 2.5 at t = 1 s (symmetric arc), and the ground track
# stays inside the axes. The height scale is deliberately modest so the whole
# z axis fits in the tilted camera view alongside the header and the t slider.
G = 5.0
V0 = 5.0
T_MAX = 2.0          # flight time, seconds
T_PEAK = T_MAX / 2   # apex, where the component breakdown is shown


def x_of(t):
    return 3.6 * t


def y_of(t):
    return 2.0 * t


def z_of(t):
    return V0 * t - 0.5 * G * t**2


FONT = "Century"

# One colour per component so the formula, the axes, and the dashed
# decomposition at the apex all speak the same language.
X_COLOR = m.RED_B      # downrange
Y_COLOR = m.GREEN_B    # cross-range
Z_COLOR = m.BLUE_B     # height
VEC_COLOR = m.YELLOW_B  # the output vector r(t) itself

# Base -> tip order of the gradient painted on r(t), matching the order the
# dashed staircase walks the components: x, then y, then z.
COMPONENT_COLORS = (X_COLOR, Y_COLOR, Z_COLOR)

# Shaft diameter of the 3D r(t) arrow, in scene units. Kept slim on purpose:
# the arrow has to sit on top of the flight path without swallowing it.
VEC_THICKNESS = 0.04

THETA = -20           # camera azimuth, degrees
PHI = 70              # camera tilt, degrees
RADIUS = 16.0         # camera distance from the axes' centre
ROTATION_RATE = 0.12  # radians per second of ambient rotation


def point_at(axes: m.ThreeDAxes, t: float) -> np.ndarray:
    """The projectile's position in scene coordinates at time t."""
    return axes.c2p(x_of(t), y_of(t), z_of(t))


def build_header() -> m.VGroup:
    title = m.Text("Vector-Valued Functions", font=FONT, font_size=32)
    subtitle = mixed_tex_parser.convert_tex_to_vgroup(
        r"a scalar $t \in \mathbb{R}$ maps to a vector "
        r"$\mathbf{r}(t) \in \mathbb{R}^3$",
        font=FONT, font_size=20,
    )
    subtitle.set_color(m.GREY_A)
    header = m.VGroup(title, subtitle).arrange(m.DOWN, buff=0.14)
    header.to_edge(m.UP, buff=0.2)
    header.fix_in_frame()
    return header


def build_formula() -> m.Tex:
    """The vector formula, pinned to the frame, one colour per component."""
    parts = {
        r"\mathbf{r}(t)": VEC_COLOR,
        r"3.6\,t": X_COLOR,
        r"2.0\,t": Y_COLOR,
        r"5.0\,t - 2.5\,t^{2}": Z_COLOR,
    }
    formula = m.Tex(
        r"\mathbf{r}(t) = (\, 3.6\,t \,,\, 2.0\,t \,,\, 5.0\,t - 2.5\,t^{2} \,)",
        isolate=list(parts.keys()),
        font_size=26,
    )
    # Tint each component to match the axes and the apex breakdown.
    for sub, color in parts.items():
        formula.select_parts(sub).set_color(color)
    formula.to_corner(m.UL, buff=0.4).shift(m.DOWN * 1.1)
    formula.shift(m.UP * 0.5)  # nudge right so the left edge doesn't collide with the frame
    formula.fix_in_frame()
    return formula


def build_axes() -> tuple[m.ThreeDAxes, m.VGroup]:
    axes = m.ThreeDAxes(
        x_range=(0, 8, 1),
        y_range=(0, 5, 1),
        z_range=(0, 3, 1),
        width=7.5,
        height=4.7,
        depth=2.8,
    )
    x_label = axes.get_x_axis_label("x", buff=0.4).set_color(X_COLOR)
    y_label = axes.get_y_axis_label("y", buff=0.4).set_color(Y_COLOR)
    # Stand the z-label upright so it stays legible as the camera orbits.
    z_label = m.Tex("z").set_color(Z_COLOR)
    z_label.rotate(90 * m.DEGREES, axis=m.RIGHT)
    z_label.next_to(axes.z_axis.get_end(), m.OUT, buff=0.2)
    labels = m.VGroup(x_label, y_label, z_label)
    return axes, labels


def build_t_bar() -> dict:
    """The scalar input, shown as a slider: a number line for t with a moving
    pointer and a live readout. Everything here is pinned to the frame so it
    reads as an on-screen control, not part of the 3D world."""
    line = m.NumberLine(
        x_range=(0, 2, 0.5),
        width=6.0,
        include_numbers=True,
        include_tip=False,
        decimal_number_config=dict(num_decimal_places=1, font_size=20),
    )
    line.to_edge(m.DOWN, buff=0.7)

    caption = m.Text("input parameter  t  (seconds)", font=FONT, font_size=20)
    caption.set_color(m.GREY_A)
    caption.next_to(line, m.DOWN, buff=0.22)

    # A downward triangle riding above the line marks the current t.
    pointer = m.Triangle().set_height(0.18)
    pointer.rotate(m.PI)  # point downward, at the line
    pointer.set_fill(VEC_COLOR, opacity=1.0).set_stroke(width=0)

    # Live readout: "t = 0.00 s".
    readout_label = m.Tex("t =", font_size=28)
    value = m.DecimalNumber(0.0, num_decimal_places=2, font_size=28)
    value.set_color(VEC_COLOR)
    unit = m.Text("s", font=FONT, font_size=24)
    readout = m.VGroup(readout_label, value, unit).arrange(m.RIGHT, buff=0.12)
    readout.next_to(line, m.UP, buff=0.35)

    group = m.VGroup(line, caption, pointer, readout)
    group.fix_in_frame()
    return dict(line=line, caption=caption, pointer=pointer,
                readout=readout, value=value, group=group)


def attach_t_updaters(t_bar: dict, t_tracker: m.ValueTracker) -> None:
    line, pointer, value = t_bar["line"], t_bar["pointer"], t_bar["value"]

    def move_pointer(mob):
        t = t_tracker.get_value()
        mob.move_to(line.n2p(t)).shift(m.UP * (mob.get_height() / 2 + 0.05))

    pointer.add_updater(move_pointer)
    value.add_updater(lambda d: d.set_value(t_tracker.get_value()))
    move_pointer(pointer)


def staircase_legs(axes: m.ThreeDAxes, t: float) -> list[float]:
    """Scene-space lengths of the three legs origin -> x -> y -> z at time t —
    the same walk the dashed breakdown draws."""
    x0, y0, z0 = x_of(t), y_of(t), z_of(t)
    o = axes.c2p(0, 0, 0)
    px = axes.c2p(x0, 0, 0)
    pxy = axes.c2p(x0, y0, 0)
    pxyz = axes.c2p(x0, y0, z0)
    return [m.get_norm(px - o), m.get_norm(pxy - px), m.get_norm(pxyz - pxy)]


def axis_gradient_rgba_func(
    start: np.ndarray,
    end: np.ndarray,
    colors,
    weights=None,
    opacity: float = 1.0,
):
    """An rgba function that paints a mobject along the start -> end direction,
    blending through `colors`. Each colour owns a share of the length given by
    `weights` (equal shares if omitted) and sits at the middle of its share, so
    every component gets a solid band with the blends happening in between.
    """
    axis = end - start
    axis_sq = float(np.dot(axis, axis))
    rgbs = np.array([m.color_to_rgb(c) for c in colors])

    w = np.ones(len(rgbs)) if weights is None else np.array(weights, dtype=float)
    w = w / w.sum() if w.sum() > 0 else np.ones(len(rgbs)) / len(rgbs)
    edges = np.concatenate([[0.0], np.cumsum(w)])
    centers = (edges[:-1] + edges[1:]) / 2

    def rgba(point: np.ndarray) -> np.ndarray:
        # How far along the arrow this vertex lies, 0 at the base, 1 at the tip.
        s = np.clip(float(np.dot(point - start, axis) / axis_sq), 0.0, 1.0)
        # np.interp clamps at the ends, so the first and last colours stay pure
        # beyond their centres instead of fading out.
        rgb = [np.interp(s, centers, rgbs[:, i]) for i in range(3)]
        return np.array([*rgb, opacity])

    return rgba


def build_vector_3d(
    start: np.ndarray,
    end: np.ndarray,
    thickness: float = VEC_THICKNESS,
    color=VEC_COLOR,
    gradient=None,
    weights=None,
) -> m.Group:
    """A genuine 3D arrow: a cylindrical shaft capped with a cone. Unlike a flat
    stroke arrow it keeps its solidity as the camera orbits, so r(t) reads as an
    object living in the same space as the trajectory.

    `thickness` is the shaft diameter; the head scales with it so the arrow stays
    proportioned at any weight.

    Pass `gradient` (a sequence of colours, optionally weighted by `weights`) to
    paint the arrow base-to-tip instead of filling it with a single `color`.
    """
    direction = end - start
    length = m.get_norm(direction)
    unit = direction / length

    # Cap the head so it never eats more than a third of a short vector.
    head_length = min(7 * thickness, 0.3 * length)
    neck = end - unit * head_length

    shaft = m.Line3D(start, neck, width=thickness)
    head = m.Cone(radius=2.5 * thickness, height=head_length, axis=unit)
    head.move_to(neck + unit * head_length / 2)

    arrow = m.Group(shaft, head)
    if gradient is None:
        arrow.set_color(color)
    else:
        rgba_func = axis_gradient_rgba_func(start, end, gradient, weights)
        for part in arrow:
            part.set_color_by_rgba_func(rgba_func)
    return arrow


def build_apex_breakdown(axes: m.ThreeDAxes) -> dict:
    """At the apex, take the output vector apart into its three components: a
    dashed staircase origin -> x -> y -> z that lands exactly on the ball,
    showing that the vector *is* those three numbers."""
    x0, y0, z0 = x_of(T_PEAK), y_of(T_PEAK), z_of(T_PEAK)

    o = axes.c2p(0, 0, 0)
    px = axes.c2p(x0, 0, 0)
    pxy = axes.c2p(x0, y0, 0)
    pxyz = axes.c2p(x0, y0, z0)

    def seg(a, b, color):
        line = m.DashedLine(a, b, dash_length=0.12)
        line.set_stroke(color, width=4, opacity=0.95)
        return line

    x_seg = seg(o, px, X_COLOR)
    y_seg = seg(px, pxy, Y_COLOR)
    z_seg = seg(pxy, pxyz, Z_COLOR)

    def comp_label(tex, color, point, direction):
        lab = m.Tex(tex, font_size=26).set_color(color)
        lab.rotate(90 * m.DEGREES, axis=m.RIGHT)  # stand upright toward camera
        lab.next_to(point, direction, buff=0.12)
        return lab

    x_lab = comp_label("x(t)", X_COLOR, (o + px) / 2, m.DOWN)
    y_lab = comp_label("y(t)", Y_COLOR, (px + pxy) / 2, m.RIGHT)
    z_lab = comp_label("z(t)", Z_COLOR, (pxy + pxyz) / 2, m.OUT)

    return dict(
        x_seg=x_seg, y_seg=y_seg, z_seg=z_seg,
        x_lab=x_lab, y_lab=y_lab, z_lab=z_lab,
    )


def build_apex_value_label(axes: m.ThreeDAxes) -> m.Tex:
    """The concrete output at the apex, floating above the ball: the same tuple
    the formula promises, now filled in with numbers. Each component wears its
    axis colour, so the label, the dashed staircase and the formula all point at
    the same three quantities."""
    x0, y0, z0 = x_of(T_PEAK), y_of(T_PEAK), z_of(T_PEAK)
    xs, ys, zs = f"{x0:.1f}", f"{y0:.1f}", f"{z0:.1f}"

    label = m.Tex(
        rf"\mathbf{{r}}({T_PEAK:.1f}) = (\, {xs} \,,\, {ys} \,,\, {zs} \,)",
        isolate=[r"\mathbf{r}", xs, ys, zs],
        font_size=28,
    )
    label.select_parts(r"\mathbf{r}").set_color(VEC_COLOR)
    for sub, color in ((xs, X_COLOR), (ys, Y_COLOR), (zs, Z_COLOR)):
        label.select_parts(sub).set_color(color)

    # Stand it upright toward the camera, like the component labels, and park it
    # just above the ball.
    label.rotate(90 * m.DEGREES, axis=m.RIGHT)
    label.next_to(axes.c2p(x0, y0, z0), m.OUT, buff=0.3)
    return label


def vector_valued_functions(s: MainTheatreScene) -> None:
    header = build_header()
    formula = build_formula()
    axes, axis_labels = build_axes()
    t_bar = build_t_bar()

    t_tracker = m.ValueTracker(0.0)
    # Bind the slider to t straight away, so the pointer and readout sit at t = 0
    # from the moment the bar fades in rather than snapping into place later.
    attach_t_updaters(t_bar, t_tracker)

    # ---- the growing flight path: a partial of the full trajectory ----
    full_path = m.ParametricCurve(
        lambda t: point_at(axes, t),
        t_range=(0, T_MAX, T_MAX / 200),
    )
    full_path.set_stroke(m.GREY_B, width=3)

    # A copy of the full trajectory, so pointwise_become_partial has matching
    # point arrays to slice; it starts collapsed and grows to the full curve.
    drawn_path = full_path.copy()
    drawn_path.set_stroke(VEC_COLOR, width=4)

    def grow_path(mob):
        # Clamp to a tiny positive floor so pointwise_become_partial always has
        # a valid sub-curve to copy (a bare origin point would be invisible).
        alpha = min(max(t_tracker.get_value() / T_MAX, 1e-4), 1.0)
        mob.pointwise_become_partial(full_path, 0, alpha)
        mob.set_stroke(VEC_COLOR, width=4)

    origin = axes.c2p(0, 0, 0)

    # ---- the projectile itself: a small sphere at the drawing head ----
    ball = m.Sphere(radius=0.11)
    ball.set_color(m.YELLOW)
    ball.add_updater(lambda mob: mob.move_to(point_at(axes, t_tracker.get_value())))

    # r(t) tag that rides just past the arrow tip.
    r_tag = m.Tex(r"\mathbf{r}(t)", font_size=30).set_color(VEC_COLOR)
    r_tag.rotate(90 * m.DEGREES, axis=m.RIGHT)

    def place_tag(mob):
        mob.next_to(point_at(axes, t_tracker.get_value()), m.OUT + m.RIGHT, buff=0.1)

    # ================= ANIMATE =================
    s.play(m.FadeIn(header, shift=m.DOWN * 0.3))

    # Settle the camera into its tilted view and start a slow ambient orbit so
    # the arc reads as genuinely three-dimensional.
    frame = s.camera.frame
    frame.reorient(THETA, PHI)
    frame.set_focal_distance(RADIUS)

    def rotate(mob, dt):
        mob.increment_theta(ROTATION_RATE * dt)

    frame.add_updater(rotate)

    s.play(
        m.ShowCreation(axes),
        m.Write(axis_labels),
        m.FadeIn(formula, shift=m.DOWN * 0.2),
        m.FadeIn(t_bar["group"]),
        run_time=1.8,
    )

    s.wait_for_button("Press SPACE to launch ")

    # Wire up the rest of what is driven by t, then sweep t from 0 to T_MAX.
    # The path draws, the vector traces, the ball flies, and the slider and
    # readout advance — all locked to the same clock.
    drawn_path.add_updater(grow_path)
    r_tag.add_updater(place_tag)
    s.add(drawn_path, ball, r_tag)

    s.play(
        t_tracker.animate.set_value(T_MAX),
        run_time=5.0,
        rate_func=m.linear,
    )

    # Freeze the finished path so it survives when we scrub t back to the apex.
    drawn_path.clear_updaters()

    s.wait_for_button()

    # Stop the orbit and swing back to the launch view. The breakdown labels are
    # built upright for this exact orientation, so they only read cleanly once
    # the camera is home again.
    frame.remove_updater(rotate)
    s.play(frame.animate.reorient(THETA, PHI), run_time=1.0)

    # ---- rewind to the apex and break the output vector into components ----
    r_tag.clear_updaters()
    s.play(m.FadeOut(r_tag), run_time=0.3)
    s.play(t_tracker.animate.set_value(T_PEAK), run_time=1.2)

    # Only now does the output vector itself appear, drawn from the origin out to
    # the apex. Holding it back until the flight is over keeps the trace clean and
    # makes r(t) land as the thing we are about to take apart.
    # It wears a gradient through the three component colours, each holding the
    # share of the arrow that its leg of the staircase contributes — so before a
    # single dashed line is drawn, the arrow already looks like x plus y plus z.
    vector = build_vector_3d(
        origin, point_at(axes, T_PEAK),
        gradient=COMPONENT_COLORS,
        weights=staircase_legs(axes, T_PEAK),
    )
    s.play(m.ShowCreation(vector), run_time=1.0)

    breakdown = build_apex_breakdown(axes)
    s.play(
        m.ShowCreation(breakdown["x_seg"]), m.Write(breakdown["x_lab"]),
        run_time=0.7,
    )
    s.play(
        m.ShowCreation(breakdown["y_seg"]), m.Write(breakdown["y_lab"]),
        run_time=0.7,
    )
    s.play(
        m.ShowCreation(breakdown["z_seg"]), m.Write(breakdown["z_lab"]),
        run_time=0.7,
    )

    # With all three components named, collect them back into a single value.
    value_label = build_apex_value_label(axes)
    s.play(m.Write(value_label), run_time=0.9)

    s.wait_for_button()

    # ---- tear down ----
    ball.clear_updaters()
    t_bar["pointer"].clear_updaters()
    t_bar["value"].clear_updaters()

    everything = m.Group(
        header, formula, axes, axis_labels, t_bar["group"],
        drawn_path, vector, ball, value_label, *breakdown.values(),
    )
    s.play(m.FadeOut(everything), run_time=0.6)
    frame.to_default_state()
