from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

from helpers import mixed_tex_parser
import manimlib as m

# ---- how big each arrow of the field is drawn -------------------------------
# VECT_WIDTH is the stroke thickness of the shaft; the arrow head is sized off
# it, so head and shaft grow together.
#
# VECT_HEIGHT is the drawn length of every arrow, as a fraction of the spacing
# between neighbouring samples (1.0 would have each arrow reach exactly to the
# next sample point). manimlib normally draws each arrow at (a squashed multiple
# of) its own magnitude, which says the same thing the colour map already says
# and shrinks the slow regions near the vortex centres to invisible stubs. Every
# arrow is drawn at this one length instead, so the grid reads as pure direction
# and speed is left entirely to the colour. See UniformVectorField.
VECT_WIDTH = 1.7
VECT_HEIGHT = 0.78

# Thickness of the input arrow — the one that grows from the origin out to the
# point being probed. Not the same unit as VECT_WIDTH: an Arrow is a filled
# shape rather than a stroke, and its shaft comes out at 0.015 scene units per
# unit of thickness (manimlib's Arrow.tickness_multiplier), so this is roughly
# twice the number that would draw the same width as a stroke.
IN_VECT_WIDTH = 1.75

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
# the frame: one swirl cell spans pi / K in each direction.
K = 1.0


def flow_field(*args: np.ndarray | float) -> np.ndarray:
    """The velocity (u, v) of the fluid at each input point (x, y).

    Written to swallow whatever the field/stream-line machinery hands it: a
    single (2,) point during ODE integration, a batched (N, 2) array of sample
    points for the arrow grid, or a loose pair of scalars x, y — which is how
    StreamLines.init_style asks for magnitudes when colouring point by point.
    The trailing axis always holds (x, y), so the same indexing covers them all.
    """
    coords = np.asarray(args[0] if len(args) == 1 else args, dtype=float)
    x, y = coords[..., 0], coords[..., 1]
    u = np.sin(K * x) * np.cos(K * y)
    v = -np.cos(K * x) * np.sin(K * y)
    return np.stack([u, v], axis=-1)


FONT = "Century"

IN_COLOR = m.TEAL_B  # the input vector: a position (x, y)
OUT_COLOR = m.YELLOW_B  # the output vector: the velocity F(x, y)
U_COLOR = m.RED_B  # first output component
V_COLOR = m.BLUE_B  # second output component

# Exactly one swirl cell, blown up to fill the frame's height. At K = 1 the
# field turns over every pi in each direction — F(x + pi, y) = -F(x, y), the
# same swirl running the other way — so a wider box would only show mirrored
# copies of what is already on screen. Cropping to one period in x keeps every
# arrow in the picture saying something new. All four edges are themselves
# stream lines (u = 0 on x = 0 and x = pi, v = 0 on y = 0 and y = pi), so the
# fluid never crosses the boundary and the crop is honest rather than arbitrary.
# Width and height match because the ranges do, which keeps the coordinate units
# square (6.0 / pi each way), so the swirl reads as round.
X_RANGE = (0, np.pi, 1)
Y_RANGE = (0, np.pi, 1)
PLANE_WIDTH = 6.0
PLANE_HEIGHT = 6.0

# How densely the plane is sampled. Turn these up for more arrows / more flow
# lines (denser but busier and slower to build), down for a sparser picture.
#
# Both are derived from a whole number of columns rather than picked freely: the
# sampler walks arange(min, max + step, step), so a density that does not divide
# the range evenly spills a row of arrows past the edge of the plane — into the
# header, in this layout. Dividing evenly lands the outermost samples exactly on
# the boundary instead, which is also what lets drop_boundary_vectors recognise
# and remove them.
FIELD_COLUMNS = 17  # arrow columns across the box; the rows match, the box being square
FLOW_COLUMNS = 9  # stream-line seed columns
FIELD_DENSITY = FIELD_COLUMNS / X_RANGE[1]  # arrows per coordinate-unit
FLOW_DENSITY = FLOW_COLUMNS / X_RANGE[1]  # seeds per coordinate-unit

# Where to probe. Snapped to the nearest *actual* sample point of the arrow grid
# (see find_probe_index), because the whole point of the probe is that the input
# lands on a vector the field has already drawn. The position points up-and-right
# while the velocity there points down-and-right, so the picture makes plain that
# the output vector is nothing like the input vector.
PROBE_TARGET = (1.15, 1.15)
FIELD_DIM_OPACITY = 0.22  # what the rest of the field fades to while probing
PROBE_WIDTH_BOOST = 2.0  # how much the probed arrow thickens
# How much room to leave around the probe once the camera has pushed in on it.
# 1.0 would crop to the input arrow and the two labels exactly; above that is
# breathing space, and the surrounding field stays visible in the margin so the
# lit vector is still read against its neighbours rather than in isolation.
PROBE_ZOOM_MARGIN = 1.45

# The colour bar that names the field's colour map. Colour is the only thing
# left carrying magnitude once every arrow is the same length, so it needs a key.
LEGEND_WIDTH = 2.4
LEGEND_HEIGHT = 0.16
LEGEND_SWATCHES = 64  # slices the bar is painted in; more is smoother


def interior_mask(coords: np.ndarray) -> np.ndarray:
    """True for sample coords strictly inside the box, False anywhere on an edge.

    Shared by the arrows and the stream lines so both are inset by exactly the
    same rule.
    """
    eps = 1e-6
    return (
        (coords[:, 0] > eps)
        & (coords[:, 1] > eps)
        & (coords[:, 0] < X_RANGE[1] - eps)
        & (coords[:, 1] < Y_RANGE[1] - eps)
    )


class UniformVectorField(m.VectorField):
    """A vector field whose arrows are all drawn at one fixed length.

    Only the geometry changes: the base class still paints every arrow from the
    colour map by its true magnitude, and dropping the length cue is what leaves
    that colour to speak for itself.
    """

    def __init__(self, *args, len_to_step: float = VECT_HEIGHT, **kwargs):
        self.len_to_step = len_to_step
        self.vect_len = None  # measured off the untrimmed grid, on first draw
        super().__init__(*args, **kwargs)  # ends by calling update_vectors()

    def update_vectors(self):
        """Lay out the arrows as usual, then re-cut them to a common length.

        This is the tail of VectorField.update_vectors with the drawn length
        held constant instead of read off the magnitude. Recomputing the points
        rather than simply scaling each arrow is what keeps the arrow *heads*
        one size: the head is a fixed length taken off the tip, not a fraction
        of the shaft.
        """
        super().update_vectors()

        points, bases = self.get_points(), self.sample_points
        # Where the base class put each tip; only the direction is kept.
        directions = points[6::8] - bases
        norms = np.linalg.norm(directions, axis=1)[:, np.newaxis]
        units = np.zeros_like(directions)
        np.true_divide(directions, norms, out=units, where=(norms > 0))

        if self.vect_len is None:
            # Sample points are ordered column by column, so neighbours in the
            # array are one grid step apart. Measured once, during the first
            # draw, so that drop_boundary_vectors cannot shift the length later.
            self.vect_len = self.len_to_step * m.get_norm(bases[1] - bases[0])

        tip_len = self.tip_len_to_width * self.tip_width_ratio * self.stroke_width
        points[0::8] = bases
        points[2::8] = bases + max(self.vect_len - tip_len, 0) * units
        points[4::8] = points[2::8]
        points[6::8] = bases + self.vect_len * units
        for i in (1, 3, 5):
            points[i::8] = 0.5 * (points[i - 1 :: 8] + points[i + 1 :: 8])
        points[7::8] = points[6:-1:8]

        # The base class thins any arrow shorter than its own head; at a
        # constant length nothing is short, so that scaling is undone.
        self.get_stroke_widths()[:] = self.stroke_width * self.base_stroke_width_array

        self.note_changed_data()
        return self


class InteriorStreamLines(m.StreamLines):
    """Stream lines seeded strictly inside the box.

    Each of the four edges is itself a stream line (u = 0 on x = 0 and x = pi,
    v = 0 on y = 0 and y = pi), so a seed landing on one produces a flash that
    slides flat along the axis or the border — animated frame decoration rather
    than fluid. This is the same rule drop_boundary_vectors applies to the
    arrows. Filtering the seeds here, before draw_lines integrates them, also
    skips the ODE work for the roughly one seed in four that sits on an edge.
    """

    def get_sample_coords(self):
        coords = super().get_sample_coords()
        return coords[interior_mask(coords)]


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
    formula.to_corner(m.UL, buff=0.35).shift(m.DOWN * 0.5).shift(m.RIGHT * 0.1)
    formula.fix_in_frame()

    return formula


def build_legend(field: m.VectorField) -> m.VGroup:
    """A colour bar reading off what the arrow colours mean.

    Painted from the field's *own* colour map and magnitude range, so the key
    cannot drift away from the arrows it explains. The bar is sliced into flat
    swatches rather than given a gradient fill, because a gradient runs around a
    rectangle's perimeter rather than across it; each swatch is drawn a little
    wider than its slot so no seam shows between neighbours.
    """
    low, high = field.magnitude_range
    slot = LEGEND_WIDTH / LEGEND_SWATCHES

    bar = m.VGroup()
    for i, alpha in enumerate(np.linspace(0, 1, LEGEND_SWATCHES)):
        swatch = m.Rectangle(width=1.5 * slot, height=LEGEND_HEIGHT)
        swatch.set_fill(m.rgb_to_color(field.color_map(np.array([alpha]))[0, :3]), 1)
        swatch.set_stroke(width=0)
        swatch.move_to(m.RIGHT * ((i + 0.5) * slot - LEGEND_WIDTH / 2))
        bar.add(swatch)
    border = m.SurroundingRectangle(bar, buff=0)
    border.set_stroke(m.GREY_B, width=1).set_fill(opacity=0)

    caption = m.Tex(r"\text{speed } |\mathbf{F}(x, y)|", font_size=22)
    caption.set_color(m.GREY_A)
    caption.next_to(border, m.UP, buff=0.1)

    ticks = m.VGroup()
    for value, edge in ((low, m.LEFT), (high, m.RIGHT)):
        tick = m.Tex(f"{value:g}", font_size=18).set_color(m.GREY_B)
        tick.next_to(border.get_corner(m.DOWN + edge), m.DOWN, buff=0.08)
        ticks.add(tick)

    legend = m.VGroup(bar, border, caption, ticks)
    # Pinned opposite the formula, at the same height, so the two frame the field.
    legend.to_corner(m.UL, buff=0.35).shift(m.DOWN * 1.2)
    legend.fix_in_frame()
    return legend


def drop_boundary_vectors(field: m.VectorField) -> None:
    """Delete the arrows sitting directly on the edges of the box.

    The boundary is a closed stream line, so the flow there runs exactly
    parallel to it and those arrows lie flat along the axes and the border,
    reading as decoration on the frame rather than as field. Dropping all four
    edges rather than just the two axes keeps the quadrant evenly inset.

    A VectorField sizes every one of its arrays from sample_coords at
    construction, so trimming the coords means rebuilding the point, colour and
    width arrays behind them.
    """
    coords = field.sample_coords
    field.set_sample_coords(coords[interior_mask(coords)])
    field.update_sample_points()
    field.init_base_stroke_width_array(len(field.sample_coords))
    field.init_points()
    # Re-establish width and opacity on the freshly sized arrays before
    # update_vectors fills in the geometry and the magnitude colours.
    field.set_stroke(width=field.stroke_width, opacity=1.0)
    field.update_vectors()


def find_probe_index(field: m.VectorField) -> int:
    """Index of the field arrow whose base sits nearest PROBE_TARGET.

    Snapping to the grid rather than trusting PROBE_TARGET keeps the probe exact
    even if the density or the coordinate ranges are later retuned.
    """
    deltas = field.sample_coords - np.array(PROBE_TARGET, dtype=float)
    return int(np.argmin(np.linalg.norm(deltas, axis=1)))


def arrow_slice(field: m.VectorField, index: int) -> slice:
    """The stretch of the field's flat arrays belonging to one arrow.

    A VectorField is a single mobject, not one mobject per arrow: every arrow is
    8 consecutive entries in the point, colour and width arrays (the very last
    one is clipped short), so this is how an individual vector gets addressed.
    """
    return slice(8 * index, min(8 * index + 8, field.get_num_points()))


def build_probe(plane: m.NumberPlane, field: m.VectorField) -> dict:
    """Pick one input point and name the output vector already sitting there.

    A faint arrow from the origin is the input vector (a position). Its tip lands
    exactly on the base of one of the field's own arrows — that arrow *is* the
    output, so nothing new is drawn for it; it only has to be lit up (see
    set_probe_highlight). Returns the pieces plus the index of that arrow.
    """
    index = find_probe_index(field)
    base = field.sample_points[index]
    tip = field.get_points()[8 * index + 6]

    input_arrow = m.Arrow(plane.get_origin(), base, buff=0, thickness=IN_VECT_WIDTH)
    input_arrow.set_color(IN_COLOR)
    input_arrow.set_opacity(0.85)
    input_dot = m.Dot(base, radius=0.03).set_color(IN_COLOR)
    input_dot.set_stroke(m.WHITE, width=1)

    # The velocity runs down-and-right from the point, so up-and-right is free.
    input_label = m.Tex("(x, y)", font_size=30).set_color(IN_COLOR)
    input_label.next_to(base, m.UR, buff=0.1)
    input_label.scale(0.75)  # the label is a little big for the arrow, so shrink it

    output_label = m.Tex(r"\mathbf{F}(x, y)", font_size=30).set_color(OUT_COLOR)
    output_label.next_to(tip, m.DR, buff=0.1)
    output_label.scale(0.75)
    return dict(
        index=index,
        input_arrow=input_arrow,
        input_dot=input_dot,
        input_label=input_label,
        output_label=output_label,
    )


def probe_focus(frame: m.CameraFrame, probe: dict) -> tuple[np.ndarray, float]:
    """Where to put the camera, and how tall to make it, to fill it with the probe.

    Measured off the probe's own mobjects rather than written down as numbers, so
    the framing follows PROBE_TARGET and the grid density if either is retuned.
    The input arrow runs from the origin to the point being probed and the output
    label sits just past the tip of F(x, y), so their union is exactly the picture
    that has to stay on screen. Fitting the width as well as the height matters
    because setting a frame's height scales it uniformly: a probe wider than it is
    tall would otherwise be cropped at the sides.

    The frame is then held over the box. The probe is anchored at the origin,
    which is the *corner* of a one-quadrant plane, so a frame centred on the probe
    alone would spill past two edges of the field and fill a quarter of the shot
    with the black outside it. Sliding it back in keeps every part of the zoom
    looking at field. On an axis where the frame is simply too big to fit, it
    centres on the box instead and the overhang is split evenly.
    """
    focus = m.VGroup(probe["input_arrow"], probe["input_label"], probe["output_label"])
    extent = max(focus.get_height(), focus.get_width() / frame.get_aspect_ratio())
    height = PROBE_ZOOM_MARGIN * extent
    spans = (height * frame.get_aspect_ratio(), height)

    center = focus.get_center().copy()
    low, high = PLANE.get_corner(m.DL), PLANE.get_corner(m.UR)
    for axis, span in enumerate(spans):
        if high[axis] - low[axis] <= span:
            center[axis] = 0.5 * (low[axis] + high[axis])
        else:
            center[axis] = np.clip(
                center[axis], low[axis] + span / 2, high[axis] - span / 2
            )
    return center, height


def set_probe_highlight(
    field: m.VectorField,
    index: int,
    base_rgba: np.ndarray,
    base_widths: np.ndarray,
    alpha: float,
) -> None:
    """Cross-fade the field between its resting look and the probed look.

    At alpha 0 it is exactly the snapshot it was built with; at alpha 1 every
    arrow has faded to a wash except the probed one, which brightens to the
    function colour and thickens. The field's own colour map runs
    blue -> green -> yellow -> red, so a bare recolour to YELLOW_B would vanish
    among its neighbours: dimming the rest is what makes the one vector read.
    """
    lit = arrow_slice(field, index)

    rgba = field.data["stroke_rgba"]
    rgba[:, :3] = base_rgba[:, :3]
    rgba[:, 3] = m.interpolate(base_rgba[:, 3], FIELD_DIM_OPACITY, alpha)
    rgba[lit, :3] = m.interpolate(base_rgba[lit, :3], m.color_to_rgb(OUT_COLOR), alpha)
    rgba[lit, 3] = base_rgba[lit, 3]

    widths = field.get_stroke_widths()
    widths[:] = base_widths
    widths[lit] = base_widths[lit] * m.interpolate(1.0, PROBE_WIDTH_BOOST, alpha)

    field.note_changed_data()


# Built once, at import time, before the presentation window opens. The stream
# lines integrate an ODE from every seed point, which is the one genuinely slow
# step here; doing it now keeps the scene from stalling when it is reached.
PLANE = m.NumberPlane(
    x_range=X_RANGE,
    y_range=Y_RANGE,
    width=PLANE_WIDTH,
    height=PLANE_HEIGHT,
    background_line_style=dict(
        stroke_color=m.BLUE_E, stroke_width=1, stroke_opacity=0.35
    ),
    faded_line_ratio=1,
)
# The origin is the lower-left corner of a first-quadrant plane; nudge the whole
# thing down so the top of the field clears the header.
PLANE.shift(m.DOWN * 0.3)

# The faded gridlines are generated half a step past the range, which on a
# one-quadrant plane leaves a stray line hanging above the box (right under the
# header) and another off its right edge. Trim them so the quadrant reads as a
# closed box with a clean border.
_BOX_UR = PLANE.background_lines.get_corner(m.UR)
PLANE.faded_lines.set_submobjects(
    [
        line
        for line in PLANE.faded_lines
        if (
            np.maximum(line.get_start(), line.get_end())[:2] <= _BOX_UR[:2] + 1e-6
        ).all()
    ]
)

FIELD = UniformVectorField(
    flow_field,
    PLANE,
    density=FIELD_DENSITY,
    magnitude_range=(0, 1.0),
    stroke_width=VECT_WIDTH,
)
drop_boundary_vectors(FIELD)

STREAM_LINES = InteriorStreamLines(
    flow_field,
    PLANE,
    density=FLOW_DENSITY,
    # Seeds are normally jittered off the grid, but the jitter is one-sided
    # (up-and-right), so a jittered seed no longer sits where the grid says it
    # does. Seeding exactly on the grid is what lets InteriorStreamLines
    # recognise the boundary seeds and drop them.
    noise_factor=0.0,
    stroke_width=2.0,
    # A single cyan for every line rather than the arrows' magnitude colour map:
    # once the field dims, the flow reads as one moving fluid instead of a second
    # copy of the speed key.
    color_by_magnitude=False,
    stroke_color="#F7FAFA",
    magnitude_range=(0, 1.0),
    stroke_opacity=0.9,
)
# Stagnation points, where the fluid stands still, integrate to a curve of zero
# length. Most of them sit on the boundary and are gone already; this catches any
# interior seed that lands on one, before it reaches the passing-flash animation,
# which would have nothing to walk along.
STREAM_LINES.set_submobjects(
    [
        line
        for line in STREAM_LINES
        if m.get_norm(np.ptp(line.get_points(), axis=0)) > 1e-3
    ]
)
FLOW = m.AnimatedStreamLines(STREAM_LINES)


def vector_fields(s: MainTheatreScene) -> None:
    header = build_header()
    formula = build_formula()
    legend = build_legend(FIELD)
    probe = build_probe(PLANE, FIELD)

    # The camera pushes in on the probed vector and pulls back out again when the
    # flow is released. Where it starts is recorded now, and get_center hands back
    # a live view into the frame's own points, so it has to be copied or "home"
    # would drift along with the zoom. The header, formula and legend are all
    # fixed in frame and so sit out both moves.
    frame = s.camera.frame
    home_center, home_height = frame.get_center().copy(), frame.get_height()
    focus_center, focus_height = probe_focus(frame, probe)

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
    # The colour key arrives with the arrows: this is the moment the colours
    # start meaning something.
    s.play(
        grow.animate.set_value(1.0),
        m.FadeIn(legend, shift=m.DOWN * 0.2),
        run_time=1.5,
    )
    FIELD.remove_updater(grow_vectors)
    FIELD.update_vectors()

    # The field at rest, captured now that update_vectors has run for the last
    # time — every later call would repaint these arrays from the colour map and
    # wipe the highlight. This snapshot is both what the highlight fades away
    # from and what the field is restored to afterwards.
    base_rgba = FIELD.data["stroke_rgba"].copy()
    base_widths = FIELD.get_stroke_widths().copy()

    s.wait_for_button("Press SPACE to probe a point ")

    # One input point in. No output arrow is drawn: the field already has one
    # rooted exactly where this arrow lands.
    s.play(
        m.GrowArrow(probe["input_arrow"]),
        m.FadeIn(probe["input_dot"]),
        run_time=0.9,
    )
    # Now say which vector that is: the rest of the field falls back, the one
    # arrow at (x, y) lights up, and both ends get their name. The camera pushes
    # in on it at the same time — every arrow is drawn short so the grid can be
    # dense, which leaves the one being singled out too small to look at on its
    # own until the frame comes down around it. The legend is fixed in frame, so
    # the zoom would leave it floating over a close-up it no longer keys; it fades
    # out with the push-in and comes back when the camera pulls out.
    s.play(
        m.UpdateFromAlphaFunc(
            FIELD,
            lambda mob, a: set_probe_highlight(
                mob, probe["index"], base_rgba, base_widths, a
            ),
        ),
        m.FadeOut(legend, shift=m.UP * 0.2),
        frame.animate.move_to(focus_center).set_height(focus_height),
        run_time=1.4,
    )
    s.wait_for_button()
    s.play(
        m.Write(probe["input_label"]),
    )
    s.wait_for_button()
    s.play(
        m.Write(probe["output_label"]),
    )
    s.wait_for_button("Press SPACE to release the flow ")

    # Turn the static arrows into moving fluid: pull the camera back out to the
    # whole swirl, dim the field, clear the probe, and let stream lines drift
    # along it so the swirls read as real flow. The zoom belongs to this beat —
    # a single point was the subject a moment ago, the whole cell is now. The
    # highlight is undone first, since set_stroke sets one opacity for the whole
    # field and would otherwise strand the probed arrow yellow and bright.
    probe_group = m.VGroup(
        *(part for part in probe.values() if isinstance(part, m.Mobject))
    )
    # Cross-fade straight from the probed look to the released one instead of
    # snapping the whole field back to full opacity first and then dimming it: the
    # dimmed neighbours already sit at 0.22, a hair off the final 0.25, so
    # animating from where they are keeps the field from flashing bright in the gap
    # between the probe and the flow. The probed arrow still un-highlights over the
    # same beat — yellow back to its magnitude colour, thickness and opacity back
    # to the field's rest values.
    probed_rgba = FIELD.data["stroke_rgba"].copy()
    probed_widths = FIELD.get_stroke_widths().copy()
    released_rgba = base_rgba.copy()
    released_rgba[:, 3] = 0.25

    def release_field(mob, a):
        mob.data["stroke_rgba"][:] = m.interpolate(probed_rgba, released_rgba, a)
        mob.get_stroke_widths()[:] = m.interpolate(probed_widths, base_widths, a)
        mob.note_changed_data()

    s.play(
        m.FadeOut(probe_group),
        m.FadeIn(legend, shift=m.DOWN * 0.2),
        m.UpdateFromAlphaFunc(FIELD, release_field),
        frame.animate.move_to(home_center).set_height(home_height),
        run_time=1.2,
    )
    s.add(FLOW)

    s.wait_for_button()

    # ---- tear down ----
    FLOW.clear_updaters()
    s.remove(FLOW)
    everything = m.Group(header, formula, legend, PLANE, FIELD)
    s.play(m.FadeOut(everything), run_time=0.6)
