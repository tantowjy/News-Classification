import csv
import requests
import re
import time
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

# CHANGE THIS URL AND END_PAGE
url = 'https://www.antaranews.com/tag/cek-fakta/'
END_PAGE = 5

# Initialize list to store data
data = []

for i in range(1, END_PAGE):
    try:
        url_page = url + '{}'.format(i)
        page = requests.get(url_page, timeout=10)
        page.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(page.text, 'html.parser')

        print(f"Processing page {i}")

        # Find all news articles
        news = soup.find_all('div', 'card__post')

        for n in news:
            title = n.find('div', 'card__post__title').find('a').get_text()
            link = n.find('div', 'card__post__title').find('a')['href']

            # Split title and category
            title_first_space_index = title.find(' ')
            category = title[:title_first_space_index]
            title_news = title[title_first_space_index + 1:].strip()

            if (category == "Hoaks!" or category == "Disinformasi!") and link is not None:
                # Get news contents
                try:
                    get_content = requests.get(link, timeout=10)
                    get_content.raise_for_status()  # Raise an HTTPError for bad responses
                    soup_content = BeautifulSoup(get_content.text, 'html.parser')
                    date = ""
                    content = soup_content.find('div', 'wrap__article-detail-content').get_text()

                    # News information source
                    is_fake = 1

                    # Append data to list
                    data.append([title_news, link, date, content, is_fake])
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching content for {link}: {e}")

        # Delay to avoid overwhelming the server
        time.sleep(2)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {i}: {e}")

# File name for the CSV
filename = 'dataset_antara_hoaks_raw.csv'

# Write data to CSV file
write_to_csv(data, filename)

print(f"Data has been written to {filename}")

def extract_content(text):
    # Normalize text to lowercase
    text = text.lower()

    # Define the start phrases
    start_phrases = [
        "jakarta (antara/jacx)"
    ]

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
with open('dataset_antara_hoaks_raw.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)

    # Skip the header row
    next(reader)

    # Create a list to store the modified data
    modified_data = []

    # Iterate over each row in the CSV file
    for row in reader:
        title = row[0]
        link = row[1]
        date = row[2]
        content = row[3]
        is_fake = row[4]

        extracted_content = extract_content(content)

        # Append data to list
        modified_data.append([title, link, date, extracted_content, is_fake])

    # File name for the CSV
    filename = 'dataset_antara_hoaks.csv'

    # Write data to CSV file
    write_to_csv(modified_data, filename)

    print(f"Data has been written to {filename}")