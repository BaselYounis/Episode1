from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

from helpers import mixed_tex_parser
import manimlib as m

# Each colorscale is a list of (color, z-value) stops, ordered by z.
# Every "func" takes (x, y, t). Static examples ignore t; examples marked
# "animated" keep evolving in time while they are on screen ("t_max", if
# given, freezes the clock once the motion has made its point).
examples = [
    {
        "name": "Terrain",
        "description": "A mountain landscape — every point on the map has an altitude",
        "legend": r"$x, y$ : map coordinates $\quad$ $z$ : altitude",
        "mapping": r"a vector $(x, y) \in \mathbb{R}^2$ maps to a single scalar $z \in \mathbb{R}$",
        # A single input point to probe, demonstrating the (x, y) -> z mapping
        # on the one static example (only defined here so the reveal happens
        # once, on a surface that holds still).
        "probe": (1.0, 0.5),
        "func": lambda x, y, t: (
            2.2 * np.exp(-((x - 1.5) ** 2 + (y - 1) ** 2) / 2)
            + 1.6 * np.exp(-((x + 1.5) ** 2 + (y + 1.5) ** 2) / 1.5)
        ),
        "z_range": (-1, 3, 1),
        "colorscale": [
            (m.GREEN_E, 0.05),
            (m.GREEN_C, 0.8),
            (m.LIGHT_BROWN, 1.5),
            (m.WHITE, 2.2),
        ],
    },
    {
        # Real seas are a superposition of traveling waves: a dominant swell,
        # a weaker crossing swell, and small ripples — each with its own
        # direction and speed, so the height at every point keeps changing.
        "name": "Ocean waves",
        "description": "The sea is a sum of traveling waves — swell, a crossing sea, and ripples",
        "legend": r"$x, y$ : position at sea $\quad$ $t$ : time $\quad$ $Z$ : wave height",
        "mapping": r"a vector $(x, y, t) \in \mathbb{R}^3$ maps to a single scalar $z \in \mathbb{R}$",
        "func": lambda x, y, t: (
            0.50 * np.sin(1.0 * x + 0.6 * y - 1.2 * t)
            + 0.25 * np.sin(0.6 * x - 1.1 * y - 0.9 * t + 2)
            + 0.12 * np.sin(2.2 * x + 1.6 * y - 2.0 * t)
        ),
        "z_range": (-1, 3, 1),
        "colorscale": [
            (m.BLUE_E, -0.85),
            (m.BLUE_D, -0.2),
            (m.BLUE_B, 0.4),
            (m.WHITE, 0.9),
        ],
        "xy_range": 4.0,
        "animated": True,
    },
]

THETA = -50  # camera azimuth, degrees
PHI = 68  # camera tilt, degrees
RADIUS = 11.0  # camera distance from the axes' center (default is ~9.66)
ROTATION_RATE = 0.15  # radians per second of ambient rotation
FONT = "Century"


INPUT_COLOR = m.TEAL_B  # the input vector (x, y)
OUTPUT_COLOR = m.YELLOW_B  # the scalar output z


def build_header() -> m.VGroup:
    title = m.Text("Multivariable Functions Examples", font=FONT, font_size=32)
    header = m.VGroup(title)
    header.to_edge(m.UP, buff=0.2)
    header.fix_in_frame()
    return header


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

    surface.set_color_by_rgb_func(rgb_at, opacity=0.90)


def refresh_mesh(mesh: m.SurfaceMesh, surface: m.Surface) -> None:
    """Redraw the existing wireframe curves over the surface's current points.

    Mirrors SurfaceMesh.init_points, but rewrites the already-created paths
    in place (with straight segments — indistinguishable at this sampling
    density) so it is cheap enough to run every frame.
    """
    full_nu, full_nv = surface.resolution
    part_nu, part_nv = mesh.resolution
    points = surface.get_points() + mesh.normal_nudge * surface.get_unit_normals()
    paths = iter(mesh.submobjects)
    for ui in np.linspace(0, full_nu - 1, part_nu):
        low = full_nv * int(np.floor(ui))
        high = full_nv * int(np.ceil(ui))
        next(paths).set_points_as_corners(
            m.interpolate(points[low:low + full_nv], points[high:high + full_nv], ui % 1)
        )
    for vi in np.linspace(0, full_nv - 1, part_nv):
        next(paths).set_points_as_corners(
            m.interpolate(
                points[int(np.floor(vi))::full_nv],
                points[int(np.ceil(vi))::full_nv],
                vi % 1,
            )
        )


def make_time_updater(built: dict):
    """Build an updater that advances the example's clock and re-evaluates
    the surface (points, height colors, wireframe) in place each frame.

    All heavy work is vectorized numpy over the surface's fixed (u, v)
    sample grid, so the per-frame cost stays well under a millisecond.
    """
    example, axes = built["example"], built["axes"]
    surface, mesh = built["surface"], built["mesh"]
    func = example["func"]
    t_max = example.get("t_max", np.inf)

    nu, nv = surface.resolution
    u_values = np.linspace(*surface.u_range, nu)
    v_values = np.linspace(*surface.v_range, nv)
    # Same u-major flattened order as Surface.init_points.
    U, V = (grid.flatten() for grid in np.meshgrid(u_values, v_values, indexing="ij"))
    eps = surface.epsilon

    stops = sorted(example["colorscale"], key=lambda stop: stop[1])
    stop_values = np.array([value for _, value in stops])
    stop_rgbs = np.array([m.color_to_rgb(color) for color, _ in stops])

    clock = {"t": 0.0}

    def advance(surf: m.Surface, dt: float) -> None:
        clock["t"] = min(clock["t"] + dt, t_max)
        t = clock["t"]
        z = func(U, V, t)
        surf.data["point"][:] = axes.c2p(U, V, z)
        surf.data["du_point"][:] = axes.c2p(U + eps, V, func(U + eps, V, t))
        surf.data["dv_point"][:] = axes.c2p(U, V + eps, func(U, V + eps, t))
        # Re-tint by height; alpha is left as set at build time.
        for channel in range(3):
            surf.data["rgba"][:, channel] = np.interp(z, stop_values, stop_rgbs[:, channel])
        surf.note_changed_data()
        refresh_mesh(mesh, surf)

    return advance


def build_probe(axes: m.ThreeDAxes, example: dict) -> dict | None:
    """Build the mobjects that pick one input point and trace it to its output.

    An arrow lying in the base plane is the input vector (x, y); a dashed
    riser climbs from it to the surface, where a single dot marks the scalar
    output z. Returns the pieces plus a reveal-order so the animation reads
    left-to-right: vector in, climb, number out.
    """
    if "probe" not in example:
        return None

    x0, y0 = example["probe"]
    z0 = float(example["func"](x0, y0, 0.0))

    origin = axes.c2p(0, 0, 0)
    base = axes.c2p(x0, y0, 0)
    top = axes.c2p(x0, y0, z0)

    input_arrow = m.Arrow(origin, base, buff=0, thickness=3)
    input_arrow.set_color(INPUT_COLOR)
    input_dot = m.Dot(base, radius=0.05).set_color(INPUT_COLOR)

    riser = m.DashedLine(base, top, dash_length=0.1)
    riser.set_stroke(m.GREY_B, width=2, opacity=0.9)

    output_dot = m.Dot(top, radius=0.07).set_color(OUTPUT_COLOR)
    output_dot.set_stroke(m.WHITE, width=1)

    # Labels stand upright (in a vertical plane) so they stay legible as the
    # camera orbits, matching how the z-axis label is oriented.
    input_label = m.Tex("(x, y)", font_size=30).set_color(INPUT_COLOR)
    input_label.rotate(90 * m.DEGREES, axis=m.RIGHT)
    input_label.next_to(base, m.DOWN + m.OUT, buff=0.12)

    output_label = m.Tex("z", font_size=34).set_color(OUTPUT_COLOR)
    output_label.rotate(90 * m.DEGREES, axis=m.RIGHT)
    output_label.next_to(top, m.OUT, buff=0.12)

    return dict(
        input_arrow=input_arrow, input_dot=input_dot, input_label=input_label,
        riser=riser, output_dot=output_dot, output_label=output_label,
    )


def build_example(font: str, header: m.VGroup, example: dict) -> dict:
    xy_range = example.get("xy_range", 3.5)
    resolution = example.get("resolution", 42)

    # The mapping notation rides with the example (not the header) so it can
    # change with the arity of the input: (x, y) for the static terrain,
    # (x, y, t) for the time-dependent examples.
    subtitle = mixed_tex_parser.convert_tex_to_vgroup(
        example["mapping"], font=font, font_size=20
    )
    subtitle.set_color(m.GREY_A)
    subtitle.next_to(header, m.DOWN, buff=0.14)
    subtitle.fix_in_frame()

    # Captions are pinned to the screen so they always face the viewer.
    name = m.Text(example["name"], font=font, font_size=28, color=m.YELLOW_B)
    description = m.Text(example["description"], font=font, font_size=20, color=m.GREY_A)
    caption = m.VGroup(name, description).arrange(
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

    # Tuck the caption under the mapping subtitle so the two never overlap.
    caption.to_edge(m.LEFT, buff=0.3)
    caption.next_to(subtitle, m.DOWN, buff=0.3, coor_mask=m.UP)

    axes = m.ThreeDAxes(
        x_range=(-xy_range, xy_range, 1),
        y_range=(-xy_range, xy_range, 1),
        z_range=example["z_range"],
        width=7.0,
        height=7.0,
        depth=3.6,
    )
    # Axis labels ride with the axes (so they morph between examples) rather
    # than being pinned to the frame.
    x_label = axes.get_x_axis_label("x", buff=0.45)
    y_label = axes.get_y_axis_label("y", buff=0.45)
    z_label = m.Tex("z")
    # Stand the label upright (in a vertical plane) instead of lying flat in
    # the xy plane, then park it above the top of the z-axis.
    z_label.rotate(90 * m.DEGREES, axis=m.RIGHT)
    z_label.next_to(axes.z_axis.get_end(), m.OUT, buff=0.2)
    axis_labels = m.VGroup(x_label, y_label, z_label)
    axis_labels.set_color(m.GREY_A)

    surface = m.ParametricSurface(
        lambda u, v: axes.c2p(u, v, example["func"](u, v, 0.0)),
        u_range=(-xy_range, xy_range),
        v_range=(-xy_range, xy_range),
        resolution=(resolution, resolution),
    )
    color_surface_by_height(surface, axes, example["colorscale"])
    mesh = m.SurfaceMesh(surface, resolution=(21, 21))
    mesh.set_stroke(m.WHITE, width=0.5, opacity=0.3)

    return dict(
        example=example, axes=axes, axis_labels=axis_labels,
        surface=surface, mesh=mesh, subtitle=subtitle, caption=caption, legend=legend,
        probe=build_probe(axes, example),
    )


# Built once, at import time, rather than when the scene reaches this
# section. ManimGL opens its preview window before importing the scene
# module, so this construction (LaTeX compilation, surface sampling,
# per-vertex coloring, mesh generation) happens while the window is still
# blank — nothing has to be computed once the presentation is running, not
# even a single freeze-frame.
HEADER = build_header()
BUILT_EXAMPLES = [build_example(FONT, HEADER, example) for example in examples]


def multi_variable_type(s: MainTheatreScene) -> None:
    s.play(m.FadeIn(HEADER, shift=m.DOWN * 0.3))

    # The camera settles into its tilted orientation once and stays there —
    # ambient rotation runs continuously through every example so nothing
    # ever snaps between them.
    frame = s.camera.frame
    frame.reorient(THETA, PHI)
    # Pull the camera back from the center of the axes. The distance is the
    # frame's focal distance, so setting it also flattens perspective slightly.
    frame.set_focal_distance(RADIUS)

    def rotate(mob, dt):
        mob.increment_theta(ROTATION_RATE * dt)

    frame.add_updater(rotate)

    previous = None
    for built in BUILT_EXAMPLES:
        previous = play_example(s, built, previous)

    frame.remove_updater(rotate)
    previous["surface"].clear_updaters()
    s.play(m.FadeOut(group_of(previous)), m.FadeOut(HEADER), run_time=0.6)
    frame.to_default_state()


def group_of(built: dict) -> m.Group:
    return m.Group(*(built[key] for key in ("axes", "axis_labels", "surface", "mesh", "subtitle", "caption", "legend")))


def play_example(s: MainTheatreScene, built: dict, previous: dict | None) -> dict:
    updater = make_time_updater(built) if built["example"].get("animated") else None
    if updater is not None:
        # Rewind to t = 0 before the surface enters, in case a previous run
        # of the section left the prebuilt mobjects mid-animation.
        updater(built["surface"], 0.0)
    if previous is not None:
        # Freeze the outgoing example so its updater doesn't fight the
        # morph into the next one.
        previous["surface"].clear_updaters()

    if previous is None:
        s.play(
            m.FadeIn(built["subtitle"]),
            m.FadeIn(built["caption"], shift=m.DOWN * 0.2),
            m.FadeIn(built["legend"]),
            m.ShowCreation(built["axes"]),
            m.Write(built["axis_labels"]),
            m.ShowCreation(built["surface"]),
            m.FadeIn(built["mesh"]),
            run_time=1.8,
        )
    else:
        # Every example shares the same mobject anatomy and sampling resolution,
        # so each piece can morph directly into its counterpart: the axes rescale
        # and the surface deforms into the next landscape in place. Text is the
        # exception — the captions have no shared structure, so they crossfade.
        s.play(
            m.FadeTransform(previous["subtitle"], built["subtitle"]),
            m.FadeTransform(previous["caption"], built["caption"]),
            m.FadeTransform(previous["legend"], built["legend"]),
            m.ReplacementTransform(previous["axes"], built["axes"]),
            m.ReplacementTransform(previous["axis_labels"], built["axis_labels"]),
            m.ReplacementTransform(previous["surface"], built["surface"]),
            m.ReplacementTransform(previous["mesh"], built["mesh"]),
            run_time=1.8,
        )

    if built["probe"] is not None:
        reveal_probe(s, built["probe"])

    if updater is not None:
        # The surface holds still at t = 0 until the presenter is ready; the
        # first button press starts the clock, and the shape only begins to
        # evolve from there. A second press then moves on to the next example.
        s.wait_for_button("Press SPACE to start time ")
        built["surface"].add_updater(updater)

    s.wait_for_button()

    if built["probe"] is not None:
        # Clear the probe before this example morphs into the next, whose
        # surface has no matching input point.
        s.play(m.FadeOut(m.VGroup(*built["probe"].values())), run_time=0.5)
        built["probe"] = None

    return built


def reveal_probe(s: MainTheatreScene, probe: dict) -> None:
    """Walk through the mapping one beat at a time: vector in, climb, scalar out."""
    s.wait_for_button("Press SPACE to probe a point ")
    # The input: a vector (x, y) in the base plane.
    s.play(
        m.GrowArrow(probe["input_arrow"]),
        m.FadeIn(probe["input_dot"]),
        m.Write(probe["input_label"]),
        run_time=0.9,
    )
    # Climb straight up to the surface it lands on.
    s.play(m.ShowCreation(probe["riser"]), run_time=0.8)
    # The output: one scalar z, the height of the surface there.
    s.play(
        m.FadeIn(probe["output_dot"], scale=0.5),
        m.Write(probe["output_label"]),
        run_time=0.7,
    )
