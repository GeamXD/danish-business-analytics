import scrapy


class OfficeclubSpider(scrapy.Spider):
    name = "officeclub"
    allowed_domains = ["www.officeclub.dk"]
    start_urls = ["https://www.officeclub.dk/"]

    def parse(self, response):

        company_desc = response.css('p ::text')

        yield {
            'company_name': 'officeclub',
            'company_desc': company_desc.getall()
        }
