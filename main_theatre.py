import manimlib as manim
from sub_scenes import introduction_scene
from helper_animated_objects.general_objects import main_background
from sub_scenes.function_intro_scene.scene import function_intro_scene


class MainTheatreScene(manim.Scene):
    def wait_for_button(self, message: str = "Press SPACE to continue ") -> None:
        prompt = manim.Text(message, font_size=24)
        prompt.set_color(manim.YELLOW_B)
        prompt.to_corner(manim.DR)
        self.add(prompt)
        self.wait()
        self.remove(prompt)

    def construct(self):
        self.presenter_mode = True
        self.add(main_background)
        # introduction_scene(self)
        function_intro_scene(self)
