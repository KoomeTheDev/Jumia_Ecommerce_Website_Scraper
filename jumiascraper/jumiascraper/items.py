# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JumiaProduct(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    current_price = scrapy.Field()
    original_price =scrapy.Field()
    discount = scrapy.Field()
    url = scrapy.Field()
    full_url =scrapy.Field()
    image = scrapy.Field()
    brand = scrapy.Field()
    product_id = scrapy.Field()

  

