import ast
from typing import List



def parse_list(llm_output: str) -> List[str] | None:
    try:
        return ast.literal_eval(llm_output)
    except (ValueError, SyntaxError):
        return None

