from pearl.parser import CGV_Parser, LotCi_Parser, Megabox_Parser, CodeParser
from pearl.parser import get_detail as _get_detail


def cgv(location, date=None, title=None):
    parser = CGV_Parser()
    return parser.search(location, date, filter_key=title)


def lotci(location, date=None, title=None):
    parser = LotCi_Parser()
    return parser.search(location, date, filter_key=title)


def megabox(location, date=None, title=None):
    parser = Megabox_Parser()
    return parser.search(location, date, filter_key=title)


def parse_code(theater, filepath):
    parser = CodeParser(theater, filepath)
    parser.parse()


get_detail = _get_detail
