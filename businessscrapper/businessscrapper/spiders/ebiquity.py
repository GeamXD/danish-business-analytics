import scrapy


class EbiquitySpider(scrapy.Spider):
    name = "ebiquity"
    allowed_domains = ["ebiquity.com"]
    start_urls = ["https://ebiquity.com/"]

    def parse(self, response):
        pass
