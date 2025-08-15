import re
from dataclasses import dataclass
from typing import Self


class InvalidCookieHeader(Exception):  # noqa: N818
    """You passed a non-cookie header into the cookie parser."""


class InvalidCookie(Exception):  # noqa: N818
    """Cookie failed to parse: something is wrong with the data."""


@dataclass
class Cookie:
    """Represents a single cookie."""

    name: str
    value: str
    http_only: bool
    secure: bool
    domain: str
    path: str
    persistent: bool
    expiry_time: str
    samesite: str

    @classmethod
    def from_str(cls, cookie: str, request_host: str) -> Self:  # noqa: PLR0912 C901
        """Parse a cookie from a string."""
        cookie, *attributes = cookie.split(";")
        if "=" not in cookie:
            raise InvalidCookie("Cookie missing name: %s", cookie)
        cookie_name, cookie_value = cookie.split("=", 1)

        cookie_name = cookie_name.strip()
        cookie_value = cookie_value.strip()

        http_only = False
        domain = None
        path = None
        persistent = False
        expiry_time = None
        secure = False
        samesite = None

        for attribute in attributes:
            attribute = attribute.strip()  # noqa: PLW2901

            if "=" not in attribute:
                match attribute.casefold():
                    case "httponly":
                        http_only = True
                    case "secure":
                        secure = True
                    case skipped:
                        print("skipping attribute: ", skipped)
                continue

            attribute, value = attribute.split("=", 1)  # noqa: PLW2901

            attribute = attribute.strip()  # noqa: PLW2901
            value = value.strip()

            match attribute.casefold():
                case "path":
                    path = value
                case "domain":
                    if domain == request_host:
                        domain = value
                case "max-age":
                    if value.isdigit():
                        expiry_time = value
                        persistent = True
                    else:
                        print("Not a valid age value:", value)
                case "expires":
                    expiry_time = value
                    persistent = True
                case "samesite":
                    samesite = value

        return cls(
            name=cookie_name,
            value=cookie_value,
            http_only=http_only,
            domain=domain,
            path=path,
            expiry_time=expiry_time,
            persistent=persistent,
            secure=secure,
            samesite=samesite,
        )


class CookieStorage:
    """A storage class for manipulating and reading internet cookies."""

    def __init__(self, cookies: list[Cookie] | None = None) -> None:
        if not cookies:
            cookies = []
        self.cookies = cookies
        # TODO: cookies get sorted, getitem behavior

    def handle_headers(self, headers: list[tuple[str, str]], request_host: str) -> None:
        """Parse a list of raw headers and update internal storage."""
        for name, value in headers:
            if name.casefold().strip() != "set-cookie":
                continue

            self.cookies.append(Cookie.from_str(value, request_host))

    @classmethod
    def from_headers(cls, cookie_headers: list[str], request_host: str) -> Self:
        """Create a new cookiestorage from the relevant set-cookie headers."""
        cookies = []
        for header in cookie_headers:
            match = re.match("(?P<name>[^:]+):(?P<value>.*)", header)
            if not match:
                raise InvalidCookieHeader("Not a header: %s", header)

            name = match["name"]
            value = match["value"]

            if name.casefold().strip() != "set-cookie":
                raise InvalidCookieHeader("Non-cookie header passed to cookie parser: %s", name)

            cookies.append(Cookie.from_str(value, request_host))

        return cls(cookies)

    def to_headers(self) -> str:
        """Return the relevant cookies to construct a Cookie: request header."""
        return {"Cookie:": self.to_cookie_string(for_javascript=False)}

    def __getitem__(self, key: str) -> list[Cookie]:
        """Select all matching cookies by name."""
        cookies = []
        for cookie in self.cookies:
            if cookie.name.casefold() == key.casefold():
                cookies.append(cookie)
        return cookies

    def set_cookie(self, cookie_data: str, request_host: str) -> None:
        """Set a single cookie from cookie data, usually from javascript."""
        self.cookies.append(Cookie.from_str(cookie_data, request_host))

    def __add__(self, other: Self) -> Self:
        """CookieStorages can be combined with +."""
        if isinstance(other, CookieStorage):
            return self.__class__(self.cookies + other.cookies)

        return NotImplemented

    def to_cookie_string(self, *, for_javascript: bool = True) -> str:
        """Read the cookiestore into a string suitable to return from window.cookie or in a cookie header."""
        return "; ".join(
            f"{cookie.name}={cookie.value}"
            for cookie in sorted(self.cookies, key=lambda cookie: (len(cookie.path) if cookie.path else 0))
            if cookie.http_only is not True
            or for_javascript is False  # http only cookies are not readable from javascript
        )

    def clear(self) -> None:
        """Clear all cookies."""
        self.cookies.clear()

    def end_session(self) -> None:
        """Clear all non-session cookies."""
        self.cookies = [cookie for cookie in self.cookies if cookie.persistent]
