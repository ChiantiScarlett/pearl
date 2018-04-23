from datetime import datetime, timedelta
import json
from urllib.request import urlopen, URLError
from bs4 import BeautifulSoup


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


class PearlError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "[*] {}".format(self.msg)


class Parser:
    def __init__(self, location_table, available_date_range):
        self._location_table = location_table
        self._available_date_range = available_date_range

    def search(self, location, date=None, filter_key=None):
        return self.parse(*self.assure_validity(location, date, filter_key))

    def parse(self, location, date, filter_key):
        """
        Override from child class
        """

        pass

    def assure_validity(self, location, date, filter_key):
        """
        Description:
            Method to check the validity of the parameters.
        Returns:
            if they are all valid, return (location, date, filter_key)
            else, return False
        """

        # Check if locations are valid
        if self._location_table is None or type(self._location_table) != dict:
            err = 'self._location_table is invalid.'
            raise PearlError(err)

        elif location not in self._location_table.keys():
            err = '{} is not a valid location name.'.format(self.location)
            raise PearlError(err)

        # Checking date validity:
        if date is None:
            date = datetime.now().strftime("%d")
        else:
            # Check if it is a valid date figure
            try:
                date = int(date)
                if not 1 <= date <= 31:
                    raise ValueError

            except ValueError:
                err = 'Invalid date `{}`.'.format(date)
                raise PearlError(err)

            # Check if the timetable for the date is available
            possible_dates = map(lambda x:
                                 (datetime.now() +
                                  timedelta(days=x)).strftime("%d"),
                                 range(self._available_date_range))
            date = '%.2d' % date

            if date not in list(possible_dates):
                err_msg = \
                    'The timetable for the date `{}` is '.format(date) + \
                    ' not available at this moment.'
                return self.raise_error(err_msg)

        return (location, date, filter_key)


class CGV_Parser(Parser):
    def __init__(self):

        location_table = json.loads(open('pearl/code_cgv.json').read())[0]
        available_date_range = 6

        super().__init__(location_table=location_table,
                         available_date_range=available_date_range)

    def parse(self, location, date, filter_key):
        print(location, date, filter_key)
        """
        Description:
            Overriding parent class method :: Parsing CGV Data
        """

        # Using bs4, parse necessary data (dirty parse)
        today = int(datetime.now().strftime("%d"))
        if int(date) < today:
            date_arg = datetime.now() + timedelta(months=1)
        else:
            date_arg = datetime.now()

        date_arg = date_arg.strftime('%Y%m') + date
        url = \
            'http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?' +\
            '{}&date={}'.format(
                self._location_table[location], date_arg)
        try:
            src = BeautifulSoup(
                urlopen(url).read().decode(), 'html.parser')
        except URLError:
            err_msg = 'Network Error : Please check your network status.'
            return self.raise_error(err_msg)

        src = src.find_all('div', {'class': 'col-times'})

        clip = Clip()

        for mv in src:
            TITLE = mv.find_all('strong')[0].text.strip()
            # For each hall, get all info of movies
            for hall in mv.find_all('div', {'class': 'type-hall'}):
                # get hall information
                HALL_INFO = hall.find_all('li')[0].text.strip() + " " + \
                    hall.find_all('li')[1].text.strip()

                TOTAL_SEATS = hall.find_all('li')[2].text[-5:-1].strip()
                # append each cinema info to CGV_Timetable class
                for t in hall.find_all('a'):
                    st = t['data-playstarttime']
                    et = t['data-playendtime']

                    clip += Clip(title=TITLE,
                                 cinfo='CGV ' + location,
                                 hinfo=HALL_INFO,
                                 avail_cap=int("%.3d" %
                                               int(t['data-seatremaincnt'])),
                                 total_cap=int(TOTAL_SEATS),
                                 start=st[:2] + ':' + st[2:],
                                 end=et[:2] + ':' + et[2:]
                                 )

        return clip
