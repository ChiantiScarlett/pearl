from pearl.parser import CGV_Parser


def cgv(location=None, date=None, filter_key=None):
    parser = CGV_Parser()
    return parser.search(location, date, filter_key)
