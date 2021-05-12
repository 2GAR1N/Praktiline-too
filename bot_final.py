from steampy.client import SteamClient, Asset
from steampy.utils import GameOptions
import json
import requests
import time
from fractions import Fraction
from selenium import webdriver
from selenium.webdriver.common.by import By


chromedriver_path = ''

stn_api_key = ''

steam_api_key = ''

steam_guard_path = ''

username = ''

password = ''


def get_desired_price():
    def truncate(n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier

    response = requests.get('https://api.stntrading.eu/GetKeyPrices/v1?apikey=' + stn_api_key)
    price_info = response.json()
    price = truncate(price_info['result']['pricing']['buyPrice'] / 9, 2)
    return price


def get_bp_bot_trade_url_and_price():
    desired_price = get_desired_price()
    driver.refresh()
    time.sleep(5)

    classifieds = driver.find_element_by_class_name('media-list')

    prices = classifieds.find_elements(By.CSS_SELECTOR, 'div[data-listing_price]')
    prices[:] = [float(item.text[0:-4]) for item in prices]

    trade_buttons = classifieds.find_elements(By.CSS_SELECTOR, 'a[data-tip]')
    trade_links = [item.get_attribute('href') for item in trade_buttons]
    trade_statuses = [item.get_attribute('title') for item in trade_buttons]

    for price, link, status in zip(prices, trade_links, trade_statuses):
        if status == 'This listing is managed by a user agent. Click to open a Trade Offer. Please only offer the buyout.':
            if price < desired_price:
                print('Profitable offer was found!\n' + 'Price: ' + str(price) + ' ref\n' +
                      'Profit: ' + str(round(desired_price - price, 2)) + ' ref\n' +
                      'Tradeoffer link: ' + link)
                return link, price
    else:
        print('There are no offers fetching your desired price ;(')
        return False


def get_steamid_from_trade_url(trade_url):
    magic_constant = 76561197960265728
    partner = parse_qs(urlparse(trade_url).query)['partner'][0]
    steam_id = int(partner) + magic_constant
    return str(steam_id)


def pick_up_metal_from_inventory(inventory, price):
    price = float(price)
    count_ref = 0
    count_rec = 0
    count_scrap = 0
    in_metal = 0.0
    offer_value = 0.0
    asset = []

    for item in inventory:
        if inventory[item]['name'] == 'Refined Metal':
            count_ref += 1
            in_metal += 1.0
        elif inventory[item]['name'] == 'Reclaimed Metal':
            count_rec += 1
            in_metal = round(in_metal + Fraction(1, 3), 2)
            if str(in_metal)[-2] != '.':
                if int(str(in_metal)[-1]) > int(str(in_metal)[-2]):
                    in_metal -= 0.01
                    in_metal = round(in_metal, 2)
                    print(in_metal, ' (-0.01)')
                elif int(str(in_metal)[-1]) < int(str(in_metal)[-2]):
                    in_metal += 0.01
                    in_metal = round(in_metal, 2)
                    print(in_metal, ' (+0.01)')
                elif str(in_metal)[-1] and str(in_metal)[-2] == '9':
                    in_metal += 0.01
                    in_metal = round(in_metal, 2)
                    print(in_metal, ' (0.99 + 0.01)')
        elif inventory[item]['name'] == 'Scrap Metal':
            count_scrap += 1
            in_metal = round(in_metal + Fraction(1, 9), 2)
            if str(in_metal)[-2] != '.':
                if int(str(in_metal)[-1]) > int(str(in_metal)[-2]):
                    in_metal -= 0.01
                    in_metal = round(in_metal, 2)
                    print(in_metal, ' (-0.01)')
                elif int(str(in_metal)[-1]) < int(str(in_metal)[-2]):
                    in_metal += 0.01
                    in_metal = round(in_metal, 2)
                    print(in_metal, ' (+0.01)')
                elif str(in_metal)[-1] and str(in_metal)[-2] == '9':
                    in_metal += 0.01
                    in_metal = round(in_metal, 2)
                    print(in_metal, ' (0.99 + 0.01)')
    print(count_ref, count_rec, count_scrap)
    print(in_metal)

    if in_metal >= price:
        for item in inventory:
            if inventory[item]['name'] == 'Refined Metal':
                offer_value += 1.0
                print(offer_value)
                asset.append(Asset(inventory[item]['id'], game))
            if offer_value == price:
                print(offer_value)
                return asset
            elif offer_value > price:
                print(offer_value)
                asset.pop()
                offer_value -= 1.0
                print(offer_value)
                break

        for item in inventory:
            if inventory[item]['name'] == 'Reclaimed Metal':
                offer_value = round(offer_value + Fraction(1, 3), 2)
                print(offer_value)
                asset.append(Asset(inventory[item]['id'], game))
                if str(offer_value)[-2] != '.':
                    if int(str(offer_value)[-1]) > int(str(offer_value)[-2]):
                        offer_value -= 0.01
                        offer_value = round(offer_value, 2)
                        print(offer_value, ' (-0.01)')
                    elif int(str(offer_value)[-1]) < int(str(offer_value)[-2]):
                        offer_value += 0.01
                        offer_value = round(offer_value, 2)
                        print(offer_value, ' (+0.01)')
                    elif str(offer_value)[-1] and str(offer_value)[-2] == '9':
                        offer_value += 0.01
                        offer_value = round(offer_value, 2)
                        print(offer_value, ' (0.99 + 0.01)')
                if offer_value == price:
                    print(offer_value)
                    return asset
                elif offer_value > price:
                    print(offer_value)
                    asset.pop()
                    offer_value = round(offer_value - Fraction(1, 3), 2)
                    print(offer_value)
                    if str(offer_value)[-2] != '.':
                        if int(str(offer_value)[-1]) > int(str(offer_value)[-2]):
                            offer_value -= 0.01
                            offer_value = round(offer_value, 2)
                            print(offer_value, ' (-0.01)')
                        elif int(str(offer_value)[-1]) < int(str(offer_value)[-2]):
                            offer_value += 0.01
                            offer_value = round(offer_value, 2)
                            print(offer_value, ' (+0.01)')
                        elif str(offer_value)[-1] and str(offer_value)[-2] == '9':
                            offer_value += 0.01
                            offer_value = round(offer_value, 2)
                            print(offer_value, ' (0.99 + 0.01)')
                    break

        for item in inventory:
            if inventory[item]['name'] == 'Scrap Metal':
                offer_value = round(offer_value + Fraction(1, 9), 2)
                print(offer_value)
                asset.append(Asset(inventory[item]['id'], game))
                if str(offer_value)[-2] != '.':
                    if int(str(offer_value)[-1]) > int(str(offer_value)[-2]):
                        offer_value -= 0.01
                        offer_value = round(offer_value, 2)
                        print(offer_value, ' (-0.01)')
                    elif str(offer_value)[-1] and str(offer_value)[-2] == '9':
                        offer_value += 0.01
                        offer_value = round(offer_value, 2)
                        print(offer_value, ' (0.99 + 0.01)')
                if offer_value == price:
                    print(offer_value)
                    return asset
                elif offer_value > price:
                    print(offer_value)
                    return 'Logic error'

        if offer_value < price:
            print('Not enough metal fractions!')
            return False
    else:
        print('Not enough metal!')


def pick_up_key_from_inventory(inventory):
    asset = []
    for item in inventory:
        if inventory[item]['name'] == 'Mann Co. Supply Crate Key':
            asset.append(Asset(inventory[item]['id'], game))
            return asset
    if not asset:
        print('Can\'t find any key!')
        return False


def wait_for_trade(trade_offer_id):
    status = False
    tries = 0
    while status is False:
        if tries == 23:
            print('Trade timed out.')
            steam_client.cancel_trade_offer(trade_offer_id)
            return False
        print('Waiting for 20 seconds...')
        time.sleep(20)
        state = steam_client.get_trade_offer(trade_offer_id)['response']['offer']['trade_offer_state']
        if state == 3:
            status = True
        elif state == 8:
            print(
                'Some of the items in the offer are no longer available (indicated by the missing flag in the output)')
            raise Exception
        print(state)
        tries += 1
    print('Trade succeeded.')
    return True


def make_a_trade():
    if not steam_client.is_session_alive():
        print('Session expired!')
        steam_client.login(username, password, steam_guard_path)

    my_items = steam_client.get_my_inventory(game)

    bp_partner_trade_url_and_price = get_bp_bot_trade_url_and_price()
    if not bp_partner_trade_url_and_price:
        return False
    bp_partner_trade_url = bp_partner_trade_url_and_price[0]
    bp_partner_id = get_steamid_from_trade_url(bp_partner_trade_url)
    bp_partner_items = steam_client.get_partner_inventory(bp_partner_id, game)
    bp_price = bp_partner_trade_url_and_price[1]


    my_bp_asset = pick_up_metal_from_inventory(my_items, bp_price)
    bp_partner_asset = pick_up_key_from_inventory(bp_partner_items)
    if not bp_partner_asset:
        print('Empty asset!')
        return False

    bp_trade = steam_client.make_offer_with_url(my_bp_asset, bp_partner_asset, bp_partner_trade_url)
    print(bp_trade)
    bp_trade_offer_id = bp_trade['tradeofferid']
    print(bp_trade)
    print(bp_trade_offer_id)
    if not wait_for_trade(bp_trade_offer_id):
        print('Trade error!')
        return False

    url = 'https://api.stntrading.eu/RequestKeyTrade/v1'
    myobj = {'apikey': stn_api_key, 'action': 'sell', 'amount': '1'}

    x = requests.post(url, data=myobj)
    res = json.loads(x.text)
    time.sleep(10)
    stn_bot_id = res['result']['tradeDetails']['bot']
    received_trades = steam_client.get_trade_offers()['response']['trade_offers_received']
    for trade_offer in received_trades:
        if int(trade_offer['accountid_other']) + 76561197960265728 == int(stn_bot_id):
            stn_trade_offer_id = trade_offer['tradeofferid']
            accept = steam_client.accept_trade_offer(stn_trade_offer_id)
            return True
    else:
        print('Can\'t find trade from STN bot!')
        return False


steam_client.login(username, password, steam_guard_path)

driver = webdriver.Chrome(chromedriver_path)
driver.get('https://backpack.tf/classifieds?item=Mann+Co.+Supply+Crate+Key&quality=6&tradable=1&craftable=1&australium=-1&killstreak_tier=0')

game = GameOptions.TF2
steam_client = SteamClient(steam_api_key)

while True:
    try:
        trade = make_a_trade()
        if not trade:
            print('Sleeping for 2 minutes...')
            time.sleep(120)
    except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as connection_error:
        print('Some connection troubles!')
        print(connection_error)
        time.sleep(15)
        pass
    except json.decoder.JSONDecodeError as json_error:
        print(json_error)
        print('Something with json')
        break
    except Exception as e:
        print(e)
        print(type(e))
        print('ERROR OCCURRED!')
        pass
