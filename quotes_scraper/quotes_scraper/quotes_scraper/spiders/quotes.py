import scrapy

# titulo = //h1/a/text()
# quotes = //span[@class="text" and @itemprop="text"]/text()
# top ten tags = //div[contains(@class, "tags-box")]//span[@class="tag-item"]/a/text()
# Next page button = //ul[@class="pager"]//li[@class="next"]/a/@href

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]
    custom_settings = {
        'FEED_URI': 'quotes.json',
        'FEED_FORMAT': 'json',
        'CONCURRENT_REQUESTS': 24,
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def parse_only_quotes(self, response, **kwargs):
        if kwargs:
            quotes = kwargs['quotes']
            author = kwargs['author']
        quotes.extend(response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall())
        author.extend(response.xpath('//small[@class="author"]/text()').getall())
        next_page_button_link = response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes': quotes, 'author': author})
        
        else:
            yield{
                'quotes': list(zip(quotes, author))
                        }
        

    def parse(self, response):

        #print(response.status, response.headers)
        title = response.xpath('//h1/a/text()').get()

        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        author = response.xpath('//small[@class="author"]/text()').getall()
        top_tags = response.xpath('//div[contains(@class, "tags-box")]//span[@class="tag-item"]/a/text()').getall()

        top = getattr(self, 'top', None)
        if top:
            top = int(top)
            top_tags = top_tags[:top]

        yield {
            'title': title,
            'top_tags': top_tags
        }

        next_page_button_link = response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes': quotes, 'author': author})
        else:
            yield {
                'quotes': list(zip(quotes, author))
            }