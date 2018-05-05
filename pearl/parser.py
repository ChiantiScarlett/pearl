from pearl.core import PearlError, Clip
import json
import re
from urllib.request import urlopen, URLError, quote
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup as Soup
from datetime import datetime, timedelta
import os


class Parser:
    def __init__(self, location_table, available_date_range):
        """
        Description:
            This class is fundamental basis for other parser modules,
            including CGV_Parser, LotCi_Parser, and Megabox_Parser.

            It basically has 3 stages, which are the followings:

            1. User calls self.search()
            2. `self.search()` judges the correctness of arguments by using
               `self.assure_validity()`.
            3. If the arguments are appropriate, this class then uses
               `self.parse()`, which literally parses movie data from each
               websites.

            `self.parse()` is overriden by the child classes, but other than
            that, CGV_Parser, LotCi_Parser, and Megabox_Parser shares the
            same tools.

        Arguments:
            [Argument]            | [Type]  | [Description]
            ------------------------------------------------------------------
            location_table        | (dict)  | contains movie codes
            available_date_range  | (int)   | set date limit for the data

        Note:
            i)   Although `location_table` reads <dict> type data, all other
                 parsers read file that is already stored in here. If you want
                 to debug or update the location_table, please take full
                 advantage of the class `CodeParser`, which is defined on
                 bottom of this page.

            ii)  Argument `location_table` is constructed in the following
                 format:

                    {NAME_OF_LOATION : UNIQUE_ID_OF_LOCATION}

                    e.g.
                    CGV     : {"부천역" : "areacode=02&theatercode=0194", ... }
                    LotCi   : {"시화" : "1|21|3016", ... }
                    Megabox : {"안동" : "7601", ... }

            iii) Currently `available_date_range` is set to 6 for every parsing
                 module. If the user selects date that is longer than 6 days,
                 the class will raise PearlError.

            iv)  Please keep in mind that all of the `self.parser` methods hold
                 nasty fabrication - meaning that any changes on the HTML might
                 invoke fatal error.
        """
        self._location_table = location_table
        self._available_date_range = available_date_range

    def search(self, location, date=None, filter_key=None):
        """
        Description:
            Prime method :: This method receive arguments, pass to other
            existing methods in this class, and returns data


        """
        return self.parse(*self.assure_validity(location, date, filter_key))

    def title_not_valid(self, title, filter_key):
        """
        Description:
            This method simply checks whether the input parameter `title`
            is valid or not.

        Returns:
            i)  if valid: True
            ii) if not:   False
        """
        if (filter_key or '') not in title:
            return True

        return False

    def parse(self, location, date, filter_key):
        """
        Description:
            The arguments are identical, but each child class will override
            with its own way of parsing movie theater data.

        Arguments:
            [Argument]           | [Type] | [Description]           | [Example]
            ------------------------------------------------------------------
            locations            | (str)  | Cinema location(s)      | '북수원'
            date      (optional) | (int)  | day of the date (1~31)  | 8
            title     (optional) | (str)  | filter out movie titles | '플레이어'

        Note:
            i)  Default value for the argument `date` is the day of
                today's date.
            ii) Movie data parsed from LotCi_Parser do not contain `rate` data.

        Returns:
            <Clip> Object

            <Clip>.data is a list type variable that contains movie timelines
            in following format:

                self.list = [
                    {
                        'rate': '12',
                        'timeline': [{
                            'avail_cap': 216,
                            'cinfo': 'CGV 수원',
                            'end': '24:09',
                            'hinfo': '2D 8관',
                            'start': '21:30',
                            'total_cap': 250
                        },{
                            'avail_cap': 235,
                            'cinfo': 'CGV 수원',
                            'end': '27:09',
                            'hinfo': '2D 8관',
                            'start': '24:30',
                            'total_cap': 250
                        }],
                        'title': '어벤져스: 인피니티 워'
                    }]
        """
        pass

    def assure_validity(self, location, date, filter_key):
        """
        Description:
            This method checks the validity of parameters.

        Returns:
            i)  if they are all valid:  (location, date, filter_key)
            ii) otherwise:              False
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
        """
        Description:
            This module is a child class. Please refer to the parent module
            for specific details.
        """

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
            src = Soup(urlopen(url).read().decode(), 'html.parser')
        except URLError:
            err = 'Cannot parse CGV data. Please check your network status.'
            raise PearlError(err)

        src = src.find_all('div', {'class': 'col-times'})

        # Initialize empty clip
        clip = Clip()

        # Fabricate
        for mv in src:
            TITLE = mv.find_all('strong')[0].text.strip()
            # See if the movie title mathces title filter key.
            # If not, do not include.
            if self.title_not_valid(TITLE, filter_key):
                continue

            # Rate Table
            r_table = {'청소': '19', '15': '15', '12': '12', '전체': 'ALL'}

            # For each hall, get all info of movies
            for hall in mv.find_all('div', {'class': 'type-hall'}):
                # get hall information
                HALL_INFO = hall.find_all('li')[0].text.strip() + " " + \
                    hall.find_all('li')[1].text.strip()

                TOTAL_SEATS = hall.find_all('li')[2].text[-5:-1].strip()

                # Parse Rate
                RATE = mv.find_all(
                    'span', {'class': 'ico-grade'})[0].text.strip()[:2]
                RATE = r_table[RATE] if RATE in r_table.keys() else RATE

                # append each cinema info to CGV_Timetable class
                for t in hall.find_all('a'):
                    try:
                        st = t['data-playstarttime']
                        et = t['data-playendtime']
                    except Exception:
                        # If the item does not have data-playstarttime, skip.
                        continue

                    clip += Clip(title=TITLE,
                                 cinfo='CGV ' + location,
                                 hinfo=HALL_INFO,
                                 avail_cap=int("%.3d" %
                                               int(t['data-seatremaincnt'])),
                                 total_cap=int(TOTAL_SEATS),
                                 start=st[:2] + ':' + st[2:],
                                 end=et[:2] + ':' + et[2:],
                                 rate=RATE
                                 )

        return clip


class LotCi_Parser(Parser):
    def __init__(self):
        """
        Description:
            This module is a child class. Please refer to the parent module
            for specific details.
        """

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
        try:
            src = urlopen(url, data=data).read().decode('utf-8')
            src = json.loads(src)
        except URLError:
            err = 'Cannot parse LotCi data. Please check your network status.'
            raise PearlError(err)

        # Initialize empty clip
        clip = Clip()

        # Fabricate URL data
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
                         end=movie['EndTime'],
                         rate=None
                         )

        return clip


class Megabox_Parser(Parser):
    def __init__(self):
        """
        Description:
            This module is a child class. Please refer to the parent module
            for specific details.
        """

        location_table = json.loads(open('pearl/code_megabox.json').read())[0]
        available_date_range = 6

        super().__init__(location_table=location_table,
                         available_date_range=available_date_range)

    def parse(self, location, date, filter_key):
        """
        Description:
            Overriding parent class method :: Parsing CGV Data
        """
        import requests
        from bs4 import BeautifulSoup as Soup

        # Get POST Request
        url = 'http://www.megabox.co.kr/pages/theater/Theater_Schedule.jsp'

        try:
            req = requests.post(url, data={
                'count': (date - datetime.today()).days + 1,
                'cinema': self._location_table[location]})

            src = Soup(req.text, 'html.parser')
            src = src.find('table', {'class': 'movie_time_table'})
        except URLError:
            err = 'Cannot parse Megabox data. ' + \
                  'Please check your network status.'
            raise PearlError(err)

        # Initialize empty clip
        clip = Clip()

        # title is getting overridden, due to its complex <tr> structure
        title = None

        # Fabricate
        for movie in src.find_all('tr', {'class': 'lineheight_80'}):
            for mv in movie.find_all('th', {'id': 'th_theaterschedule_title'}):
                if mv.find('a') is not None:
                    title = mv.find('a').text

            hall_name = movie.find('th', {'id': 'th_theaterschedule_room'})
            hinfo = hall_name.find('div').text

            for item in movie.find_all('div', {'class': 'cinema_time'}):
                # Get hall info

                # If the time is all sold out, skip
                if 'done' in item.attrs['class']:
                    continue

                # Parse necessary data
                time_data = item.find('span', {'class': 'hover_time'}).text
                start, end = time_data.split('~')

                seat_data = item.find('span', {'class': 'seat'}).text
                avail_cap, total_cap = map(int, seat_data.split('/'))

                # mtype = item.find('span', {'class': 'type'}).text

                clip += Clip(title=title,
                             cinfo='메가박스 ' + location,
                             hinfo=hinfo,
                             avail_cap=avail_cap,
                             total_cap=total_cap,
                             start=start,
                             end=end,
                             rate=None
                             )

        return clip


class CodeParser:
    def __init__(self, theater, filename):
        """
        Description:
            This class creates location_table, which is one of the prime
            resources that is used for parsing movie data.

        Arguments:
            [Argument]  | [Type] | [Description]
            ------------------------------------------------------------------
            theater     | (str)  | theater that you want to parse data from
            filename    | (str)  | filename that you want to save your data

        Note:
            i)   Argument `theater` only accepts 'cgv', 'lotci', or 'megabox'.
            ii)  Make sure you set the extension to `.json` for the `filename`.

        Returns:
            None

            Instead, it creates file to certain directory, in accordance with
            pre-defined filename.
        """

        opts = {
            'cgv': self.get_cgv_code,
            'lotci': self.get_lotci_code,
            'megabox': self.get_megabox_code
        }

        # If theater name is invalid, raise error
        if str(theater).lower() not in opts.keys():
            err = '`{}` is not a valid movie theater name.'
            raise PearlError(err.format(theater))

        # If filename is invalid, raise error
        try:
            with open(filename, 'w') as fp:
                fp.write('')
            os.remove(filename)

        except Exception:
            raise PearlError('Failed to create `{}`.'.format(filename))

        # Create variables for global usage
        self._theater = theater
        self._filename = filename

        # Set `self.parse` method based on `theater` argument
        self.parse = opts[str(theater)]

    def get_cgv_code(self):
        """
        Description:
            This method parses CGV theater code data, and creates
            JSON type file.
        """
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

        with open(self._filename, 'w', encoding='utf-8') as fp:
            json.dump([codes], fp, ensure_ascii=False)

        print('[*] Successfully created file `{}`.'.format(self._filename))

    def get_lotci_code(self):
        """
        Description:
            This method parses Lotte Cinema theater code data, and creates
            JSON type file.
        """
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
        with open(self._filename, 'w', encoding='utf-8') as fp:
            json.dump([codes], fp, ensure_ascii=False)

        print('[*] Successfully created file `{}`.'.format(self._filename))

    def get_megabox_code(self):
        """
        Description:
            This method parses Megabox code data, and creates
            JSON type file.
        """

        # Get region code
        areaGroupCodes = []
        soup = urlopen('http://www.megabox.co.kr/?menuId=theater')
        soup = Soup(soup.read().decode('utf-8'), 'html.parser')

        ul = soup.find('ul', {'class': 'menu'})
        for li in ul.find_all('li')[1:]:
            code = li.a['onclick'].split("'")[1]
            areaGroupCodes.append(code)

        # Dict to return
        megabox_code = {}

        # send POST Request and get response
        for areacode in areaGroupCodes:
            url = 'http://www.megabox.co.kr/DataProvider'
            req = requests.post(url, data={
                '_command': 'Cinema.getCinemasInRegion',
                'siteCode': 36,
                'areaGroupCode': areacode,
                'reservationYn': 'N'})

            data = json.loads(req.text)['cinemaList']

            for item in data:
                # Remove parenthesis in theater names
                location_name = re.sub(
                    re.escape('(') + "[\s\S]+?" + re.escape(')'),
                    '',
                    item['cinemaName'])

                # Append
                megabox_code[location_name] = item['cinemaCode']

        with open(self._filename, 'w', encoding='utf-8') as fp:
            json.dump([megabox_code], fp, ensure_ascii=False)

        print('[*] Successfully created file `{}`.'.format(self._filename))


def get_detail(items=100, start_year=None, end_year=None):
    """
    Description:
        This function is used for getting detail information of a movie.
        It uses open API from KOBIS(영화진흥위원회, Korean Film Council),
        according to the arguments.

    Arguments:
        [Argument]            | [Type] | [Description]
        ------------------------------------------------------------------
        items      (optional) | (str)  | maximum number of items
        start_year (optional) | (int)  | filter specific start year
        end_year   (optional) | (int)  | filter specific end year

    Note:
        i)   Argument `start_year` and `end_year` should be 4-digit integer.
        ii)  Please keep in mind this open API is kind of slow, compared to
             other paser modules.
        iii) Since I had no other choice, I used API key with plain text here.
             But if you are trying to get heavy data out of it, I strongly
             recommend you to get your own key and read the full documents.
             You can get free keys and more detailed documents from the below.

             http://www.kobis.or.kr/kobisopenapi

    Returns:
        <dict>

        Returns data with the following format:
        e.g.
        {
            '기억의 밤': {
                'directors': '장항준',
                'genre': '미스터리,스릴러',
                'nationality': '한국',
                'openDate': datetime.datetime(2017, 11, 29, 0, 0),
                'title_EN': 'Forgotten'
            },
            '독전': {
                'directors': '이해영',
                'genre': '범죄,액션',
                'nationality': '한국',
                'openDate': datetime.datetime(2018, 5, 22, 0, 0),
                'title_EN': 'Believer'}
            },
            ...
        }
    """

    # Parse movie detail info from kobis.or.kr
    baseURL = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/" + \
              "movie/searchMovieList.json?"
    # Option for the request
    opts = {
        'key': '03de300d95f7573393586e64780fd59a',
        'openEndDt': start_year or int(datetime.now().strftime('%Y')),
        'openStartDt': end_year or int(datetime.now().strftime('%Y')) - 1,
        'itemPerPage': items
    }

    # Raise PearlError if the arg `start_year` or `end_year` is not int
    if type(opts['openStartDt']) != int or type(opts['openEndDt']) != int:
        err = 'Argument`start_year` or `end_year` must be <int> or <None>.'
        raise PearlError(err)

    # Make opts into string
    opts_list = []
    for key in opts:
        opts_list.append('{}={}'.format(key, opts[key]))

    # Read json data, if fails, raise Error
    try:
        data = urlopen(baseURL + "&".join(opts_list))
        data = json.loads(data.read().decode('utf-8'))
        data = data['movieListResult']['movieList']
    except URLError:
        err = 'Cannot parse movie detail info. ' + \
              'Please check your network status.'
        raise PearlError(err)
    except Exception:
        err = 'Cannot parse movie detail info. ' + \
              'Please check your request parameter.'
        raise PearlError(err)

    # Fabricate data
    movies = {}
    for raw_info in data:
        title = raw_info['movieNm']
        info = {}
        info['title_EN'] = raw_info['movieNmEn']
        info['genre'] = raw_info['genreAlt']
        info['nationality'] = raw_info['repNationNm']
        info['openDate'] = datetime.strptime(raw_info['openDt'], "%Y%m%d")

        directors = map(lambda x: x['peopleNm'], raw_info['directors'])
        info['directors'] = ", ".join(list(directors))

        movies[title] = info

    return movies
