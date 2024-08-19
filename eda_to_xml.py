from datetime import datetime
import sys, os, json, requests, fake_useragent 
from art import tprint
from help import *

def get_json(url_page):
    header = { 'User-Agent':str(fake_useragent.UserAgent().google), }
    try:
        res = requests.get(url=url_page, headers = header, timeout = 10)
        return res.json()    
    except Exception as e:
        print(sys.exc_info()[1])
        return False  

def set_xml():
    pass

def t_color(text, color_num = 2):
    ''' color text '''
    return f'\033[3{color_num}m{text}\033[0m'

def get_place(url_brand_slug, get_palce_slug):
    data_json = get_json(url_brand_slug)
    if data_json is False:
        pc(f'[-] return false', 1)
        return False

    try:
        place = data_json['payload']['foundPlace']['place']
        write_json(place, f'./json/brand_slug_{get_palce_slug}.json')
    except KeyError:
        pc("[-] Key not found!", 1)
        return False
    
    return place

def get_menu(url_menu, get_palce_slug):
    data_json_menu = get_json(url_menu)
    if data_json_menu is False:
        pc(f'[-] return false', 1)
        return False
    
    try:
        menu = data_json_menu['payload']['categories']
        write_json(menu, f'./json/menu_{get_palce_slug}.json')
    except KeyError:
        pc("[-] Key not found!", 1)
        return False
    
    return menu

def main():
    start = datetime.now()
    #--------- the code
    tprint('EDA>>TO>>XML', font='bulbhead')

    # t_input = t_color('[+] input slug: ', 3)
    # get_palce_slug = input(t_input)
    get_palce_slug = 'tashir_gnorv'

    # t_input_region = t_color('[+] input id region: ', 3)
    # get_region_id = input(t_input_region)
    get_region_id = int('1')

    pc(f'[+] brand_slug: {get_palce_slug}', color_num=6)
    pc(f'[+] region_id: {get_region_id}', color_num=6)

    # ----- place brand
    url_brand_slug = f'https://eda.yandex.ru/eats/v1/eats-catalog/v2/brand/place?brand_slug={get_palce_slug}&region_id={get_region_id}'
    place = get_place(url_brand_slug, get_palce_slug)
    if place is False:
        pc("[-] place is False", 1)    
        return False

    # ----- menu catalog
    latitude = place["address"]["location"]["latitude"]
    longitude = place["address"]["location"]["longitude"]
    slug = place["slug"]
    
    url_menu = f'https://eda.yandex.ru/api/v2/menu/retrieve/{slug}?regionId={get_region_id}&autoTranslate=false&latitude={latitude}&longitude={longitude}'
    menu = get_menu(url_menu, get_palce_slug)
    if menu is False:
        pc("[-] menu is False", 1)
        return False
    
    # ----- to xml
    

    #--------- quit code
    pc(f'[+] lead time {str(datetime.now()-start)}', 3)

if __name__ == '__main__':
    main()