from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join
import re

class JumiaProductLoader(ItemLoader):
    default_output_processor = TakeFirst()

    # ===== NAME FIELD =====
    name_in = MapCompose(
        str.strip,
        lambda x: re.sub(r'\s+', ' ', x)
    )

    # ===== CURRENT PRICE FIELD =====
    current_price_in = MapCompose(
        str.strip,
        lambda x: x.replace('KSh', '').strip(),
        lambda x: x.replace(' ', ''),
        lambda x: x if x else None
    )

    # ===== ORIGINAL PRICE FIELD =====
    original_price_in = MapCompose(
        str.strip,
        lambda x: x.replace('KSh', '').strip(),
        lambda x: x.replace(',', ''),
        lambda x: x if x else None
    )
    # ===== DISCOUNT FIELD =====
    discount_in = MapCompose(
        str.strip
    )

    # ===== URL FIELD =====
    url_in = MapCompose(
        str.strip
    )

    # ===== FULL_URL FIELD =====
    full_url_in = MapCompose(
        str.strip,
        lambda x: f'https://www.jumia.co.ke{x}'if x and not x.startswith('http') else x
    )

    # ===== BRAND FIELD =====
    brand_in = MapCompose(
        str.strip,
        lambda x: x.title() if x else None
    )

    # ===== PRODUCT_ID FIELD =====
    product_id_in = MapCompose(
        str.strip
    )

    





