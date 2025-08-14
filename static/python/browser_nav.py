class WebPage:
    """A node that represents a single page."""

    def __init__(self, url: str, next=None, previous=None) -> None:  # noqa: ANN001
        self.url = url
        self.next = next
        self.previous = previous


class BrowserHistory:
    """A doubly linked list used for linking visited pages."""

    def __init__(self, current_page) -> None:  # noqa: ANN001
        self.current_page = WebPage(current_page)

    def backward(self) -> None:
        """Goes back to the previous page."""
        if self.current_page.previous is None:
            return

        self.current_page = self.current_page.previous

    def forward(self) -> None:
        """Goes to the next page."""
        if self.current_page.next is None:
            return

        self.current_page = self.current_page.next

    def load_page(self, url: str) -> None:  # noqa: D102
        new_page = WebPage(url=url)
        new_page.previous = self.current_page
        self.current_page.next = new_page
        self.current_page = self.current_page.next
