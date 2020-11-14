import bs4
import re
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
import pandas
from pandas import DataFrame
import csv

#command to create a structure of csv file in which we will populate our scraped data
with open('lands.csv', mode='w') as csv_file:
   fieldnames = ['link', 'title', 'perch', 'price']
   writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
   writer.writeheader()

#Creating an empty lists of variables
product_link = []
product_title = []
product_perch = []
product_price = []

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

    response= requests.get(str(next_page))
    soup = BeautifulSoup(response.content, "html.parser")
    #print(soup.prettify())

    wrapper = soup.findAll("li", {"class": re.compile("^normal--*")})
    
    if (len(wrapper) > 0):

        for item in range(len(wrapper)):
            link = base_url + wrapper[item].a['href']

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

        page_number = page_number + 1
        scrape(page_number)
    else:
        print("end of pagination")


scrape(1)
   
#creating the data frame and populating its data into the csv file
data = { 'link': product_link, 'title': product_title, 'perch': product_perch, 'price': product_price}
print(data)

df = DataFrame(data, columns=['link', 'title', 'perch', 'price'])
df.to_csv(r'lands.csv')