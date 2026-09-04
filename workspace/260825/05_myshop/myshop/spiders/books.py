import scrapy

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    # headers
    def parse(self, response):
        for card in response.css("article.product_pod"):
            yield {
                "title": card.css("h3 a::attr(title)").get(),
                "price": card.css("p.price_color::text").get(),
            }
        nxt = response.css("li.next a::attr(href)").get()
        if nxt:
            yield response.follow(nxt, self.parse) # 다음페이지
