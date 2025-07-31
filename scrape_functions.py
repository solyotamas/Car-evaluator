import re
from playwright.sync_api import Browser, BrowserContext, Page
from dotenv import load_dotenv
import os
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# =========================

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

    # Manufacturer
    manufacturer = manufacturer_modell_wrapper_items.nth(2).inner_text().strip()

    # Modell
    count = manufacturer_modell_wrapper_items.count()
    if count > 3:
        modell = manufacturer_modell_wrapper_items.nth(3).inner_text().strip()
        for i in range(4, count):
            modell += " " + manufacturer_modell_wrapper_items.nth(i).inner_text().strip()
    else:
        modell = None

    return manufacturer, modell

# =========================

def clean_price(value: str) -> int:
    if not value:
        return None
    
    value = value.replace("Ft", "").replace(" ", "").replace("\xa0", "").strip()
    return int(value) if value.isdigit() else None

def clean_sale_price(value: str) -> int:
    if not value:
        return None
    
    value = value.replace("Akciós:", "").replace("Ft", "").replace(" ", "").replace("\xa0", "").strip()
    return int(value) if value.isdigit() else None

def clean_evjarat(value: str) -> float:
    if not value or not re.match(r"^\d{4}", value):
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

    return int(km) if km else None # sometimes nem skippelik hanem texttel adjak meg pl.: Nincs megadva

def clean_teljesitmeny(value: str):
    if not value:
        return None, None
    
    match = re.match(r"(\d+) kW, (\d+) LE", value)
    if not match:
        return None, None
    
    kw = int(match.group(1))
    le = int(match.group(2))
    return kw, le 

def clean_szemelyek_szama(value: str) -> int:
    if not value:
        return None
    
    szemelyek_szama = re.sub(r"[^\d]", "", value)
    return int(szemelyek_szama) if szemelyek_szama else None

def clean_valto(value: str):
    if not value:
        return None, None, None
    
    main_type = value.split('(')[0].strip()
    
    inside = re.search(r'\((.*)\)', value)
    if inside:
        details = inside.group(1)
        
        gears_match = re.search(r'(\d+)', details)
        gears = int(gears_match.group(1)) if gears_match else None
        
        subtype = re.sub(r'\d+|fokozatú', '', details).strip() or None
    else:
        gears = None
        subtype = None
    
    return main_type, gears, subtype

def clean_hengerurtartalom(value: str) -> int:
    if not value:
        return None
    
    hengerurtartalom = re.sub(r"[^\d]", "", value)
    return int(hengerurtartalom) if hengerurtartalom else None

def clean_csomagtarto(value: str):
    if not value:
        return None
    
    csomagtarto = re.sub(r"[^\d]", "", value)
    return int(csomagtarto) if csomagtarto else None

def clean_vegyes_fogyasztas(value: str) -> float:
    if not value:
        return None

    match = re.search(r'(\d+)(?:,(\d+))?\s*l/100km', value)
    if not match:
        return None

    whole = match.group(1)
    fraction = match.group(2) if match.group(2) else "0"

    return float(f"{whole}.{fraction}")

# ==========================

def switch_proxy(proxy_cycle, browser : Browser, context : BrowserContext, main_page : Page, car_page : Page, username, password, page_num):
    if car_page:
        car_page.close()
    if main_page:
        main_page.close()
    if context:
        context.close()

    proxy = next(proxy_cycle)
    print(f"Switching proxy to: {proxy}")

    context = browser.new_context(proxy={"server": proxy, "username":username, "password":password})
    
    main_page = context.new_page()
    main_page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    main_page.goto(f"https://www.hasznaltauto.hu/talalatilista/PCOHKVCBN3RTADH4RNPZAOCJXOVRY52RUBABD5GUVPA5VDFDLAJAHCJWTICP362SW2JVURXWMRREMIRZEPJKBVQLOUGWVGNLVQA4NGV4QYOXNWKWWCS4VQQFFWNDHNCMHW2FMGMY6TQG5RAP3JL4QGB2VAQFZMXNU5NIYSJ2QEG7RQTKC6JSYVEWZUM7RGRSDOKWD24L4TPO4EIRV7O6WS2VA6DIWI3Y3P3HSVFW5S746KVLYGBSWNIYDUPBZSFDKIYOIHTQKLZRGPM2AMZD3ID7VNGPVI5ADGMYWW4ZXEW7IASHQ3RQ2F5BPNISARV5KY2GFSZ3GYITYBLPMJCY3R6QDIHLCALJHXP7JHP4TK74DH7A66ET734HWMT7PIJLDSF6NEV7NQBZG7OTQHPT2WLCJXXLKGXIU77NNR7LNZKLZOBJ23Q4KD3XWSVV7NDB6Q7QTK5SFAH6A25BRKJJZQ4SNFBMH73JKFQMCN2Q5CYYC2BOKVUMYHMREOWE63JYUKM42ETW6I4MBKLZO5YGEXVDHN4SYMY6CL77MMW5ZSGZ2D3IIISRGKT5WWZBTYGOKDP7HARROARM5NVAG3VKVB7R57DUJK7FCDTTDTUHPAK6HVIQV5R3YHTCPHGG6CKW4I63UGT55N454WGKUW5RGHJ6GI2YKDFUQUPZDLOBQAESUIWEIWB7MQSNNRNE4XL3QPR3MW3ATC7LUHFGCAXI23CCGPCZ7YRQ2BPH6JJDEIUBU3BYBZKCRYGTIBZCTVRQVUGLNUZTTDIZ4YXNERN37HPIHN6WTSE5XMUSOTTAHDGRV3OI2GATZVKT7R47RW6IPJHFCWPOYZUJWSENX4F2TBXORSQ5RE5PYHMETH67QPE3EGD7VFWC3OSJWPP76ABZU2WZU/page{page_num}")
    main_page.wait_for_load_state('load')

    car_page = context.new_page()
    car_page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    cookieButton = main_page.locator("#didomi-notice-agree-button")

    try:
        cookieButton.wait_for(state="visible", timeout=30000)
        if cookieButton.is_enabled():
            cookieButton.click()
            print("✔ Cookie button clicked")
    except PlaywrightTimeoutError:
        print("⌛ Cookie button not visible (timeout) — probably not shown")
    except Exception as e:
        print(f"⚠️ Unexpected error with cookie button: {e}")


    return context, main_page, car_page