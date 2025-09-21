import re
from playwright.sync_api import Browser, BrowserContext, Page
from playwright._impl._errors import Error as PlaywrightError 
from dotenv import load_dotenv
import os
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import time
import random
from datetime import datetime
from sql.models import CarData, CarDetails 
import json
import asyncio
from playwright.async_api import async_playwright
from twocaptcha import TwoCaptcha
import re

# =========================

API_KEY = os.getenv("2CAPTCHA_API_KEY")
solver = TwoCaptcha(API_KEY)


# =========================
def extract_car_basic_specs(car_page, text):
    wrapper = car_page.locator(
        'div.print-highlighted-info__item',
        has=car_page.locator('div.small.text-body-secondary.mb-1', has_text=text)
    )
    if wrapper.count() == 0:
        return None
    
    spec = wrapper.locator('div > div').nth(1).inner_text().strip()
    return spec

def extract_car_extra_specs(car_page, text):
    wrapper = car_page.locator(
        'div.print-basic-info-item',
        has=car_page.locator('div.print-basic-info-item__label', has_text=text)
    )
    if wrapper.count() == 0:
        return None
    
    spec = wrapper.locator('div.row > div.col-6').nth(1).inner_text().strip()
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

def build_car_dict(id, price, manufacturer, modell, evjarat, km_ora, uzemanyag, teljesitmeny, allapot,
    csomagtarto, kivitel, szemelyek_szama, szin, hengerurtartalom, hajtas, valto, href):
    
    # Cleaning
    price = clean_price(price)
    evjarat = clean_evjarat(evjarat)
    km_ora = clean_km_ora(km_ora)
    kw, le = clean_teljesitmeny(teljesitmeny)
    csomagtarto = clean_csomagtarto(csomagtarto)
    szemelyek_szama = clean_szemelyek_szama(szemelyek_szama)
    hengerurtartalom = clean_hengerurtartalom(hengerurtartalom)
    valto_tipus, valto_szam, valto_subtipus = clean_valto(valto)
    
    # Build dicts
    car_details = {
        'id': id,
        'price': price,
        'manufacturer': manufacturer,
        'model': modell,
        'year': evjarat,
        'kilometers': km_ora,
        'fuel_type': uzemanyag,
        'kw': kw,
        'le': le,
        'condition': allapot,
        'trunk_capacity': csomagtarto,
        'body_type': kivitel,
        'seats': szemelyek_szama,
        'color': szin,
        'engine_capacity': hengerurtartalom,
        'drive_type': hajtas,
        'transmission_type': valto_tipus,
        'number_of_gears': valto_szam,
        'transmission_subtype': valto_subtipus
    }

    car_data = {
        'id': id,
        'active': True,
        'first_seen': datetime.now().replace(second=0, microsecond=0),
        'last_seen': datetime.now().replace(second=0, microsecond=0),
        'url': href
    }

    return car_details, car_data

# ========================== SQL
def load_existing_ids(session):
    existing_ids = session.query(CarData.id).all()
    id_set = {id[0] for id in existing_ids}
    
    print(f"Loaded {len(id_set)} existing IDs into cache")
    return id_set

def update_existing_car(session, car_id, new_price):
    """
        Update existing car's price and last_seen timestamp
    """
    car_detail = session.get(CarDetails, car_id)
    car_data = session.get(CarData, car_id)
    
    
    if car_detail.price != new_price:
        print(f"Price updated for ID {car_id}: {car_detail.price} -> {new_price}")
        car_detail.price = new_price
    
    car_data.last_seen = datetime.now().replace(second=0, microsecond=0)
    car_data.active = True
    
    session.commit()



# ==========================
'''
async def solve_turnstile_challenge(url, proxy_config=None, timeout=300):
    """
    Solve Turnstile challenge and return success status
    
    Args:
        url: The URL that has the Turnstile challenge
        proxy_config: Dict with proxy settings {"server": "http://ip:port", "username": "user", "password": "pass"}
        api_key: 2captcha API key
        timeout: Max time to wait for challenge solving
    
    Returns:
        bool: True if challenge was solved successfully, False otherwise
    """
    
    
    challenge_solved = False
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(proxy=proxy_config)
            
        page = await context.new_page()
        
        # Load inject.js content
        script_dir = os.path.dirname(os.path.abspath(__file__))
        inject_js_path = os.path.join(script_dir, 'inject.js')

        with open(inject_js_path, 'r', encoding='utf-8') as f:
            inject_js = f.read()
        
        await page.add_init_script(inject_js)
        
        # Console message handler
        async def handle_console(msg):
            nonlocal challenge_solved
            txt = msg.text
            if 'intercepted-params:' in txt:
                params_json = txt.replace('intercepted-params:', '')
                params = json.loads(params_json)
                print("Intercepted Turnstile params")
                
                try:
                    print("Solving captcha...")
                    
                    result = solver.turnstile(
                        sitekey=params['sitekey'],
                        url=params['pageurl'],
                        data=params.get('data'),
                        pagedata=params.get('pagedata'),
                        action=params.get('action'),
                        useragent=params.get('userAgent')
                    )
                    
                    print(f"Captcha solved: {result['captchaId']}")
                    token = result['code']
                    
                    # Call the callback with the token
                    await page.evaluate(f"cfCallback('{token}')")
                    challenge_solved = True
                    
                except Exception as e:
                    print(f"Error solving captcha: {e}")
        
        page.on('console', handle_console)
        
        try:
            await page.goto(url)
            
            # Wait for challenge to be solved or timeout
            start_time = asyncio.get_event_loop().time()
            while not challenge_solved and (asyncio.get_event_loop().time() - start_time) < timeout:
                await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Error navigating to challenge page: {e}")
        
        await browser.close()
    
    return challenge_solved

def handle_challenge_in_sync_scraper(url, proxy_config):
    """
    Wrapper to call async Turnstile solver from sync code
    """
    import threading
    import asyncio

    result = [False]
    
    def async_worker():
        try:
            # Create fresh event loop in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async function
            result[0] = loop.run_until_complete(
                solve_turnstile_challenge(url, proxy_config)
            )
            
            loop.close()
        except Exception as e:
            print(f"Async worker error: {e}")
    
    # Run in separate thread
    worker = threading.Thread(target=async_worker)
    worker.start()
    worker.join(timeout=300)  # 5 minute timeout
    
    return result[0]
'''
# ==========================

def wait_for_main_page_load(main_page : Page, timeout : int = 45000):
    try:

        main_page.locator('div.row.talalati-sor').first.wait_for(state="visible", timeout=timeout)
        main_page.locator('ul.pagination > li.next').last.wait_for(state="attached", timeout=timeout)
        print("Main page loaded")

    except PlaywrightTimeoutError:
        print("Main page not loaded (timeout)")
        raise
    except PlaywrightError as e:
        print(f"Unexpected error with main page load: {e}")
        raise

def wait_for_car_page_load(car_page: Page, timeout: int = 45000):
    try:
        print("Waiting for - Essential stats to appear")
        car_page.locator('div.print-highlighted-info__item').first.wait_for(state="visible", timeout=timeout)
        
        print("Waiting for - Basic stats to appear")
        car_page.locator('div.print-basic-info-item').first.wait_for(state="visible", timeout=timeout)
        
        print("Waiting for - Manufacturer and Model to appear")
        car_page.locator('ol#breadcrumb').wait_for(state="visible", timeout=timeout)

        print("Car page loaded successfully.")
    except PlaywrightTimeoutError as e:
        print(f"Car page not loaded (timeout) on selector: {e}")
        raise
    except PlaywrightError as e:
        print(f"Unexpected error with car page load: {e}")
        raise

def switch_proxy(proxy_cycle, browser : Browser, context : BrowserContext, main_page : Page, car_page : Page, username, password, page_num):
    if car_page:
        car_page.close()
    if main_page:
        main_page.close()
    if context:
        context.close()

        

    # Proxy
    proxy = next(proxy_cycle)
    print(f"Switching proxy to: {proxy}")


    # Context
    context = browser.new_context(proxy={"server": proxy, "username":username, "password":password})

    enhanced_stealth = """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        delete window.chrome.runtime.onConnect;
        delete window.chrome.runtime.onMessage;
        window.chrome = {runtime: {}};
    """

    # Main page
    main_page = context.new_page()
    #main_page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Car page
    car_page = context.new_page()
    #car_page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    main_page.add_init_script(enhanced_stealth)
    car_page.add_init_script(enhanced_stealth)
    # Stabilize proxy
    time.sleep(random.uniform(2, 3))

    return context, main_page, car_page, proxy