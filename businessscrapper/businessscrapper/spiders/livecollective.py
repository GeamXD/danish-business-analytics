import scrapy


class LivecollectiveSpider(scrapy.Spider):
    name = "livecollective"
    allowed_domains = ["livecollective.dk"]
    start_urls = ["https://livecollective.dk"]

    def parse(self, response):

        company_desc = response.css('p ::text')
        yield {
            'company_name': 'livecollective',
            'company_desc': company_desc.getall()
        }
