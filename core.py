import sys
import traceback


class PearlError(Exception):
    def __init__(self, msg):
        self.msg = msg
        # Set custom exception handler for Exception printouts
        sys.excepthook = self.Exception_Handler

    def Exception_Handler(self, exception_type, exception, tb):

        # Error message format:
        err_msg = "\n".join([
                            "[*] PearlError on < {filename}, Line {line} >",
                            "    :: {err_msg}",
                            ])

        # Fabricate traceback message and print
        tb = traceback.extract_tb(tb)[0]
        err_msg = err_msg.format(err_msg=exception,
                                 filename=tb[0],
                                 line=tb[1],
                                 code=tb[3])
        print(err_msg)

    def __str__(self):
        return "{}".format(self.msg)


class Clip:
    def __init__(self, *args, **kwargs):
        self._data = []
        self._is_addable = True

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
        if not (self._is_addable and other._is_addable):
            err = 'Cannot add Clips class after the `sort` method.'
            raise PearlError(err)

        self._data += other._data
        return self

    def to_json(self):
        pass

    def sort(self):
        """
        Group self._data into titles, sort them in time ascending order
        """

        # Create dictionary and initialize keys
        movies = {}
        titles = set(map(lambda x: x['title'], self._data))
        for title in titles:
            movies[title] = []

        # Add items
        for movie in self._data:
            movies[movie.pop('title')].append(movie)

        # Sort each movie by start time
        for movie in movies:
            schedule = movies[movie]
            schedule = sorted(schedule, key=lambda k: k['start'])
            movies[movie] = schedule

        # Diable __add__ method with other Clip classes
        self._is_addable = False

        # Save data
        self._data = movies
