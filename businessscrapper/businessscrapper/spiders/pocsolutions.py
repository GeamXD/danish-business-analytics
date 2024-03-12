import scrapy


class PocsolutionsSpider(scrapy.Spider):
    name = "pocsolutions"
    allowed_domains = ["www.pocsolutions.com"]
    start_urls = ["http://www.pocsolutions.com/"]

    def parse(self, response):
        
        company_desc = response.css('p ::text')

        yield {
            'company_name': 'pocsolutions',
            'company_desc': company_desc.getall()
        }
