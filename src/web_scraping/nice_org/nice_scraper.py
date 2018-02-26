import scrapy
import re
import json



data = {}
class NiceSpider(scrapy.Spider):
    name = "nice_spider"
    start_urls = ['https://bnf.nice.org.uk/interaction/']



    def parse(self, response):
        body = response.xpath("//ul")
        print("starting ")
        list_of_names = body[5:30]
        for item in list_of_names:
            href = item.css("a::attr('href')").extract()
            for link in href:
                full_link ='https://bnf.nice.org.uk/interaction/' + link
                print(full_link)
                yield scrapy.Request(full_link, callback=self.parse_sub_page)






    def parse_sub_page(self, response):

        header = response.css('.interaction-heading > span:nth-child(1)::text')

        active = header.extract()[0]
        active = active.strip()
        print("Writing: " + active)
        body = response.css('.interaction-list')
        body2 = body.css('.interaction.scroll-target.row')
        for item in body2:
            interactant = item.css(".interactant")
            name_of_interactant = interactant.css('span::text').extract_first()

            message = item.css(".interaction-message")

            message2 = message.css('div::text')
            message_of_interaction = message2[1].extract()
            message_of_interaction = re.sub('\\n', '', message_of_interaction)


            text = message.extract()[0]
            matches = re.findall('<dd>(.*)<\/dd>',text)
            severity_of_interaction = ''
            evidence_for_interaction = ''
            if(len(matches) == 2):
                severity_of_interaction = matches[0]
                evidence_for_interaction = matches[1]

            name_of_interactant = name_of_interactant.strip()
            message_of_interaction = message_of_interaction.strip()
            severity_of_interaction = severity_of_interaction.strip()
            evidence_for_interaction = evidence_for_interaction.strip()


            if active not in data:
                data[active] = []

            data[active].append({
                'interactant': name_of_interactant,
                'message': message_of_interaction,
                'severity_of_interaction': severity_of_interaction,
                'evidence_for_interaction': evidence_for_interaction
            })
        with open('interactions.json', 'w') as outfile:
            json.dump(data, outfile)

