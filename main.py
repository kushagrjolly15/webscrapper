import urllib.request
from urllib.request import build_opener, HTTPCookieProcessor
from bs4 import BeautifulSoup as BS
import re
import json
import requests
import pandas as pd
from cosmosclient import CosmosClient as cc
from cosmosclient import BlobStorageClient as bc
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import os
from fake_useragent import UserAgent
import urllib3

exclude_cat_prod = ["accessor", "wrap", "scarves", "scarf", "sock", "jewelry", "shoe", "belt", "glasses", "earring", "bracelet", "necklace", "watch", "ring"]
include_cat_prod = ["cloth", "men", "man", "plus", "tall", "petite", "bottom", "pant", "jean", "legging", "short", "top", "shirt", "tee", "tank", "blouse", "bra", "dress", "suit", "romper", "knit", "sweater", "hood", "windbreaker", "jacket", "swim"]

def shopify(website):
    urllib3.disable_warnings()
    size_guide_url = ''
    size_guide_table = None
    df = None
    ua = UserAgent()
    headers = {
        'user-agent': ua.random,
    }
    f=open("categories_links.txt", "a+")
    f1=open("products_links.txt", "a+")
    grab = requests.get(website, headers = headers, verify = False)
    if grab.url[-1] == '/':
        website = grab.url[:-1]
    else: website = grab.url
    print(website)
    soup = BS(grab.text, 'html.parser')
    categories = set()
    products = set()
    # Start by finding all the a tags in the landing page of any shofiy based website
    for link in soup.find_all("a"):
        # Check if any of the href has a regex for size guide which is the primary target for the scraper
        # if found then we extract size guide by checking if it not a image but in a tabular format
        if size_guide_url == '' and link.get('href') != None and re.search('.*/(size-chart|size-guide|sizing|fit-guide).*', link.get('href'), re.IGNORECASE):
            if website not in link.get('href'):
                size_guide_url = website + link.get('href')
            else:
                size_guide_url = link.get('href')
            if size_guide_url != '':
                with urllib.request.urlopen(urllib.request.Request(size_guide_url, headers = headers)) as url:
                    soup = BS(url.read(), 'html.parser')
                    size_guide_table = soup.find_all("table")
                    if size_guide_table:
                        df = pd.read_html(str(size_guide_table))[0]
                        df = df.to_json()
        # we start by extracting other href while filtering out only collections and also having the inclusion list keywords and not having the exlusion list keywords
        category_links = link.get('href')
        if link.get('href') ==  None:
            continue
        if 'collections/' in category_links and (website + category_links) not in categories and (any(include_cat_prod) in category_links and any(exclude_cat_prod) not in category_links):
            if 'http' in category_links:
                categories.add(category_links)
                f.write(category_links+ '\n')
            else:
                categories.add(website + category_links)
                f.write(website + category_links + '\n') 
    f.close()
    # First check if size guide table exists then only iterate over the categories otherwise skip it
    if size_guide_table != None and size_guide_table !='':
        for category in categories:
            # Create random UserAgent so that websites dont block our scraper out
            headers = {
            'user-agent': ua.random,
            }
            grab = requests.get(category, headers = headers, verify = False)
            soup = BS(grab.text, 'html.parser')
            # get all the product links containing keyword 'products' in them 
            for link in soup.find_all("a"):
                product_links = link.get('href')
                if link.get('href') ==  None:
                    continue
                if 'products/' in product_links and (website + product_links) not in products and (any(include_cat_prod) in product_links and any(exclude_cat_prod) not in product_links):
                    if 'shopify' not in product_links and 'http' not in product_links:
                        products.add(website + product_links)
                        f1.write(website + product_links + '\n')
                    elif 'shopify' not in product_links:
                        products.add(product_links)
                        f1.write(product_links + '\n')
        f1.close()   
        # iterate over all the products link and gather all the necessary information     
        for product in products:
            images_blob = []
            # remove unnecessary part of product link
            if '?' in product:
                product = product.split('?')[0]
            ua = UserAgent()
            headers = {
                'user-agent': ua.random,
            }
            try:
                try:
                    if df != None and df != '':
                        try:
                            # open the json page of each product link and start gathering the required information
                            with urllib.request.urlopen(urllib.request.Request(product + '.json', headers = headers)) as url:
                                sizes, colors, price = 'NA', 'NA', 'NA'
                                url_data = json.loads(url.read().decode())
                                # extract name of product
                                name = url_data["product"]["title"]
                                # extract product id of product
                                prod_id = url_data["product"]["id"]
                                body_html = url_data["product"]["body_html"]
                                # extract material of product
                                material = re.findall("(\d+(\.\d+)?%(\s)\w*)", body_html)
                                material = ' '.join(m[0] for m in material)
                                if len(material.strip()) == 0:
                                    material = 'NA'
                                # extract size of product
                                if "options" in url_data["product"]:
                                    for o, option_type in enumerate(url_data["product"]["options"]):
                                        if url_data["product"]["options"][o]["name"].lower() == "size":
                                            sizes = url_data["product"]["options"][o]["values"]
                                        elif url_data["product"]["options"][o]["name"].lower() == "color":
                                            colors = url_data["product"]["options"][o]["values"]
                                # extract images of product
                                if "images" in url_data["product"]:
                                    for o, option_type in enumerate(url_data["product"]["images"]):
                                        if url_data["product"]["images"][o]["src"].lower():
                                            images_blob.append(bc.add_blob_to_container(requests.get(url_data["product"]["images"][o]["src"]).content))
                                # extract price of product
                                if "variants" in url_data["product"]:
                                    for o, option_type in enumerate(url_data["product"]["variants"]):
                                        price = url_data["product"]["variants"][o]["price"]
                                if colors == 'NA' and '-' in name:
                                    name, colors = name.split('-')
                                elif colors == 'NA' and '|' in name:
                                    name, colors = name.split('|')
                                # push the required information to db
                                push_to_db(str(prod_id), name, price, sizes, colors, product, images_blob, material, df)
                        except:
                            print("Connection Reset1")
                except:
                    print("Connection Reset2")
            except:
                print("Connection Reset3")
        


def lululemon():
    # Landing page api url of lululemon
    urls = 'https://shop.lululemon.com/api'
    grab = requests.get(urls)
    soup = BS(grab.text, 'html.parser')
    categories = []
    # iterate over all 'a' tag and get href links
    # and check if it contains '/c/' which is keyword for categories
    for link in soup.find_all("a"):
        data = link.get('href')
        if '/c/' in data: 
            if '//shop.lululemon.com' not in data:
                data = 'https://shop.lululemon.com/api' + data
            elif 'https' not in data:
                data = 'https:' + data
                data = data[:len('https://shop.lululemon.com/')] + 'api/' + data[len('https://shop.lululemon.com/'):]
            else:
                data = data[:len('https://shop.lululemon.com/')] + 'api/' + data[len('https://shop.lululemon.com/'):]
            categories.append(data)
    # iterate over each category to get product link from the api url which is a json response
    # record[pdp-url] contains the links of all product
    for category in categories:
        grab = requests.get(category)
        json_data = json.loads(str(BS(grab.text, 'html.parser').text))
        records = json_data["data"]["attributes"]["main-content"][0]["records"]
        for record in records:
            opener = build_opener(HTTPCookieProcessor())
            response = opener.open('https://shop.lululemon.com'+record['pdp-url'])
            html = response.read()
            soup = BS(html, 'html.parser')
            # Extract name of the product
            for node in soup.findAll("div", {"itemprop": "name"}):
                name = ''.join(node.findAll(text=True))
                encoded_string = name.encode("ascii", "ignore")
                name = encoded_string.decode()
            # Extract price of the product
            for node in soup.findAll("span", {"class": "price-1SDQy price"}):
                price = ''.join(node.findAll(text=True))
                encoded_string = price.encode("ascii", "ignore")
                price = encoded_string.decode()
            # Extract colors of the product    
            colors = []
            color_container  = soup.find('div', { "class" : "swatches-container"}) 
            rows  = color_container.find_all('div', { "class" : "swatch available"})
            for row in rows:
                colors.append(row['aria-label'])
            for node in soup.findAll("span", {"class": "purchase-attribute-carousel-counter__label"}):
                selected_length = ''.join(node.findAll(text=True))
                encoded_string = selected_length.encode("ascii", "ignore")
                selected_length = encoded_string.decode()
            # Extract length of the product
            lengths = []
            for node in soup.findAll("div", {"class": "buttonTile-1ov4u _3agOmHg-k134lEW9nyc_xv"}):
                length= ''.join(node.findAll(text=True))
                encoded_string = length.encode("ascii", "ignore")
                length = encoded_string.decode()
                lengths.append(length)

            api_url = 'https://shop.lululemon.com/api' + record['pdp-url']
            data = json.loads(str(soup.find("script", {"type": "application/json"}).text))

            size_guide_url = 'https:' + data['props']['initialReduxState']['rootReducer']['pages'][api_url]['data']['purchase-attributes']['size-guide-url']
            sizeGuideCategory = data['props']['initialReduxState']['rootReducer']['pages'][api_url]['data']['purchase-attributes']['sizeGuideCategory']
            # Extract url of the product
            url = 'https:' + data['props']['initialReduxState']['rootReducer']['productDetailPageOld']['product-summary']['product-site-map-pdp-url']
            images_url = data['props']['initialReduxState']['rootReducer']['pages'][api_url]['data']['product-carousel'][0]['image-info']
            color_code = data['props']['initialReduxState']['rootReducer']['pages'][api_url]['data']['product-carousel'][0]['color-code']
            materials = data['props']['initialReduxState']['rootReducer']['pages'][api_url]['data']['colorAttributes'][color_code]['careAndContent']['sections'][0]['attributes'][0]['list']['items']
            all_sizes = data['props']['initialReduxState']['rootReducer']['productDetailPageOld']['product-summary']['product-sizes']
            size_driver = data['props']['initialReduxState']['rootReducer']['pages'][api_url]['data']['purchase-attributes']["size-driver"]
            color_mapping = {}
            for product in data['props']['initialReduxState']['rootReducer']['pages'][api_url]['data']['purchase-attributes']['all-color']:
                color_mapping[product['color-code']] = product['display-name']

            available_size_color = []  
            for size in size_driver:
                for color in size['colors']:
                    if color not in color_mapping.keys():
                        break
                    size['colors'][size['colors'].index(color)] = color_mapping[color]
                available_size_color.append(size)
            # Extract images of the product
            images_blob = []
            for image in images_url:
                images_blob.append(requests.get(image).content)

            gender = sizeGuideCategory.split('-')[0]
            sizeGuideCategoryType = sizeGuideCategory.split('-')[1]
            response1 = opener.open(size_guide_url)
            html1 = response1.read()
            soup1 = BS(html1, 'html.parser')
            # Extract size guide of the product
            tag = soup1.find("div", {"id": gender[:-1] + "-tab"})
            size_guide_tab = tag.find("section", {"id": gender + sizeGuideCategory + '-tab'})
            size_chart_tag_centimeters= size_guide_tab.find(id='centimeters-tabpanel')
            size_chart_table_centimeters = size_chart_tag_centimeters.findAll("table")

            df1 = pd.read_html(str(size_chart_table_centimeters))[0]
            df1 = df1.to_json()
            # Saving the required information to DB
            push_to_db("Integration_Test_Product", name, price, available_size_color, colors, url, images_blob, materials, df1)

def push_to_db(id, name, price, size, colors, url, image_blob, materials, size_guide):
    json_result = {
        "id": id,
        "name" : name,
        "price" : price,
        "size" : size,
        "colors" : colors,
        "url" : url,
        "images-blob" : image_blob,
        "materials" : materials,
        "size_chart" : size_guide
        }
    cc.create_product(json_result)
    print("Data Entered into DB")


if __name__ == "__main__":
    with open('categories_links.txt', 'w') as fp:
        pass
    with open('products_links.txt', 'w') as fp:
        pass
    with open('config.txt', 'r') as cf:
        content = cf.readlines()
    content = [x.strip() for x in content]
    if(len(content) > 0):
        print("Config File consists of "+ str(len(content))+" brand URLS")
        for brand_website in content:
            shopify(brand_website)
    else:
        print("Config File does not contain brand URLS, hence proceeding with BuildWith API")
        # Get list of all shopify websites using the builtwith API
        website = 'https://api.builtwith.com/lists7/api.json?KEY=1b240590-8b39-42b7-bc74-3f416163dfdd&TECH=Shopify&META=yes'
        url = urllib.request.urlopen(website)
        url_data = json.loads(url.read().decode())
        final_list = []
        interesting_data = url_data['Results']
        # Filter out those websites which have 'Style and Fashion' as there vertical
        for interest in interesting_data:
            if interest['META']['Vertical'] == 'Style And Fashion':
                final_list.append('https://' + interest['D'])
                shopify('https://' + interest['D'])