from playwright.sync_api import sync_playwright
import csv
import os
import sys
import argparse

def clean_text(text):
    return ' '.join(text.split())

def extract_table_data(table):
    rows = table.query_selector_all('tr')
    table_data = []
    for row in rows:
        cells = row.query_selector_all('td, th')
        row_data = [clean_text(cell.inner_text()) for cell in cells]
        table_data.append(row_data)
    return table_data

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def main(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        # Find all table elements
        tables = page.query_selector_all('table')

        for i, table in enumerate(tables):
            table_data = extract_table_data(table)
            
            if table_data:  # Only save if the table contains data
                filename = f"table_{i+1}.csv"
                save_to_csv(table_data, filename)
                print(f"Saved data from table {i+1} to {filename}")
            else:
                print(f"Table {i+1} is empty, skipping.")

        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web scraper for extracting table data to CSV files.")
    parser.add_argument("url", help="The URL of the webpage to scrape")
    args = parser.parse_args()

    main(args.url)