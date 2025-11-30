import scrapy
from jumiascraper.items import JumiaProduct
from jumiascraper.itemloaders import JumiaProductLoader

class JumiaSpiderSpider(scrapy.Spider):
    name = 'jumiaspider'
    start_urls = ['https://www.jumia.co.ke/smartphones/']

    def parse(self, response):
        products = response.css('a.core')
        self.logger.info(f'Found{len(products)} product on {response.url}')

        for product in products:
            name = (
                product.css('div.name::text').get() or
                product.css('h3.name::text').get() or
                product.css('.name::text').get()
            )

            if not name:
                self.logger.warning("Skipping product without name")
                continue
            
            product_id =product.css('::attr(data-gtm-id)').get()
            if not product_id:
                continue

            loader = JumiaProductLoader(item = JumiaProduct(), selector = product)

            #Basic Information
            loader.add_css('name', 'div.name::text')
            loader.add_css('product_id', '::attr(data-gtm-id)')
            loader.add_css('brand', '::attr(data-gtm-brand)')
            

            # Pricing Information
            loader.add_css('current_price', 'div.prc::text')
            loader.add_css('original_price', 'div.prc::attr(data-oprc)')
            loader.add_css('discount', 'div.bdg._dsct::text')


            # Url
            loader.add_value('url', product.attrib.get('href', ''))
            loader.add_value('full_url', response.urljoin(product.attrib.get('href', '')))

            # Media
            loader.add_css('image', 'img.img::attr(data-src)')


            yield loader.load_item()
        
        next_page = response.css('a[aria-label = "Next Page"]::attr(href)').get()

        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f'Following next page: {next_page_url}')
            yield response.follow(next_page_url, callback = self.parse)

        else:
            self.logger.info('Reached last page - Scraping Complete.')

  

     