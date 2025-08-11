# Reference: https://html.spec.whatwg.org/
from dataclasses import dataclass
from typing import Literal


def parser_error(row: int, col: int, message: str) -> None:
    """Print error messages for debugging purposes."""
    message = f"{message} at line:{row}, col:{col}"
    print(message)


@dataclass
class Token:
    """Represent HTML tokens."""

    kind: str
    char: str
    tag_name: str | None = None
    flags: list[str] | None = None


@dataclass
class Element:
    """Represent HTML elements."""

    tag_name: str
    attrs: dict[str, str]
    text: str
    children: list["Element"]


@dataclass
class Document:
    """Represent the HTML document."""

    metadata: dict[str, str]
    root: Element


def is_appropriate_end_tag_token(
    end_tag_token: Token,  # noqa: ARG001
) -> bool:  # https://html.spec.whatwg.org/multipage/parsing.html#appropriate-end-tag-token
    """Find the last start-tag token whose name matches the end-tag token name.

    Args:
        end_tag_token (Token): token to find a start tag for

    Returns:
        bool

    """
    # TODO: Write this function's logic
    return False


def tree_constructor(token: Token) -> None:  # https://html.spec.whatwg.org/multipage/parsing.html#tree-construction
    """Construct HTML document tree."""
    # TODO: Write this function's logic
    print(token)


@dataclass
class ParserState:
    """Represent state of the parser."""

    pause: bool
    token: Token
    temp_buff: str
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
    return_state = ""
    need_to_reconsume: bool = False


class Tokenizer:
    """HTML Tokenizer."""

    def __init__(self, char: str, pos: tuple[int, int], parser_state: ParserState) -> None:
        self.char = char
        self.col, self.row = pos
        self.parser_state = parser_state

    def _emit_token(self, token: Token) -> None:
        """Emit a token for `self.char` if the param `char` is not specified."""
        tree_constructor(token)

    def _create_token(self, kind: str, **kwargs: str) -> None:
        """Create a token for `self.char` if the param `char` is not specified before emitting it."""
        if "char" not in kwargs:
            self.parser_state.token = Token(kind=kind, char=self.char)
        elif "char" in kwargs:
            self.parser_state.token = Token(kind=kind, char=kwargs["char"])

    def _switch_to_char_ref_state(
        self,
        return_to: str,
    ) -> None:  # https://html.spec.whatwg.org/multipage/parsing.html#character-reference-state
        self.parser_state.return_state = return_to
        self.parser_state.state = "character reference"

    # For all the tokenizer state specs:
    # refer to https://html.spec.whatwg.org/multipage/parsing.html#tokenization
    def _data_state(self) -> None:
        match self.char:
            case "&":
                self._switch_to_char_ref_state("data")
            case "<":
                self.parser_state.state = "tag open"
            case "":
                self._emit_token(Token("EOF", ""))
            case _:
                self._emit_token(Token("char", self.char))

    def _rcdata_state(self) -> None:
        match self.char:
            case "&":
                self._switch_to_char_ref_state("rcdata")
            case "<":
                self.parser_state.state = "rcdata lt sign"
            case "":
                self._emit_token(Token("EOF", ""))
            case _:
                self._emit_token(Token("char", self.char))

    def _rawtext_state(self) -> None:
        match self.char:
            case "&":
                self._switch_to_char_ref_state("rawtext")
            case "<":
                self.parser_state.state = "rcdata lt sign"
            case "":
                self._emit_token(Token("EOF", ""))
            case _:
                self._emit_token(Token("char", self.char))

    def _script_data_state(self) -> None:
        match self.char:
            case "<":
                self.parser_state.state = "script data lt sign"
            case "":
                self._emit_token(Token("EOF", ""))
            case _:
                self._emit_token(Token("char", self.char))

    def _plaintext_state(self) -> None:
        match self.char:
            case "":
                self._emit_token(Token("EOF", ""))
            case _:
                self._emit_token(Token("char", self.char))

    def _tag_open_state(self) -> None:
        match self.char:
            case "!":
                self.parser_state.state = "markup declaration"
            case "/":
                self.parser_state.state = "end tag open"
            case "?":
                errormsg: str = "Unexpected question mark instead of tag-name"
                parser_error(self.row, self.col, errormsg)
                self.parser_state.need_to_reconsume = True
                self.parser_state.state = "bogus comment"
            case "":
                self._emit_token(Token("char", char="<"))
                self._emit_token(Token("EOF", ""))
            case _:
                if self.char.isalpha():
                    self._create_token("start tag", name="")
                    self.parser_state.state = "tag name"
                    self.parser_state.need_to_reconsume = True
                else:
                    errormsg: str = "Invalid first character of tag-name"
                    parser_error(self.row, self.col, errormsg)
                    self._emit_token(Token("char", char="<"))
                    self.parser_state.state = "data"
                    self.parser_state.need_to_reconsume = True

    def _end_tag_open_state(self) -> None:
        match self.char:
            case ">":
                errormsg: str = "Missing end tag name"
                parser_error(self.row, self.col, errormsg)
                self.parser_state.state = "data"
            case "":
                errormsg: str = "EOF before tag name"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token("char", char="<"))
                self._emit_token(Token("char", char="/"))
                self._emit_token(Token("EOF", ""))
            case _:
                if self.char.isalpha():
                    self._create_token("start tag", name="")
                    self.parser_state.state = "tag name"
                    self.parser_state.need_to_reconsume = True
                else:
                    errormsg: str = "Invalid first character of tag-name"
                    parser_error(self.row, self.col, errormsg)

    def _tag_name_state(self) -> None:
        match self.char:
            case "\t" | "\n" | "\f" | " ":
                self.parser_state.state = "before attr name"
            case "/":
                self.parser_state.state = "self-closing start tag"
            case ">":
                self.parser_state.state = "data"
                self._emit_token(self.parser_state.token)
                self.parser_state.token.tag_name = None
            case "":
                errormsg: str = "EOF in tag"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token("EOF", ""))
            case _:
                if self.char.isalpha():
                    self.parser_state.token.tag_name += self.char.lower()  # pyright: ignore[reportOperatorIssue]
                else:
                    self.parser_state.token.tag_name += self.char  # pyright: ignore[reportOperatorIssue]

    def _rcdata_lt_sign_state(self) -> None:
        match self.char:
            case "/":
                self._create_token("end tag")
                self.parser_state.token.tag_name = ""
                self.parser_state.temp_buff = ""
                self.parser_state.need_to_reconsume = True
                self.parser_state.state = "rcdata end tag open"
            case _:
                self._emit_token(Token("char", char="<"))
                self._emit_token(Token("char", char="/"))
                self.need_to_reconsume = True
                self.state = "rcdata"

    def _rcdata_end_tag_name_state(self) -> None:
        def anything_else() -> None:
            self._emit_token(Token("char", char="<"))
            self._emit_token(Token("char", char="/"))
            for char in self.parser_state.temp_buff[::-1]:
                self._emit_token(Token("char", char=char))

        match self.char:
            case "\t" | "\n" | "\f" | " ":
                if is_appropriate_end_tag_token(self.parser_state.token):
                    self.parser_state.state = "before attr name"
                else:
                    anything_else()
            case "/":
                if is_appropriate_end_tag_token(self.parser_state.token):
                    self.parser_state.state = "self-closing start tag"
                else:
                    anything_else()
            case ">":
                if is_appropriate_end_tag_token(self.parser_state.token):
                    self.parser_state.state = "data"
                    self._emit_token(self.parser_state.token)
                else:
                    anything_else()
            case _:
                anything_else()

    def next_state(self) -> None:
        """Determine the next state."""
        match self.state:
            # this is the initial state
            case "data":
                self._data_state()
            case "rcdata":
                self._rcdata_state()
            case "rawtext":
                self._rawtext_state()
            case "script data":
                self._script_data_state()
            case "plaintext":
                self._plaintext_state()
            case "tag open":
                self._tag_open_state()
            case "end tag open":
                self._end_tag_open_state()
            case "tag name":
                self._tag_name_state()
            case _:
                pass


def parse_html(html: str) -> None:
    """Parse HTML by line.

    Args:
        html (list[str]): The full html string

    Returns:
        Element: A class representation of the HTML document

    """
