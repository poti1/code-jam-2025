from enum import Enum


class MetadataElement(Enum):
    """Represents document metadata elements."""

    head = 0
    title = 1
    base = 2
    link = 3
    meta = 4
    style = 5


class SectionElement(Enum):
    """Represents section elements."""

    body = 0
    article = 1
    section = 2
    nav = 3
    aside = 4
    h1 = 5
    h2 = 6
    h3 = 7
    h4 = 8
    h5 = 9
    h6 = 10
    hgroup = 11
    header = 12
    footer = 13
    address = 14


class GroupingElement(Enum):
    """Represents grouping content elements."""

    p = 0
    hr = 1
    pre = 2
    blockquote = 3
    ol = 4
    ul = 5
    menu = 6
    li = 7
    dl = 8
    dt = 9
    dd = 10
    figure = 11
    figcaption = 12
    main = 13
    search = 14
    div = 15


class TextElements(Enum):
    """Represents text elements."""

    p = 0
    hr = 1
    pre = 2
    blockquote = 3
    ol = 4
    ul = 5
    menu = 6
    li = 7
    dl = 8
    dt = 9
    dd = 10
    figure = 11
    figcaption = 12
    main = 13
    search = 14
    div = 15
