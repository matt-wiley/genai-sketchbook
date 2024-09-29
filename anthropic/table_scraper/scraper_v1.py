from playwright.sync_api import sync_playwright
from typing import List, Tuple

def clean_text(text: str) -> str:
    return ' '.join(text.split())

def extract_table_data(table) -> List[Tuple[str, ...]]:
    rows = table.query_selector_all('tr')
    table_data = []
    for row in rows:
        cells = row.query_selector_all('td, th')
        row_data = tuple(clean_text(cell.inner_text()) for cell in cells)
        table_data.append(row_data)
    return table_data

def scrape_tables(url: str) -> List[List[Tuple[str, ...]]]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        tables = page.query_selector_all('table')
        all_table_data = []

        for table in tables:
            table_data = extract_table_data(table)
            if table_data:
                all_table_data.append(table_data)

        browser.close()

    return all_table_data

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = scrape_tables(url)
    
    for i, table in enumerate(result, 1):
        print(f"Table {i}:")
        for row in table:
            print(row)
        print()