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

    switch_proxy
)
from itertools import cycle
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright._impl._errors import Error as PlaywrightError



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
    # browser = pw.chromium.launch(headless=False, args=[f"--proxy-server={proxy}"])
    browser = pw.chromium.launch(headless=False)
    
    context = None
    main_page = None
    car_page = None

    # =============================

    for k in range(0,100):

        if (page_num - 1)  % 5 == 0:
            context, main_page, car_page = switch_proxy(proxy_cycle = proxy_cycle, browser = browser, context = context,
                main_page = main_page, car_page = car_page, username = username, password = password, page_num = page_num              
            )
            time.sleep(random.uniform(3, 5))
            
            listings = main_page.locator('div.row.talalati-sor')
            count = listings.count()
            
            df1 = pd.DataFrame(car_specs)
            df2 = pd.DataFrame(car_data)

            df1.to_csv('car_specs.csv', index=False)
            df2.to_csv('car_data.csv', index=False)
            print(f"✔ Data saved")
        


        print("Page number: ", page_num, '\n')

        # Car listings on the page given page
        listings = main_page.locator('div.row.talalati-sor')
        count = listings.count()

        for i in range(count):

            while True:
                try:
                    #listings = main_page.locator('div.row.talalati-sor')
                    car_listing_element = listings.nth(i)
                    car_listing_link_element = car_listing_element.locator('h3 > a').first
                    href = car_listing_link_element.get_attribute('href')

                    car_page.goto(href, timeout=60000)
                    break

                except PlaywrightTimeoutError:
                    print("Timeout Error")
                    context, main_page, car_page = switch_proxy(proxy_cycle = proxy_cycle, browser = browser, context = context,
                        main_page = main_page, car_page = car_page, username = username, password = password, page_num = page_num              
                    )
                    time.sleep(random.uniform(3, 5))

                    listings = main_page.locator('div.row.talalati-sor')
                    count = listings.count()
                    continue

                except PlaywrightError as e:
                    print("Other")
                    context, main_page, car_page = switch_proxy(proxy_cycle = proxy_cycle, browser = browser, context = context,
                        main_page = main_page, car_page = car_page, username = username, password = password, page_num = page_num              
                    )
                    time.sleep(random.uniform(3, 5))

                    listings = main_page.locator('div.row.talalati-sor')
                    count = listings.count()
                    continue



            # On Main Page
            # Price, Sale Price 
            price_locator = listings.nth(i).locator('div.pricefield-primary').first
            sale_locator = listings.nth(i).locator('div.pricefield-secondary-basic').first
            price = price_locator.inner_text().strip() if price_locator.count() > 0 else None
            sale = sale_locator.inner_text().strip() if sale_locator.count() > 0 else None

            # URL, ID, 
            href = href
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
            vegyes_fogyasztas = clean_vegyes_fogyasztas(vegyes_fogyasztas)

            # Car data table
            


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
                'valto subtipus' : valto_subtipus,
                'vegyes fogyasztas' : vegyes_fogyasztas
            })
            
            
            car_data.append({
                'id' : id,
                'active' : True,
                'first seen' : datetime.now().replace(second=0, microsecond=0),
                'last seen' : datetime.now().replace(second=0, microsecond=0),
                'url' : href
            })

            print('Scraped: ' + manufacturer + ' ' + modell)
            print(i)
            


        # Next page
        next_button = main_page.locator('ul.pagination > li.next').first

        if next_button.is_enabled():
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    next_button.click()
                    main_page.wait_for_load_state('load', timeout=60000)
                    page_num += 1
                    break  # success, exit retry loop
                except PlaywrightTimeoutError:
                    retry_count += 1
                    print(f"Pagination timeout, retrying... ({retry_count}/{max_retries})")
                    time.sleep(2)
                    if retry_count == max_retries:
                        print("Max retries reached. Switching proxy.")
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
                        time.sleep(random.uniform(3, 5))
                        break
        else:
            break

        
    car_page.close()
    main_page.close()
    context.close()
    browser.close()


    df1 = pd.DataFrame(car_specs)
    df2 = pd.DataFrame(car_data)

    df1.to_csv('car_specs.csv', index=False)
    df2.to_csv('car_data.csv', index=False)

