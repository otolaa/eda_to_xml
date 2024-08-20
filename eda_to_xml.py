from typing import Dict, List
from lxml import etree, objectify
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

def get_modifiers_groups(menu: Dict) -> list:
    m_groups = []
    for m in menu:
        for item_ in m['items']:
            if 'optionsGroups' not in item_:
                continue
            if len(item_['optionsGroups']) == 0:
                continue
            for option in item_['optionsGroups']:
                m_groups.append(option)

    return m_groups

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
    
    # ----- to xml -----
    today = datetime.today()
    today_format = today.strftime("%Y-%m-%dT%H:%M:%S%Z")
    pageYmlCatalog = etree.Element('yml_catalog', date=str(today_format))
    
    doc = etree.ElementTree(pageYmlCatalog)

    # add the subelements
    pageElementShop = etree.SubElement(pageYmlCatalog, 'shop')

    # for multiple multiple attributes, use as shown above
    etree.SubElement(pageElementShop, 'name').text = place['name']
    etree.SubElement(pageElementShop, 'company').text = f"<![CDATA[{place['footerDescription']}]]>"
    etree.SubElement(pageElementShop, 'url').text = place['sharedLink']
    
    # add delivery_conditions ?!
    etree.SubElement(pageElementShop, 'deliveryConditions').text = place['deliveryConditions']

    # add currency
    currenciesElem = etree.SubElement(pageElementShop, 'currencies')
    etree.SubElement(currenciesElem, 'currency', id=place['currency']['code'], rate='1')

    # add tags ?!
    if 'tags' in place and len(place['tags']):
        tags_elem = etree.SubElement(pageElementShop, 'tags')
        for t_ in place['tags']:
            etree.SubElement(tags_elem, 'tag', id=str(t_['id'])).text = t_['name']

    # add categories
    categoryElement = etree.SubElement(pageElementShop, 'categories')
    for c_item in menu:
        id_item = str(c_item['id']) if 'id' in c_item else str(161803)
        etree.SubElement(categoryElement, 'category', id=id_item).text = c_item['name']
    
    # add modifiersGroups
    modifiersGroups = etree.SubElement(pageElementShop, 'modifiersGroups')
    for m_group in get_modifiers_groups(menu):
        modifiersGroup = etree.SubElement(modifiersGroups, 'modifiersGroup', id = str(m_group['id']), required=str(m_group['required']).lower())
        etree.SubElement(modifiersGroup, 'name').text = m_group['name']
        etree.SubElement(modifiersGroup, 'type').text = 'all_one' if 'multiplier' in m_group['options'][0] else 'one_one' # all_one, one_one
        etree.SubElement(modifiersGroup, 'minimum').text = str(m_group['minSelected'])
        etree.SubElement(modifiersGroup, 'maximum').text = str(m_group['maxSelected'])

    # write file
    obj_xml = etree.tostring(doc, xml_declaration=True, encoding='utf-8')    
    with open(f'./xml/x_{get_palce_slug}_{get_region_id}.xml', 'wb') as f:
        f.write(obj_xml)

    #--------- quit code
    pc(f'[+] lead time {str(datetime.now()-start)}', 3)

if __name__ == '__main__':
    main()