# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class JumiascraperPipeline:
    def process_item(self, item, spider):
        return item


class PriceConverterPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('current_price'):
            try:
                adapter['current_price'] = float(adapter['current_price'])
                spider.logger.debug(
                    f" Converted price to float: {adapter['current_price']}"
                )
            except (ValueError, TypeError) as e:
                spider.logger.warning(
                    f" Could not convert price to float: {adapter.get('current_price')} - Error: {e}"
                )
        
        if adapter.get('original_price'):
            try:
                adapter['original_price'] = float(adapter['original_price'])
            except (ValueError, TypeError) as e:
                spider.logger.warning(
                    f" Could not convert original_price: {adapter.get('original_price')}"

                )
        return item

class PriceToZARPipeline:
    ksh_to_zar_rate = 0.15

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('current_price'):
            try:
                original_ksh = adapter['current_price']
                adapter['current_price'] = round(
                    adapter['current_price'] * self.ksh_to_zar_rate,
                    2
                )
                spider.logger.debug(
                    f" Converted {original_ksh} KSh → {adapter['current_price']} ZAR"
                )
            except (TypeError, ValueError) as e:
                spider.logger.warning(
                    f" Could not convert original price: {e}"
                )
        adapter['currency'] = 'ZAR'
        return item
    
class DropNoPricePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get('current_price'):
            return item
        else:
            spider.logger.warning(
                f" Dropping item (no price): {adapter.get('name', 'Unknown')}"
            )
            raise DropItem(f"Missing price in {adapter.get('name', 'item')}")

class DuplicatesPipeline:
    def __init__(self):
        self.names_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        product_name = adapter.get('name')

        if product_name in self.names_seen:
            spider.logger.warning(
                f" Duplicate found (dropping): {product_name}"
            )
            raise DropItem(f"Duplicate item: {product_name}")
        else:
            self.names_seen.add(product_name)
            spider.logger.debug(
                f" New unique product: {product_name}"
            )

class CalculateSavingsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        current = adapter.get('current_price')
        original = adapter.get('original_price')

        if current and original:
            try:
                savings = round(original - current, 2)
                adapter['savings_amount'] = savings

                if original > 0:
                    savings_percent = round((savings / original) * 100, 1)
                    adapter['savings_percent'] = f"{savings_percent}%"

                    spider.logger.debug(
                        f" Calculated savings: {savings} ZAR ({adapter.get('savings_percent')})"
                    )
            except (TypeError, ValueError) as e:
                spider.logger.warning(
                    f"Could not calculate saving: {e}"
                )
        return item
    
class ValidateItemPipeline:
    required_fields = ['name','product_id','current_price']
    
    def process_item(self,item,spider):
        adapter = ItemAdapter(item)

        missing_fields = []
        for field in self.required_fields:
            if not adapter.get(field):
                missing_fields.append(field)

        if missing_fields:
            spider.logger.error(
                f" Item missing required fields:{missing_fields}"
            )
            raise DropItem(
                f"Missing required field {missing_fields} in {adapter.get('name','unknown item')}"
            )
        return item
    
