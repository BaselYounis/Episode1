from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

import manimlib as m

FONT = "Century"
ACCENT = "#4CC9F0"   # machine / signature accent
PROC = "#F72585"     # processing pulse


def sorting_function_example(s: MainTheatreScene) -> None:
    """Sorting presented as a mathematical function  f : Z^n -> Z^n."""

    unsorted = [5, 2, 8, 1, 9, 3]

    # ---------- blue sadient: low value = faint, high value = saturated ----------
    # Both the hue and the fill opacity ramp with value: low values are a pale,
    # translucent tint of BLUE_C, high values are the full, opaque colour.
    BASE = m.BLUE_C
    lo, hi = min(unsorted), max(unsorted)

    def value_ratio(value):
        return (value - lo) / (hi - lo)

    def value_color(value):
        # Lighten toward white for low values; land on full BLUE_C at the top.
        return m.interpolate_color(m.BLUE, BASE, 0.3 + 0.7 * value_ratio(value))

    def value_opacity(value):
        return 0.4 + 0.6 * value_ratio(value)

    # ---------- helpers ----------
    def make_box(value):
        sq = m.RoundedRectangle(
            width=0.62, height=0.62, corner_radius=0.08,
            fill_color=value_color(value), fill_opacity=value_opacity(value),
            stroke_color=m.WHITE, stroke_width=2.2,
        )
        num = m.Text(str(value), font=FONT, font_size=26,
                     color=m.BLACK, weight=m.BOLD)
        num.move_to(sq)
        return m.VGroup(sq, num)

    def brackets(column):
        """Square brackets around a vertical column, vector-style."""
        top = column.get_top()[1] + 0.12
        bot = column.get_bottom()[1] - 0.12
        w = 0.16
        group = m.VGroup()
        for left in (True, False):
            x = (column.get_left()[0] - 0.16) if left else (column.get_right()[0] + 0.16)
            tip = w if left else -w
            pts = [
                [x + tip, top, 0], [x, top, 0],
                [x, bot, 0], [x + tip, bot, 0],
            ]
            br = m.VMobject().set_points_as_corners([np.array(p) for p in pts])
            br.set_stroke(m.WHITE, 3)
            group.add(br)
        return group

    # ---------- function signature ----------
    signature = m.Tex(
        r"\operatorname{sort}",
        r":\ \mathbb{Z}^{n}\ \longrightarrow\ \mathbb{Z}^{n}",
        font_size=52,
    )
    signature[0].set_color(ACCENT)
    signature.to_edge(m.UP, buff=0.55)

    # ---------- input vector x ----------
    in_col = m.VGroup(*[make_box(v) for v in unsorted]).arrange(m.DOWN, buff=0.12)
    in_col.to_edge(m.LEFT, buff=1.5).shift(m.DOWN * 0.15)
    in_br = brackets(in_col)
    x_label = m.Tex(r"\mathbf{x}", font_size=42).next_to(in_br, m.UP, buff=0.22)
    input_grp = m.VGroup(in_br, in_col, x_label)

    # ---------- machine f ----------
    body = m.RoundedRectangle(
        width=2.4, height=4.0, corner_radius=0.28,
        fill_color="#161B26", fill_opacity=1.0,
        stroke_color=ACCENT, stroke_width=3,
    ).shift(m.DOWN * 0.15)
    f_label = m.Tex(r"f", font_size=72, color=ACCENT).move_to(body)
    machine = m.VGroup(body, f_label)

    # ---------- output vector y ----------
    out_col = m.VGroup(*[make_box(v) for v in sorted(unsorted)]).arrange(m.DOWN, buff=0.12)
    out_col.to_edge(m.RIGHT, buff=1.5).shift(m.DOWN * 0.15)
    out_br = brackets(out_col)
    y_label = m.Tex(r"\mathbf{y}", font_size=42).next_to(out_br, m.UP, buff=0.22)

    # ---------- flow arrows ----------
    a_in = m.Arrow(in_br.get_right(), body.get_left(), buff=0.2,
                   fill_color=m.GREY_C, thickness=3,
                   max_tip_length_to_length_ratio=0.2)
    a_out = m.Arrow(body.get_right(), out_br.get_left(), buff=0.2,
                    fill_color=m.GREY_C, thickness=3,
                    max_tip_length_to_length_ratio=0.2)

    # ================= ANIMATE =================
    s.play(m.Write(signature), run_time=1.3)
    s.play(
        m.LaggedStartMap(m.FadeIn, in_col, shift=m.RIGHT * 0.25, lag_ratio=0.1),
        m.ShowCreation(in_br), m.FadeIn(x_label, shift=m.DOWN * 0.15),
        run_time=1.2,
    )
    s.play(m.DrawBorderThenFill(body), m.Write(f_label),
           m.GrowArrow(a_in), m.GrowArrow(a_out), run_time=1.1)
    s.wait(0.2)

    # feed COPIES through the machine (keep x intact)
    feeders = in_col.copy()
    s.add(feeders)
    s.play(
        m.LaggedStart(*[
            b.animate(path_arc=-0.5).move_to(body.get_center()).scale(0.12).set_opacity(0)
            for b in feeders
        ], lag_ratio=0.14),
        run_time=1.9,
    )
    s.remove(feeders)

    # processing pulse
    s.play(body.animate.set_stroke(PROC, 6), f_label.animate.set_color(PROC),
           rate_func=m.there_and_back, run_time=0.55)

    # emit y
    for b in out_col:
        b.save_state()
        b.move_to(body.get_center()).scale(0.12).set_opacity(0)
    s.add(out_col)
    s.play(m.ShowCreation(out_br), m.FadeIn(y_label, shift=m.DOWN * 0.15), run_time=0.5)
    s.play(
        m.LaggedStart(*[b.animate(path_arc=-0.5).restore() for b in out_col],
                      lag_ratio=0.14),
        run_time=1.9,
    )

    # ---------- the equation ----------
    equation = m.Tex(r"f(\mathbf{x})", r"=", r"\mathbf{y}", font_size=52)
    equation.to_edge(m.DOWN, buff=0.6)
    s.play(m.Write(equation), run_time=1.0)

    s.wait_for_button()

    everything = m.VGroup(
        signature, input_grp, machine, out_col, out_br, y_label,
        a_in, a_out, equation,
    )
    s.play(m.FadeOut(everything), run_time=0.5)
