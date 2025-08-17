from __future__ import annotations

from dataclasses import InitVar, dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import htmlparser._types as parsertypes

from js import window


@dataclass
class Pos:
    """Represent position of Boxes and their content."""

    x: InitVar[int] = None
    y: InitVar[int] = None


@dataclass
class Box:
    """Represent element container."""

    top: InitVar[int] = 0
    right: InitVar[int] = 0
    bottom: InitVar[int] = 0
    left: InitVar[int] = 0


@dataclass
class Border(Box):
    """Represent border, inherit box, and add style and color attributes."""

    style: InitVar[str] = None
    color: InitVar[list[int]] = None


class Element:
    """Represent the element being painted to canvas, as opposed to one represented in the HTML parser."""

    def __init__(self, content: parsertypes.Element) -> None:
        self.pos: Pos = Pos()
        self.padding: Box = Box()
        self.border: Border = Border()
        self.margin: Box = Box()
        self.content_pos: Pos = Pos()
        self.content_height: int = 0
        self.content_width: int = None
        self.background_color: list[int] = [255, 255, 255]
        self.content: parsertypes.Element = content
        del self.content.children

    def calc_total_hw(self) -> tuple[int, int]:
        """Calculate the total height and width of the boxes and element."""
        total_height: int = sum(
            (
                self.content_height,
                self.margin.top,
                self.margin.bottom,
                self.border.top,
                self.border.bottom,
                self.padding.top,
                self.padding.bottom,
            ),
        )
        total_width: int = sum(
            (
                self.content_width,
                self.margin.left,
                self.margin.right,
                self.border.left,
                self.border.right,
                self.padding.left,
                self.padding.right,
            ),
        )
        return (total_height, total_width)

    def update_pos(self) -> None:
        """Update position of the boxes and element."""
        # Canvas origin is top left
        self.margin.x = self.pos.x
        self.margin.y = self.pos.y
        self.border.x = self.pos.x + self.margin.left
        self.border.y = self.pos.y + self.margin.top
        self.padding.x = self.margin.x + self.border.left
        self.padding.y = self.margin.y + self.border.top
        self.content_pos.x = self.padding.x + self.padding.left
        self.content_pos.y = self.padding.y + self.padding.top


class BlockElement(Element):
    """Base class for block elements."""

    def __init__(self, content: parsertypes.Element) -> None:
        super().__init__(content)
        self.padding.top: int = 5
        self.padding.bottom: int = 5
        _height, _width = self.calc_total_hw()
        self.total_height = _height
        self.total_width = _width
        if self.content_width is None:
            self.content_width: int = (
                window.innerWidth
                - self.padding.left
                - self.padding.right
                - self.margin.left
                - self.margin.right
                - self.border.left
                - self.border.right
            )


class InlineElement(Element):
    """Base class for inline elements. i.e <span>, <str>, etc."""

    def __init__(self, content: parsertypes.Element) -> None:
        super().__init__(content)
        _height, _width = self.calc_total_hw()
        self.total_height = _height
        self.total_width = _width


class ElementNotFoundError(Exception):
    """Risen from ElementList.find()."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ElementNode:
    """Node in a doubly linked list with other elements."""

    def __init__(self, element: Element) -> None:
        self.element: Element = element
        self.next: ElementNode | None
        self.prev: ElementNode | None

    def insert_next(self, element: Element) -> None:
        """Insert a node after this one."""
        new: ElementNode = ElementNode(element)
        new.prev = self
        self.next.prev = new
        self.next = new

    def insert_prev(self, element: Element) -> None:
        """Insert a node a before this one."""
        new: ElementNode = ElementNode(element)
        new.next = self
        self.prev.next = new
        self.prev = new


class ElementList:
    """Doubly linked list of elements to make updating positions easier."""

    def __init__(self, element: Element) -> None:
        self.head: ElementNode = ElementNode(element)
        self.length: int = 1
        self.end: ElementNode = self.head

    def find(self, element: Element) -> ElementNode:
        """Find and element in the list."""
        if self.length == 1 and self.head.element == element:
            return self.head
        length_is_even: bool = self.length % 2 == 0
        left_curr: ElementNode = self.head
        right_curr: ElementNode = self.end
        while (left_curr.next != right_curr and length_is_even) or (left_curr != right_curr and not length_is_even):
            if element == left_curr.element:
                return left_curr
            if element == right_curr.element:
                return right_curr
            left_curr = left_curr.next
            right_curr = right_curr.prev
        raise ElementNotFoundError(str(element.content))

    def prepend(self, element: Element) -> None:
        """Add a new head node."""
        new: ElementNode = ElementNode(element)
        self.head.insert_prev(new)
        self.head = new
        self.length += 1

    def append(self, element: Element) -> None:
        """Add a new end node."""
        new: ElementNode = ElementNode(element)
        self.end.insert_next(new)
        self.end = new
        self.length += 1

    def insert_after(self, element: Element, new_element: Element) -> None:
        """Insert a new node after an existing node."""
        el: ElementNode = self.find(element)
        el.insert_next(new_element)
        self.length += 1

    def insert_before(self, element: Element, new_element: Element) -> None:
        """Insert a new node before an existing node."""
        el: ElementNode = self.find(element)
        el.insert_prev(new_element)
        self.length += 1

    def delete(self, element: Element | ElementNode) -> None:
        """Find and delete a node."""
        if element is Element:
            el: ElementNode = self.find(element)
            el.prev.next = el.next
            el.next.prev = el.prev
            del el
        elif element is ElementNode:
            element.prev.next = element.next
            element.next.prev = element.prev
            del element
        self.length -= 1
