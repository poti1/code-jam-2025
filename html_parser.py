# Reference: https://html.spec.whatwg.org/
from dataclasses import dataclass
from typing import Literal


def parser_error(row: int, col:int, message: str) -> None:
        message = f"{message} at line:{row}, col:{col}"
        print(message)

@dataclass
class ParserState:
    pause: bool
    insertion_mode: Literal[
    "initial", "before html", "before head", "in head","in head noscript",
    "after head", "in body", "text", "in table", "in table text", "in caption",
    "in column group", "in table body", "in row", "in cell", "in template",
    "after body", "in frameset", "after frameset", "after after body",
    "after after frameset"] = "initial"

@dataclass
class Token:
    kind: str
    char: str
    tag_name: str | None = None
    flags: list[str] | None = None

@dataclass
class Element:
    tag_name: str
    attrs: dict[str,str]
    text: str
    children: list['Element']

@dataclass
class Document:
    metadata: dict[str,str]
    root: Element

tokens: list[Token] = []

def is_appropriate_end_tag_token(end_tag_token:Token) -> bool: # https://html.spec.whatwg.org/multipage/parsing.html#appropriate-end-tag-token
    """Find the last start-tag token whose name matches the end-tag token name.

    Args:
        end_tag_token (Token): token to find a start tag for
    Returns:
        bool
    """
    # TODO: Write this function's logic
    return False

def tree_constructor(token: Token): # https://html.spec.whatwg.org/multipage/parsing.html#tree-construction
    # TODO: Write this function's logic
    pass

class Tokenizer:
    """HTML Tokenizer."""

    def __init__(self, char:str, pos:tuple[int,int]) -> None:
        self.char = char
        self.col, self.row = pos
        self.state: str = "data"
        # state to return to after being in put in the character reference state
        self.return_state = ""
        self.token: Token
        self.temp_buff:str
        self.need_to_reconsume: bool = False
    def _emit_token(self, token:Token) -> None:
        # TODO: The state functions should modify self.token directly
        """Emit a token for `self.char` if the param `char` is not specified."""
        tree_constructor(token)
    def _create_token(self, kind:str, **kwargs: str) -> None:
        """Create a token for `self.char` if the param `char` is not specified before emitting it."""
        if "char" not in kwargs:
            self.token = Token(kind=kind, char=self.char)
        elif "char" in kwargs:
            self.token = Token(kind=kind, char=kwargs["char"])

    def _switch_to_char_ref_state(self, return_to:str) -> None: # https://html.spec.whatwg.org/multipage/parsing.html#character-reference-state
        self.return_state = return_to
        self.state = "character reference"

    # For all the tokenizer state specs:
    # refer to https://html.spec.whatwg.org/multipage/parsing.html#tokenization
    def _data_state(self) -> None:
        match self.char:
            case "&":
                self._switch_to_char_ref_state("data")
            case "<":
                self.state = "tag open"
            case "":
                self._emit_token(Token("EOF",""))
            case _:
                self._emit_token(Token("char",self.char))
    def _rcdata_state(self) -> None:
        match self.char:
            case "&":
                self._switch_to_char_ref_state("rcdata")
            case "<":
                self.state = "rcdata lt sign"
            case "":
                self._emit_token(Token("EOF",""))
            case _:
                self._emit_token(Token("char",self.char))
    def _rawtext_state(self) -> None:
        match self.char:
            case "&":
                self._switch_to_char_ref_state("rawtext")
            case "<":
                self.state = "rcdata lt sign"
            case "":
                self._emit_token(Token("EOF",""))
            case _:
                self._emit_token(Token("char",self.char))
    def _script_data_state(self) -> None:
        match self.char:
            case "<":
                self.state = "script data lt sign"
            case "":
                self._emit_token(Token("EOF",""))
            case _:
                self._emit_token(Token("char",self.char))
    def _plaintext_state(self) -> None:
        match self.char:
            case "":
                self._emit_token(Token("EOF",""))
            case _:
                self._emit_token(Token("char",self.char))
    def _tag_open_state(self) -> None:
        match self.char:
            case "!":
                self.state = "markup declaration"
            case "/":
                self.state = "end tag open"
            case "?":
                errormsg: str = "Unexpected question mark instead of tag-name"
                parser_error(self.row,self.col,errormsg)
                self.need_to_reconsume = True
                self.state = "bogus comment"
            case "":
                self._emit_token(Token("char", char="<"))
                self._emit_token(Token("EOF",""))
            case _:
                if self.char.isalpha():
                    self._create_token("start tag", name = "")
                    self.state = "tag name"
                    self.need_to_reconsume = True
                else:
                    errormsg: str = "Invalid first character of tag-name"
                    parser_error(self.row,self.col,errormsg)
                    self._emit_token(Token("char", char="<"))
                    self.state = "data"
                    self.need_to_reconsume = True
    def _end_tag_open_state(self) -> None:
        match self.char:
            case ">":
                errormsg: str = "Missing end tag name"
                parser_error(self.row, self.col, errormsg)
                self.state = "data"
            case "":
                errormsg: str = "EOF before tag name"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token("char", char="<"))
                self._emit_token(Token("char", char="/"))
                self._emit_token(Token("EOF",""))
            case _:
                if self.char.isalpha():
                    self._create_token("start tag", name = "")
                    self.state = "tag name"
                    self.need_to_reconsume = True
                else:
                    errormsg: str = "Invalid first character of tag-name"
                    parser_error(self.row, self.col, errormsg)
    def _tag_name_state(self) -> None:
        match self.char:
            case "\t" | "\n" | "\f" | " ":
                self.state = "before attr name"
            case "/":
                self.state = "self-closing start tag"
            case ">":
                self.state = "data"
                self._emit_token(self.token)
                self.token.tag_name = None
            case "":
                errormsg: str = "EOF in tag"
                parser_error(self.row,self.col,errormsg)
                self._emit_token(Token("EOF",""))
            case _:
                if self.char.isalpha():
                    self.token.tag_name += self.char.lower() # pyright: ignore[reportOperatorIssue]
                else:
                    self.token.tag_name += self.char # pyright: ignore[reportOperatorIssue]
    def _rcdata_lt_sign_state(self) -> None:
        match self.char:
            case "/":
                self._create_token("end tag")
                self.token.tag_name = ""
                self.temp_buff = ""
                self.need_to_reconsume = True
                self.state = "rcdata end tag open"
            case _:
                self._emit_token(Token("char", char="<"))
                self._emit_token(Token("char", char="/"))
                self.need_to_reconsume = True
                self.state = "rcdata"
    def _rcdata_end_tag_name_state(self) -> None:
        def anything_else()->None:
            self._emit_token(Token("char",char="<"))
            self._emit_token(Token("char",char="/"))
            for char in self.temp_buff[::-1]:
                self._emit_token(Token("char",char=char))
        match self.char:
            case "\t" | "\n" | "\f" | " ":
                if is_appropriate_end_tag_token(self.token):
                    self.state = "before attr name"
                else:
                    anything_else()
            case "/":
                if is_appropriate_end_tag_token(self.token):
                    self.state = "self-closing start tag"
                else:
                    anything_else()
            case ">":
                if is_appropriate_end_tag_token(self.token):
                    self.state = "data"
                    self._emit_token(self.token)
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

def parse_html(html: str) -> Element:
    """Parse HTML by line.

    Args:
        html_lines (list[str]): The full html string

    Returns:
        Document: A class representation of the HTML document

    """
    pos: int = 0
    line_no: int = 0
    line_char_no: int = 0
    last: bool = False
    ParserState.pause = False


