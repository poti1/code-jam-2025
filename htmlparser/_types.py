from dataclasses import dataclass
from typing import Literal


@dataclass
class Attribute:
    """Represents a tags attribute(s)."""

    name: str
    value: str


@dataclass
class Token:
    """Represent HTML tokens."""

    kind: str | None = None
    char: str | None = None
    tag_name: str | None = None
    attrs: list[Attribute] | None = None
    curr_attr: int | None = None
    self_closing: bool = False
    data: str | None = None


@dataclass
class Element:
    """Represent HTML elements."""

    name: str
    attrs: dict[str, str]
    text: str
    children: list["Element"]


@dataclass
class Document:
    """Represent the HTML document."""

    metadata: dict[str, str]
    root: Element
    head: Element | None = None
    form: Element | None = None


@dataclass
class ParserState:
    """Represent state of the parser."""

    token: Token | None = None
    temp_buff: str | None = None
    pause: bool = False
    insertion_mode: Literal[
        "initial",
        "before html",
        "before head",
        "in head",
        "in head noscript",
        "after head",
        "in body",
        "text",
        "in table",
        "in table text",
        "in caption",
        "in column group",
        "in table body",
        "in row",
        "in cell",
        "in template",
        "after body",
        "in frameset",
        "after frameset",
        "after after body",
        "after after frameset",
    ] = "initial"
    state: str = "data"
    # state to return to after being in put in the character reference state
    return_state: str = ""
    need_to_reconsume: bool = False
    head_ptr: bool = False
