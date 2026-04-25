import re
import manimlib as m


def parse_tex_text(text: str, font: str = "Century", font_size: int = 28) -> m.VGroup:
    segments = re.split(r"\\nd", text)
    parsed_segments = []
    for segment in segments:
        parsed_segments.append(parse_tex_row(segment, font, font_size))
    result = m.VGroup(*parsed_segments).arrange(m.DOWN, buff=0.15)
    fix_text_horzintal_alignment(result)
    return result


def fix_text_horzintal_alignment(group: m.VGroup) -> None:
    max_width = max(part.get_width() for part in group)
    for part in group:
        current_part_width = part.get_width()
        displacement = (max_width - current_part_width) / 2
        part.shift(m.LEFT * displacement)


def parse_tex_row(text: str, font: str = "Century", font_size=28) -> m.VGroup:
    segments = re.split(r"\$(.+?)\$", text)
    mobjects = []
    for i, seg in enumerate(segments):
        if seg == "":
            continue
        if i % 2 == 0:
            mobjects.append(m.Text(seg, font_size=font_size, font=font))
        else:
            mobjects.append(m.Tex(seg, font_size=font_size))
    return m.VGroup(*mobjects).arrange(m.RIGHT, buff=0.15)


def select_tex(mobject: m.VGroup, tex_string: str) -> m.VGroup | None:

    parts = []
    for part in mobject:
        if isinstance(part, m.Tex) and part.tex_string == tex_string:
            parts.append(part)
    if parts:
        return m.VGroup(*parts)
    return None


def select_tex_that_includes_substring(
    mobject: m.VGroup, substring: str
) -> m.VGroup | None:
    parts = []
    for part in mobject:
        if isinstance(part, m.Tex) and substring in part.tex_string:
            parts.append(part)
    if parts:
        return m.VGroup(*parts)
    return None


def map_tex_to_color(groups: m.VGroup, tex_to_color_map: dict[str, m.Color]) -> None:
    for group in groups:
        for part in group:
            if isinstance(part, m.Tex):
                for tex_string, color in tex_to_color_map.items():
                    if tex_string in part.tex_string:
                        part.set_color_by_tex_to_color_map({tex_string: color})
