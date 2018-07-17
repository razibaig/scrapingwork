import scrapy
from bs4 import BeautifulSoup as B
from parsel import Selector


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://www.espncricinfo.com/pakistan/content/player/568276.html',
    ]

    def parse(self, response):
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
        for tag in head:
            t = head.__getitem__(i)
            key = t.contents[0].string
            print(key)
            info = []
            for j in range(2, len(t.contents)):
                if t.contents[j].string != ' ':
                    info.append(t.contents[j].string)
            print(info)
            i += 1

        all_tables = response.css("table.engineTable").extract()
        for table in all_tables:
            self.print_table(table, "engineTable")

        player_table_s = response.css("div#shrtPrfl").extract_first()
        if player_table_s:
            player_prof_s = B(''.join(player_table_s), 'html.parser')
            for tag in player_prof_s.find_all('p'):
                print(tag.string)

        player_table = response.css("div#plrpfl").extract()
        if player_table:
            player_prof = B(''.join(player_table), 'html.parser')
            for tag in player_prof.find_all('p'):
                print(tag.string)

        articles = response.css("div.headline").extract_first()
        soup = B(''.join(articles), 'html.parser')
        for a in soup.find_all('a', href=True):
            print('{0}{1}'.format("http://www.espncricinfo.com", a['href']))

        photos = response.css("div.ciPicHldr").extract()
        soup = B(''.join(photos), 'html.parser')
        for a in soup.find_all('a', href=True):
            print('{0}'.format(soup.img['src']))

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
                print("{0}{1}{2}".format(field[0].strip(), "\t", field[1].strip()))


class Player:
    fullname = []
    born = []
    current_age = []
    major_teams = []
    playing_role = []
    batting_style = []
    education = []
    relation = []

    batting_averages = []
    bowling_averages = []
    recent_matches = []
    profile_information = []
    latest_articles = []
    latest_photos = []
