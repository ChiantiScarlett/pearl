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

        location_table = CGV_CODE
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

        location_table = LOTCI_CODE
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

        location_table = MEGABOX_CODE
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
                    if self.title_not_valid(title, filter_key):
                        continue

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


# LOCATION CODE
CGV_CODE = {"부천역": "areacode=02&theatercode=0194",
            "포항": "areacode=204&theatercode=0045",
            "평택소사": "areacode=02&theatercode=0214",
            "용산아이파크몰": "areacode=01&theatercode=0013",
            "파주문산": "areacode=02&theatercode=0148",
            "대구한일": "areacode=11&theatercode=0147",
            "영등포": "areacode=01&theatercode=0059",
            "광주충장로": "areacode=206%2C04%2C06&theatercode=0244",
            "아시아드": "areacode=05%2C207&theatercode=0160",
            "여수웅천": "areacode=206%2C04%2C06&theatercode=0208",
            "구리": "areacode=02&theatercode=0232",
            "죽전": "areacode=02&theatercode=0055",
            "대학로": "areacode=01&theatercode=0063",
            "춘천명동": "areacode=12&theatercode=0189",
            "여의도": "areacode=01&theatercode=0112",
            "순천신대": "areacode=206%2C04%2C06&theatercode=0268",
            "압구정": "areacode=01&theatercode=0040",
            "야탑": "areacode=02&theatercode=0003",
            "대구": "areacode=11&theatercode=0058",
            "용인": "areacode=02&theatercode=0271",
            "통영": "areacode=204&theatercode=0156",
            "김포풍무": "areacode=02&theatercode=0126",
            "하계": "areacode=01&theatercode=0164",
            "서면": "areacode=05%2C207&theatercode=0005",
            "중계": "areacode=01&theatercode=0131",
            "대전터미널": "areacode=03%2C205&theatercode=0127",
            "대구월성": "areacode=11&theatercode=0216",
            "대전탄방": "areacode=03%2C205&theatercode=0202",
            "인천논현": "areacode=202&theatercode=0254",
            "천안펜타포트": "areacode=03%2C205&theatercode=0110",
            "하단": "areacode=05%2C207&theatercode=0245",
            "안동": "areacode=204&theatercode=0272",
            "울산삼산": "areacode=05%2C207&theatercode=0128",
            "해운대": "areacode=05%2C207&theatercode=0253",
            "제주노형": "areacode=206%2C04%2C06&theatercode=0259",
            "남포": "areacode=05%2C207&theatercode=0065",
            "미아": "areacode=01&theatercode=0057",
            "군자": "areacode=01&theatercode=0095",
            "서현": "areacode=02&theatercode=0196",
            "구로": "areacode=01&theatercode=0010",
            "판교": "areacode=02&theatercode=0181",
            "범계": "areacode=02&theatercode=0155",
            "광주첨단": "areacode=206%2C04%2C06&theatercode=0218",
            "천안": "areacode=03%2C205&theatercode=0044",
            "제주": "areacode=206%2C04%2C06&theatercode=0121",
            "광양": "areacode=206%2C04%2C06&theatercode=0220",
            "CINE de CHEF 용산아이파크몰": "areacode=01&theatercode=P013",
            "명동역 씨네라이브러리": "areacode=01&theatercode=0105",
            "신촌아트레온": "areacode=01&theatercode=0150",
            "청주(북문)": "areacode=03%2C205&theatercode=0084",
            "순천": "areacode=206%2C04%2C06&theatercode=0114",
            "인천연수": "areacode=202&theatercode=0258",
            "마산": "areacode=204&theatercode=0033",
            "일산": "areacode=02&theatercode=0054",
            "광양아울렛": "areacode=206%2C04%2C06&theatercode=0221",
            "송파": "areacode=01&theatercode=0088",
            "홍대": "areacode=01&theatercode=0191",
            "화명": "areacode=05%2C207&theatercode=0159",
            "목동": "areacode=01&theatercode=0011",
            "대전가오": "areacode=03%2C205&theatercode=0154",
            "청담씨네시티": "areacode=01&theatercode=0107",
            "나주": "areacode=206%2C04%2C06&theatercode=0237",
            "원주": "areacode=12&theatercode=0144",
            "대구수성": "areacode=11&theatercode=0157",
            "청주(서문)": "areacode=03%2C205&theatercode=0228",
            "불광": "areacode=01&theatercode=0030",
            "춘천": "areacode=12&theatercode=0070",
            "대구현대": "areacode=11&theatercode=0109",
            "수원": "areacode=02&theatercode=0012",
            "의정부태흥": "areacode=02&theatercode=0187",
            "유성노은": "areacode=03%2C205&theatercode=0206",
            "왕십리": "areacode=01&theatercode=0074",
            "보령": "areacode=03%2C205&theatercode=0275",
            "오리": "areacode=02&theatercode=0004",
            "이천": "areacode=02&theatercode=0205",
            "대한": "areacode=05%2C207&theatercode=0151",
            "청주터미널": "areacode=03%2C205&theatercode=0183",
            "산본": "areacode=02&theatercode=0242",
            "양산물금": "areacode=204&theatercode=0222",
            "동탄": "areacode=02&theatercode=0106",
            "군산": "areacode=206%2C04%2C06&theatercode=0277",
            "평택비전": "areacode=02&theatercode=0190",
            "상암": "areacode=01&theatercode=0014",
            "건대입구": "areacode=01&theatercode=0229",
            "동탄역": "areacode=02&theatercode=0265",
            "강릉": "areacode=12&theatercode=0139",
            "화정": "areacode=02&theatercode=0145",
            "수유": "areacode=01&theatercode=0276",
            "인천공항": "areacode=202&theatercode=0118",
            "김포": "areacode=02&theatercode=0177",
            "평촌": "areacode=02&theatercode=0195",
            "성신여대입구": "areacode=01&theatercode=0083",
            "세종": "areacode=03%2C205&theatercode=0219",
            "강동": "areacode=01&theatercode=0060",
            "동래": "areacode=05%2C207&theatercode=0042",
            "강남": "areacode=01&theatercode=0056",
            "안산": "areacode=02&theatercode=0211",
            "정관": "areacode=05%2C207&theatercode=0238",
            "청주지웰시티": "areacode=03%2C205&theatercode=0142",
            "전주고사": "areacode=206%2C04%2C06&theatercode=0213",
            "CINE de CHEF 센텀": "areacode=05%2C207&theatercode=P004",
            "부평": "areacode=202&theatercode=0021",
            "정읍": "areacode=206%2C04%2C06&theatercode=0186",
            "진주": "areacode=204&theatercode=0081",
            "광명철산": "areacode=02&theatercode=0182",
            "센텀시티": "areacode=05%2C207&theatercode=0089",
            "거제": "areacode=204&theatercode=0263",
            "북포항": "areacode=204&theatercode=0097",
            "계양": "areacode=202&theatercode=0043",
            "대전": "areacode=03%2C205&theatercode=0007",
            "평택": "areacode=02&theatercode=0052",
            "익산": "areacode=206%2C04%2C06&theatercode=0020",
            "역곡": "areacode=02&theatercode=0029",
            "창원": "areacode=204&theatercode=0023",
            "시흥": "areacode=02&theatercode=0073",
            "김포운양": "areacode=02&theatercode=0188",
            "동수원": "areacode=02&theatercode=0041",
            "홍성": "areacode=03%2C205&theatercode=0217",
            "강변": "areacode=01&theatercode=0001",
            "경기광주": "areacode=02&theatercode=0260",
            "목포": "areacode=206%2C04%2C06&theatercode=0026",
            "부천": "areacode=02&theatercode=0015",
            "대구칠곡": "areacode=11&theatercode=0071",
            "창원더시티": "areacode=204&theatercode=0079",
            "동백": "areacode=02&theatercode=0124",
            "북수원": "areacode=02&theatercode=0049",
            "천호": "areacode=01&theatercode=0199",
            "상봉": "areacode=01&theatercode=0046",
            "대구스타디움": "areacode=11&theatercode=0108",
            "구미": "areacode=204&theatercode=0053",
            "대연": "areacode=05%2C207&theatercode=0061",
            "동대문": "areacode=01&theatercode=0252",
            "인천": "areacode=202&theatercode=0002",
            "피카디리1958": "areacode=01&theatercode=0223",
            "연수역": "areacode=202&theatercode=0247",
            "의정부": "areacode=02&theatercode=0113",
            "주안역": "areacode=202&theatercode=0027",
            "대구이시아": "areacode=11&theatercode=0117",
            "서산": "areacode=03%2C205&theatercode=0091",
            "소풍": "areacode=02&theatercode=0143",
            "김천율곡": "areacode=204&theatercode=0240",
            "김해장유": "areacode=204&theatercode=0239",
            "CINE de CHEF 압구정": "areacode=01&theatercode=P001",
            "당진": "areacode=03%2C205&theatercode=0207",
            "김해": "areacode=204&theatercode=0028",
            "남주안": "areacode=202&theatercode=0198",
            "광주상무": "areacode=206%2C04%2C06&theatercode=0193",
            "명동": "areacode=01&theatercode=0009",
            "배곧": "areacode=02&theatercode=0226",
            "유성온천": "areacode=03%2C205&theatercode=0209",
            "광주용봉": "areacode=206%2C04%2C06&theatercode=0210",
            "전주효자": "areacode=206%2C04%2C06&theatercode=0179",
            "광주터미널": "areacode=206%2C04%2C06&theatercode=0090",
            "대구아카데미": "areacode=11&theatercode=0185"}
LOTCI_CODE = {"시화": "1|21|3016",
              "청량리": "1|21|1008",
              "오투": "1|80|2011",
              "청주용암": "1|105|4007",
              "대전둔산": "1|29|4006",
              "안산고잔": "1|23|3028",
              "율하": "1|10|5006",
              "광복": "1|11|2009",
              "광교아울렛": "1|2|3030",
              "마석": "1|8|3021",
              "성서": "1|8|5004",
              "포항": "1|11|5007",
              "안산": "1|22|3004",
              "부산본점": "1|40|2004",
              "안양": "1|25|3007",
              "진접": "1|37|3010",
              "진주혁신": "1|100|5017",
              "센트럴락": "1|18|3012",
              "독산": "1|7|1017",
              "프리미엄만경": "1|12|9066",
              "부평": "1|12|3003",
              "에비뉴엘": "1|15|1001",
              "울산": "1|83|5001",
              "노원": "1|6|1003",
              "라페스타": "1|7|3002",
              "인천": "1|33|3006",
              "신림": "1|14|1007",
              "가산디지털": "1|1|1013",
              "평촌": "1|40|3018",
              "장안": "1|20|9053",
              "서면": "1|52|2008",
              "서산": "1|53|9044",
              "성남신흥": "1|17|9027",
              "산본피트인": "1|15|3031",
              "동부산아울렛": "1|32|2010",
              "대전": "1|28|4002",
              "구미": "1|3|9001",
              "광주터미널": "1|5|3020",
              "안양일번가": "1|26|3032",
              "안성": "1|24|3022",
              "프리미엄진주": "1|114|9003",
              "수유": "1|12|1022",
              "수완": "1|7|6004",
              "광주광산": "1|2|9065",
              "주엽": "1|36|3013",
              "브로드웨이": "1|8|9056",
              "구미공단": "1|4|5013",
              "아산터미널": "1|69|4005",
              "의정부민락": "1|31|3033",
              "광명아울렛": "1|4|3025",
              "부천역": "1|11|9054",
              "전주평화": "1|9|6006",
              "합정": "1|22|1010",
              "부천": "1|10|3011",
              "통영": "1|108|9036",
              "원주무실": "1|85|9062",
              "청주충대": "1|106|9058",
              "서귀포": "1|51|9013",
              "창원": "1|102|5002",
              "구리아울렛": "1|6|3026",
              "김해아울렛": "1|23|5011",
              "오산": "1|28|9060",
              "서울대입구": "1|10|1012",
              "광주": "1|1|6001",
              "청주": "1|104|4003",
              "위례": "1|30|3037",
              "김포공항": "1|5|1009",
              "경주": "1|2|9050",
              "수락산": "1|11|1019",
              "울산성남": "1|84|5014",
              "파주운정": "1|39|3034",
              "광명": "1|3|3027",
              "사상": "1|46|2005",
              "용산": "1|17|1014",
              "건대입구": "1|4|1004",
              "인천터미널": "1|35|3038",
              "대구광장": "1|5|5012",
              "충장로": "1|10|9047",
              "목포": "1|6|9004",
              "인덕원": "1|32|3023",
              "가양": "1|2|1018",
              "인천아시아드": "1|34|3035",
              "향남": "1|41|3036",
              "병점": "1|9|3017",
              "김해부원": "1|22|5015",
              "동해": "1|34|7002",
              "홍대입구": "1|23|1005",
              "동성로": "1|6|5005",
              "파주아울렛": "1|38|3014",
              "마산터미널": "1|36|9042",
              "센텀시티": "1|59|2006",
              "양주고읍": "1|27|9063",
              "성남": "1|16|9009",
              "대영": "1|27|2012",
              "송탄": "1|19|3029",
              "서청주": "1|55|4004",
              "경산": "1|1|5008",
              "상인": "1|7|5016",
              "진해": "1|101|5009",
              "영주": "1|9|9064",
              "수원": "1|20|3024",
              "황학": "1|24|1011",
              "은평": "1|19|1021",
              "신도림": "1|13|1015",
              "월드타워": "1|18|1016",
              "검단": "1|1|3015",
              "강동": "1|3|9010",
              "전주": "1|8|6002",
              "남원주": "1|24|7001",
              "군산나운": "1|4|6007",
              "프리미엄칠곡": "1|13|9057",
              "동래": "1|31|2007",
              "해운대": "1|117|9059",
              "부평역사": "1|13|3008",
              "영등포": "1|16|1002"}
MEGABOX_CODE = {"안동": "7601",
                "울산": "6811",
                "EOE4": "1002",
                "대구": "7022",
                "제주아라": "6902",
                "양주": "4821",
                "백석": "4113",
                "문경": "7451",
                "송파파크하비오": "1381",
                "일산": "4111",
                "일산벨라시타": "4104",
                "ARTNINE": "1562",
                "양산": "6261",
                "이수": "1561",
                "신촌": "1202",
                "김천": "7401",
                "남포항": "7901",
                "전주": "5063",
                "영통": "4431",
                "세종": "3391",
                "부산대": "6906",
                "오창": "3631",
                "제천": "3901",
                "여수": "5551",
                "화곡": "1571",
                "청라": "4042",
                "부산극장": "6001",
                "목포하당": "5302",
                "남춘천": "2001",
                "서면": "6141",
                "파주금촌": "4132",
                "원주센트럴": "2202",
                "남양주": "4721",
                "덕천": "6161",
                "송도": "4062",
                "파주운정": "4115",
                "별내": "4722",
                "동탄": "4451",
                "경주": "7801",
                "원주": "2201",
                "검단": "4041",
                "삼천포": "6642",
                "천안": "3301",
                "수원남문": "4421",
                "하남스타필드": "4651",
                "제주": "6901",
                "북대구": "7021",
                "정관": "6191",
                "구미강동": "7303",
                "남원": "5901",
                "전대": "5001",
                "경산하양": "7122",
                "시흥배곧": "4291",
                "동대문": "1003",
                "목동": "1581",
                "대구신세계": "7011",
                "구미": "7304",
                "파주출판도시": "4131",
                "오산": "4471",
                "평택": "4501",
                "경남대": "6311",
                "첨단": "5064",
                "진천": "3651",
                "광주하남": "5061",
                "충주": "3801",
                "송천": "5612",
                "의정부민락": "4804",
                "안산중앙": "4253",
                "사천": "6641",
                "강남": "1372",
                "홍성내포": "3501",
                "속초": "2171",
                "창동": "1321",
                "마산": "6312",
                "광주상무": "5021",
                "김포": "4151",
                "마곡": "1572",
                "광주": "5011",
                "창원": "6421",
                "센트럴": "1371",
                "킨텍스": "4112",
                "은평": "1221",
                "여수웅천": "5552",
                "수원": "4411",
                "인천논현": "4051",
                "고양스타필드": "4121",
                "순천": "5401",
                "목포": "5301",
                "공주": "3141",
                "강남대로": "1359",
                "청라지젤": "4043",
                "코엑스": "1351",
                "거창": "6701",
                "분당": "4631",
                "대전": "3021",
                "상봉": "1311",
                "해운대": "6121"}
