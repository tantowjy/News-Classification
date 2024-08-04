import csv
import requests
import re
from bs4 import BeautifulSoup

# Function to write data to CSV file
def write_to_csv(data, filename):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header row
        writer.writerow(['title', 'link', 'date', 'content', 'is_fake'])
        # Write data rows
        for row in data:
            writer.writerow(row)

# CHANGE YEAR
YEAR = 2024
MONTH = '08'
url = f'https://www.tempo.co/indeks/{YEAR}-{MONTH}-'

# Initialize list to store data
data = []

for i in range(1, 31):
  print(i)
  url_page = url+'{}/nasional'.format(i)
  page = requests.get(url_page)
  soup = BeautifulSoup(page.text, 'html')

  # Find all news articles
  news = soup.find_all('div', 'card-box')

  for n in news:
    link = n.find('a')['href']

    if(link != ''):
      # Get news contents
      get_content = requests.get(link)
      soup_content = BeautifulSoup(get_content.text, 'html')
      title = soup_content.find('h1', 'title').get_text()
      date = soup_content.find('p', 'date').get_text()
      content = soup_content.find('div', 'detail-konten').find_all('p')
      paragraph = ''
      for p in content:
        paragraph += p.get_text()

      # News information source
      is_fake = 0

      # Append data to list
      data.append([title, link, date, paragraph, is_fake])

# File name for the CSV
filename = 'dataset_tempo_raw.csv'

# Write data to CSV file
write_to_csv(data, filename)

print(f"Data has been written to {filename}")

def extract_content(text):
    # Normalize text to lowercase
    text = text.lower()

    # Define the start and end phrases
    start_phrases = [
        "jakarta -",
        "jakarta-"]

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
with open('dataset_tempo_raw.csv', 'r') as csvfile:
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
    filename = 'dataset_tempo.csv'

    # Write data to CSV file
    write_to_csv(modified_data, filename)

    print(f"Data has been written to {filename}")