from __future__ import annotations
from typing import TYPE_CHECKING

from .ann_section import ann_scene

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene
import manimlib as m


def basmallah_scene(s: MainTheatreScene) -> None:
    title = m.Text(
        text="بسم الله الرحمن الرحيم",
        font_size=48,
        font="Arial",
    )
    s.play(m.FadeIn(title))
    s.wait_for_button()
    s.play(m.FadeOut(title))


def introduction_scene(s: MainTheatreScene) -> None:
    basmallah_scene(s)
    llm_label = m.Text("Large Language Models", font_size=24, font="Century")
    vision_label = m.Text(
        "Image & Video Generation Models", font_size=24, font="Century"
    )
    llm_texts = ["ChatGPT", "Gemini", "Claude"]
    llm_colors = "#10A37F", "#2596be", "#F4A261"
    vision_texts = ["DALL-E", "Sora\n(RIP)", "Nano Banana"]
    vision_colors = "#7B61FF", "#00AEEF", "#FFD84D"
    llm_rects = []
    llm_rect_anims = []
    vision_rects = []
    vision_rects_anims = []
    rects_size_factor = 0.8
    for text, color in zip(llm_texts, llm_colors):
        rect = m.Rectangle(
            width=3.5 * rects_size_factor,
            height=1.5 * rects_size_factor,
            color=color,
            fill_color=color,
            fill_opacity=0.5,
            stroke_color=color,
            stroke_width=2,
        )
        rect_text = m.Text(text, font_size=24, font="Century")
        rect_text.move_to(rect.get_center())
        llm_rects.append(m.VGroup(rect, rect_text))
        text_creation_anim = m.Write(rect_text)
        rect_creation_anim = m.ShowCreation(rect)
        llm_rect_anims.append(
            m.AnimationGroup(rect_creation_anim, text_creation_anim, lag_ratio=0.5)
        )
    for text, color in zip(vision_texts, vision_colors):
        rect = m.Rectangle(
            width=3.5 * rects_size_factor,
            height=1.5 * rects_size_factor,
            color=color,
            fill_color=color,
            fill_opacity=0.5,
            stroke_color=color,
            stroke_width=2,
        )
        rect_text = m.Text(text, font_size=24, font="Century")
        rect_text.move_to(rect.get_center())
        vision_rects.append(m.VGroup(rect, rect_text))
        text_creation_anim = m.Write(rect_text)
        rect_creation_anim = m.ShowCreation(rect)
        vision_rects_anims.append(
            m.AnimationGroup(rect_creation_anim, text_creation_anim, lag_ratio=0.5)
        )
    llm_rects_group = m.VGroup(*llm_rects).arrange(m.DOWN, buff=0.9)
    vision_rects_group = m.VGroup(*vision_rects).arrange(m.DOWN, buff=0.9)
    llm_rects_group.to_edge(m.LEFT, buff=1.0)
    vision_rects_group.to_edge(m.RIGHT, buff=1.0)
    llm_label.next_to(llm_rects_group, m.UP, buff=0.5)
    vision_label.next_to(vision_rects_group, m.UP, buff=0.5)

    s.play(m.Write(llm_label), run_time=1)
    s.play(m.AnimationGroup(*llm_rect_anims, lag_ratio=0.5), run_time=3)
    s.wait_for_button()
    s.play(m.Write(vision_label), run_time=1)
    s.play(m.AnimationGroup(*vision_rects_anims, lag_ratio=0.5), run_time=3)
    s.wait_for_button()
    llm_group = m.VGroup(llm_label, llm_rects_group)
    vision_group = m.VGroup(vision_label, vision_rects_group)
    network_with_text = ann_scene(s)
    s.wait_for_button()
    s.play(m.AnimationGroup(m.FadeOut(llm_group), m.FadeOut(vision_group)))
    s.play(m.FadeOut(network_with_text))
