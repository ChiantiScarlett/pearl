from pearl.parser import CGV_Parser, LotCi_Parser, CodeParser


def cgv(location=None, date=None, filter_key=None):
    parser = CGV_Parser()
    return parser.search(location, date, filter_key)


def lotci(location=None, date=None, filter_key=None):
    parser = LotCi_Parser()
    return parser.search(location, date, filter_key)


def parse_code(theater=None, filepath=None):
    parser = CodeParser(theater, filepath)
    parser.parse()
