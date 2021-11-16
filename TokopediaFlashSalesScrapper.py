from selenium import webdriver
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
import re
import datetime
import os

class HTML:
    Schedule = 'css-1g5b64m'
    ProductContainer = 'css-y5gcsw'
    TimeStamp = 'css-mdfmy2'
    ProductName = 'css-12fc2sy'
    PriceDiscount = 'css-a94u6c'
    Price = 'css-hwbdeb'
    Location = 'css-qjiozs'

class DateParser:
    def __init__(self, time):
        self.time = time
        self.flash_sale_time = ''.join(re.findall(r'(\d{2}\_\d{2})', self.time)[0])
        self.datetimenow = datetime.datetime.now().strftime('%Y-%m-%d')

    def __str__(self):
        return str(self.datetimenow + '-' + self.flash_sale_time)

class TokopediaScrapper:
    def __init__(self, url):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.url = url
        self.data = []

    def Scrapper(self):
        self.driver.get(self.url)
        self.driver.maximize_window()

        self.time = self.driver.find_element(By.CLASS_NAME, HTML.TimeStamp).text.replace(".", "_").replace(":", "_")
        self.date = DateParser(self.time)

        catch = self.driver.find_element(By.CLASS_NAME, HTML.Schedule).text.split('\n')[0]
        if catch == 'Dimulai dalam':
            self.driver.quit()
            print('Menunggu Flash Sales!')
        else:
            element = wait(self.driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, HTML.ProductContainer)))
            while True:
                self.driver.execute_script('arguments[0].scrollIntoView();', element[-1])
                try:
                    wait(self.driver, 15).until(lambda driver: len(wait(driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, HTML.ProductContainer)))) > len(element))
                    element = wait(self.driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, HTML.ProductContainer)))
                except:
                    break

            for number, product in enumerate(element):
                try:
                    product_name = product.find_element(By.CLASS_NAME, HTML.ProductName).text
                    product_price = product.find_element(By.CLASS_NAME, HTML.Price).text.replace('\n','').replace('Rp', '').replace('.', '')
                    product_price_discount = product.find_element(By.CLASS_NAME, HTML.PriceDiscount).text.replace('Rp', '').strip().replace('.', '')
                    store_location = product.find_element(By.CLASS_NAME, HTML.Location).text
                    print(f"{number + 1}. {product_name} | {product_price[3:].strip()} | {product_price_discount} | {product_price[0:3].strip()} | {store_location}")
                    self.data.append((number + 1,
                                      product_name,
                                      product_price[3:].strip(),
                                      product_price_discount,
                                      product_price[0:3].strip(),
                                      store_location))
                except Exception as why:
                    print(why)
                    break

            print('Scrapping Selesai!')
            self.driver.quit()

    def ExportCSV(self):
        database = pd.DataFrame(self.data, columns=('No.', 'Product_name', 'price_before_discount', 'price_after_discount', 'discount', 'store_location'))
        database.to_csv(f"Tokopedia_Flash_Sale_Data {self.date}.csv", index=False)
        print(os.path.abspath(f"Tokopedia_Flash_Sale_Data {self.date}.csv"))

def main():
    TokopediaFlashSale = TokopediaScrapper("https://www.tokopedia.com/discovery/kejar-diskon")
    TokopediaFlashSale.Scrapper()

    if input('Save to CSV?').title() == 'Yes':
        TokopediaFlashSale.ExportCSV()
    else:
        pass
main()

