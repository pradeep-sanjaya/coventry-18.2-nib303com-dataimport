import bs4
import re
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
import pandas
from pandas import DataFrame
import csv
import time

#command to create a structure of csv file in which we will populate our scraped data
with open('lands.csv', mode='w') as csv_file:
   fieldnames = ['link', 'title', 'perch', 'price', 'district', 'city', 'address']
   writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
   writer.writeheader()

#Creating an empty lists of variables
product_link = []
product_title = []
product_perch = []
product_price = []
product_district = []
product_city = []
product_address = []

base_url = 'https://ikman.lk'
url = 'https://ikman.lk/en/ads/colombo/land?sort=date&order=desc&buy_now=0&urgent=0&page='

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def scrape(page_number):
    global url
    next_page = url + str(page_number)
    print(next_page)

    response = requests.get(str(next_page))
    soup = BeautifulSoup(response.content, "html.parser")
    #print(soup.prettify())

    wrapper = soup.findAll("li", {"class": re.compile("^normal--*")})
    #print(wrapper)
    if (len(wrapper) > 0):

        for item in range(len(wrapper)):
            link = base_url + wrapper[item].a['href']
            print(link)

            district = ""
            city = ""
            address = ""

            page = requests.get(link)
            soup_page = BeautifulSoup(page.content, "html.parser")

            posted = soup_page.h3.text
            parts = posted.split(", ")

            if (len(parts) == 3):
                district = parts[2]
                city = parts[1]
                address = city + ", " + district

            title = wrapper[item].h2.text

            perch = wrapper[item].find_all('div')[4].text

            if (re.search('\d\sperches$', perch)):
                perch = perch.replace('perches', '')
            else:
                perch = 0.0

            perch_numeric = float(perch)

            price_text = wrapper[item].span.text

            price_numeric = price_text.replace('Rs ', '').replace(',', '').replace(' total price', '').replace(' per perch', '').replace(' per acre', '').replace(' ', '')

            price = 0.0
            if (perch_numeric > 0):
                if (re.search('total price$', price_text) and re.search('perches$', perch)):
                    price = round(price_numeric / perch_numeric, 2)
                else:
                    price = float(price_numeric)

            product_link.append(link)
            product_title.append(title)
            product_perch.append(perch_numeric)
            product_price.append(price_numeric)
            product_district.append(district)
            product_city.append(city)
            product_address.append(address)

        page_number = page_number + 1
        scrape(page_number)
    else:
        print("end of pagination")



start_time = time.time()
scrape(1)

#creating the data frame and populating its data into the csv file
data = { 'link': product_link, 'title': product_title, 'perch': product_perch, 'price': product_price, 'district': product_district, 'city': product_city, 'address': product_address}

df = DataFrame(data, columns=['link', 'title', 'perch', 'price', 'district', 'city', 'address'])
df.to_csv(r'lands.csv')

print("--- %s seconds ---" % (time.time() - start_time))
