from pearl.core import PearlError, Clip
import json
import re
from urllib.request import urlopen, URLError, quote
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os


class Parser:
    def __init__(self, location_table, available_date_range):
        self._location_table = location_table
        self._available_date_range = available_date_range

    def search(self, location, date=None, filter_key=None):
        return self.parse(*self.assure_validity(location, date, filter_key))

    def title_not_valid(self, title, filter_key):
        if (filter_key or '') not in title:
            return True
        return False

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
            date = datetime.now()
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

            # Variable `date` is 2-digit day.
            date = '%.2d' % date

            if date not in list(possible_dates):
                err_msg = \
                    'The timetable for the date `{}` is '.format(date) + \
                    ' not available at this moment.'
                return self.raise_error(err_msg)

            today = datetime.now()
            # Check if the date is on next month.
            if int(today.strftime('%d')) > int(date):
                today += timedelta(months=1)

            date = datetime.strptime(today.strftime('%Y%m') + date, '%Y%m%d')

        return (location, date, filter_key)


class CGV_Parser(Parser):
    def __init__(self):

        location_table = json.loads(open('pearl/code_cgv.json').read())[0]
        available_date_range = 6

        super().__init__(location_table=location_table,
                         available_date_range=available_date_range)

    def parse(self, location, date, filter_key):
        """
        Description:
            Overriding parent class method :: Parsing CGV Data
        """

        # Using bs4, parse necessary data (dirty parse)
        url = \
            'http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?' +\
            '{}&date={}'.format(
                self._location_table[location], date.strftime("%Y%m%d"))
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
            # See if the movie title mathces title filter key.
            # If not, do not include.
            if self.title_not_valid(TITLE, filter_key):
                continue

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


class LotCi_Parser(Parser):
    def __init__(self):

        location_table = json.loads(open('pearl/code_lotci.json').read())[0]
        available_date_range = 6

        super().__init__(location_table=location_table,
                         available_date_range=available_date_range)

    def parse(self, location, date, filter_key):
        """
        Description:
            Overriding parent class method :: Parsing CGV Data
        """
        url = 'https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx'
        param_list = {
            'channelType': 'MW',
            'osType': '',
            'osVersion': '',
            'MethodName': 'GetPlaySequence',
            'playDate': date.strftime("%Y-%m-%d"),
            'representationMovieCode': '',
            'cinemaID': self._location_table[location]
        }
        # Adding payload and parse json
        data = urlencode({'ParamList': json.dumps(param_list)}).encode('utf-8')
        src = urlopen(url, data=data).read().decode('utf-8')
        src = json.loads(src)

        clip = Clip()

        t_table = {}  # For saving movie Title based on its ID code
        for movie in src['PlaySeqsHeader']['Items']:
            t_table[movie['RepresentationMovieCode']] = movie['MovieNameKR']

        for movie in src['PlaySeqs']['Items']:
            TITLE = t_table[movie['RepresentationMovieCode']]

            # See if the movie title mathces title filter key.
            # If not, do not include.
            if self.title_not_valid(TITLE, filter_key):
                continue

            # Check 4D
            if movie['FourDTypeCode'] == 200:
                hall_info = '4D ' + movie['ScreenNameKR']
            # Check 3D
            elif movie['FilmCode'] == 300:
                hall_info = '3D ' + movie['ScreenNameKR']
            # Else 2D
            else:
                hall_info = '2D ' + movie['ScreenNameKR']

            # Else, append clip
            clip += Clip(title=TITLE,
                         cinfo='롯데시네마 ' + movie['CinemaNameKR'],
                         hinfo=hall_info,
                         avail_cap=(movie['BookingSeatCount']),
                         total_cap=movie['TotalSeatCount'],
                         start=movie['StartTime'],
                         end=movie['EndTime']
                         )

        return clip


class Megabox_Parser:
    def __init__(self):

        location_table = json.loads(open('pearl/code_megabox.json').read())[0]
        available_date_range = 6

        super().__init__(location_table=location_table,
                         available_date_range=available_date_range)

    def parse(self, location, date, filter_key):
        """
        Description:
            Overriding parent class method :: Parsing CGV Data
        """
        clip = Clip()
        return clip


class CodeParser:
    _action = None
    _theater = None
    _filepath = None

    def __init__(self, theater, filepath):

        opts = {
            'cgv': self.get_cgv_code,
            'lotci': self.get_lotci_code,
            'megabox': self.get_megabox_code
        }

        # If theater name is invalid, raise error
        if str(theater).lower() not in opts.keys():
            err = '`{}` is not a valid movie theater name.'
            raise PearlError(err.format(theater))

        # If filepath is invalid, raise error
        try:
            with open(filepath, 'w') as fp:
                fp.write('')
            os.remove(filepath)

        except Exception:
            raise PearlError('Failed to create `{}`.'.format(filepath))

        self._theater = theater
        self._filepath = filepath

        self.parse = opts[str(theater)]

    def get_cgv_code(self):
        # get CGV JSON data
        src = urlopen(
            "http://www.cgv.co.kr/theaters/").read().decode('utf-8')
        START_KEY = re.escape('[{"AreaTheaterDetailList":')
        END_KEY = re.escape(';')
        src = re.findall(START_KEY + "[\s\S]+?" + END_KEY, src)[0][:-1]
        src = json.loads(src)

        codes = {}
        for area in src:
            for item in area['AreaTheaterDetailList']:
                # compare the keyword with names
                name = item['TheaterName']
                name = name[3:] if name.startswith("CGV") else name

                codes[name] = 'areacode={}&theatercode={}'.format(
                    quote(area['RegionCode']), quote(item['TheaterCode']))

        with open(self._filepath, 'w', encoding='utf-8') as fp:
            json.dump([codes], fp, ensure_ascii=False)

        print('[*] Successfully created file `{}`.'.format(self._filepath))

    def get_lotci_code(self):
        url = 'https://www.lottecinema.co.kr/LCWS/Cinema/CinemaData.aspx'
        param_list = {
            'channelType': 'MW',
            'osType': '',
            'osVersion': '',
            'MethodName': 'GetCinemaItems'
        }

        data = urlencode({'ParamList': json.dumps(param_list)}).encode('utf-8')
        src = urlopen(url, data=data).read().decode('utf-8')
        src = json.loads(src)

        codes = {}

        for theater in src['Cinemas']['Items']:
            # Create cinema code
            cinema_code = '{}|{}|{}'.format(
                theater['DivisionCode'],
                theater['SortSequence'],
                theater['CinemaID']
            )
            # Remove parenthesis in theater names
            name = re.sub(
                re.escape('(') + "[\s\S]+?" + re.escape(')'),
                '',
                theater['CinemaNameKR'])
            # Append. If there are identical names, keep the original.
            if name in codes.keys():
                pass
            else:
                codes[name] = cinema_code
        # Save file into json format.
        with open(self._filepath, 'w', encoding='utf-8') as fp:
            json.dump([codes], fp, ensure_ascii=False)

        print('[*] Successfully created file `{}`.'.format(self._filepath))

    def get_megabox_code(self):
        pass
