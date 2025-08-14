# Reference: https://html.spec.whatwg.org/multipage/parsing.html#tree-construction
from _types import Document, Element, Token

open_element_stack: list = []


def new_element(token: Token, parent: Element | Document, *, dont_display: bool = False) -> Element:
    """Create a new element from token."""
    attrs: dict[str, str] = {a.name: a.value for a in token.attrs} if token.attrs is not None else {}
    return Element(name=token.tag_name, attrs=attrs, text="", children=[], parent=parent, dont_display=dont_display)


html_doc: Document = Document()


def tree_constructor(token: Token) -> None:
    """Construct HTML document tree."""
    parent: Element | Document = open_element_stack[-1] if len(open_element_stack) > 0 else html_doc
    if token.kind == "start tag":
        match token.tag_name:
            case "head" | "template" | "script":
                el: Element = new_element(token, parent, dont_display=True)
                parent.children.append(el)
                open_element_stack.append(el)
            case (
                "area"
                | "base"
                | "br"
                | "col"
                | "embed"
                | "hr"
                | "img"
                | "input"
                | "link"
                | "menuitem"
                | "meta"
                | "param"
                | "source"
                | "template"
                | "track"
                | "wbr"
            ):  # in case tokenizer marks self-closing as start tag
                el: Element = new_element(token, parent)
                if el.parent.dont_display:
                    el.dont_display = True
                parent.children.append(el)
            case _:
                el: Element = new_element(token, parent)
                parent.children.append(el)
                open_element_stack.append(el)
    elif parent.is_element:
        if token.kind == "char":
            parent.text += token.char
    elif token.kind == "end tag":
        open_element_stack.pop()
