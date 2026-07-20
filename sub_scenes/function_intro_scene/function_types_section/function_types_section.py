from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_theatre import MainTheatreScene

from sub_scenes.function_intro_scene.function_types_section import (
    multi_variable_type,
    single_variable_type,
    sorting_function_example,
    vector_valued_functions,
    mutli_variable_vector_valued_functions,
)



def function_types_section(s: MainTheatreScene) -> None:
    # single_variable_type.single_variable_type(s)
    # multi_variable_type.multi_variable_type(s)
    # vector_valued_functions.vector_valued_functions(s)
    mutli_variable_vector_valued_functions.mutli_variable_vector_valued_functions(s)
    # sorting_function_example.sorting_function_example(s)
