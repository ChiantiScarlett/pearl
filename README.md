![Alt text](images/sample.png?raw=true "Pearl")

# Pearl

> A simple module that parses Korean cinema schedules.

<br><br><br>

## Installation

You can get the latest version of `pearl` using pip:

```
$ pip install chianti-pearl
```

or you can manually download the wheel file from [here](https://pypi.org/project/chianti-pearl/#files) as well.

<br><br><br>

## Quick Example

<br>

### Printing out time schedule on a console screen

```python
from pearl import lotci
lotci('수원', date=9).show()
```

<br>

### Receiving time schedule data in JSON

```python
from pearl import cgv
data = cgv('북수원', date=21).to_json()
```

<br>

### Receiving time schedule data in &lt;list&gt; type

```python
from pearl import cgv
data = cgv('북수원', date=21).to_list()
```

<br><br>

## Usage and Description

<br>

### Abstract

These are the functions that you can use with the module `pearl`:

- `pearl.cgv(location, date=None, title=None)`
- `pearl.lotci(location, data=None, title=None)`
- `pearl.megabox(location, data=None, title=None)`
- `pearl.get_detail(items=100, start_year=None, end_year=None)`
- `pearl.available_location(cinema)`

<br><br>

`pearl.cgv`, `pearl.lotci`, and `pearl.megabox` returns a &lt;Clip&gt; class object. **Please keep in mind that &lt;Clip&gt; object is addable with other &lt;Clip&gt; objects**. This means that you can also do things like below:

```python
from pearl import cgv, lotci, megabox
data = (cgv('북수원') + lotci.cgv('수원') + megabox('수원')).to_json()
```

<br><br>

### pearl.cgv, pearl.lotci, pearl.megabox

#### Basic Usage (to &lt;list&gt;):
```python
from pearl import cgv
cgv_data = cgv('신촌아트레온').to_list()
```

#### Basic Usage (to JSON):
```python
from pearl import megabox
megabox_data = megabox('신촌').to_json()
```

#### Printing out on a console screen
You can also print out the data on terminal, by using `show()` method. In this case, it automatically triggers `get_detail()` function, so as to grab specific movie detail info.

```python
from pearl import lotci
lotci('수원', date=10, title='어벤져스').show()
```

#### Arguments / Returns
`cgv`, `lotci`, and `megabox` functions take identical parameters. If date is not specified, it selects date of today by default.

``` plain
Arguments:
    [Argument]           | [Type] | [Description]           | [Example]
    ------------------------------------------------------------------
    locations            | (str)  | Cinema location(s)      | '북수원'
    date      (optional) | (int)  | day of the date (1~31)  | 8
    title     (optional) | (str)  | filter out movie titles | '플레이어'

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
```


<br>

### pearl.get_detail

`get_detail` is a function that brings movie information detail from KOBIS. It uses open API from KOBIS(영화진흥위원회, Korean Film Council),  according to the arguments. Please keep in mind that this open API is kind of slow compared to other parser modules.

<br>

If the sole purpose of using this module is to get heavy movie data out of it, I strongly recommend you to get your own key and read the full documents, because this module uses limited functions. You can get free keys and more detailed documents from [here](http://www.kobis.or.kr/kobisopenapi).

<br>

#### Sample Usage
```python
from pearl import get_detail
details = get_detail(items=200)
```

#### Arguments / Returns
 Argument `start_year` and `end_year` should be 4-digit integer (e.g. 2018). 
 And by default, this function gets 100 items, 1-year-range from year of today.

``` plain
Arguments:
    [Argument]            | [Type] | [Description]
    ------------------------------------------------------------------
    items      (optional) | (str)  | maximum number of items
    start_year (optional) | (int)  | filter specific start year
    end_year   (optional) | (int)  | filter specific end year

Returns:
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

```

<br>

### pearl.available_location

`pearl.available_location` is a function that returns available location argument for `cgv`, `lotci`, and `megabox`.


#### Sample Usage
```python
from pearl import available_location
locations = available_location('cgv')
```

#### Arguments / Returns
Argument `cinema` should be either 'cgv', 'lotci', or 'megabox'.

``` plain
Arguments:
    [Argument] | [Type] | [Description]
    ------------------------------------------------------------------
    cinema     | (str)  | name of the cinema you want to parse from

Returns:
    <list> type of location values.
    
    e.g.
    ['경산하양', '신촌', '덕천', 'ARTNINE', '대구신세계', ... ]
```
<br>

<br><br>

## Built With

* [Sublime Text3](http://www.dropwizard.io/1.0.2/docs/) - Awesome text editor that I use every day :D
* [Google Chrome Developer Tools](https://maven.apache.org/) - Testing and tracing appropriate data
* [Python3.5.2](https://rometools.github.io/rome/) - Main version, ran on Linux Mint 18.3.

<br><br>

## Notes

I do not claim any ownership of the movie data that was parsed with the cinemas, and these are for personal use only. Other than that, I do not mind anyone peeking through the code or tweaking around the module.

Appreciate any bug reports or improvements.

<br><br>

## Author :: Chianti Shiina

![Profile](https://secure.gravatar.com/avatar/cfbdcf8a254e3230621e8577619c6941?s=200)

- Keybase:  [/ChiantiShiina](https://keybase.io/chiantishiina)
- GMail:    chianti.shiina@gmail.com
- Telegram: [@ChiantiShiina](https://t.me/chiantishiina)
- Mastodon: [@ChiantiShiina](https://mastodon.social/@ChiantiShiina)
- Blog:     [chianti.shiina.io](https://chianti.shiina.io)

<br><br>

## Acknowledgments

* Gained a lot of information from [this article](https://medium.com/bothub-studio-ko/%EC%B1%97%EB%B4%87-%EB%A7%8C%EB%93%A4%EA%B8%B0-%EC%98%81%ED%99%94-%EC%83%81%EC%98%81%EA%B4%80-%EC%B0%BE%EA%B8%B0-ec9bbff353d8).
* This module uses movie info that were brought up from KOBIS. You can get the official open API from [here](http://www.kobis.or.kr/kobisopenapi/).
* Special thanks to Starbucks, for providing perfect circumstance to write these codes during the weekends.

<br>