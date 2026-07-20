from __future__ import annotations
from typing import TYPE_CHECKING

from sub_scenes.function_intro_scene.function_types_section import (
    multi_variable_type,
    single_variable_type,
    sorting_function_example
)

if TYPE_CHECKING:
    from main_theatre import MainTheatreScene




def function_types_section(s: MainTheatreScene) -> None:
    # single_variable_type.single_variable_type(s)
    multi_variable_type.multi_variable_type(s)
    sorting_function_example.sorting_function_example(s)
