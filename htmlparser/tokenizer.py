from _types import Attribute, ParserState, Token

from treeconstructor import tree_constructor


def parser_error(row: int, col: int, message: str) -> None:
    """Print error messages for debugging purposes."""
    message = f"{message} at line:{row}, col:{col}"
    print(message)


last_start_tag_emitted: Token | None


def is_appropriate_end_tag_token(
    end_tag_token: Token,
    last_start_tag_emitted: Token | None,
) -> bool:  # https://html.spec.whatwg.org/multipage/parsing.html#appropriate-end-tag-token
    """Find the last start-tag if any token whose name matches the end-tag token name.

    Args:
        end_tag_token (Token): token to find a start tag for
        last_start_tag_emitted (Token | None): The last start tag emitted by the tokenizer

    Returns:
        bool

    """
    if last_start_tag_emitted is not None:
        return end_tag_token.tag_name == last_start_tag_emitted.tag_name
    return False


class Tokenizer:
    """HTML Tokenizer."""

    def __init__(self, char: str, pos: tuple[int, int], parser_state: ParserState) -> None:
        self.char = char
        self.row, self.col = pos
        self.parser_state = parser_state

    def _emit_token(self, token: Token) -> None:
        """Emit a token to the tree constructor."""
        tree_constructor(token)

    def _emit_token_from_parser_state(self, token: Token) -> None:
        """Emit a token from ParserState to the tree constructor."""
        tree_constructor(token)
        self.parser_state.token = None

    def _create_token(self, token: Token) -> None:
        """Create a token."""
        self.parser_state.token = token

    def _create_attr(self, attr: Attribute) -> None:
        """Create a new attribute for the current token in ParserState."""
        # start a new attr list if one doesn't exist and create an empty name, value pair
        if self.parser_state.token.attrs is None:
            self.parser_state.token.curr_attr = 0
            self.parser_state.token.attrs = [attr]
        # otherwise append a new one:
        else:
            self.parser_state.token.attrs.append(attr)
            self.parser_state.token.curr_attr += 1

    def _append_to_curr_attr_name(self, char: str) -> None:
        curr_attr: int = self.parser_state.token.curr_attr
        self.parser_state.token.attrs[curr_attr].name += char

    def _append_to_curr_attr_val(self, char: str) -> None:
        curr_attr: int = self.parser_state.token.curr_attr
        self.parser_state.token.attrs[curr_attr].value += char

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
                self._emit_token(Token(kind="EOF"))
            case _:
                self._emit_token(Token(kind="char", char=self.char))

    def _rcdata_state(self) -> None:
        match self.char:
            case "&":
                self._switch_to_char_ref_state("rcdata")
            case "<":
                self.parser_state.state = "rcdata lt sign"
            case "":
                self._emit_token(Token(kind="EOF"))
            case _:
                self._emit_token(Token(kind="char", char=self.char))

    def _rawtext_state(self) -> None:
        match self.char:
            case "&":
                self._switch_to_char_ref_state("rawtext")
            case "<":
                self.parser_state.state = "rcdata lt sign"
            case "":
                self._emit_token(Token(kind="EOF"))
            case _:
                self._emit_token(Token(kind="char", char=self.char))

    def _script_data_state(self) -> None:
        match self.char:
            case "<":
                self.parser_state.state = "script data lt sign"
            case "":
                self._emit_token(Token(kind="EOF"))
            case _:
                self._emit_token(Token(kind="char", char=self.char))

    def _plaintext_state(self) -> None:
        match self.char:
            case "":
                self._emit_token(Token(kind="EOF"))
            case _:
                self._emit_token(Token(kind="char", char=self.char))

    def _tag_open_state(self) -> None:
        match self.char:
            case "!":
                # (state not implemented yet)
                pass
            case "/":
                self.parser_state.state = "end tag open"
            case "?":
                errormsg: str = "Unexpected question mark instead of tag-name"
                parser_error(self.row, self.col, errormsg)
                # (state not implemented yet)
            case "":
                self._emit_token(Token(kind="char", char="<"))
                self._emit_token(Token(kind="EOF"))
            case _:
                if self.char.isalpha():
                    self._create_token(Token("start tag", tag_name=""))
                    self.parser_state.state = "tag name"
                    self.parser_state.need_to_reconsume = True
                else:
                    errormsg: str = "Invalid first character of tag-name"
                    parser_error(self.row, self.col, errormsg)
                    self._emit_token(Token(kind="char", char="<"))
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
                self._emit_token(Token(kind="char", char="<"))
                self._emit_token(Token(kind="char", char="/"))
                self._emit_token(Token(kind="EOF"))
            case _:
                if self.char.isalpha():
                    self._create_token(Token(kind="end tag", tag_name=""))
                    self.parser_state.need_to_reconsume = True
                    self.parser_state.state = "tag name"
                else:
                    errormsg: str = "Invalid first character of tag-name"
                    self._create_token(Token(kind="", data=""))
                    self.parser_state.need_to_reconsume = True
                    parser_error(self.row, self.col, errormsg)

    def _tag_name_state(self) -> None:
        match self.char:
            case "\t" | "\n" | "\f" | " ":
                self.parser_state.state = "before attr name"
            case "/":
                self.parser_state.state = "self-closing start tag"
            case ">":
                self.parser_state.state = "data"
                self._emit_token_from_parser_state(self.parser_state.token)
            case "":
                errormsg: str = "EOF in tag"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token(kind="EOF"))
            case _:
                if self.char.isalpha():
                    self.parser_state.token.tag_name += self.char.lower()
                else:
                    self.parser_state.token.tag_name += self.char

    def _rcdata_lt_sign_state(self) -> None:
        match self.char:
            case "/":
                self._create_token("end tag")
                self.parser_state.token.tag_name = ""
                self.parser_state.temp_buff = ""
                self.parser_state.need_to_reconsume = True
                self.parser_state.state = "rcdata end tag open"
            case _:
                self._emit_token(Token(kind="char", char="<"))
                self._emit_token(Token(kind="char", char="/"))
                self.parser_state.need_to_reconsume = True
                self.parser_state.state = "rcdata"

    def _rcdata_end_tag_name_state(self) -> None:
        def anything_else() -> None:
            self._emit_token(Token(kind="char", char="<"))
            self._emit_token(Token(kind="char", char="/"))
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
                    self._emit_token_from_parser_state(self.parser_state.token)
                else:
                    anything_else()
            case _:
                anything_else()

    def _before_attr_name_state(self) -> None:
        match self.char:
            case "\t" | "\n" | "\f" | " ":
                pass
            case "/" | ">" | "":
                self.parser_state.state = "after attr name"
                self.parser_state.need_to_reconsume = True
            case "=":
                errormsg: str = "Unexpected equals sign before attribute name"
                parser_error(self.row, self.col, errormsg)
                self._create_attr(Attribute(name=self.char, value=""))
                self.parser_state.state = "attr name"
            case _:
                self._create_attr(Attribute(name="", value=""))
                self.parser_state.need_to_reconsume = True
                self.parser_state.state = "attr name"

    def _attr_name_state(self) -> None:
        match self.char:
            case "\t" | "\n" | "\f" | " " | "/" | ">" | "":
                self.parser_state.need_to_reconsume = True
                self.parser_state.state = "after attr name"
            case "=":
                self.parser_state.state = "before attr value"
            case '"' | "'" | "<":
                errormsg: str = "Unexpected character in attribute name"
                parser_error(self.row, self.col, errormsg)
                self._append_to_curr_attr_name(self.char)
            case _:
                if self.char.isalpha():
                    self._append_to_curr_attr_name(self.char.lower())
                else:
                    self._append_to_curr_attr_name(self.char)

    def _after_attr_name_state(self) -> None:
        match self.char:
            case "\t" | "\n" | "\f" | " ":
                pass
            case "/":
                self.parser_state.state = "self-closing start tag"
            case "=":
                self.parser_state.state = "before attr value"
            case ">":
                self.parser_state.state = "data"
                self._emit_token_from_parser_state(self.parser_state.token)
            case "":
                errormsg: str = "EOF in tag"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token(kind="EOF"))
            case _:
                self._create_attr(Attribute(name="", value=""))
                self.parser_state.state = "attr name"

    def _before_attr_value_state(self) -> None:
        match self.char:
            case "\t" | "\n" | "\f" | " ":
                pass
            case '"':
                self.parser_state.state = "attr value (double-quoted)"
            case "'":
                self.parser_state.state = "attr value (single-quoted)"
            case ">":
                errormsg: str = "Missing attribute value"
                parser_error(self.row, self.col, errormsg)
                self.parser_state.state = "data"
                self._emit_token_from_parser_state(self.parser_state.token)
            case _:
                self.parser_state.need_to_reconsume = True
                self.parser_state.state = "attr value (unquoted)"

    def _attr_value_double_quoted_state(self) -> None:
        match self.char:
            case '"':
                self.parser_state.state = "after attr value (quoted)"
            case "&":
                self._switch_to_char_ref_state(return_to="attr value (double-quoted)")
            case "":
                errormsg: str = "EOF in tag"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token(kind="EOF"))
            case _:
                self._append_to_curr_attr_val(self.char)

    def _attr_value_single_quoted_state(self) -> None:
        match self.char:
            case '"':
                self.parser_state.state = "after attr value (quoted)"
            case "&":
                self._switch_to_char_ref_state(return_to="attr value (single-quoted)")
            case "":
                errormsg: str = "EOF in tag"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token(kind="EOF"))
            case _:
                self._append_to_curr_attr_val(self.char)

    def _attr_value_unquoted_state(self) -> None:
        match self.char:
            case "\t" | "\n" | "\f" | " ":
                self.parser_state.state = "before attr name"
            case "&":
                self._switch_to_char_ref_state(return_to="attr value (unquoted)")
            case ">":
                self.parser_state.state = "data"
                self._emit_token_from_parser_state(self.parser_state.token)
            case '"' | '"' | "<" | "=" | "`":
                errormsg: str = "Unexpected character in unquoted attribute value"
                parser_error(self.row, self.col, errormsg)
                self._append_to_curr_attr_val(self.char)
            case "":
                errormsg: str = "EOF in tag"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token("EOF"))
            case _:
                self._append_to_curr_attr_val(self.char)

    def _after_attr_value_quoted_state(self) -> None:
        match self.char:
            case "\t" | "\n" | "\f" | " ":
                self.parser_state.state = "before attr name"
            case "/":
                self.parser_state.state = "self-closing start tag"
            case ">":
                self.parser_state.state = "data"
                self._emit_token_from_parser_state(self.parser_state.token)
            case "":
                errormsg: str = "EOF in tag"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token("EOF"))
            case _:
                errormsg: str = "Missing whitespace between attributes"
                parser_error(self.row, self.col, errormsg)
                self.parser_state.need_to_reconsume = True
                self.parser_state.state = "before attr name"

    def _self_closing_start_tag_state(self) -> None:
        match self.char:
            case ">":
                self.parser_state.token.self_closing = True
                self.parser_state.state = "data"
                self._emit_token_from_parser_state(self.parser_state.token)
            case "":
                errormsg: str = "EOF in tag"
                parser_error(self.row, self.col, errormsg)
                self._emit_token(Token("EOF"))
            case _:
                errormsg: str = "Unexpected solidus in tag"
                parser_error(self.row, self.col, errormsg)
                self.parser_state.need_to_reconsume = True
                self.parser_state.state = "before attr name"

    def _character_reference_state(self) -> None:
        self.parser_state.state = "data"
        self.parser_state.need_to_reconsume = True
        self.parser_state.state = self.parser_state.return_state
        self.parser_state.return_state = ""

    def next_state(self) -> None:  # noqa: C901, PLR0912
        """Determine the next state."""
        match self.parser_state.state:
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
            case "rcdata lt sign":
                self._rcdata_lt_sign_state()
            case "rcdata end tag name":
                self._rcdata_end_tag_name_state()
            case "before attr name":
                self._before_attr_name_state()
            case "attr name":
                self._attr_name_state()
            case "after attr name":
                self._after_attr_name_state()
            case "before attr value":
                self._before_attr_value_state()
            case "attr value (double-quoted)":
                self._attr_value_double_quoted_state()
            case "attr value (single-quoted)":
                self._attr_value_single_quoted_state()
            case "attr value (unquoted)":
                self._attr_value_unquoted_state()
            case "after attr value (quoted)":
                self._after_attr_value_quoted_state()
            case "self-closing start tag":
                self._self_closing_start_tag_state()
            case "character reference":
                self._character_reference_state()
            case _:
                pass
