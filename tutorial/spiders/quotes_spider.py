import scrapy
from bs4 import BeautifulSoup as B
from parsel import Selector
import copy
import json


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://www.espncricinfo.com/england/content/player/351588.html',
    ]
    INDEX = 0
    DATA_LIST = {}

    def parse(self, response):
        player = Player()
        p_info = []
        l_articles = []
        l_photos = []

        file = open("player.html", "w")
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
            info = []
            for j in range(2, len(t.contents)):
                if t.contents[j].string != ' ':
                    info.append(t.contents[j].string)
            personal_info[key] = info
            i += 1

        player.personal_info['Personal Information'] = personal_info

        ind = 0
        all_tables = response.css("table.engineTable").extract()
        for table in all_tables:
            (self.print_table(table, "engineTable"))
            ind += 1
        # print(self.DATA_LIST)

        player.batting_averages['Batting Averages'] = self.DATA_LIST[0]
        player.bowling_averages['Bowling Averages'] = self.DATA_LIST[1]
        player.recent_matches['Recent Mathces'] = self.DATA_LIST[3]

        player_table_s = response.css("div#shrtPrfl").extract_first()
        if player_table_s:
            player_prof_s = B(''.join(player_table_s), 'html.parser')
            for tag in player_prof_s.find_all('p'):
                p_info.append(tag.string)

        player_table = response.css("div#plrpfl").extract()
        if player_table:
            player_prof = B(''.join(player_table), 'html.parser')
            for tag in player_prof.find_all('p'):
                p_info.append(tag.string)

        player.profile_info['Profile Info'] = p_info
        # print(player.profile_info)

        articles = response.css("div.headline").extract_first()
        soup = B(''.join(articles), 'html.parser')
        for a in soup.find_all('a', href=True):
            l_articles.append("http://www.espncricinfo.com" + a['href'])

        player.latest_articles['Latest Articles'] = l_articles

        photos = response.css("div.ciPicHldr").extract()
        soup = B(''.join(photos), 'html.parser')
        for a in soup.find_all('a', href=True):
            l_photos.append(soup.img['src'])

        player.latest_photos['Latest Photos'] = l_photos

        json_write = []

        # json_string = json.dumps([player.personal_info, player.batting_averages, player.bowling_averages,
        #                           player.recent_matches, player.profile_info, player.latest_articles,
        #                           player.latest_photos])

        json_write.append(json.dumps([player.personal_info]))
        json_write.append(json.dumps([player.batting_averages]))
        json_write.append(json.dumps([player.bowling_averages]))
        json_write.append(json.dumps([player.recent_matches]))
        json_write.append(json.dumps([player.profile_info]))
        json_write.append(json.dumps([player.latest_articles]))
        json_write.append(json.dumps([player.latest_photos]))

        with open('player.json', "w") as file:
            for data in json_write:
                file.write(data + "\n")

        player.print_player()

    def print_table(self, table, class_name):

        soup = B(''.join(table), "html.parser")
        table = soup.find("table", attrs={"class": class_name})

        # The first tr contains the field names.
        headings = [th.get_text() for th in table.find("tr").find_all("th")]

        datasets = []
        for row in table.find_all("tr")[1:]:
            dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
            datasets.append(dataset)

        tuple_list = []
        for dataset in datasets:
            tuple = {}
            for field in dataset:
                tuple[field[0].strip()] = field[1].strip()
                # print("{0}{1}{2}".format(field[0].strip(), "\t", field[1].strip()))
            tuple_list.append(tuple)

        self.DATA_LIST[self.INDEX] = tuple_list
        self.INDEX += 1

        # print(self.DATA_LIST)


class Player:

    personal_info = {}
    batting_averages = {}
    bowling_averages = {}
    recent_matches = {}
    profile_info = {}
    latest_articles = {}
    latest_photos = {}

    def add_person_info(self, data):
        self.personal_info = copy.deepcopy(data)

    def print_player(self):
        print(self.personal_info)
        print(self.batting_averages)
        print(self.bowling_averages)
        print(self.recent_matches)
        print(self.profile_info)
        print(self.latest_articles)
        print(self.latest_photos)
