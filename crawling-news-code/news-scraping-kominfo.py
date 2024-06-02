from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import pandas as pd

# Inisialisasi WebDriver
driver = webdriver.Chrome()

# Fungsi untuk scroll sampai halaman habis atau sampai batas tertentu
def infinite_scroll(driver, max_scrolls=1):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0
    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Tunggu beberapa detik untuk memuat halaman
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scroll_count += 1

# Buka halaman utama
driver.get("https://www.kominfo.go.id/content/all/laporan_isu_hoaks")

# Scroll halaman sampai habis atau sampai batas tertentu
infinite_scroll(driver, max_scrolls=1000)

# Ambil semua elemen dengan class 'title'
soup = BeautifulSoup(driver.page_source, 'html.parser')
titles = soup.find_all('a', class_='title')
print("link:")
print(titles[1]['href'])

# Loop melalui semua link berita
data_list = []
for title in titles:
    link = "https://www.kominfo.go.id"+title['href']
    print(link)
    driver.get(link)
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'title')))
    except TimeoutException:
        print(f"Timed out waiting for page to load {link}")
        continue
    
    news_soup = BeautifulSoup(driver.page_source, 'html.parser')
    news_title = news_soup.find('h1', class_='title').text
    news_date = news_soup.find('div', class_='date').text
    news_content = news_soup.find_all('p')[1].text
    
    data_list.append({
        'title': news_title,
        'link': link,
        'date': news_date,
        'content': news_content,
        'is_fake': 1,
        'media_bias': 'netral'
    })

# Tutup WebDriver
driver.quit()

# Buat DataFrame dari data_list
df = pd.DataFrame(data_list)

# Simpan DataFrame ke dalam file JSON
df.to_json('data_hoax_reports.json', orient='records', lines=True)

print("Data berhasil disimpan dalam bentuk JSON")
