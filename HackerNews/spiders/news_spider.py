import scrapy
import itertools
from ..items import HackernewsItem, MetaDataItem

class NewsSpider(scrapy.Spider):
    name = 'news'
    page_number = 2
    start_urls = [
        'https://news.ycombinator.com/news?p=1'
    ]

    def parse(self, response):

        items = HackernewsItem()

        all_titles_url = response.css('td.title')
        all_meta_data = response.css('td.subtext')

        title_list = []
        url_list = []
        for val in all_titles_url:
            title = val.css('.storylink::text').extract_first()
            url = val.css('a::attr(href)').extract_first()
            if (title is not None) and (title not in title_list):
                title_list.append(title)
                url_list.append(url)

        vote = []
        for value in all_meta_data:
            temp = value.css('.score::text').extract_first()
            vote.append(temp)

        for (title, url, score) in zip(title_list, url_list, vote):
            items['title'] = title
            items['url'] = url
            items['score'] = score
            yield items
        
        for url in url_list:
            yield response.follow(url, callback=self.parse_meta)
        
        next_page = 'https://news.ycombinator.com/news?p=' + str(NewsSpider.page_number)
        if NewsSpider.page_number < 20:
            NewsSpider.page_number += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_meta(self, response):
        items = MetaDataItem()
        description = response.css('p::text').extract()
        images = response.css('img').xpath('@src').getall()
        items['description'] = description
        items['images'] = images
        yield items