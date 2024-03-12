import scrapy


class TawiSpider(scrapy.Spider):
    name = "tawi"
    allowed_domains = ["www.tawi.com"]
    start_urls = ["https://www.tawi.com/why-tawi/about-tawi/"]

    def parse(self, response):
        
        company_desc = response.css('p ::text')

        yield {
            'company_name': 'tawi',
            'company_desc': company_desc.getall()
        }
