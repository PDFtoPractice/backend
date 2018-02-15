import scrapy
import re
import json

f = open('links.txt','r')


data = {}

class BrickSetSpider(scrapy.Spider):
    name = "drug_spider"
    start_urls = f.readlines()
    start_urls = [line.strip('\n') for line in start_urls]
    # start_urls = start_urls[0:1000]

    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
    }


    def parse(self,response):



        url = response.request.url
        p = re.compile('prodName=(.*)&subsName=')
        product_name = p.search(url).group(1)

        p = re.compile('subsName=(.*)&pageID')
        drug = p.search(url).group(1)


        search_result_selector = '.searchResults'
        table = response.css(search_result_selector)
        for smg in table:
            link = smg.css("a::attr('href')").extract()[0]
            print(smg.css("a::attr('href')").extract()[0])
            p = re.compile('>(.*).pdf')
            a_tag = p.search(smg.css("a").extract()[0]).group(1)
            print(a_tag)


            active = re.sub('%20',' ',drug)
            drug = active
            active = re.sub('///','/',drug)


            product = re.sub('%20',' ',product_name)
            product_name = product
            product = re.sub('///','/',product_name)

            tag = re.sub('%20',' ',a_tag)
            a_tag = tag
            tag = re.sub('///','/',a_tag)


            if active not in data:
                data[active] = []



            data[active].append({
                'product': product,
                'link': link,
                'pdf_name': tag
            })
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)



