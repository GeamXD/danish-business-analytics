import scrapy


class InviocareSpider(scrapy.Spider):
    name = "inviocare"
    allowed_domains = ["inviocare.com"]
    start_urls = ["https://inviocare.com/en/about-inviocare/"]

    def parse(self, response):
                
        company_desc = response.css('p ::text')

        yield {
            'company_name': 'inviocare',
            'company_desc': company_desc.getall()
        }
