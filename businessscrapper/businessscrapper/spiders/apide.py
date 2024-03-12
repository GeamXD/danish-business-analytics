import scrapy


class ApideSpider(scrapy.Spider):
    name = "apide"
    allowed_domains = ["apide.com"]
    start_urls = ["https://apide.com/"]

    def parse(self, response):
        
        company_desc = response.css('p ::text')
        yield {
            'company_name': 'apide',
            'company_desc': company_desc.getall()
        }
