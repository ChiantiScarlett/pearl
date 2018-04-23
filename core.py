class PearlError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "[*] {}".format(self.msg)


class Clip:
    def __init__(self, *args, **kwargs):
        self._data = []

        # If param is empty, then skip
        if not (len(args) + len(kwargs)):
            pass

        else:
            valid_keys = ('title', 'cinfo', 'hinfo', 'start',
                          'end', 'avail_cap', 'total_cap')
            if set(kwargs.keys()) != set(valid_keys):
                raise PearlError(
                    'Invalid input param(s) for the class `Clip`.')

            self._data.append(kwargs)

    def __add__(self, other):
        self._data += other._data
        return self
