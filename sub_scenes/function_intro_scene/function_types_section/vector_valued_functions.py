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
#          (  3.6 t ,  2.0 t ,  9.8 t - 4.9 t^2  )
#
# The numbers are chosen so the flight reads cleanly: launch at t = 0, land at
# t = 2 s, peak height 4.9 at t = 1 s (symmetric arc), and the ground track
# stays inside the axes.
G = 9.8
T_MAX = 2.0          # flight time, seconds
T_PEAK = T_MAX / 2   # apex, where the component breakdown is shown


def x_of(t):
    return 3.6 * t


def y_of(t):
    return 2.0 * t


def z_of(t):
    return 9.8 * t - 0.5 * G * t**2


FONT = "Century"

# One colour per component so the formula, the axes, and the dashed
# decomposition at the apex all speak the same language.
X_COLOR = m.RED_B      # downrange
Y_COLOR = m.GREEN_B    # cross-range
Z_COLOR = m.BLUE_B     # height
VEC_COLOR = m.YELLOW_B  # the output vector r(t) itself

THETA = -60           # camera azimuth, degrees
PHI = 70              # camera tilt, degrees
RADIUS = 12.0         # camera distance from the axes' centre
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
        r"9.8\,t - 4.9\,t^{2}": Z_COLOR,
    }
    formula = m.Tex(
        r"\mathbf{r}(t) = (\, 3.6\,t \,,\, 2.0\,t \,,\, 9.8\,t - 4.9\,t^{2} \,)",
        isolate=list(parts.keys()),
        font_size=26,
    )
    # Tint each component to match the axes and the apex breakdown.
    for sub, color in parts.items():
        formula.select_parts(sub).set_color(color)
    formula.to_corner(m.UL, buff=0.4).shift(m.DOWN * 1.1)
    formula.fix_in_frame()
    return formula


def build_axes() -> tuple[m.ThreeDAxes, m.VGroup]:
    axes = m.ThreeDAxes(
        x_range=(0, 8, 1),
        y_range=(0, 5, 1),
        z_range=(0, 5, 1),
        width=7.5,
        height=4.7,
        depth=4.0,
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


def vector_valued_functions(s: MainTheatreScene) -> None:
    header = build_header()
    formula = build_formula()
    axes, axis_labels = build_axes()
    t_bar = build_t_bar()

    t_tracker = m.ValueTracker(0.0)

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

    # ---- the tracing vector: origin -> current position ----
    origin = axes.c2p(0, 0, 0)

    def draw_vector():
        p = point_at(axes, t_tracker.get_value())
        if m.get_norm(p - origin) < 0.2:
            return m.VectorizedPoint(origin)  # too short to draw cleanly yet
        arrow = m.Arrow(origin, p, buff=0, thickness=3.5)
        arrow.set_color(VEC_COLOR)
        return arrow

    vector = m.always_redraw(draw_vector)

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

    # Wire up everything that is driven by t, then sweep t from 0 to T_MAX.
    # The path draws, the vector traces, the ball flies, and the slider and
    # readout advance — all locked to the same clock.
    drawn_path.add_updater(grow_path)
    r_tag.add_updater(place_tag)
    attach_t_updaters(t_bar, t_tracker)
    s.add(drawn_path, vector, ball, r_tag)

    s.play(
        t_tracker.animate.set_value(T_MAX),
        run_time=5.0,
        rate_func=m.linear,
    )

    # Freeze the finished path so it survives when we scrub t back to the apex.
    drawn_path.clear_updaters()

    s.wait_for_button()

    # ---- rewind to the apex and break the output vector into components ----
    r_tag.clear_updaters()
    s.play(m.FadeOut(r_tag), run_time=0.3)
    s.play(t_tracker.animate.set_value(T_PEAK), run_time=1.2)

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

    s.wait_for_button()

    # ---- tear down ----
    frame.remove_updater(rotate)
    ball.clear_updaters()
    t_bar["pointer"].clear_updaters()
    t_bar["value"].clear_updaters()
    vector.clear_updaters()

    everything = m.Group(
        header, formula, axes, axis_labels, t_bar["group"],
        drawn_path, vector, ball, *breakdown.values(),
    )
    s.play(m.FadeOut(everything), run_time=0.6)
    frame.to_default_state()
