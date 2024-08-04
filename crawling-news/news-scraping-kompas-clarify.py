import csv
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Function to write data to CSV file
def write_to_csv(data, filename):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header row
        writer.writerow(['title', 'link', 'date', 'content', 'is_fake'])
        # Write data rows
        for row in data:
            writer.writerow(row)

# CHANGE THIS URL AND END_PAGE
url = 'https://www.kompas.com/cekfakta/hoaks-atau-fakta'
END_PAGE = 3

# Initialize list to store data
data = []

for i in range(1, END_PAGE):
  url_page = url+'/{}'.format(i)
  page = requests.get(url_page)
  soup = BeautifulSoup(page.text, 'html')

  # Find all news articles
  news = soup.find_all('div', 'col-bs9-3')

  for n in news:
    title_category = n.find('h1', 'cekfakta-list-title').get_text()
    link = n.find('a', 'cekfakta-list-link')['href']
    date_str = n.find('p', 'cekfakta-text-date').get_text().split(',')
    date = datetime.strptime(date_str[0].strip(), '%d/%m/%Y').date()

    # Split title and category
    part_title = title_category.split(']')
    if len(part_title) == 2:
      category = part_title[0].strip('[').strip()
      title = part_title[1].strip()

      if category == "KLARIFIKASI" and link is not None:
        # Get news contents
        get_content = requests.get(link)
        soup_content = BeautifulSoup(get_content.text, 'html')
        content = soup_content.find('div', 'read__content').find_all('p')
        paragraph = ''
        for p in content:
          paragraph += p.get_text()

        # News information source
        is_fake = 0

        # Append data to list
        data.append([title, link, date, paragraph, is_fake])

# File name for the CSV
filename = 'dataset_kompas_klarifikasi_raw.csv'

# Write data to CSV file
write_to_csv(data, filename)

print(f"Data has been written to {filename}")

def extract_content(text):
    # Normalize text to lowercase
    text = text.lower()

    # Define the start and end phrases
    start_phrases = [
        "kompas.com - ",
        ".kompas.com",
        "kompas.com-"]

    # Initialize the pattern with the start phrases
    start_pattern = "|".join(map(re.escape, start_phrases))
    pattern = f"({start_pattern})(.*)"

    # Use regular expressions to find the content after the start phrases
    match = re.search(pattern, text, re.DOTALL)

    if match:
        # Extract and return the found content
        return match.group(2).strip()
    else:
        return text

# Open the CSV file in read mode
with open('dataset_kompas_klarifikasi_raw.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)

    # Create a list to store the modified data
    modified_data = []

    # Iterate over each row in the CSV file
    for row in reader:
        title = row['title']
        link = row['link']
        date = row['date']
        content = row['content']
        is_fake = row['is_fake']

        extracted_content = extract_content(content)

        # Append data to list
        modified_data.append([title, link, date, extracted_content, is_fake])

    # File name for the CSV
    filename = 'dataset_kompas_klarifikasi.csv'

    # Write data to CSV file
    write_to_csv(modified_data, filename)

    print(f"Data has been written to {filename}")