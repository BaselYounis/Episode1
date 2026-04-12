
import manimlib as manim
from sub_scenes.introduction import introduction_scene


class MainTheatreScene(manim.Scene):
    def wait_for_button(self, message: str = "Press SPACE to continue ") -> None:
        prompt = manim.Text(message, font_size=24, color=manim.YELLOW)
        prompt.to_corner(manim.DR)
        self.add(prompt)
        self.wait()
        self.remove(prompt)

    def construct(self):
        self.presenter_mode = True
        introduction_scene(self)
