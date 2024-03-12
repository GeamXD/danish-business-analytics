import scrapy


class AmpliqonSpider(scrapy.Spider):
    name = "ampliqon"
    allowed_domains = ["ampliqon.com"]
    start_urls = ["https://ampliqon.com/en/ampliqon/about-us/"]

    def parse(self, response):
        company_desc = response.css('div.col-md-6.col-sm-8 > div > div > div > div > div > div p ::text')
        yield {
            'company_name':'ampliqon',
            'company_desc': company_desc.getall()
        }
