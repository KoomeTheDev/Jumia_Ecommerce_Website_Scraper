import scrapy

class JumiaSpiderSpider(scrapy.Spider):
    """
    A spider to scrape smartphone data from Jumia Kenya
    
    What this robot does:
    1. Goes to Jumia smartphones page
    2. Finds all phone products
    3. Extracts name, price, image, etc.
    4. Clicks "Next Page" and repeats
    5. Stops when there are no more pages
    6. Saves all data to a file
    """
    
    # Give our robot a name
    name = 'jumiaspider'
    
    # Tell the robot where to start
    start_urls = ['https://www.jumia.co.ke/smartphones/']
    
    def parse(self, response):
        """
        Main function that processes each page
        
        Think of this as the robot's instruction manual:
        - response = The webpage the robot is looking at
        """
        
        # STEP 1: Find all product boxes on the page
        # Like finding all toy boxes on a shelf
        products = response.css('a.core')
        
        # STEP 2: Log how many products we found
        # Like the robot saying "I found 40 toys on this shelf!"
        self.logger.info(f'Found {len(products)} products on {response.url}')
        
        # STEP 3: Look at each product one by one
        for product in products:
            
            # STEP 3A: Try to find the product name
            # We try multiple places because different products 
            # might store the name in different boxes
            name = (
                product.css('div.name::text').get() or  # Try div first
                product.css('h3.name::text').get() or   # Then try h3
                product.css('.name::text').get()         # Finally try any .name
            )
            
            # STEP 3B: If we couldn't find a name, skip this product
            # It's probably an ad or banner, not a real product
            if not name:
                self.logger.warning(f"Skipping product without name")
                continue  # Skip to next product
            
            # STEP 3C: Clean the name (remove extra spaces)
            name = name.strip()
            
            # STEP 3D: Get the product ID to verify it's real
            product_id = product.css('::attr(data-gtm-id)').get()
            
            # STEP 3E: If there's no product ID, it's not a real product
            if not product_id:
                continue  # Skip to next product
            
            # STEP 3F: Extract all the product information
            # Like filling out a form with all the toy details
            item = {
                'name': name,
                'current_price': self._clean_text(
                    product.css('div.prc::text').get()
                ),
                'original_price': product.css('div.prc::attr(data-oprc)').get(),
                'discount': self._clean_text(
                    product.css('div.bdg._dsct::text').get()
                ),
                'url': product.attrib.get('href', ''),
                'full_url': response.urljoin(
                    product.attrib.get('href', '')
                ),
                'image': product.css('img.img::attr(data-src)').get(),
                'brand': product.css('::attr(data-gtm-brand)').get(),
                'product_id': product_id,
            }
            
            # STEP 3G: Put this product in our basket
            yield item
        
        # STEP 4: Look for the "Next Page" button
        # Like looking for a sign that says "More shelves this way →"
        next_page = response.css('a[aria-label="Next Page"]::attr(href)').get()
        
        # STEP 5: If we found a next page, go there
        if next_page is not None:
            # Make the full URL
            next_page_url = response.urljoin(next_page)
            
            # Log that we're going to the next page
            self.logger.info(f'Following next page: {next_page_url}')
            
            # Go to the next page and run this same function again
            # This is where the magic loop happens!
            yield response.follow(next_page_url, callback=self.parse)
        else:
            # No more pages - we're done!
            self.logger.info('Reached last page - scraping complete! 🎉')
    
    def _clean_text(self, text):
        """
        Helper function to clean text
        
        Like using a towel to wipe dirt off a toy
        - Removes extra spaces
        - Returns None if there's no text
        """
        if text:
            return text.strip()
        return None