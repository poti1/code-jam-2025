# Reference: https://html.spec.whatwg.org/
from htmlparser_types import Document, ParserState
from tokenizer import Tokenizer
from treeconstructor import html_doc


def parse_html(html: str) -> Document:
    """Parse HTML string.

    Args:
        html (str): The full html string

    Returns:
        Document: Python representation of html

    """
    parser_state: ParserState = ParserState()
    pos: int = 0
    row: int = 0
    col: int = 0
    while pos < len(html):
        parser_state.need_to_reconsume = False
        char = html[pos]
        Tokenizer(char, (row, col), parser_state).next_state()
        if parser_state.need_to_reconsume:
            continue
        pos += 1
        if char == "\n":
            row += 1
            col = 0
        else:
            col += 1
    return html_doc


if __name__ == "__main__":
    """
        Run as:
        python htmlparser/_htmlparser.py index.html
        python htmlparser/_htmlparser.py
        python htmlparser/_htmlparser.py --help
    """
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(prog="HTML Parser", description="Parse HTML into a Python Object")

    parser.add_argument(
        "filename",
        default="index.html",
        nargs="?",
        help="HTML file to parse",
    )

    args = parser.parse_args()

    with Path(args.filename).open(encoding="utf-8") as f:
        parse_html(f.read()).print(as_json=True)
