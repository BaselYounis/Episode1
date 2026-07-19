
import manimlib as manim
from constants.colors import main_background_color


main_background = manim.FullScreenRectangle(
    fill_color=main_background_color, fill_opacity=1, stroke_width=0
)
# Keep the backdrop glued to the screen even when a 3D scene reorients the
# camera — otherwise it tilts along with everything else and lets the
# renderer's default gray clear-color show through at the edges.
main_background.fix_in_frame()


