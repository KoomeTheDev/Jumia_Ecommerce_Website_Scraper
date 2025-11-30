from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class PriceConverterPipeline:
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Check if current_price exists and is not empty
        if adapter.get('current_price'):
            try:
                price_str = str(adapter['current_price'])
                
                # Extra cleaning: remove any remaining commas, spaces, currency symbols
                price_str = price_str.replace(',', '').replace(' ', '')
                price_str = price_str.replace('KSh', '').replace('Ksh', '').replace('ksh', '')
                price_str = price_str.strip()
                
                # Convert to float
                adapter['current_price'] = float(price_str)
                
                spider.logger.debug(
                    f"✅ Converted price to float: {adapter['current_price']}"
                )
                
            except (ValueError, TypeError) as e:
                spider.logger.warning(
                    f"⚠️ Could not convert price '{adapter.get('current_price')}' to float: {e}"
                )
                # Set to None if conversion fails
                adapter['current_price'] = None
        
        # Check original_price too
        if adapter.get('original_price'):
            try:
                orig_price_str = str(adapter['original_price'])
                
                # Extra cleaning
                orig_price_str = orig_price_str.replace(',', '').replace(' ', '')
                orig_price_str = orig_price_str.replace('KSh', '').replace('Ksh', '').replace('ksh', '')
                orig_price_str = orig_price_str.strip()
                
                # Convert to float
                adapter['original_price'] = float(orig_price_str)
                
            except (ValueError, TypeError) as e:
                spider.logger.warning(
                    f"⚠️ Could not convert original_price '{adapter.get('original_price')}': {e}"
                )
                adapter['original_price'] = None
        
        return item

class PriceToZARPipeline:
    """
    Convert Kenyan Shillings (KSh) to South African Rand (ZAR)
    """
    ksh_to_zar_rate = 0.15
    
    def process_item(self, item, spider):
        """
        Convert prices from KSh to ZAR
        """
        adapter = ItemAdapter(item)
        
        # Convert current price
        if adapter.get('current_price'):
            try:
                # Multiply by exchange rate
                original_ksh = adapter['current_price']
                adapter['current_price'] = round(
                    adapter['current_price'] * self.ksh_to_zar_rate, 
                    2  # Round to 2 decimal places
                )
                
                spider.logger.debug(
                    f"💱 Converted {original_ksh} KSh → {adapter['current_price']} ZAR"
                )
                
            except (TypeError, ValueError) as e:
                spider.logger.warning(f"⚠️ Could not convert currency: {e}")
        
        # Convert original price
        if adapter.get('original_price'):
            try:
                adapter['original_price'] = round(
                    adapter['original_price'] * self.ksh_to_zar_rate,
                    2
                )
            except (TypeError, ValueError) as e:
                spider.logger.warning(f"⚠️ Could not convert original price: {e}")
        
        # Add a currency field to show what currency it is now
        adapter['currency'] = 'ZAR'
        
        return item

class DropNoPricePipeline:
    """
    Drop (remove) items that don't have a price
    """
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Check if current_price exists and is valid
        if adapter.get('current_price'):
            # Price exists! Item is good, let it continue
            return item
        else:
            # No price! Drop this item
            spider.logger.warning(
                f"🗑️ Dropping item (no price): {adapter.get('name', 'Unknown')}"
            )
            raise DropItem(f"Missing price in {adapter.get('name', 'item')}")

class DuplicatesPipeline:
    """
    Remove duplicate products
    """
    
    def __init__(self):
        """
        Initialize the pipeline
        """
        self.names_seen = set()
    
    def process_item(self, item, spider):
        """
        Check if we've seen this product before
        """
        adapter = ItemAdapter(item)
        
        # Get the product name
        product_name = adapter.get('name')
        
        # IMPORTANT: Skip items without names (don't drop them here)
        if not product_name:
            spider.logger.warning(
                f"⚠️ Item has no name, skipping duplicate check"
            )
            return item  # Let it continue to next pipeline
        
        # Check if we've seen this name before
        if product_name in self.names_seen:
            # DUPLICATE! Drop it
            spider.logger.warning(
                f"🔄 Duplicate found (dropping): {product_name}"
            )
            raise DropItem(f"Duplicate item: {product_name}")
        else:
            # NEW PRODUCT! Add to our "seen" list and continue
            self.names_seen.add(product_name)
            spider.logger.debug(
                f"✅ New unique product: {product_name}"
            )
            return item




class CalculateSavingsPipeline:
    """
    Calculate how much money you save with the discount
    """
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        current = adapter.get('current_price')
        original = adapter.get('original_price')
        
        # Calculate savings if both prices exist
        if current and original:
            try:
                savings = round(original - current, 2)
                adapter['savings_amount'] = savings
                
                # Calculate percentage saved
                if original > 0:
                    savings_percent = round((savings / original) * 100, 1)
                    adapter['savings_percent'] = f"{savings_percent}%"
                
                spider.logger.debug(
                    f"💰 Calculated savings: {savings} ZAR ({adapter.get('savings_percent')})"
                )
            except (TypeError, ValueError) as e:
                spider.logger.warning(f"Could not calculate savings: {e}")
        
        return item


class ValidateItemPipeline:
    """
    Validate that items have all required fields
    Required fields:
    - name
    - product_id
    - current_price
    """
    
    required_fields = ['name', 'product_id', 'current_price']
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Check each required field
        missing_fields = []
        for field in self.required_fields:
            if not adapter.get(field):
                missing_fields.append(field)
        
        # If any required fields are missing, drop the item
        if missing_fields:
            spider.logger.error(
                f"❌ Item missing required fields: {missing_fields}"
            )
            raise DropItem(
                f"Missing required fields {missing_fields} in {adapter.get('name', 'unknown item')}"
            )
        
        return item