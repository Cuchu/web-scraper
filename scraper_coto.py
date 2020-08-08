import requests

from bs4 import BeautifulSoup
import re

def scrape_menu(url, shop=1):
    base_url = "https://www.cotodigital3.com.ar"
    categories = []
    html = requests.get(url)
    content = BeautifulSoup(html.content, "html5lib")

    li_categories = content.find_all("li", class_="atg_store_dropDownParent")

    for s_cat in li_categories:
        super_cat = s_cat.a.get_text().split()
        super_cat_desc = " ".join(super_cat)

        m_cat = s_cat.find_all("ul", class_="sub_category")
        for ul in m_cat:
            span_tag = ul.a.span
            span_tag.decompose()
            middle_cat = ul.a.get_text().split()
            middle_cat_desc = " ".join(middle_cat)
            div_categories = ul.find("div", id=re.compile("thrd_level_catv"))

            for li in div_categories.find_all("li"):
                cat_url = base_url + li.a.get("href")
                cat_desc = li.a.get_text().strip()
                categories.append([cat_desc, middle_cat_desc, super_cat_desc, cat_url])

    return categories



def scrape_web(url, shop=1):
    html = requests.get(url)
    content = BeautifulSoup(html.content, "html5lib")
    return get_products(content, shop)


def get_products(content, shop=1):
    list_products = content.find("ul", id="products")
    if list_products is None:
        return []

    products = list_products.find_all("li")
    return get_data(products, shop)


def get_data(products, shop=1):

    base_url = "https://www.cotodigital3.com.ar"
    elements = []

    for li in products:
        prod_id = li.get("id").replace("li_prod", "")
        prod_url = base_url + li.a.get('href')
        prod_desc = li.find("div", id="descrip_full_sku"+prod_id).get_text()
        prod_price = get_price(li, shop)
        product = [prod_id, prod_url, prod_desc, prod_price]
        elements.append(product)

    return elements


def get_price(content, shop=1):
    price = 0.00


    # Coto
    if shop == 1:
        block = content.find("span", class_="atg_store_newPrice")
        if block is None:
            return float(price)

        span_tag = block.span
        span_tag.decompose()
        br_tag = block.br
        br_tag.decompose()
        price = block.get_text().replace("$", "")
        price = price.replace(",", "")

    return float(price.strip())
