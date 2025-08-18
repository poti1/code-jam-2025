import render_types


class Renderer:
    """Represent base render class."""

    def __init__(self, ctx) -> None:  # noqa: ANN001
        self.ctx = ctx

    def draw_text(self, el: render_types.Element, x: int, y: int):
        """Render the text onto the canvas element."""
        if hasattr(el.content, "text"):
            self.ctx.fillStyle = "black"
            self.ctx.fillText(el.content.text, x, y)

    def draw_tree(self, elements: list):
        """Render elements tree wise."""
        y = 30
        node = elements.head

        while node:
            element = node.element
            self.draw_text(element, 20, y)
            y += 20  # line spacing
            node = node.txt
