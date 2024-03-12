import scrapy


class BystedSpider(scrapy.Spider):
    name = "bysted"
    allowed_domains = ["bystedpartners.dk"]
    start_urls = ["https://bystedpartners.dk/"]

    def parse(self, response):
        
        company_desc = response.css('p ::text')
        
        yield {
            'company_name': 'bytedpartners',
            'company_desc': company_desc.getall()
        }

