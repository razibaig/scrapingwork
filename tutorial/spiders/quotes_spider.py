import scrapy
from bs4 import BeautifulSoup as B
from parsel import Selector
import copy
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle
import sys


DATA_LIST = {}
sys.setrecursionlimit(10000)


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://www.espncricinfo.com/england/content/player/351588.html',
    ]

    def parse(self, response):
        player = Player()
        data_dict = {}

        page = response.url.split("/")[-2]
        filename = '%s.html' % page
        file = open(filename, "w")
        file.write(response.text)
        file.close()

        response = Selector(response.text)
        test_header2 = response.css("p.ciPlayerinformationtxt").extract()
        pl = B(''.join(test_header2), 'html.parser')
        head = pl.find_all('p')

        i = 0
        personal_info = {}
        for tag in head:
            t = head.__getitem__(i)
            key = t.contents[0].string
            # print(key)
            info = []
            for j in range(2, len(t.contents)):
                if t.contents[j].string != ' ':
                    info.append(t.contents[j].string)
            personal_info[key] = info
            i += 1

        player.add_person_info(personal_info)

        ind = 0
        all_tables = response.css("table.engineTable").extract()
        for table in all_tables:
            table_list = copy.deepcopy(self.print_table(table, "engineTable"))
            data_dict[ind] = table_list
            ind += 1
        # print(data_dict)

        player_table_s = response.css("div#shrtPrfl").extract_first()
        if player_table_s:
            player_prof_s = B(''.join(player_table_s), 'html.parser')
            for tag in player_prof_s.find_all('p'):
                player.profile_info.append(tag.string)

        player_table = response.css("div#plrpfl").extract()
        if player_table:
            player_prof = B(''.join(player_table), 'html.parser')
            for tag in player_prof.find_all('p'):
                player.profile_info.append(tag.string)

        # print(player.profile_info)

        articles = response.css("div.headline").extract_first()
        soup = B(''.join(articles), 'html.parser')
        for a in soup.find_all('a', href=True):
            player.latest_articles.append("http://www.espncricinfo.com" + a['href'])

        photos = response.css("div.ciPicHldr").extract()
        soup = B(''.join(photos), 'html.parser')
        for a in soup.find_all('a', href=True):
            player.latest_photos.append(soup.img['src'])

        # player.print_player()

        # json_string = json.dumps(player.__dict__)
        # json_string = json.dumps(player, default=set_default)

        json_string = dumps(player, cls=PythonObjectEncoder)
        print(json_string)

        print(loads(json_string, object_hook=as_python_object))

        filename = 'player.json'
        file = open(filename, "w")
        file.write(json_string)
        file.close()

    def print_table(self, table, class_name):
        soup = B(''.join(table), "html.parser")
        table = soup.find("table", attrs={"class": class_name})

        # The first tr contains the field names.
        headings = [th.get_text() for th in table.find("tr").find_all("th")]

        datasets = []
        for row in table.find_all("tr")[1:]:
            dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
            datasets.append(dataset)

        for dataset in datasets:
            for field in dataset:
                DATA_LIST[field[0].strip()] = field[1].strip()
                # print("{0}{1}{2}".format(field[0].strip(), "\t", field[1].strip()))

        return DATA_LIST


def obj_dict(obj):
    return obj.__dict__


def obj_str(obj):
    return obj.__str__


def set_default(Player):
    if isinstance(Player, set):
        return list(Player)
    raise TypeError


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        return json.JSONEncoder.default(self, obj)


class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        return {'_python_object': pickle.dumps(obj)}


def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct


class Player:

    personal_info = {}
    fullname = []
    born = []
    current_age = []
    major_teams = []
    playing_role = []
    batting_style = []
    education = []
    relation = []

    batting_averages = {}
    bowling_averages = {}
    recent_matches = {}
    profile_info = []
    latest_articles = []
    latest_photos = []

    def add_person_info(self, data):
        self.personal_info = copy.deepcopy(data)

    def add_bat_averages(self, data):
        self.batting_averages = copy.deepcopy(data)

    def add_bowl_averages(self, data):
        self.bowling_averages = copy.deepcopy(data)

    def add_recent_matches(self, data):
        self.recent_matches = copy.deepcopy(data)

    def print_player(self):
        print(self.personal_info)
        print(self.profile_info)
        print(self.latest_articles)
        print(self.latest_photos)

    def __dict__(self):
        return self.__dict__

    def __str__(self):
        return self.__str__
