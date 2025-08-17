import json
import urllib.parse

from cookies import CookieStorage
from js import KeyboardEvent, MouseEvent, console
from pyodide.ffi.wrappers import add_event_listener
from pyodide.http import FetchResponse, pyfetch
from pyscript import document


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
cookie_storage = CookieStorage()
user_history = []


async def load_page(url: str) -> dict:
    """Load a page, handling cookies and api interfacing."""
    resp = await pyfetch(
        "http://127.0.0.1:8000/webpage/",
        method="POST",
        body=json.dumps(
            {
                "target": url,
                "headers": cookie_storage.to_headers(),
            },
        ),
        headers={"Content-Type": "application/json"},
    )

    data = await resp.json()

    console.log(data)

    # Parse out cookie headers
    cookie_storage.handle_headers(
        headers=data["headers"],
        request_host=url,
    )

    return data


async def reload_handler(event: MouseEvent) -> None:  # noqa: ARG001
    """Re-fetches the web page."""
    textarea_element = document.getElementsByTagName("textarea")[0]
    current_website_url: str = browser_history_obj.get_current_page()

    if current_website_url:
        resp = await load_page(current_website_url)
        textarea_element.value = resp["final_url"]
        # Access the response data and pass to the parser to display it correctly.
        browser_body = document.getElementsByClassName("browser-body")  # noqa: F841


async def web_search(query: str) -> FetchResponse:
    """Modify a URL query for searches."""
    encoded_query: str = urllib.parse.quote_plus(
        string=query,
    )

    resp = await load_page(f"https://www.mojeek.com/search?q={encoded_query}")
    console.log(resp["content"])

    return resp["content"], resp["final_url"]


async def keypress(event: KeyboardEvent) -> None:
    """Perform address bar related operations."""
    if event.key == "Enter":
        event.preventDefault()

        if event.target.value != "":
            input_url = event.target.value.lower()
            textarea_element = await direct_address_bar()

            if "\n" in input_url:
                input_url = input_url.replace("\n", "")
                textarea_element.value = input_url

            if input_url.startswith("http://"):
                input_url = input_url.replace("http://", "https://")
                textarea_element.value = input_url

            if input_url.startswith(("https://", "ftp://")):
                browser_history_obj.load_page(url=input_url)
                resp = await load_page(input_url)

                if resp is not None:
                    textarea_element.value = resp["final_url"]
                    user_history.append(resp["final_url"])
            else:
                resp, final_url = await web_search(query=event.target.value)
                browser_history_obj.load_page(url=final_url)
                textarea_element.value = final_url
                user_history.append(final_url)


async def backward_handler(event: MouseEvent) -> None:  # noqa: ARG001
    """Handle the backward button functionality."""
    textarea_element = await direct_address_bar()
    backward_url: str = browser_history_obj.backward()

    console.log(backward_url)

    if backward_url is not None:
        resp = await load_page(backward_url)
        textarea_element.value = resp["final_url"]
        console.log(resp["content"])


async def forward_handler(event: MouseEvent) -> None:  # noqa: ARG001
    """Handle the forward button functionality."""
    textarea_element = await direct_address_bar()
    forward_url: str = browser_history_obj.backward()

    if forward_url is not None:
        resp = await load_page(forward_url)
        textarea_element.value = resp["final_url"]
        console.log(resp["content"])


async def direct_address_bar():  # noqa: ANN201
    """Return the direct element for the address bar."""
    return document.getElementById("direct-url-bar")


address_bar = document.getElementsByClassName("url-bar")[0]
add_event_listener(address_bar, "keypress", keypress)

reload_element = document.getElementsByClassName("reload")[0]
add_event_listener(reload_element, "click", reload_handler)

forward_element = document.getElementsByClassName("forward-arrow")[0]
add_event_listener(forward_element, "click", forward_handler)

backward_element = document.getElementsByClassName("backward-arrow")[0]
add_event_listener(backward_element, "click", backward_handler)
