from playwright.sync_api import sync_playwright
import re
import pandas as pd
from datetime import datetime
import time
import random
from dotenv import load_dotenv
import os
from scrape_functions import(
    extract_car_extra_specs,
    extract_car_basic_specs,
    extract_car_vegyes_fogyasztas,
    extract_car_manufacturer_modell,

    clean_price,
    clean_sale_price,
    clean_evjarat,
    clean_km_ora,
    clean_teljesitmeny,
    clean_szemelyek_szama,
    clean_valto,
    clean_hengerurtartalom
)
from itertools import cycle




# Credentials 

load_dotenv("shhh.env")
username = os.getenv("PROXY_USERNAME")
password = os.getenv("PROXY_PASSWORD")
proxy_ips = os.getenv("PROXIES").split(',')
ports = os.getenv("PORTS").split(',')
port = 12323

# ========

car_specs = []
car_data = []
    

page_num = 1
proxy_list = [
    f"http://{ip}:{port}"
    for ip in proxy_ips
]
proxy_cycle = cycle(proxy_list)


# ========

with sync_playwright() as pw:
    browser = None
    
    context = None
    main_page = None
    car_page = None

    # =============================

    while True:

        if (page_num - 1)  % 5 == 0:
            if car_page:
                car_page.close()
            if main_page:
                main_page.close()
            if context:
                context.close()
            if browser:
                browser.close()

            
            proxy = next(proxy_cycle)
            print(f"Switching proxy to: {proxy}")

            # New context and pages with the proxy
            browser = pw.chromium.launch(headless=False, args=[f"--proxy-server={proxy}"])
            context = browser.new_context(proxy={"server": proxy, "username":username, "password":password})
            main_page = context.new_page()
            main_page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            main_page.goto(f"https://www.hasznaltauto.hu/talalatilista/PCOHKVCBN3RTADH4RNPZAOCJXOVRY52RUBABD5GUVPA5VDFDLAJAHCJWTICP362SW2JVURXWMRREMIRZEPJKBVQLOUGWVGNLVQA4NGV4QYOXNWKWWCS4VQQFFWNDHNCMHW2FMGMY6TQG5RAP3JL4QGB2VAQFZMXNU5NIYSJ2QEG7RQTKC6JSYVEWZUM7RGRSDOKWD24L4TPO4EIRV7O6WS2VA6DIWI3Y3P3HSVFW5S746KVLYGBSWNIYDUPBZSFDKIYOIHTQKLZRGPM2AMZD3ID7VNGPVI5ADGMYWW4ZXEW7IASHQ3RQ2F5BPNISARV5KY2GFSZ3GYITYBLPMJCY3R6QDIHLCALJHXP7JHP4TK74DH7A66ET734HWMT7PIJLDSF6NEV7NQBZG7OTQHPT2WLCJXXLKGXIU77NNR7LNZKLZOBJ23Q4KD3XWSVV7NDB6Q7QTK5SFAH6A25BRKJJZQ4SNFBMH73JKFQMCN2Q5CYYC2BOKVUMYHMREOWE63JYUKM42ETW6I4MBKLZO5YGEXVDHN4SYMY6CL77MMW5ZSGZ2D3IIISRGKT5WWZBTYGOKDP7HARROARM5NVAG3VKVB7R57DUJK7FCDTTDTUHPAK6HVIQV5R3YHTCPHGG6CKW4I63UGT55N454WGKUW5RGHJ6GI2YKDFUQUPZDLOBQAESUIWEIWB7MQSNNRNE4XL3QPR3MW3ATC7LUHFGCAXI23CCGPCZ7YRQ2BPH6JJDEIUBU3BYBZKCRYGTIBZCTVRQVUGLNUZTTDIZ4YXNERN37HPIHN6WTSE5XMUSOTTAHDGRV3OI2GATZVKT7R47RW6IPJHFCWPOYZUJWSENX4F2TBXORSQ5RE5PYHMETH67QPE3EGD7VFWC3OSJWPP76ABZU2WZU/page{page_num}")
            car_page = context.new_page()
            car_page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Accept cookie
            cookieButton = main_page.locator("#didomi-notice-agree-button")
            cookieButton.wait_for(state="visible", timeout=0)
            cookieButton.click()

        

        print("Page number: ", page_num, '\n')

        # Car listings on the page given page
        listings = main_page.locator('div.row.talalati-sor')
        count = listings.count()

        for i in range(count):
            # Price, Sale Price 
            price_locator = listings.nth(i).locator('div.pricefield-primary').first
            sale_locator = listings.nth(i).locator('div.pricefield-secondary-basic').first
            price = price_locator.inner_text().strip() if price_locator.count() > 0 else None
            sale = sale_locator.inner_text().strip() if sale_locator.count() > 0 else None

            # URL, ID, 
            car_listing_element = main_page.locator('.row.talalati-sor').nth(i)
            car_listing_link_element = car_listing_element.locator('h3 > a').first
            href = car_listing_link_element.get_attribute('href')
            id_search = re.search(r'-(\d+)(?:[#?]|$)', href)
            id = id_search.group(1)


            # Navigating to specific car pages
            try:
                print("Trying to load car page..")
                car_page.goto(href, timeout=60000)
                
            except TimeoutError:      
                continue

            # Manufacturer, Modell
            manufacturer, modell = extract_car_manufacturer_modell(car_page = car_page)
        
            # Basics
            evjarat = extract_car_basic_specs(car_page = car_page, text = 'Évjárat')
            km_ora = extract_car_basic_specs(car_page = car_page, text = 'Km. óra állás')
            uzemanyag = extract_car_basic_specs(car_page = car_page, text = 'Üzemanyag')
            teljesitmeny = extract_car_basic_specs(car_page = car_page, text = 'Teljesítmény')
            allapot = extract_car_basic_specs(car_page = car_page, text = 'Állapot')
            csomagtarto = extract_car_basic_specs(car_page = car_page, text = 'Csomagtartó')
            #print(evjarat, km_ora, uzemanyag, teljesitmeny, allapot, csomagtarto, sep='\n')

            # Extra
            kivitel = extract_car_extra_specs(car_page = car_page, text = 'Kivitel')
            szemelyek_szama = extract_car_extra_specs(car_page = car_page, text = 'Szállítható szem. száma')
            szin = extract_car_extra_specs(car_page = car_page, text = 'Szín')
            hengerurtartalom = extract_car_extra_specs(car_page = car_page, text = 'Hengerűrtartalom')
            hajtas = extract_car_extra_specs(car_page = car_page, text = 'Hajtás')
            valto = extract_car_extra_specs(car_page = car_page, text = 'Sebességváltó')
            #print(kivitel, szemelyek_szama, szin, hengerurtartalom, hajtas, valto, sep='\n')

            # Fogyasztas
            vegyes_fogyasztas = extract_car_vegyes_fogyasztas(car_page = car_page)
            #print(vegyes_fogyasztas, sep='\n')

            
            
            # =====================

            car_specs.append({
                'id': id, 
                'price': price,
                'sale price': sale,
                'gyarto': manufacturer,
                'modell': modell,
                'evjarat' : evjarat,
                'km ora' : km_ora,
                'uzemenyag': uzemanyag,
                'teljesitmeny' : teljesitmeny,
                'allapot' : allapot,
                'csomagtarto' : csomagtarto,
                'kivitel' : kivitel,
                'szemelyek_szama' : szemelyek_szama,
                'szin' : szin,
                'hengerurtartalom': hengerurtartalom,
                'hajtas' : hajtas,
                'valto' : valto,
                'vegyes fogyasztas' : vegyes_fogyasztas
            })
            
            car_data.append({
                'id' : id,
                'active' : True,
                'first seen' : datetime.now().replace(second=0, microsecond=0),
                'last seen' : datetime.now().replace(second=0, microsecond=0),
                'url' : href
            })


        # Next page
        next_button = main_page.locator('ul.pagination > li.next').first

        if next_button.is_enabled():
            next_button.click()
            main_page.wait_for_load_state('load')
            page_num += 1
        else:
            break

        
    car_page.close()
    main_page.close()


    df1 = pd.DataFrame(car_specs)
    df2 = pd.DataFrame(car_data)

    df1.to_csv('car_specs.csv', index=False)
    df2.to_csv('car_data.csv', index=False)

