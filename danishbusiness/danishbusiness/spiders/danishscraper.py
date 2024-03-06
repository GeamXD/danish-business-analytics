import scrapy


class DanishscraperSpider(scrapy.Spider):
    name = "danishscraper"
    allowed_domains = ["www.letrang.dk"]
    start_urls = ["https://www.letrang.dk/produkter"]

    def parse(self, response):
        pass
