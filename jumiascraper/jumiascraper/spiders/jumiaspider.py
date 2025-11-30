import scrapy
from jumiascraper.items import JumiaProduct
from jumiascraper.itemloaders import JumiaProductLoader

class JumiaSpiderSpider(scrapy.Spider):
    name = 'jumiaspider'
    start_urls = ['https://www.jumia.co.ke/smartphones/']
    
    def parse(self, response):
        products = response.css('a.core')
        self.logger.info(f'Found {len(products)} products on {response.url}')
        
        for product in products:
            # Validate product has required data
            name = (
                product.css('div.name::text').get() or
                product.css('h3.name::text').get() or
                product.css('.name::text').get()
            )
            
            if not name:
                self.logger.warning("Skipping product without name")
                continue
            
            product_id = product.css('::attr(data-gtm-id)').get()
            if not product_id:
                continue
            
            # Create loader
            loader = JumiaProductLoader(item=JumiaProduct(), selector=product)
            
            # Add data using VALUES we already have
            loader.add_value('name', name.strip())
            loader.add_value('product_id', product_id)
            
            # Add the rest with CSS selectors
            loader.add_css('brand', '::attr(data-gtm-brand)')
            loader.add_css('current_price', 'div.prc::text')
            loader.add_css('original_price', 'div.prc::attr(data-oprc)')
            loader.add_css('discount', 'div.bdg._dsct::text')
            
            # URLs
            loader.add_value('url', product.attrib.get('href', ''))
            loader.add_value('full_url', response.urljoin(product.attrib.get('href', '')))
            
            # Media
            loader.add_css('image', 'img.img::attr(data-src)')
            
            yield loader.load_item()
        
        # Pagination
        next_page = response.css('a[aria-label="Next Page"]::attr(href)').get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f'Following next page: {next_page_url}')
            yield response.follow(next_page_url, callback=self.parse)
        else:
            self.logger.info('Reached last page - Scraping Complete.')