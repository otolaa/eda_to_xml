## eda.yandex to xml

0 - parse detaul page and to xml

```
 # 0 - brand place company
https://eda.yandex.ru/eats/v1/eats-catalog/v2/brand/place?brand_slug=tashir_gnorv&region_id=1&latitude=55.65679838701938&longitude=37.38758568101073

# 1 - catalog menu
url_r = f"https://eda.yandex.ru/api/v2/menu/retrieve/{m.place_slug}?regionId={m.region.rid}&autoTranslate=false"

# 2 - seo for meta
https://eda.yandex.ru/web-api/seo-meta-tags?longitude=37.38758568101073&latitude=55.65679838701938&url=https%3A%2F%2Feda.yandex.ru%2Fmoscow%3FshippingType%3Ddelivery&lang=ru&asset=desktop&serviceBrand=yandex

# 3 - region country
https://eda.yandex.ru/web-api/initial-server-data?lang=ru&asset=desktop&serviceBrand=yandex

# 4 - detail
https://eda.yandex.ru/r/tashir_gnorv?placeSlug=tashir_2d8q5
```

1 - start script
```
$ python3 eda_to_xml.py
```