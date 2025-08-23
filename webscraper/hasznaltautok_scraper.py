from playwright.sync_api import sync_playwright
import re
from dotenv import load_dotenv
import os
from webscraper.scrape_functions import(
    extract_car_extra_specs,
    extract_car_basic_specs,
    extract_car_manufacturer_modell,
    switch_proxy,
    wait_for_car_page_load,
    wait_for_main_page_load,
    build_car_dict,
    load_existing_ids,
    clean_price,
    update_existing_car,
)
from itertools import cycle
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright._impl._errors import Error as PlaywrightError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sql.models import CarData, CarDetails


# ======== ENV
load_dotenv("shhh.env")
username = os.getenv("PROXY_USERNAME")
password = os.getenv("PROXY_PASSWORD")
proxy_ips = os.getenv("PROXIES").split(',')
ports = os.getenv("PORTS").split(',')
# ======== SQL
engine_connection = os.getenv("SQL_ENGINE")
engine = create_engine(engine_connection)
Session = sessionmaker(bind=engine)
session = Session()
existing_car_ids_cache = load_existing_ids(session = session)
# ======== OTHER VARIABLES
car_details_page = []
car_data_page = []
    

page_num = 1
proxy_list = [
    f"http://{ip}:{port}" 
    for port in ports 
    for ip in proxy_ips
]
proxy_cycle = cycle(proxy_list)



# =============================

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    
    context = None
    main_page = None
    car_page = None

    
    while True:
        
        '''
        Switching proxy every 10th page
        '''
        if (page_num - 1) % 10 == 0:
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
            
            while True:
                try:
                    main_page.goto(f"https://www.hasznaltauto.hu/talalatilista/PCOHKVCBN3RTADH4RNPZAOCJXOVRY52RUBABD5GUVPA5VDFDLAJAHCJWTICP362SW2JVURXWMRREMIRZEPJKBVQLOUGWVGNLVQA4NGV4QYOXNWKWWCS4VQQFFWNDHNCMHW2FMGMY6TQG5RAP3JL4QGB2VAQFZMXNU5NIYSJ2QEG7RQTKC6JSYVEWZUM7RGRSDOKWD24L4TPO4EIRV7O6WS2VA6DIWI3Y3P3HSVFW5S746KVLYGBSWNIYDUPBZSFDKIYOIHTQKLZRGPM2AMZD3ID7VNGPVI5ADGMYWW4ZXEW7IASHQ3RQ2F5BPNISARV5KY2GFSZ3GYITYBLPMJCY3R6QDIHLCALJHXP7JHP4TK74DH7A66ET734HWMT7PIJLDSF6NEV7NQBZG7OTQHPT2WLCJXXLKGXIU77NNR7LNZKLZOBJ23Q4KD3XWSVV7NDB6Q7QTK5SFAH6A25BRKJJZQ4SNFBMH73JKFQMCN2Q5CYYC2BOKVUMYHMREOWE63JYUKM42ETW6I4MBKLZO5YGEXVDHN4SYMY6CL77MMW5ZSGZ2D3IIISRGKT5WWZBTYGOKDP7HARROARM5NVAG3VKVB7R57DUJK7FCDTTDTUHPAK6HVIQV5R3YHTCPHGG6CKW4I63UGT55N454WGKUW5RGHJ6GI2YKDFUQUPZDLOBQAESUIWEIWB7MQSNNRNE4XL3QPR3MW3ATC7LUHFGCAXI23CCGPCZ7YRQ2BPH6JJDEIUBU3BYBZKCRYGTIBZCTVRQVUGLNUZTTDIZ4YXNERN37HPIHN6WTSE5XMUSOTTAHDGRV3OI2GATZVKT7R47RW6IPJHFCWPOYZUJWSENX4F2TBXORSQ5RE5PYHMETH67QPE3EGD7VFWC3OSJWPP76ABZU2WZU/page{page_num}", wait_until='domcontentloaded')
                    wait_for_main_page_load(main_page = main_page)
                    break
                except (PlaywrightTimeoutError, PlaywrightError):
                    print(f"Switching proxy, failed to load main page")
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


        ''' 
        Car listings on the page given page
        '''
        listings = main_page.locator('div.row.talalati-sor')
        count = listings.count()
        print("Page number: ", page_num, '\n')


        for i in range(count):

            car_listing_element = listings.nth(i)
            car_listing_link_element = car_listing_element.locator('h3 > a').first
            href = car_listing_link_element.get_attribute('href')

            id_search = re.search(r'-(\d+)(?:[#?]|$)', href)
            id = id_search.group(1)
            id = int(id)


            price_locator = listings.nth(i).locator('div.pricefield-primary').first
            inactive_price_locator = listings.nth(i).locator('div.pricefield-inactive').first
            if price_locator.count() > 0:
                price = price_locator.inner_text().strip()
            elif inactive_price_locator.count() > 0:
                price = inactive_price_locator.inner_text().strip()
            else:
                price = None
            price = clean_price(price)


            if id in existing_car_ids_cache:
                print(f"ID {id} exists - updating if neccessary")
                update_existing_car(session, id, price)
                continue


            while True:
                try:
                    car_page.goto(href, wait_until='domcontentloaded')
                    wait_for_car_page_load(car_page = car_page)
                    break

                except (PlaywrightTimeoutError, PlaywrightError):
                    print(f"Switching proxy, failed to load car page.")
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

                    while True:
                        try:
                            main_page.goto(f"https://www.hasznaltauto.hu/talalatilista/PCOHKVCBN3RTADH4RNPZAOCJXOVRY52RUBABD5GUVPA5VDFDLAJAHCJWTICP362SW2JVURXWMRREMIRZEPJKBVQLOUGWVGNLVQA4NGV4QYOXNWKWWCS4VQQFFWNDHNCMHW2FMGMY6TQG5RAP3JL4QGB2VAQFZMXNU5NIYSJ2QEG7RQTKC6JSYVEWZUM7RGRSDOKWD24L4TPO4EIRV7O6WS2VA6DIWI3Y3P3HSVFW5S746KVLYGBSWNIYDUPBZSFDKIYOIHTQKLZRGPM2AMZD3ID7VNGPVI5ADGMYWW4ZXEW7IASHQ3RQ2F5BPNISARV5KY2GFSZ3GYITYBLPMJCY3R6QDIHLCALJHXP7JHP4TK74DH7A66ET734HWMT7PIJLDSF6NEV7NQBZG7OTQHPT2WLCJXXLKGXIU77NNR7LNZKLZOBJ23Q4KD3XWSVV7NDB6Q7QTK5SFAH6A25BRKJJZQ4SNFBMH73JKFQMCN2Q5CYYC2BOKVUMYHMREOWE63JYUKM42ETW6I4MBKLZO5YGEXVDHN4SYMY6CL77MMW5ZSGZ2D3IIISRGKT5WWZBTYGOKDP7HARROARM5NVAG3VKVB7R57DUJK7FCDTTDTUHPAK6HVIQV5R3YHTCPHGG6CKW4I63UGT55N454WGKUW5RGHJ6GI2YKDFUQUPZDLOBQAESUIWEIWB7MQSNNRNE4XL3QPR3MW3ATC7LUHFGCAXI23CCGPCZ7YRQ2BPH6JJDEIUBU3BYBZKCRYGTIBZCTVRQVUGLNUZTTDIZ4YXNERN37HPIHN6WTSE5XMUSOTTAHDGRV3OI2GATZVKT7R47RW6IPJHFCWPOYZUJWSENX4F2TBXORSQ5RE5PYHMETH67QPE3EGD7VFWC3OSJWPP76ABZU2WZU/page{page_num}", wait_until='domcontentloaded')
                            wait_for_main_page_load(main_page = main_page)
                            break
                        except (PlaywrightTimeoutError, PlaywrightError):
                            print(f"Switching proxy, failed to load main page")
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
                    count = listings.count()

                    car_listing_element = listings.nth(i)
                    car_listing_link_element = car_listing_element.locator('h3 > a').first
                    href = car_listing_link_element.get_attribute('href')

                    id_search = re.search(r'-(\d+)(?:[#?]|$)', href)
                    id = id_search.group(1)
                    id = int(id)

                    if id in existing_car_ids_cache:
                        print(f"After reload, ID {id} exists - updating")
                        update_existing_car(session, id, price)
                        break
                    
            # So I dont try to scrape the unloaded car pages stats, break -> into continue
            if id in existing_car_ids_cache:
                continue

            id_search = re.search(r'-(\d+)(?:[#?]|$)', href)
            id = id_search.group(1)
            id = int(id)

            price_locator = listings.nth(i).locator('div.pricefield-primary').first
            inactive_price_locator = listings.nth(i).locator('div.pricefield-inactive').first
            if price_locator.count() > 0:
                price = price_locator.inner_text().strip()
            elif inactive_price_locator.count() > 0:
                price = inactive_price_locator.inner_text().strip()
            else:
                price = None

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
            
            # =====================

            car_details, car_data = build_car_dict(
                id, price, manufacturer, modell, evjarat, km_ora, uzemanyag, teljesitmeny, allapot,
                csomagtarto, kivitel, szemelyek_szama, szin, hengerurtartalom, hajtas, valto, href
            )
            car_details_page.append(car_details)
            car_data_page.append(car_data)
            print('Scraped: ' + str(i))

            existing_car_ids_cache.add(id)
            


        # ======================= Saving new cars to db
        car_details_objects = [CarDetails(**car) for car in car_details_page]
        car_data_objects = [CarData(**car) for car in car_data_page]
        session.bulk_save_objects(car_details_objects)
        session.bulk_save_objects(car_data_objects)
        session.commit()


        car_details_page.clear()
        car_data_page.clear()


        # ======================= Next page
        page_num += 1
        next_button = main_page.locator('ul.pagination > li.next').first
        next_classes = next_button.get_attribute('class')

        #print(f"Next button classes: '{next_classes}'")

        if 'disabled' not in next_classes:
            while True:
                try:
                    if (page_num - 1) % 10 == 0:
                        print(f"Page {page_num} will trigger proxy switch, skipping navigation")
                        break
                    else:
                        main_page.goto(f"https://www.hasznaltauto.hu/talalatilista/PCOHKVCBN3RTADH4RNPZAOCJXOVRY52RUBABD5GUVPA5VDFDLAJAHCJWTICP362SW2JVURXWMRREMIRZEPJKBVQLOUGWVGNLVQA4NGV4QYOXNWKWWCS4VQQFFWNDHNCMHW2FMGMY6TQG5RAP3JL4QGB2VAQFZMXNU5NIYSJ2QEG7RQTKC6JSYVEWZUM7RGRSDOKWD24L4TPO4EIRV7O6WS2VA6DIWI3Y3P3HSVFW5S746KVLYGBSWNIYDUPBZSFDKIYOIHTQKLZRGPM2AMZD3ID7VNGPVI5ADGMYWW4ZXEW7IASHQ3RQ2F5BPNISARV5KY2GFSZ3GYITYBLPMJCY3R6QDIHLCALJHXP7JHP4TK74DH7A66ET734HWMT7PIJLDSF6NEV7NQBZG7OTQHPT2WLCJXXLKGXIU77NNR7LNZKLZOBJ23Q4KD3XWSVV7NDB6Q7QTK5SFAH6A25BRKJJZQ4SNFBMH73JKFQMCN2Q5CYYC2BOKVUMYHMREOWE63JYUKM42ETW6I4MBKLZO5YGEXVDHN4SYMY6CL77MMW5ZSGZ2D3IIISRGKT5WWZBTYGOKDP7HARROARM5NVAG3VKVB7R57DUJK7FCDTTDTUHPAK6HVIQV5R3YHTCPHGG6CKW4I63UGT55N454WGKUW5RGHJ6GI2YKDFUQUPZDLOBQAESUIWEIWB7MQSNNRNE4XL3QPR3MW3ATC7LUHFGCAXI23CCGPCZ7YRQ2BPH6JJDEIUBU3BYBZKCRYGTIBZCTVRQVUGLNUZTTDIZ4YXNERN37HPIHN6WTSE5XMUSOTTAHDGRV3OI2GATZVKT7R47RW6IPJHFCWPOYZUJWSENX4F2TBXORSQ5RE5PYHMETH67QPE3EGD7VFWC3OSJWPP76ABZU2WZU/page{page_num}", wait_until='domcontentloaded')
                        wait_for_main_page_load(main_page=main_page)
                        break       
                except (PlaywrightTimeoutError, PlaywrightError):
                    print("Switching proxies, next page did not load.")
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
                    next_button = main_page.locator('ul.pagination > li.next').first
        else:
            print("Scraped all, no more pages left")
            break
        

    # End

    car_page.close()
    main_page.close()
    context.close()
    browser.close()


