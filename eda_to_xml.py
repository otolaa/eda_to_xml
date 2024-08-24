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

def is_int(rid) -> bool:
    try:
        rid = int(rid)
        if isinstance(rid, int) is False:
            return False
    except Exception as e:
        return False
    
    return True

def main():
    start = datetime.now()
    #--------- the code
    tprint('EDA>>TO>>XML', font='bulbhead')

    t_input = t_color('[+] input slug: ', 3)
    get_palce_slug = input(t_input).strip()

    t_input_region = t_color('[+] input id region: ', 3)
    get_region_id = input(t_input_region).strip()

    if is_int(get_region_id) is False:
        pc(f'[-] region is not integer ?!', 1)
        return False

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
    g_mg = get_modifiers_groups(menu)
    for m_group in g_mg:
        modifiersGroup = etree.SubElement(modifiersGroups, 'modifiersGroup', id = str(m_group['id']), required=str(m_group['required']).lower())
        etree.SubElement(modifiersGroup, 'name').text = m_group['name']
        etree.SubElement(modifiersGroup, 'type').text = 'all_one' if 'multiplier' in m_group['options'][0] else 'one_one' # all_one, one_one
        etree.SubElement(modifiersGroup, 'minimum').text = str(m_group['minSelected'])
        etree.SubElement(modifiersGroup, 'maximum').text = str(m_group['maxSelected'])

    # add modifiers
    modifierList = etree.SubElement(pageElementShop, 'modifiers')
    for m_modi in g_mg:
        if 'options' not in m_modi:
            continue

        for m_modifier in m_modi['options']:
            modifierElem = etree.SubElement(modifierList, 'modifier', id=str(m_modifier['id']))
            etree.SubElement(modifierElem, 'name').text = m_modifier['name']
            etree.SubElement(modifierElem, 'price').text = f"+{str(m_modifier['price'])}"
            etree.SubElement(modifierElem, 'modifiersGroupId').text = str(m_modi['id'])

    # add offers
    offersElement = etree.SubElement(pageElementShop, 'offers')
    for m_items in menu:
        if 'items' not in m_items:
            continue
        # get id category
        id_category = str(m_items['id']) if 'id' in m_items else str(161803)        
        # add offer
        for offer in m_items['items']:
            offerElem = etree.SubElement(offersElement, 'offer', id=str(offer['id']), available=str(offer['available']).lower())
            etree.SubElement(offerElem, 'name').text = offer['name']
            
            if 'description' in offer:
                etree.SubElement(offerElem, 'description').text = offer['description']
            
            etree.SubElement(offerElem, 'price').text = str(offer['price'])
            etree.SubElement(offerElem, 'picture').text = f"https://eda.yandex{str(offer['picture']['uri']).replace('{w}','400').replace('{h}','400')}"
            etree.SubElement(offerElem, 'categoryId').text = id_category

            if 'optionsGroups' in offer and len(offer['optionsGroups']):
                mGroupsIds = etree.SubElement(offerElem, 'modifiersGroupsIds')
                for o_modifier in offer['optionsGroups']:
                    etree.SubElement(mGroupsIds, 'modifiersGroupId').text = str(o_modifier['id'])
            
            # add adult
            if 'adult' in offer:
                etree.SubElement(offerElem, 'adult').text = str(offer['adult']).lower()

            # add weight in offer
            if 'weight' in offer and 'measure' in offer:
                ''' Единица измерения — килограммы. 
                Можно дроби: разделитель — точка или запятая, 
                не больше трех цифр после него. '''
                if offer['measure']['measure_unit'] == 'g' or offer['measure']['measure_unit'] == 'kg':
                    measure_value = offer['measure']['value']
                    if offer['measure']['measure_unit'] == 'g':
                        measure_value = int(offer['measure']['value'])/1000

                    etree.SubElement(offerElem, 'weight').text = str(measure_value)

            if 'measure' in offer and 'measure_unit' in offer['measure']:
                etree.SubElement(offerElem, 'measureUnit').text = offer['measure']['value']
                etree.SubElement(offerElem, 'measure').text = offer['measure']['measure_unit']
            
            # add param
            if 'nutrients' in offer and len(offer['nutrients']):
                for p_item in offer['nutrients'].items():
                    etree.SubElement(offerElem, 'param', name=p_item[1]['name'], unit=p_item[1]['unit']).text = p_item[1]['value']

    # write file
    obj_xml = etree.tostring(doc, xml_declaration=True, encoding='utf-8')    
    with open(f'./xml/x_{get_palce_slug}_{get_region_id}.xml', 'wb') as f:
        f.write(obj_xml)

    #--------- quit code
    pc(f'[+] lead time {str(datetime.now()-start)}', 3)

if __name__ == '__main__':
    main()