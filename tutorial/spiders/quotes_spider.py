import scrapy
from bs4 import BeautifulSoup

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://www.espncricinfo.com/england/content/player/351588.html',
    ]

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        test_header = response.css("tr.head")
        test_data = response.css("tr.data1")[0]

        print("\n\n\n\n")
        print(test_header)
        print("\n\n\n\n")
        print(test_data)
        print("\n\n\n\n")



