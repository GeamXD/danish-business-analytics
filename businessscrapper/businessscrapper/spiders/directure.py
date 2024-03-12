import scrapy


class DirectureSpider(scrapy.Spider):
    name = "directure"
    allowed_domains = ["www.directure.com"]
    start_urls = ["https://www.directure.com/"]

    def parse(self, response):
                
        company_desc = response.css('p ::text')

        yield {
            'company_name': 'directure',
            'company_desc': company_desc.getall()
        }

