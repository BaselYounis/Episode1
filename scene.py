import manimlib as manim


class InteractiveScene(manim.Scene):
    """
    Interactive presentation scene.

    Run with:
        manimgl scene.py InteractiveScene

    Press SPACE or the RIGHT ARROW key to advance to the next animation.
    Press Ctrl+Q to quit.
    """

    # ------------------------------------------------------------------
    # Helper: show a "press to continue" prompt, wait, then remove it
    # ------------------------------------------------------------------
    def wait_for_button(self, message: str = "Press SPACE to continue  ") -> None:
        prompt = manim.Text(message, font_size=24, color=manim.YELLOW)
        prompt.to_corner(manim.DR)  # bottom-right corner
        self.add(prompt)  # show instantly (no play cost)
        self.wait()  # blocks until SPACE / →
        self.remove(prompt)  # hide instantly before next play

    # ------------------------------------------------------------------
    # Scene content
    # ------------------------------------------------------------------
    def construct(self):
        # presenter_mode makes every self.wait() block until SPACE / → is pressed
        self.presenter_mode = True

        bg = manim.FullScreenRectangle(
            fill_color=manim.BLACK, fill_opacity=1, stroke_width=0
        )
        self.add(bg)

        # ── Animation 1 ───────────────────────────────────────────────
        title = manim.Text("Step 1: Draw a Circle", font_size=56)
        circle = manim.Circle(color=manim.BLUE, fill_opacity=0.5)

        self.play(manim.Write(title))
        self.play(title.animate.to_edge(manim.UP))
        self.play(manim.ShowCreation(circle))

        self.wait_for_button()  # ← pauses here

        # ── Animation 2 ───────────────────────────────────────────────
        square = manim.Square(color=manim.YELLOW, fill_opacity=0.5)
        title2 = manim.Text("Step 2: Transform to Square", font_size=56)
        title2.to_edge(manim.UP)

        self.play(manim.Transform(title, title2))
        self.play(manim.Transform(circle, square))

        self.wait_for_button()  # ← pauses here

        # ── Animation 3 ───────────────────────────────────────────────
        self.play(manim.FadeOut(circle), manim.FadeOut(title))
        final = manim.Text("The End", font_size=72, color=manim.GREEN)
        self.play(manim.Write(final))

        self.wait_for_button("Press SPACE to exit  ")  # ← final pause
