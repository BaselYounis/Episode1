"""The first way to find a function: a chain of assumptions and logical steps
that lands on a closed form.

Worked through the classic example — where is a ball thrown into the air? —
from F = m_B a all the way down to p = 1/2 g t^2 + v_0 t + p_0.

Layout: the derivation stacks in a column on the left and a panel on the right
holds the ball-and-Earth diagram, which gives way at the end to a graph of the
formula being read at one chosen instant.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from helpers import mixed_tex_parser

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

import manimlib as m

FONT = "Century"

# One colour per physical quantity, shared by the equations and the diagram so
# a symbol and the thing it measures always read as the same object.
FORCE_COLOR = m.RED_B  # F
BALL_COLOR = m.YELLOW_B  # m_B, and the ball itself
EARTH_COLOR = m.BLUE_C  # m_E, and the Earth
R_COLOR = m.TEAL_B  # r, and the radius arrow
CONST_COLOR = m.GREEN_B  # G, g, r_c — anything that stops varying
MOTION_COLOR = m.PURPLE_B  # a, v, p
INIT_COLOR = m.MAROON_B  # v_0, p_0

EQ_FONT_SIZE = 30
INTRO_FONT_SIZE = 28

# ---- left column geometry ----
COLUMN_EDGE_BUFF = 0.8
COLUMN_TOP_Y = 2.4
COLUMN_LINE_BUFF = 0.35

# ---- right panel geometry ----
PANEL_X = 3.7
EARTH_R = 1.15
EARTH_CENTER = np.array([PANEL_X, -1.2, 0.0])
BALL_LOW = EARTH_R + 0.25  # distance from Earth's centre at h = 0
BALL_HIGH = EARTH_R + 1.15  # distance from Earth's centre at h = H_MAX

H_MAX = 20.0  # metres — the ball's greatest height
R_EARTH_KM = 6371.0  # the constant that height is dwarfed by

# ---- the payoff graph ----
# One particular throw, fed straight into the formula the derivation lands on.
# g keeps its minus sign — the formula is p = 1/2 g t^2 + ..., so gravity has to
# enter as a downward acceleration. The other two are picked so the readout at
# T_PROBE still lands on an exact figure, which is what makes it legible.
G_NUM = -9.8  # m/s^2, pointing down
V0_NUM = 12.0  # m/s
P0_NUM = 1.0  # m
T_PROBE = 2.0  # the instant we ask the function about
P_PROBE = 5.4  # ...and the height it answers with

GRAPH_CENTER = np.array([PANEL_X + 0.15, -0.35, 0.0])
GRAPH_WIDTH = 4.8
GRAPH_HEIGHT = 3.5


# =============================== builders ===============================


def build_equation(
    tex: str, colors: dict[str, str], font_size: int = EQ_FONT_SIZE
) -> m.Tex:
    """One Tex with every keyed substring isolated, so it can be recoloured and
    transform-matched piece by piece.

    `colors` must be ordered least-specific first: `select_parts("v")` also
    catches the `v` of `v_0`, so `v_0` has to be applied afterwards to win.
    """
    equation = m.Tex(tex, isolate=list(colors.keys()), font_size=font_size)
    for substring, color in colors.items():
        equation.select_parts(substring).set_color(color)
    return equation


def place_first(equation: m.Mobject) -> m.Mobject:
    """Anchor an equation at the top of the left column."""
    equation.to_edge(m.LEFT, buff=COLUMN_EDGE_BUFF)
    equation.set_y(COLUMN_TOP_Y)
    return equation


def place_below(equation: m.Mobject, previous: m.Mobject) -> m.Mobject:
    equation.next_to(previous, m.DOWN, buff=COLUMN_LINE_BUFF, aligned_edge=m.LEFT)
    return equation


def strike_through(part: m.Mobject) -> m.Line:
    """A diagonal slash across a symbol that is about to cancel."""
    line = m.Line(part.get_corner(m.DL), part.get_corner(m.UR))
    line.scale(1.35)
    line.set_stroke(m.RED, width=4)
    return line


def ball_position(height_m: float) -> np.ndarray:
    """Where the ball sits for a given height in metres. The height is wildly
    exaggerated on screen — and that exaggeration is exactly what the r readout
    is about to undercut."""
    alpha = height_m / H_MAX
    distance = BALL_LOW + alpha * (BALL_HIGH - BALL_LOW)
    return EARTH_CENTER + m.UP * distance


def build_diagram(h_tracker: m.ValueTracker) -> dict:
    """The right-hand panel: Earth, ball, the radius r, and the force on the
    ball — everything driven off the ball's height, so r can be *seen* barely
    moving when that height changes."""
    earth = m.Circle(radius=EARTH_R)
    earth.move_to(EARTH_CENTER)
    earth.set_fill(EARTH_COLOR, opacity=0.18)
    earth.set_stroke(EARTH_COLOR, width=2)

    centre_dot = m.Dot(EARTH_CENTER, radius=0.05).set_color(EARTH_COLOR)
    earth_label = m.Tex("m_E", font_size=26).set_color(EARTH_COLOR)
    earth_label.move_to(EARTH_CENTER + m.DOWN * 0.5)

    ball = m.Dot(radius=0.1).set_color(BALL_COLOR)
    ball.add_updater(lambda mob: mob.move_to(ball_position(h_tracker.get_value())))

    ball_label = m.Tex("m_B", font_size=26).set_color(BALL_COLOR)
    ball_label.add_updater(lambda mob: mob.next_to(ball, m.RIGHT, buff=0.18))

    r_arrow = m.Arrow(EARTH_CENTER, ball_position(0), buff=0, thickness=2.5)
    r_arrow.set_color(R_COLOR)
    r_arrow.add_updater(
        lambda mob: mob.put_start_and_end_on(EARTH_CENTER, ball.get_center())
    )

    r_label = m.Tex("r", font_size=28).set_color(R_COLOR)
    r_label.add_updater(lambda mob: mob.next_to(r_arrow, m.LEFT, buff=0.12))

    force_arrow = m.Arrow(
        ball_position(0), ball_position(0) + m.DOWN * 0.6, buff=0, thickness=2.5
    )
    force_arrow.set_color(FORCE_COLOR)
    force_arrow.add_updater(
        lambda mob: mob.put_start_and_end_on(
            ball.get_center(), ball.get_center() + m.DOWN * 0.6
        )
    )

    force_label = m.Tex("F", font_size=26).set_color(FORCE_COLOR)
    force_label.add_updater(lambda mob: mob.next_to(force_arrow, m.RIGHT, buff=0.12))

    # Live readout of r in kilometres — the whole assumption rests on how
    # little these digits move.
    readout_label = m.Tex("r =", font_size=26).set_color(R_COLOR)
    readout_value = m.DecimalNumber(R_EARTH_KM, num_decimal_places=3, font_size=26)
    readout_value.set_color(R_COLOR)
    readout_value.add_updater(
        lambda d: d.set_value(R_EARTH_KM + h_tracker.get_value() / 1000.0)
    )
    readout_unit = m.Text("km", font=FONT, font_size=22).set_color(R_COLOR)
    readout = m.VGroup(readout_label, readout_value, readout_unit)
    readout.arrange(m.RIGHT, buff=0.12)
    readout.move_to(np.array([PANEL_X, 2.05, 0.0]))

    caption = m.Text("(height exaggerated)", font=FONT, font_size=16)
    caption.set_color(m.GREY_B)
    caption.next_to(earth, m.DOWN, buff=0.18)

    # Let the updaters settle before the first frame is drawn.
    for mob in (ball, ball_label, r_arrow, r_label, force_arrow, force_label):
        mob.update()

    return dict(
        earth=earth,
        centre_dot=centre_dot,
        earth_label=earth_label,
        ball=ball,
        ball_label=ball_label,
        r_arrow=r_arrow,
        r_label=r_label,
        force_arrow=force_arrow,
        force_label=force_label,
        readout=readout,
        readout_value=readout_value,
        caption=caption,
        group=m.VGroup(
            earth,
            centre_dot,
            earth_label,
            ball,
            ball_label,
            r_arrow,
            r_label,
            force_arrow,
            force_label,
            readout,
            caption,
        ),
    )


def extend_arrow(arrow: m.Arrow, start: np.ndarray, end: np.ndarray, **kwargs):
    """Animate an arrow growing out of `start` until its tip reaches `end`.

    GrowArrow would scale the finished arrow up from its start point, which
    shrinks the head along with the shaft. Re-laying the points out at every
    frame instead keeps the shaft at full thickness and lets Arrow size the
    head for the current length, so it reads as a vector being drawn outwards
    from the origin rather than a picture of an arrow zooming in.

    suspend_mobject_updating defaults to True: the arrow's own
    put_start_and_end_on updater would otherwise run after each interpolation
    and snap it straight back to full length.
    """

    def lay_out(mob: m.Arrow, alpha: float) -> None:
        # A hair above zero at alpha = 0 — a zero-length arrow has no direction
        # to point in, so the first frame would flicker as a stray dot.
        tip = m.interpolate(start, end, max(alpha, 1e-3))
        mob.set_points_by_ends(start, tip)

    kwargs.setdefault("suspend_mobject_updating", True)
    return m.UpdateFromAlphaFunc(arrow, lay_out, **kwargs)


def height_at(t: float) -> float:
    """The formula the derivation just landed on, with one throw's numbers in."""
    return 0.5 * G_NUM * t * t + V0_NUM * t + P0_NUM


# When the ball comes back down to p = 0 — the far end of the curve.
T_LAND = float((-V0_NUM - np.sqrt(V0_NUM**2 - 2 * G_NUM * P0_NUM)) / G_NUM)


def build_graph_panel() -> dict:
    """The payoff: p(t) plotted, then interrogated at one instant.

    The point is not the parabola — it is that picking a t and reading the
    curve hands back the ball's height without ever throwing the ball.
    """
    axes = m.Axes(
        # Out to 3 s so the last tick clears T_LAND ≈ 2.53 and the curve lands
        # on the axis rather than running out through the arrowhead.
        x_range=[0, 3, 0.5],
        y_range=[0, 9, 2],
        width=GRAPH_WIDTH,
        height=GRAPH_HEIGHT,
        axis_config=dict(
            include_tip=True,
            tip_config=dict(width=0.12, length=0.12),
        ),
    )
    axes.move_to(GRAPH_CENTER)

    # add_numbers parents the digits to the axis, so ShowCreation(axes) would
    # stroke-draw them stroke-by-stroke along with the lines. Lift them back out
    # and fade them in as their own group instead.
    x_numbers = axes.x_axis.add_numbers(
        np.arange(0.5, 3.1, 0.5), num_decimal_places=1, font_size=16
    )
    y_numbers = axes.y_axis.add_numbers(
        np.arange(2, 9, 2), num_decimal_places=0, font_size=16
    )
    axes.x_axis.remove(x_numbers)
    axes.y_axis.remove(y_numbers)
    numbers = m.VGroup(x_numbers, y_numbers)
    numbers.set_color(m.GREY_A)

    x_axis_label = m.Text("t (s)", font=FONT, font_size=20).set_color(m.GREY_A)
    x_axis_label.next_to(axes.x_axis.get_end(), m.DR, buff=0.12)
    y_axis_label = m.Text("p (m)", font=FONT, font_size=20).set_color(MOTION_COLOR)
    y_axis_label.next_to(axes.y_axis.get_end(), m.UL, buff=0.1)

    graph = axes.get_graph(height_at, x_range=(0.0, T_LAND, 0.02))
    graph.set_stroke(MOTION_COLOR, width=3)

    # ---- the probe: one chosen t, read across to one height ----
    base = axes.c2p(T_PROBE, 0)  # the input, on the t-axis
    top = axes.c2p(T_PROBE, P_PROBE)  # where it lands on the curve
    out = axes.c2p(0, P_PROBE)  # the output, on the p-axis

    t_dot = m.Dot(base, radius=0.055).set_color(m.GREY_A)
    t_label = m.Tex(r"t = 2\,\mathrm{s}", font_size=24).set_color(m.GREY_A)
    # Clear of the tick numbers, which already sit just under the axis here.
    t_label.next_to(base, m.DOWN, buff=0.45)

    riser = m.DashedLine(base, top, dash_length=0.1)
    riser.set_stroke(m.GREY_A, width=2, opacity=0.9)

    ball = m.Dot(top, radius=0.09).set_color(BALL_COLOR)
    ball.set_stroke(m.WHITE, width=1)

    crossbar = m.DashedLine(top, out, dash_length=0.1)
    crossbar.set_stroke(MOTION_COLOR, width=2, opacity=0.9)

    p_dot = m.Dot(out, radius=0.06).set_color(MOTION_COLOR)
    p_label = m.Tex(r"p = 5.4\,\mathrm{m}", font_size=24).set_color(MOTION_COLOR)
    # Inside the arc: the curve is well above the crossbar across its middle.
    p_label.next_to(crossbar, m.UP, buff=0.1)

    # Two halves, because they have different lifetimes. The probe answers one
    # question and is done; the axes and the curve outlive this section and are
    # handed on to the one that follows.
    curve_group = m.VGroup(axes, numbers, x_axis_label, y_axis_label, graph)
    probe_group = m.VGroup(t_dot, t_label, riser, ball, crossbar, p_dot, p_label)

    return dict(
        axes=axes,
        numbers=numbers,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        graph=graph,
        t_dot=t_dot,
        t_label=t_label,
        riser=riser,
        ball=ball,
        crossbar=crossbar,
        p_dot=p_dot,
        p_label=p_label,
        curve_group=curve_group,
        probe_group=probe_group,
        group=m.VGroup(curve_group, probe_group),
    )


def matched_pairs(source: m.Tex, target: m.Tex, keys: list) -> list:
    """Explicit source/target pairs for TransformMatchingParts.

    manimgl's TransformMatchingTex assumes one character of the TeX string maps
    to one glyph, which stops being true the moment a `\\frac` shows up (it
    raises an IndexError). Pairing isolated parts up by hand sidesteps that and
    says exactly which symbol becomes which.

    Each key is either a substring present in both equations, or a
    (source_substring, target_substring) tuple.
    """
    pairs = []
    for key in keys:
        source_key, target_key = (key, key) if isinstance(key, str) else key
        source_parts = source.select_parts(source_key)
        target_parts = target.select_parts(target_key)
        if len(source_parts) == 0 or len(target_parts) == 0:
            continue
        pairs.append((source_parts, target_parts))
    return pairs


# =============================== the section ===============================


def ball_thrown_section(s: MainTheatreScene) -> dict:
    """Returns the graph panel, with the axes and curve still on screen — the
    next section keeps interrogating that same graph."""
    # ---------------- 0. the framing ----------------
    two_ways = m.Text(
        "There are two ways to find the function", font=FONT, font_size=36
    )
    s.play(m.Write(two_ways), run_time=1.2)
    s.wait_for_button()

    heading = m.Text(
        "1 — A sequence of assumptions & logical steps to reach a closed form solution",
        font=FONT,
        font_size=30,
    )
    s.play(m.FadeTransform(two_ways, heading), run_time=1.0)
    s.wait_for_button()

    # Shrink it into a section heading so the stage is free.
    heading_target = heading.copy()
    heading_target.scale(26 / 30)
    heading_target.set_color(m.GREY_A)
    heading_target.to_edge(m.UP, buff=0.25)
    s.play(m.Transform(heading, heading_target), run_time=0.9)
    s.wait_for_button()

    intro = mixed_tex_parser.convert_tex_to_vgroup(
        "let's take for example the simple problem of determining"
        r"\nd"
        "the position of a ball thrown in the air",
        font=FONT,
        font_size=INTRO_FONT_SIZE,
    )
    intro.center()
    s.play(m.FadeIn(intro, shift=m.UP * 0.25), run_time=0.8)
    s.wait_for_button()

    # Clear the stage for the derivation.
    s.play(m.FadeOut(intro, shift=m.UP * 0.25), run_time=0.7)

    # ---------------- 1. the diagram ----------------
    h_tracker = m.ValueTracker(H_MAX * 0.65)
    diagram = build_diagram(h_tracker)

    s.play(
        m.ShowCreation(diagram["earth"]),
        m.FadeIn(diagram["centre_dot"]),
        m.FadeIn(diagram["earth_label"]),
        m.FadeIn(diagram["caption"]),
        run_time=0.9,
    )
    s.play(
        m.FadeIn(diagram["ball"], scale=0.5),
        m.FadeIn(diagram["ball_label"]),
        m.ShowCreation(diagram["force_arrow"]),
        m.FadeIn(diagram["force_label"]),
        run_time=0.8,
    )
    s.wait_for_button()

    # ---------------- 2. F = m_B a ----------------
    eq_newton = build_equation(
        r"F = m_B \, a",
        {"F": FORCE_COLOR, "m_B": BALL_COLOR, "a": MOTION_COLOR},
    )
    place_first(eq_newton)

    s.play(m.FadeIn(eq_newton, shift=m.UP * 0.4), run_time=0.9)
    s.wait_for_button()

    # ---------------- 3. a = F / m_B ----------------
    eq_accel = build_equation(
        r"a = \frac{F}{m_B}",
        {"a": MOTION_COLOR, "F": FORCE_COLOR, "m_B": BALL_COLOR},
    )
    place_below(eq_accel, eq_newton)

    s.play(m.FadeIn(eq_accel, shift=m.UP * 0.4), run_time=0.9)
    s.wait_for_button()

    # ---------------- 4. the gravitational force ----------------
    eq_gravity = build_equation(
        r"F = \frac{G \, m_B \, m_E}{r^{2}}",
        {
            "F": FORCE_COLOR,
            "G": CONST_COLOR,
            "m_B": BALL_COLOR,
            "m_E": EARTH_COLOR,
            "r^{2}": R_COLOR,
        },
    )
    place_below(eq_gravity, eq_accel)

    # Reveal r on the diagram at the moment it enters the algebra. The arrow
    # extends out of Earth's centre until its tip reaches the ball, so the
    # reveal reads as the radius being measured rather than a shape appearing.
    #
    # r_label is written with suspend_mobject_updating so it stays put at its
    # final spot instead of being dragged out from Earth's centre by the
    # updater that tracks the growing arrow.
    s.play(
        m.FadeIn(eq_gravity, shift=m.UP * 0.4),
        extend_arrow(
            diagram["r_arrow"], EARTH_CENTER, diagram["ball"].get_center()
        ),
        m.Write(diagram["r_label"], suspend_mobject_updating=True),
        m.FadeIn(diagram["readout"]),
        run_time=1.0,
    )
    s.wait_for_button()

    # ---------------- 5. substitute ----------------
    eq_substituted = build_equation(
        r"a = \frac{G \, m_B \, m_E}{r^{2}} \cdot \frac{1}{m_B}",
        {
            "a": MOTION_COLOR,
            "G": CONST_COLOR,
            "m_B": BALL_COLOR,
            "m_E": EARTH_COLOR,
            "r^{2}": R_COLOR,
        },
    )
    place_below(eq_substituted, eq_gravity)

    s.play(m.FadeIn(eq_substituted, shift=m.UP * 0.4), run_time=0.9)
    s.wait_for_button()

    # ---------------- 6. punchline one: the ball's mass cancels ----------------
    slashes = m.VGroup(
        *(strike_through(part) for part in eq_substituted.select_parts("m_B"))
    )
    s.play(m.ShowCreation(slashes), run_time=0.8)
    s.wait_for_button()

    eq_reduced = build_equation(
        r"a = \frac{G \, m_E}{r^{2}}",
        {
            "a": MOTION_COLOR,
            "G": CONST_COLOR,
            "m_E": EARTH_COLOR,
            "r^{2}": R_COLOR,
        },
    )
    eq_reduced.move_to(eq_substituted, aligned_edge=m.LEFT)

    s.play(
        m.FadeOut(slashes),
        m.TransformMatchingParts(
            eq_substituted,
            eq_reduced,
            matched_pairs=matched_pairs(
                eq_substituted, eq_reduced, ["a", "G", "m_E", "r^{2}"]
            ),
            run_time=1.4,
        ),
    )
    s.wait_for_button()

    # The earlier lines have done their job — clear them and re-anchor.
    spent_lines = m.VGroup(eq_newton, eq_accel, eq_gravity)
    eq_reduced_home = eq_reduced.copy()
    place_first(eq_reduced_home)
    s.play(
        m.FadeOut(spent_lines, shift=m.UP * 0.3),
        m.Transform(eq_reduced, eq_reduced_home),
        run_time=0.9,
    )
    s.wait_for_button()

    # ---------------- 7. the assumption: r barely changes ----------------
    # Throw the ball up and let it fall back: on screen it travels a long way,
    # and the readout hardly budges. That gap *is* the assumption.
    s.play(h_tracker.animate.set_value(H_MAX), run_time=1.4, rate_func=m.smooth)
    s.play(h_tracker.animate.set_value(0.0), run_time=1.4, rate_func=m.smooth)
    s.wait_for_button()

    # Freeze it: the arrow and the readout stop being variables.
    diagram["r_arrow"].clear_updaters()
    diagram["r_label"].clear_updaters()
    diagram["readout_value"].clear_updaters()
    frozen_label = m.Tex("r_c", font_size=28).set_color(CONST_COLOR)
    frozen_label.move_to(diagram["r_label"], aligned_edge=m.RIGHT)
    s.play(
        m.FlashAround(diagram["readout"]),
        diagram["r_arrow"].animate.set_color(CONST_COLOR),
        diagram["readout"].animate.set_color(CONST_COLOR),
        m.FadeTransform(diagram["r_label"], frozen_label),
        run_time=1.0,
    )
    diagram["group"].remove(diagram["r_label"])
    diagram["group"].add(frozen_label)
    diagram["r_label"] = frozen_label
    s.wait_for_button()

    eq_frozen = build_equation(
        r"a = \frac{G \, m_E}{r_c^{2}}",
        {
            "a": MOTION_COLOR,
            "G": CONST_COLOR,
            "m_E": EARTH_COLOR,
            "r_c^{2}": CONST_COLOR,
        },
    )
    eq_frozen.move_to(eq_reduced, aligned_edge=m.LEFT)
    s.play(
        m.TransformMatchingParts(
            eq_reduced,
            eq_frozen,
            matched_pairs=matched_pairs(
                eq_reduced, eq_frozen, ["a", "G", "m_E", ("r^{2}", "r_c^{2}")]
            ),
            run_time=1.3,
        )
    )
    s.wait_for_button()

    # ---------------- 8. punchline two: it is all one constant ----------------
    fraction = m.VGroup(
        eq_frozen.select_parts("G"),
        eq_frozen.select_parts("m_E"),
        eq_frozen.select_parts("r_c^{2}"),
    )
    brace = m.Brace(fraction, m.DOWN, buff=0.12)
    brace.set_color(CONST_COLOR)
    brace_text = m.Text("constant", font=FONT, font_size=20).set_color(CONST_COLOR)
    brace_text.next_to(brace, m.DOWN, buff=0.12)
    brace_text_anim = m.FadeIn(brace_text, shift=m.UP * 0.15, run_time=0.5)
    # GrowFromCenter rather than ShowCreation: a Brace is the filled TeX glyph
    # \underbrace{\qquad}, which is 7 family members, and ShowCreation defaults
    # to lag_ratio=1.0 — so the pieces are traced strictly one after another and
    # the last one does not even begin until 86% of the run time. That stagger
    # is what makes the brace crawl in. GrowFromCenter is also what manimlib's
    # own BraceLabel.creation_anim uses.
    # No run_time on s.play: a play-level run_time overwrites the run_time of
    # every animation passed to it, which would silently discard the 0.5 above.
    s.play(
        m.GrowFromCenter(brace, run_time=0.7),
        brace_text_anim,
        eq_frozen.select_parts("m_E").animate.set_color(CONST_COLOR),
    )
    s.wait_for_button()

    eq_g = build_equation(r"a = g", {"a": MOTION_COLOR, "g": CONST_COLOR})
    eq_g.move_to(eq_frozen, aligned_edge=m.LEFT)
    s.play(
        m.FadeOut(brace),
        m.FadeOut(brace_text),
        m.TransformMatchingParts(
            eq_frozen,
            eq_g,
            matched_pairs=matched_pairs(eq_frozen, eq_g, ["a"]),
            run_time=1.4,
        ),
    )
    s.wait_for_button()

    # ---------------- 9. integrate, twice ----------------
    # Each step is posed as an integral first, then resolved into its result in
    # place. The leading symbol has to be paired with select_part rather than
    # select_parts: `select_parts("v")` also catches the v inside v_0, and
    # handing that pair to the transform would smear one glyph across two.
    int_velocity = build_equation(
        r"v = \int g \, dt",
        {"v": MOTION_COLOR, "g": CONST_COLOR},
    )
    place_below(int_velocity, eq_g)

    s.play(m.FadeIn(int_velocity, shift=m.UP * 0.4), run_time=1.0)
    s.wait_for_button()

    eq_velocity = build_equation(
        r"v = g \, t + v_0",
        {"v": MOTION_COLOR, "g": CONST_COLOR, "v_0": INIT_COLOR},
    )
    eq_velocity.move_to(int_velocity, aligned_edge=m.LEFT)

    s.play(
        m.TransformMatchingParts(
            int_velocity,
            eq_velocity,
            matched_pairs=[
                (int_velocity.select_part("v"), eq_velocity.select_part("v")),
                (int_velocity.select_part("g"), eq_velocity.select_part("g")),
            ],
            run_time=1.4,
        )
    )
    s.wait_for_button()

    int_position = build_equation(
        r"p = \int \left( g \, t + v_0 \right) dt",
        {"p": MOTION_COLOR, "g": CONST_COLOR, "v_0": INIT_COLOR},
    )
    place_below(int_position, eq_velocity)

    s.play(m.FadeIn(int_position, shift=m.UP * 0.4), run_time=1.0)
    s.wait_for_button()

    eq_position = build_equation(
        r"p = \frac{1}{2} \, g \, t^{2} + v_0 \, t + p_0",
        {
            "p": MOTION_COLOR,
            "g": CONST_COLOR,
            "v_0": INIT_COLOR,
            "p_0": INIT_COLOR,
        },
    )
    eq_position.move_to(int_position, aligned_edge=m.LEFT)

    s.play(
        m.TransformMatchingParts(
            int_position,
            eq_position,
            matched_pairs=[
                (int_position.select_part("p"), eq_position.select_part("p")),
                (int_position.select_part("g"), eq_position.select_part("g")),
                (int_position.select_part("v_0"), eq_position.select_part("v_0")),
            ],
            run_time=1.4,
        )
    )
    s.wait_for_button()

    # ---------------- 10. the payoff ----------------
    # The formula is general; make it concrete by fixing one throw's numbers,
    # then ask it a question it could not be asked before: where is the ball at
    # t = 2 s? The diagram has nothing left to say, so it clears out and the
    # graph takes the panel.
    for key in ("ball", "ball_label", "force_arrow", "force_label"):
        diagram[key].clear_updaters()

    givens_caption = m.Text("for one particular throw:", font=FONT, font_size=18)
    givens_caption.set_color(m.GREY_B)
    place_below(givens_caption, eq_position)

    givens = build_equation(
        r"g = -9.8 \quad v_0 = 12 \quad p_0 = 1",
        {"g": CONST_COLOR, "v_0": INIT_COLOR, "p_0": INIT_COLOR},
        font_size=26,
    )
    place_below(givens, givens_caption)

    s.play(m.FadeOut(diagram["group"]), run_time=0.8)
    s.play(
        m.FadeIn(givens_caption, shift=m.UP * 0.3),
        m.FadeIn(givens, shift=m.UP * 0.3),
        run_time=0.9,
    )
    s.wait_for_button()

    graph_panel = build_graph_panel()

    s.play(
        m.ShowCreation(graph_panel["axes"]),
        m.FadeIn(graph_panel["numbers"]),
        m.FadeIn(graph_panel["x_axis_label"]),
        m.FadeIn(graph_panel["y_axis_label"]),
        run_time=1.2,
    )
    s.wait_for_button()

    s.play(m.ShowCreation(graph_panel["graph"]), run_time=1.6)
    s.wait_for_button()

    # Pick a time...
    s.play(
        m.FadeIn(graph_panel["t_dot"], scale=0.5),
        m.Write(graph_panel["t_label"]),
        run_time=0.7,
    )
    s.wait_for_button()

    # ...climb to the curve...
    s.play(
        m.ShowCreation(graph_panel["riser"]),
        m.FadeIn(graph_panel["ball"], scale=0.5),
        run_time=0.9,
    )
    s.wait_for_button()

    # ...and read the height straight off the other axis. The crossbar starts on
    # the ball, so re-adding the ball afterwards keeps it drawn on top of the
    # dashes rather than half-buried under them.
    s.play(m.ShowCreation(graph_panel["crossbar"]), run_time=0.8)
    s.add(graph_panel["ball"])
    s.play(
        m.FadeIn(graph_panel["p_dot"], scale=0.5),
        m.Write(graph_panel["p_label"]),
        run_time=0.7,
    )
    s.wait_for_button()

    # The same answer the long way round: the parentheses are what keep each
    # value isolatable, since a bare "1" also lives inside \frac{1}{2} and 12.
    evaluation = build_equation(
        r"p(2) = \frac{1}{2}(-9.8)(2)^{2} + (12)(2) + (1) = 5.4",
        {
            "p": MOTION_COLOR,
            "(-9.8)": CONST_COLOR,
            "(12)": INIT_COLOR,
            "(1)": INIT_COLOR,
        },
        font_size=24,
    )
    place_below(evaluation, givens)

    s.play(m.FadeIn(evaluation, shift=m.UP * 0.3), run_time=0.9)
    s.play(m.FlashAround(graph_panel["p_label"]), run_time=1.0)
    s.wait_for_button()

    # ---------------- tear down ----------------
    # The axes and the curve stay: the next section takes the same graph, moves
    # it to centre stage and starts measuring it. Only the probe goes, having
    # already answered its one question.
    s.play(
        m.FadeOut(
            m.VGroup(
                heading,
                eq_g,
                eq_velocity,
                eq_position,
                givens_caption,
                givens,
                evaluation,
                graph_panel["probe_group"],
            )
        ),
        run_time=0.6,
    )

    return graph_panel
