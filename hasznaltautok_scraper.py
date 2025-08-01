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
    clean_csomagtarto,
    clean_szemelyek_szama,
    clean_valto,
    clean_hengerurtartalom,
    clean_vegyes_fogyasztas,

    switch_proxy,
    wait_for_car_page_load,
    wait_for_main_page_load
)
from itertools import cycle
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright._impl._errors import Error as PlaywrightError



# ======== 

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
    browser = pw.chromium.launch(headless=False)
    
    context = None
    main_page = None
    car_page = None

    # =============================

    for k in range(0,100):

        if (page_num - 1)  % 5 == 0:
            context, main_page, car_page = switch_proxy(
                proxy_cycle=proxy_cycle,
                browser=browser,
                context=context,
                main_page=main_page,
                car_page=car_page,
                username=username,
                password=password,
                page_num=page_num
            )  
            
            max_retries_with_current_proxy_main_page = 3
            retries_main_page = 0

            while True:
                try:
                    main_page.goto(f"https://www.hasznaltauto.hu/talalatilista/PCOHKVCBN3RTADH4RNPZAOCJXOVRY52RUBABD5GUVPA5VDFDLAJAHCJWTICP362SW2JVURXWMRREMIRZEPJKBVQLOUGWVGNLVQA4NGV4QYOXNWKWWCS4VQQFFWNDHNCMHW2FMGMY6TQG5RAP3JL4QGB2VAQFZMXNU5NIYSJ2QEG7RQTKC6JSYVEWZUM7RGRSDOKWD24L4TPO4EIRV7O6WS2VA6DIWI3Y3P3HSVFW5S746KVLYGBSWNIYDUPBZSFDKIYOIHTQKLZRGPM2AMZD3ID7VNGPVI5ADGMYWW4ZXEW7IASHQ3RQ2F5BPNISARV5KY2GFSZ3GYITYBLPMJCY3R6QDIHLCALJHXP7JHP4TK74DH7A66ET734HWMT7PIJLDSF6NEV7NQBZG7OTQHPT2WLCJXXLKGXIU77NNR7LNZKLZOBJ23Q4KD3XWSVV7NDB6Q7QTK5SFAH6A25BRKJJZQ4SNFBMH73JKFQMCN2Q5CYYC2BOKVUMYHMREOWE63JYUKM42ETW6I4MBKLZO5YGEXVDHN4SYMY6CL77MMW5ZSGZ2D3IIISRGKT5WWZBTYGOKDP7HARROARM5NVAG3VKVB7R57DUJK7FCDTTDTUHPAK6HVIQV5R3YHTCPHGG6CKW4I63UGT55N454WGKUW5RGHJ6GI2YKDFUQUPZDLOBQAESUIWEIWB7MQSNNRNE4XL3QPR3MW3ATC7LUHFGCAXI23CCGPCZ7YRQ2BPH6JJDEIUBU3BYBZKCRYGTIBZCTVRQVUGLNUZTTDIZ4YXNERN37HPIHN6WTSE5XMUSOTTAHDGRV3OI2GATZVKT7R47RW6IPJHFCWPOYZUJWSENX4F2TBXORSQ5RE5PYHMETH67QPE3EGD7VFWC3OSJWPP76ABZU2WZU/page{page_num}")
                    wait_for_main_page_load(main_page = main_page)

                    '''
                    # Cookie button
                    cookieButton = main_page.locator("#didomi-notice-agree-button")
                    try:
                        cookieButton.wait_for(state="visible", timeout=30000)
                        if cookieButton.is_enabled():
                            cookieButton.click()
                            print("✔ Cookie button clicked")
                    except PlaywrightTimeoutError:
                        print("Cookie button not visible (timeout) — probably not shown")
                    except PlaywrightError as e:
                        print(f"Unexpected error with cookie button: {e}")
                    '''
                    break

                except (PlaywrightTimeoutError, PlaywrightError):
                    retries_main_page += 1
                    print(f"Attempt {retries_main_page} failed with current proxy while loading main page")

                    if retries_main_page >= max_retries_with_current_proxy_main_page:
                        print("Max retries reached, switching proxy")
                        context, main_page, car_page = switch_proxy(
                            proxy_cycle=proxy_cycle,
                            browser=browser,
                            context=context,
                            main_page=main_page,
                            car_page=car_page,
                            username=username,
                            password=password,
                            page_num=page_num
                        )
                        retries_main_page = 0
                        continue
                    else:
                        print("Retrying with current proxy.")
                        continue


        # Car listings on the page given page
        print('finding listings')
        listings = main_page.locator('div.row.talalati-sor')
        print('found')
        count = listings.count()
        print("Page number: ", page_num, '\n')


        for i in range(count):

            max_retries_with_current_proxy_car_page = 3
            retries_car_page = 0
            while True:
                try:
                    car_listing_element = listings.nth(i)
                    car_listing_link_element = car_listing_element.locator('h3 > a').first
                    href = car_listing_link_element.get_attribute('href')

                    car_page.goto(href, wait_until='domcontentloaded')
                    wait_for_car_page_load(car_page = car_page)
                    break

                except (PlaywrightTimeoutError, PlaywrightError):
                    retries_car_page += 1
                    print(f"Attempt {retries_car_page} failed with current proxy while loading car page.")

                    if retries_car_page >= max_retries_with_current_proxy_car_page:
                        print("Max retries reached, switching proxy")
                        context, main_page, car_page = switch_proxy(
                            proxy_cycle=proxy_cycle,
                            browser=browser,
                            context=context,
                            main_page=main_page,
                            car_page=car_page,
                            username=username,
                            password=password,
                            page_num=page_num
                        )
                        listings = main_page.locator('div.row.talalati-sor')
                        retries_car_page = 0
                        continue
                    else:
                        print("Retrying with current proxy.")
                        continue



            # On Main Page
            # Price, Sale Price 
            price_locator = listings.nth(i).locator('div.pricefield-primary').first
            sale_locator = listings.nth(i).locator('div.pricefield-secondary-basic').first
            price = price_locator.inner_text().strip() if price_locator.count() > 0 else None
            sale = sale_locator.inner_text().strip() if sale_locator.count() > 0 else None

            # URL, ID, 
            id_search = re.search(r'-(\d+)(?:[#?]|$)', href)
            id = id_search.group(1)

            
            
            # On Car Page  
            # Manufacturer, Modell
            manufacturer, modell = extract_car_manufacturer_modell(car_page = car_page)
            # Basics
            evjarat = extract_car_basic_specs(car_page = car_page, text = 'Évjárat')
            km_ora = extract_car_basic_specs(car_page = car_page, text = 'Km. óra állás')
            uzemanyag = extract_car_basic_specs(car_page = car_page, text = 'Üzemanyag')
            teljesitmeny = extract_car_basic_specs(car_page = car_page, text = 'Teljesítmény')
            allapot = extract_car_basic_specs(car_page = car_page, text = 'Állapot')
            csomagtarto = extract_car_basic_specs(car_page = car_page, text = 'Csomagtartó')
            # Extra
            kivitel = extract_car_extra_specs(car_page = car_page, text = 'Kivitel')
            szemelyek_szama = extract_car_extra_specs(car_page = car_page, text = 'Szállítható szem. száma')
            szin = extract_car_extra_specs(car_page = car_page, text = 'Szín')
            hengerurtartalom = extract_car_extra_specs(car_page = car_page, text = 'Hengerűrtartalom')
            hajtas = extract_car_extra_specs(car_page = car_page, text = 'Hajtás')
            valto = extract_car_extra_specs(car_page = car_page, text = 'Sebességváltó')
            # Fogyasztas
            #vegyes_fogyasztas = extract_car_vegyes_fogyasztas(car_page = car_page)

            
            # =====================

            # Cleaning
            # Car specs table
            id = id
            price = clean_price(price)
            sale = clean_sale_price(sale)
            manufacturer = manufacturer
            modell = modell
            evjarat = clean_evjarat(evjarat)
            km_ora = clean_km_ora(km_ora)
            uzemanyag = uzemanyag
            kw, le = clean_teljesitmeny(teljesitmeny)
            allapot = allapot
            csomagtarto = clean_csomagtarto(csomagtarto)
            kivitel = kivitel
            szemelyek_szama = clean_szemelyek_szama(szemelyek_szama)
            szin = szin
            hengerurtartalom = clean_hengerurtartalom(hengerurtartalom)
            hajtas = hajtas
            valto_tipus, valto_szam, valto_subtipus = clean_valto(valto)
            #vegyes_fogyasztas = clean_vegyes_fogyasztas(vegyes_fogyasztas)
            
            
            car_specs.append({
                'id': id, 
                'price': price,
                'sale price': sale,
                'gyarto': manufacturer,
                'modell': modell,
                'evjarat' : evjarat,
                'km ora' : km_ora,
                'uzemenyag': uzemanyag,
                'KW' : kw,
                'LE' : le,
                'allapot' : allapot,
                'csomagtarto' : csomagtarto,
                'kivitel' : kivitel,
                'szemelyek_szama' : szemelyek_szama,
                'szin' : szin,
                'hengerurtartalom': hengerurtartalom,
                'hajtas' : hajtas,
                'valto tipus' : valto_tipus,
                'valto szam' : valto_szam,
                'valto subtipus' : valto_subtipus
                #'vegyes fogyasztas': vegyes_fogyasztas
            })
            print({
                'id': id, 
                'price': price,
                'sale price': sale,
                'gyarto': manufacturer,
                'modell': modell,
                'evjarat' : evjarat,
                'km ora' : km_ora,
                'uzemenyag': uzemanyag,
                'KW' : kw,
                'LE' : le,
                'allapot' : allapot,
                'csomagtarto' : csomagtarto,
                'kivitel' : kivitel,
                'szemelyek_szama' : szemelyek_szama,
                'szin' : szin,
                'hengerurtartalom': hengerurtartalom,
                'hajtas' : hajtas,
                'valto tipus' : valto_tipus,
                'valto szam' : valto_szam,
                'valto subtipus' : valto_subtipus
                #'vegyes fogyasztas' : vegyes_fogyasztas
            })
            
            
            car_data.append({
                'id' : id,
                'active' : True,
                'first seen' : datetime.now().replace(second=0, microsecond=0),
                'last seen' : datetime.now().replace(second=0, microsecond=0),
                'url' : href
            })

            print('Scraped: ' + str(i))
            

        # Next page
        next_button = main_page.locator('ul.pagination > li.next').first

        if next_button.is_enabled():
            retry_count_next_button = 0
            max_retries_next_button = 3
            while True:
                try:
                    next_button.click()
                    wait_for_main_page_load(main_page= main_page)

                    

                    page_num += 1
                    break
                    
                except (PlaywrightTimeoutError, PlaywrightError):
                    retry_count_next_button += 1
                    print(f"Attempt {max_retries_next_button} failed with current proxy while loading next main page")

                    if retry_count_next_button >= max_retries_next_button:
                        print("Max retries reached, switching proxy")
                        context, main_page, car_page = switch_proxy(
                            proxy_cycle=proxy_cycle,
                            browser=browser,
                            context=context,
                            main_page=main_page,
                            car_page=car_page,
                            username=username,
                            password=password,
                            page_num=page_num
                        )
                        max_retries_next_button = 0
                        continue
                    else:
                        print("Retrying with current proxy.")
                        continue
                
        

        
    car_page.close()
    main_page.close()
    context.close()
    browser.close()


    df1 = pd.DataFrame(car_specs)
    df2 = pd.DataFrame(car_data)

    df1.to_csv('car_specs.csv', index=False)
    df2.to_csv('car_data.csv', index=False)

