# Reference: https://html.spec.whatwg.org/multipage/parsing.html#tree-construction
from _types import Document, Element, ParserState, Token

def tree_constructor(token: Token, parser_state: ParserState) -> Document:
    """Construct HTML document tree."""
