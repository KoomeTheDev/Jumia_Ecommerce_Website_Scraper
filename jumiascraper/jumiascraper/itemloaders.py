from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader
import re


class JumiaProductLoader(ItemLoader):
    default_output_processor = TakeFirst()
    
    name_in = MapCompose(
        str.strip,  
        lambda x: re.sub(r'\s+', ' ', x)  
    )
    
    current_price_in = MapCompose(
        lambda x: x.strip() if x else None,  # Remove spaces
        lambda x: x.replace('KSh', '').replace('Ksh', '').replace('ksh', '').strip() if x else None,  # Remove "KSh"
        lambda x: x.replace(',', '').replace(' ', '') if x else None,  # Remove commas AND spaces
        lambda x: x if x and x.replace('.', '').isdigit() else None  # Only keep if it's a number
    )
    
    original_price_in = MapCompose(
        lambda x: x.strip() if x else None,
        lambda x: x.replace('KSh', '').replace('Ksh', '').replace('ksh', '').strip() if x else None,
        lambda x: x.replace(',', '').replace(' ', '') if x else None,
        lambda x: x if x and x.replace('.', '').isdigit() else None
    )
    
    discount_in = MapCompose(
        str.strip
    )

    url_in = MapCompose(
        str.strip
    )
    
    full_url_in = MapCompose(
        str.strip,
        lambda x: f'https://www.jumia.co.ke{x}' if x and not x.startswith('http') else x
    )
    

    image_in = MapCompose(
        str.strip,
        lambda x: x if x and x.startswith('http') else None
    )
    
    brand_in = MapCompose(
        str.strip,
        lambda x: x.title() if x else None  # Capitalize first letter
    )
    
    product_id_in = MapCompose(
        str.strip
    )

def remove_currency_symbol(value):
    if not value:
        return None
    # Remove common currency symbols
    return re.sub(r'[KSh$£€¥₹]', '', value).strip()


def clean_number(value):
    """
    Clean numeric strings: remove commas and spaces
    """
    if not value:
        return None
    return re.sub(r'[,\s]', '', value)


def to_float(value):
    """
    Convert string to float (for calculations)
    """
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


# ===== OPTIONAL: More Advanced Item Loader =====

class JumiaProductLoaderAdvanced(ItemLoader):
    """
    Advanced version with more aggressive cleaning
    and type conversion
    """
    
    default_output_processor = TakeFirst()
    
    # Clean and convert prices to floats
    current_price_in = MapCompose(
        str.strip,
        remove_currency_symbol,
        clean_number,
        to_float
    )
    
    original_price_in = MapCompose(
        str.strip,
        remove_currency_symbol,
        clean_number,
        to_float
    )
    
    # Extract just the number from discount
    # "25%" → "25"
    discount_in = MapCompose(
        str.strip,
        lambda x: re.sub(r'[^\d.]', '', x) if x else None
    )
    
    # All other fields same as basic version
    name_in = MapCompose(str.strip, lambda x: re.sub(r'\s+', ' ', x))
    url_in = MapCompose(str.strip)
    full_url_in = MapCompose(
        str.strip,
        lambda x: f'https://www.jumia.co.ke{x}' if x and not x.startswith('http') else x
    )
    image_in = MapCompose(str.strip)
    brand_in = MapCompose(str.strip, lambda x: x.title() if x else None)
    product_id_in = MapCompose(str.strip)