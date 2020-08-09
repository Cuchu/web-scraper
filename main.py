import scraper_coto as scrap
import psycopg2
from datetime import datetime
import time

conn = psycopg2.connect("host=127.0.0.1 dbname=prices port=5432 user=postgres password=postgres")
cursor = conn.cursor()


def disconnect():
    cursor.close()
    conn.close()


def update_price(prod_shop_id, price=0.00):
    today = datetime.today().strftime('%Y-%m-%d')
    query = f"INSERT INTO price (productshopid,date,price) VALUES (%s,%s,%s) ON CONFLICT (productshopid,date) DO UPDATE SET price = excluded.price;"
    cursor.execute(query, (prod_shop_id, today, price))


def update_product(prod_shop_id, prod_url, prod_name, prod_category, prod_m_category, prod_s_category, shop_id = 1):
    query = f"INSERT INTO product (productshopid,category,url,name,shopid, mcategory, scategory) VALUES (%s,%s,%s,%s,%s,%s,%s) " \
            f"ON CONFLICT (productshopid) DO " \
            f"UPDATE SET url = excluded.url, name = excluded.name, mcategory = excluded.mcategory, scategory = excluded.scategory;"
    cursor.execute(query, (prod_shop_id, prod_category, prod_url, prod_name, shop_id, prod_m_category, prod_s_category))


def update_ids():
    query = "UPDATE price " \
            "SET productid = product.id " \
            "FROM product WHERE product.productshopid = price.productshopid AND price.productid IS NULL"
    cursor.execute(query)


def start_log(categories):
    status = False
    today = datetime.today().strftime('%Y-%m-%d')
    for category in categories:
        cat_desc = category[0].strip()
        cat_m_desc = category[1].strip()
        cat_s_desc = category[2].strip()
        cat_url = category[3]

        query = f"INSERT INTO log (category, url, status, mcategory, scategory, date) VALUES (%s,%s,%s,%s,%s,%s);"
        cursor.execute(query, (cat_desc, cat_url, status, cat_m_desc, cat_s_desc, today))


def get_log():
    today = datetime.today().strftime('%Y-%m-%d')
    cursor.execute(f"SELECT category, mcategory, scategory, url FROM log WHERE status = false AND date = '{today}'")
    return cursor.fetchall()


def execution_completed():
    today = datetime.today().strftime('%Y-%m-%d')
    cursor.execute(f"SELECT category, mcategory, scategory, url FROM log WHERE status = true AND date = '{today}'")
    return cursor.fetchall()


def update_log(category):
    today = datetime.today().strftime('%Y-%m-%d')
    cursor.execute(f"UPDATE log SET status = true WHERE category = '{category}' AND date = '{today}'")
    return


def update_variations():
    today = datetime.today().strftime('%Y-%m-%d')
    cursor.execute(f"DELETE FROM variation WHERE date = '{today}'")
    conn.commit()
    variations = f"INSERT INTO variation \
                   select price.productid, price.productshopid, aux.date, aux.price, (aux.price - price.price) as diff \
                   from price \
                   join  (select productid, date, price from price ) as aux on price.productid = aux.productid and price.price <> aux.price and price.date = (aux.date - 1) \
                   where price.price <> 0 and aux.date = '{today}' \
                   order by price.productid desc;"

    cursor.execute(variations)
    print(f"Cambio de precios: {cursor.rowcount} / día {today}")
    conn.commit()
    return


# categories = [["Cerveza","Bebidas con Alcohol","Bebidas","https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-bebidas-bebidas-con-alcohol-cerveza/_/N-137sk0z"]]
categories = get_log()
completed_categories = execution_completed()

if len(categories) == 0 and len(completed_categories) > 0:
    print(f"Categorías procesadas - Fin")
    exit(0)

if len(categories) == 0:
    print(f"Cargamos categorías")
    categories = scrap.scrape_menu("https://www.cotodigital3.com.ar/sitios/cdigi/")

    categories.append(['Herramientas Eléctricas', 'Ferretería', 'Hogar', 'https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-hogar-ferreteria-herramientas-eléctricas/_/N-1otsfuy'])
    categories.append(['Herramientas Manuales', 'Ferretería', 'Hogar',
                       'https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-hogar-ferreteria-herramientas-manuales/_/N-1dw5vl8'])

    start_log(categories)
else:
    print(f"Leemos categorías desde db")


conn.commit()


start_time = time.time()
url_params = "?No=0&Nrpp=250"

print(f"Cantidad de categorias: {len(categories)}")
products_count = 0
count = 0
for category in categories:
    cat_desc = category[0].strip()
    cat_m_desc = category[1].strip()
    cat_s_desc = category[2].strip()
    cat_url = category[3] + url_params

    print(f"Scrap {cat_url}")
    products = scrap.scrape_web(cat_url)
    for prod in products:
        update_price(prod[0], prod[3])
        update_product(prod[0], prod[1], prod[2], cat_desc, cat_m_desc, cat_s_desc)

    conn.commit()

    update_ids()
    conn.commit()

    products_count += len(products)
    print(f"{cat_desc}: {len(products)} productos")

    if len(products) > 0:
        update_log(cat_desc)
        conn.commit()


update_variations()

disconnect()
print(f"Total de productos: {products_count}")

print("--- %s seconds ---" % (time.time() - start_time))


