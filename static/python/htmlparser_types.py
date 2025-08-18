from collections import deque
from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Literal, Union


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
class Document:
    """Represent the HTML document."""

    is_element: bool = False
    children: list["Element"] = field(default_factory=list)

    def traverse(self) -> Generator["Element", None, None]:
        """Traverse HTML Document object."""
        q = deque([self])
        while q:
            curr = q.popleft()
            yield curr
            q.extend(curr.children)

    def print(self, *, as_json: bool = False) -> None:
        """Print document in lines or as json."""
        import json  # noqa: PLC0415

        for node in self.traverse():
            if node.is_element:
                name_str: str = node.name + "; " if node.attrs != {} else node.name
                attrs_str: str = str(node.attrs) if node.attrs != {} else ""
                attrs_str += "; " if node.text.strip() != "" else attrs_str

                if as_json:
                    print(
                        json.dumps(
                            {
                                "name_str": name_str,
                                "attrs_str": attrs_str,
                            },
                            sort_keys=True,
                            indent=4,
                        ),
                    )
                else:
                    print(f"{name_str}{attrs_str}{node.text.strip()}")


@dataclass
class Element:
    """Represent HTML elements."""

    name: str
    attrs: dict[str, str]
    text: str
    children: list["Element"]
    parent: Union["Element", Document]
    dont_display: bool
    is_element: bool = True


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
        "in style",
        "after frameset",
        "after after body",
        "after after frameset",
    ] = "initial"
    state: str = "data"

    # state to return to after being in put in the character reference state
    return_state: str = ""
    need_to_reconsume: bool = False
    head_ptr: bool = False
