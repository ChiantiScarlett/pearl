# Pearl

A simple module that parses data from Korean movie theaters.


## Getting Started

[/]

### Prerequisites

You need to install colorama in order to print out on your console. You can do this by using pip:


```
# on Linux
sudo pip3 install colorama

# on Windows
pip install colorama
```

### Installing

[/]

## Usage

Basically there are two ways you can get data. One is by the .show() method (which is designed for using on the interactive mode), and the other is .to_json() method, literally returning JSON data.

Since this module was envisaged for variety of users' taste, you can add, put options, or gather

There are four different major functions that you can use, which are

```
pearl.cgv(location, date=None, title=None)
pearl.lotci(location, data=None, title=None)
pearl.megabox(location, data=None, title=None)
pearl.get_detail(items=100, start_year=None, end_year=None)
```


```python
from pearl import cgv, lotci, megabox
```

```python
def cgv(location, date=None, title=None):
    """
    Description:
        This function parses data from CGV
        (www.cgv.co.kr)

    Args:
        [Argument]           | [Type] | [Description]           | [Example]
        ------------------------------------------------------------------
        locations            | (str)  | Cinema location(s)      | '북수원'
        date      (optional) | (int)  | day of the date (1~31)  | 8
        title     (optional) | (str)  | filter out movie titles | '플레이어'

    Note:
        Default value for the argument `date` is the day of today's date.

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


def lotci(location, date=None, title=None):
    """
    Description:
        This function parses data from Lotte Cinema(롯데시네마)
        (www.lottecinema.co.kr/)

    Args, Returns -> identical to self.cgv()

    """


def megabox(location, date=None, title=None):
    """
    Description:
        This function parses data from Megabox(메가박스)
        (www.megabox.co.kr/)

    Args, Returns -> identical to self.cgv()

    """

def parse_code(theater, filepath):
```

### Basic Example



### Basic Usage

Basically you can get data in two ways. One is to show on the terminal screen, the other is to receive data as a JSON format.

#### Print data on terminal :: show()

```python
from pearl import cgv

cgv('북수원').show()
```

#### Return JSON data :: to_json()

```python
from pearl import lotci

data = lotci('북수원').to_json()
```

#### Adding 
[/]

## Built With

* [Sublime Text3](http://www.dropwizard.io/1.0.2/docs/) - Awesome text editor that I use every day :D
* [Google Chrome Developer Tools](https://maven.apache.org/) - Testing and tracking appropriate data
* [Python3.5.2](https://rometools.github.io/rome/) - Main version, ran on Linux Mint 18.3

## Authors

* **Chianti Shiina** - *Initial work* - [Pearl](https://github.com/ChiantiShiina/pearl)

## License

This project is licensed under the MIT License.

## Acknowledgments

* Inspired by the article [챗봇 만들기 — 영화 상영관 찾기](https://medium.com/bothub-studio-ko/%EC%B1%97%EB%B4%87-%EB%A7%8C%EB%93%A4%EA%B8%B0-%EC%98%81%ED%99%94-%EC%83%81%EC%98%81%EA%B4%80-%EC%B0%BE%EA%B8%B0-ec9bbff353d8)
* Detail movie information was from KOBIS(), and you can easily get the open API from [here](http://www.kobis.or.kr/kobisopenapi/).
* Special acknowledgment to my coffee mug.
