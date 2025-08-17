import importlib
import urllib.parse

from js import KeyboardEvent, MouseEvent, console
from pyodide.ffi.wrappers import add_event_listener
from pyodide.http import FetchResponse, pyfetch
from pyscript import document

importlib.invalidate_caches()
from renderer import Renderer  # noqa: E402, F401


class WebPage:
    """A node that represents a single page."""

    def __init__(self, url: str, next=None, previous=None) -> None:  # noqa: ANN001
        self.url = url
        self.next = next
        self.previous = previous


class BrowserHistory:
    """A doubly linked list used for linking visited pages."""

    def __init__(self) -> None:
        self.current_page = None

    def backward(self) -> str:
        """Goes back to the previous page."""
        if self.current_page.previous is None:
            return None

        self.current_page = self.current_page.previous

        return self.current_page.url

    def forward(self) -> str:
        """Goes to the next page."""
        if self.current_page.next is None:
            return None

        self.current_page = self.current_page.next

        return self.current_page.url

    def load_page(self, url: str) -> None:  # noqa: D102
        new_page = WebPage(url=url)

        if self.current_page is not None:
            self.current_page.next = None
            new_page.previous = self.current_page
            self.current_page.next = new_page
            self.current_page = self.current_page.next

        self.current_page = new_page

    def get_current_page(self) -> str:  # noqa: D102
        return self.current_page.url


browser_history_obj = BrowserHistory()
user_history = []


async def reload_handler(event: MouseEvent) -> None:  # noqa: ARG001
    """Re-fetches the web page."""
    current_website_url: str = browser_history_obj.get_current_page()

    if current_website_url:
        resp = await pyfetch(
            f"http://127.0.0.1:8000/webpage/?domain={current_website_url}",
        )

        console.log(await resp.text())

        # Access the response data and pass to the parser to display it correctly.


async def google_search(query: str) -> FetchResponse:
    """Modify a Google URL query for searches."""
    encoded_query: str = urllib.parse.quote_plus(
        string=query,
    )

    resp = await pyfetch(
        f"http://127.0.0.1:8000/webpage/?domain=https://www.google.com/search?q={encoded_query}",
    )

    return resp, encoded_query


async def keypress(event: KeyboardEvent) -> None:
    """Perform address bar related operations."""
    if event.key == "Enter":
        event.preventDefault()

        if event.target.value != "":
            input_url = event.target.value.lower()

            if input_url.lower().startswith(("https://", "ftp://")):
                browser_history_obj.load_page(url=input_url)
                resp = await pyfetch(
                    f"http://127.0.0.1:8000/webpage/?domain={input_url}",
                )
                user_history.append(input_url)
                console.log(await resp.text())
            else:
                resp, encoded_query = await google_search(query=event.target.value)
                browser_history_obj.load_page(url=encoded_query)
                user_history.append(encoded_query)
                console.log(await resp.text())


async def backward_handler(event: MouseEvent) -> None:  # noqa: ARG001
    """Handle the backward button functionality."""
    backward_url: str = browser_history_obj.backward()

    console.log(backward_url)

    if backward_url is not None:
        resp = await pyfetch(
            f"http://127.0.0.1:8000/webpage/?domain={backward_url}",
        )

        console.log(await resp.text())


async def forward_handler(event: MouseEvent) -> None:  # noqa: ARG001
    """Handle the forward button functionality."""
    forward_url: str = browser_history_obj.backward()

    if forward_url is not None:
        resp = await pyfetch(
            f"http://127.0.0.1:8000/webpage/?domain={forward_url}",
        )

        console.log(await resp.text())


address_bar = document.getElementsByClassName("url-bar")[0]
add_event_listener(address_bar, "keypress", keypress)

reload_element = document.getElementsByClassName("reload")[0]
add_event_listener(reload_element, "click", reload_handler)

forward_element = document.getElementsByClassName("forward-arrow")[0]
add_event_listener(forward_element, "click", forward_handler)

backward_element = document.getElementsByClassName("backward-arrow")[0]
add_event_listener(backward_element, "click", backward_handler)
