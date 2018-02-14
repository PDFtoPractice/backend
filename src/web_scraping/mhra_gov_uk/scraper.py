import scrapy
import re

f = open('links.txt', 'w')


class DrugSpider(scrapy.Spider):
    name = "drug_spider"
    start_urls = ['http://www.mhra.gov.uk/spc-pil/']

    # make url_list from all letter [A,B...,Z]
    def parse(self, response):
        panel_index_selector = '.panel'
        url_list = ['http://www.mhra.gov.uk/spc-pil/']
        panel = response.css(panel_index_selector)
        search_results_selector = '.current'
        counter = 0

        for current in panel.css(search_results_selector):
            if (counter < 26):
                href = current.css("a::attr('href')").extract()
                url = 'http://www.mhra.gov.uk/spc-pil/' + href[0]
                url_list.append(url)
            counter = counter + 1
            # go to each letter's page
        for url in url_list:
            print(url)
            yield scrapy.Request(url, callback=self.parse_first_dir_contents)

    # get all subletters [a-e, e-i,...]
    def parse_first_dir_contents(self, response):
        panel_index_selector = '.panel'
        url_list = []
        panel = response.css(panel_index_selector)
        search_results_selector = '.current'
        counter = 0

        for current in panel.css(search_results_selector):
            if (counter >= 26):
                href = current.css("a::attr('href')").extract()
                url = 'http://www.mhra.gov.uk/spc-pil/' + href[0]
                url_list.append(url)
                yield scrapy.Request(url, callback=self.parse_main_page)
                print(url)
            counter = counter + 1

    def parse_main_page(self, response):
        search_result_selector = '.searchResults'
        table = response.css(search_result_selector)
        current_selector = '.current'
        counter = 0
        for smt in table.css(current_selector):
            if (counter < 26):
                text = re.sub('<[^>]*>', '', smt.extract())
                href = smt.css("a::attr('href')").extract()
                url = 'http://www.mhra.gov.uk/spc-pil/' + href[0]
                drug = text
                yield scrapy.Request(url, callback=self.parse_2)
            counter = counter + 1

    # get all the links(where pages consists PDF links)
    # And write everything to the file
    def parse_2(self, response):
        search_result_selector = '.searchResults'
        table = response.css(search_result_selector)
        current_selector = '.current'
        for data in table.css(current_selector):
            href = data.css("a::attr('href')").extract()
            url = 'http://www.mhra.gov.uk/spc-pil/' + href[0]
            f.write(url + '\n')
            print(url + '\n')






