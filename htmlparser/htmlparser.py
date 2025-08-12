# Reference: https://html.spec.whatwg.org/


def parse_html(html: str) -> None:
    """Parse HTML string.

    Args:
        html (list[str]): The full html string

    Returns:
        None

    """

def main():
    print('Starting up parser ...')

    parse_html('<div>hello python</div>')


if __name__ == "__main__":
    main()

#   parser_state: ParserState = ParserState()
#   pos: int = 0
#   row: int = 0
#   col: int = 0
#   while pos < len(html):
#       parser_state.need_to_reconsume = False
#       char = html[pos]
#       Tokenizer(char,(row,col),parser_state).next_state()
#       if parser_state.need_to_reconsume:
#           continue
#       pos += 1
#       if char == "\n":
#           row += 1
#           col = 0
#       else:
#           col += 1

