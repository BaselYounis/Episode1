"""The first way to find a function: a chain of assumptions and logical steps
that lands on a closed form.

Worked through the classic example — where is a ball thrown into the air? —
from F = m_B a all the way down to p = 1/2 g t^2 + v_0 t + p_0.

Layout: the derivation stacks in a column on the left and a ball-and-Earth
diagram lives in a panel on the right.
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

# ---- the payoff trajectory ----
# Sized to fill the right panel once the Earth diagram has cleared out.
T_MAX = 2.0
VX_VIS = 2.0
V0_VIS = 4.2
G_VIS = 4.2
LAUNCH_ORIGIN = np.array([PANEL_X - 2.3, -2.4, 0.0])


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


def trajectory_point(t: float) -> np.ndarray:
    """p(t) for the closing animation, in scene coordinates."""
    return (
        LAUNCH_ORIGIN
        + m.RIGHT * (VX_VIS * t)
        + m.UP * (V0_VIS * t - 0.5 * G_VIS * t * t)
    )


def build_trajectory(t_tracker: m.ValueTracker) -> dict:
    """The payoff: the formula finally drawn as a path through the air."""
    ground = m.Line(LAUNCH_ORIGIN + m.LEFT * 0.7, LAUNCH_ORIGIN + m.RIGHT * 4.6)
    ground.set_stroke(m.GREY_B, width=2)

    # The curve the formula predicts, shown faintly before the ball sets off.
    full_path = m.ParametricCurve(trajectory_point, t_range=(0.0, T_MAX, T_MAX / 200))
    full_path.set_stroke(m.GREY_B, width=1.5, opacity=0.45)

    trace = full_path.copy()
    trace.set_stroke(MOTION_COLOR, width=4)

    def grow_trace(mob: m.VMobject) -> None:
        alpha = min(max(t_tracker.get_value() / T_MAX, 1e-4), 1.0)
        mob.pointwise_become_partial(full_path, 0, alpha)
        mob.set_stroke(MOTION_COLOR, width=4)

    trace.add_updater(grow_trace)

    ball = m.Dot(radius=0.11).set_color(BALL_COLOR)
    ball.add_updater(lambda mob: mob.move_to(trajectory_point(t_tracker.get_value())))

    for mob in (trace, ball):
        mob.update()

    return dict(
        ground=ground,
        full_path=full_path,
        trace=trace,
        ball=ball,
        group=m.VGroup(ground, full_path, trace, ball),
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


def ball_thrown_section(s: MainTheatreScene) -> None:
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
    for key in ("ball", "ball_label", "force_arrow", "force_label"):
        diagram[key].clear_updaters()

    t_tracker = m.ValueTracker(0.0)
    trajectory = build_trajectory(t_tracker)

    s.play(m.FadeOut(diagram["group"]), run_time=0.8)
    s.play(
        m.ShowCreation(trajectory["ground"]),
        m.ShowCreation(trajectory["full_path"]),
        m.FadeIn(trajectory["ball"], scale=0.5),
        run_time=0.9,
    )
    # The trace has an updater that paints it in as t advances, so it only needs
    # to be present in the scene — never animated in. Re-adding the ball keeps
    # it drawn on top of the line it is leaving behind.
    s.add(trajectory["trace"], trajectory["ball"])
    s.wait_for_button("Press SPACE to launch ")

    s.play(
        t_tracker.animate.set_value(T_MAX),
        run_time=3.0,
        rate_func=m.linear,
    )
    trajectory["trace"].clear_updaters()
    trajectory["ball"].clear_updaters()
    s.wait_for_button()

    # ---------------- tear down ----------------
    s.play(
        m.FadeOut(
            m.VGroup(
                heading,
                eq_g,
                eq_velocity,
                eq_position,
                trajectory["group"],
            )
        ),
        run_time=0.6,
    )
