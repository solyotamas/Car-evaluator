import re

def extract_car_extra_specs(car_page, text):
    wrapper = car_page.locator(
        'div.print-basic-info-item',
        has=car_page.locator('div.print-basic-info-item__label', has_text=text)
    )
    if wrapper.count() == 0:
        return None
    
    spec = wrapper.locator('div.row > div.col-6').nth(1).inner_text().strip()
    return spec

def extract_car_basic_specs(car_page, text):
    wrapper = car_page.locator(
        'div.print-highlighted-info__item',
        has=car_page.locator('div.small.text-body-secondary.mb-1', has_text=text)
    )
    if wrapper.count() == 0:
        return None
    
    spec = wrapper.locator('div > div').nth(1).inner_text().strip()
    return spec

def extract_car_vegyes_fogyasztas(car_page):
    wrapper = car_page.locator(
        'tr.align-middle',
        has=car_page.locator('td.text-body-secondary.col-6', has_text='Vegyes fogyasztás')
    )
    if wrapper.count() == 0:
        return None
    
    spec = wrapper.locator('td.col-6').nth(1).inner_text().strip()
    return spec

def extract_car_manufacturer_modell(car_page):
    manufacturer_modell_wrapper = car_page.locator('ol#breadcrumb')
    manufacturer_modell_wrapper_items = manufacturer_modell_wrapper.locator('li > a')

    manufacturer = manufacturer_modell_wrapper_items.nth(2).inner_text().strip()
    modell = manufacturer_modell_wrapper_items.nth(3).inner_text().strip()
    for i in range(4, manufacturer_modell_wrapper_items.count()):
        modell += " " + manufacturer_modell_wrapper_items.nth(i).inner_text().strip()

    return manufacturer, modell

# =========================

def clean_price(value: str) -> int:
    if not value:
        return None
    
    value = value.replace("Ft", "").replace(" ", "").replace("\xa0", "").strip()
    return int(value)

def clean_sale_price(value: str) -> int:
    if not value:
        return None
    
    value = value.replace("Akciós:", "").replace("Ft", "").replace(" ", "").replace("\xa0", "").strip()
    return int(value)

def clean_evjarat(value: str) -> float:
    if not value:
        return None
    
    match = re.match(r"(\d{4})(?:/(\d{1,2}))?", value)
    if not match:
        return None
    
    year = int(match.group(1))
    month = int(match.group(2)) if match.group(2) else 1

    decimal_year = year + (month - 1) / 12 
    return round(decimal_year, 2)

def clean_km_ora(value: str) -> int:
    if not value:
        return None
    
    km = re.sub(r"[^\d]", "", value)
    return int(km)

def clean_teljesitmeny(value: str):
    if not value:
        return None, None
    
    match = re.match(r"(\d+) kW, (\d+) LE", value)
    if not match:
        return (None, None)
    
    kw = int(match.group(1))
    le = int(match.group(2))
    return kw, le 

def clean_szemelyek_szama(value: str) -> int:
    if not value:
        return None
    
    szemelyek_szama = re.sub(r"[^\d]", "", value)
    return int(szemelyek_szama)

def clean_valto(value: str):
    if not value:
        return None, None, None
    
    main_type = value.split('(')[0].strip()
    
    inside = re.search(r'\((.*)\)', value)
    if inside:
        details = inside.group(1)
        
        gears_match = re.search(r'(\d+)', details)
        gears = int(gears_match.group(1)) if gears_match else None
        # Extract subtype (non-digit words inside parentheses)
        subtype = re.sub(r'\d+|fokozatú', '', details).strip() or None
    else:
        gears = None
        subtype = None
    
    return main_type, gears, subtype

def clean_hengerurtartalom(value: str) -> int:
    if not value:
        return None
    
    hengerurtartalom = re.sub(r"[^\d]", "", value)
    return int(hengerurtartalom)
