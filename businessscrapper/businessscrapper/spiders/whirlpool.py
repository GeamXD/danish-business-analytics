import scrapy


class WhirlpoolSpider(scrapy.Spider):
    name = "whirlpool"
    allowed_domains = ["www.whirlpool.com"]
    start_urls = ["https://www.whirlpool.com/services/about-us.html"]

    def parse(self, response):

        company_desc = response.css('p ::text')

        yield {
            'company_name': 'whirlpool',
            'company_desc': company_desc.getall()
        }
