[!Alt Sample]("./sample.png")

# Pearl

A simple module that parses data from Korean movie theaters.


## Installation

You can install pearl with pip

```
$ pip install chianti-pearl
```

or you can manually download the wheel file from [here](https://pypi.org/project/chianti-pearl/#files).


## Quick Example

### Printing out time schedule on a console screen:

```python
from pearl import lotci
lotci('수원', date=9).show()
```

### Receiving time schedule data in JSON

```python
from pearl import cgv
data = cgv('북수원', date=21).to_json()
```



## Usage and Description

### Abstract

These are the functions that you can use with the module pearl:

- pearl.`cgv(location, date=None, title=None)`
- pearl.`lotci(location, data=None, title=None)`
- pearl.`megabox(location, data=None, title=None)`
- pearl.`get_detail(items=100, start_year=None, end_year=None)`
- pearl.`parse_code(theater, filepath)`


### pearl.cgv, pearl.lotci, pearl.megabox

`cgv`, `lotci`, and `megabox` takes same parameters.


```
def cgv(location, date=None, title=None):
    """
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
```


### Adding <Clip> objects

 pearl.cgv, pearl.lotci, and pearl.megabox returns a &lt;Clip&gt; class object. &lt;Clip&gt; **is addable with other &lt;Clip&gt; objects**. This means that you can also do something like the below.


```python
from pearl import cgv, lotci, megabox
data = (cgv('북수원') + lotci.cgv('수원') + megabox('수원')).to_json()
```



## Built With

* [Sublime Text3](http://www.dropwizard.io/1.0.2/docs/) - Awesome text editor that I use every day :D
* [Google Chrome Developer Tools](https://maven.apache.org/) - Testing and tracing appropriate data
* [Python3.5.2](https://rometools.github.io/rome/) - Main version, ran on Linux Mint 18.3.



## Authors

* **Chianti Shiina** - *Initial work* - [Pearl](https://github.com/ChiantiShiina/pearl)



## Acknowledgments

* Inspired by the article [챗봇 만들기 — 영화 상영관 찾기](https://medium.com/bothub-studio-ko/%EC%B1%97%EB%B4%87-%EB%A7%8C%EB%93%A4%EA%B8%B0-%EC%98%81%ED%99%94-%EC%83%81%EC%98%81%EA%B4%80-%EC%B0%BE%EA%B8%B0-ec9bbff353d8)
* Using the movie detail info from KOBIS. You can get the official open API from [here](http://www.kobis.or.kr/kobisopenapi/).
* Special acknowledgment to the Starbucks, for providing perfect circumstance of writing these codes.