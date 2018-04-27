from pearl.parser import CGV_Parser, LotCi_Parser, CodeParser, Megabox_Parser


def cgv(location=None, date=None, title=None):
    parser = CGV_Parser()
    return parser.search(location, date, filter_key=title)


def lotci(location=None, date=None, title=None):
    parser = LotCi_Parser()
    return parser.search(location, date, filter_key=title)


def megabox(location=None, date=None, title=None):
    parser = Megabox_Parser()
    return parser.search(location, date, filter_key=title)


def parse_code(theater=None, filepath=None):
    parser = CodeParser(theater, filepath)
    parser.parse()
