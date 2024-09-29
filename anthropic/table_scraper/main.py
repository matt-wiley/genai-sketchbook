import os

import scraper_v1 as scraper
import tuple_to_csv

OUTPUT_DIR = f".local/output/{os.path.basename(os.path.dirname(__file__))}"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]

    # Transform the url into a printable filename, omit the protocol and replace slashes with underscores
    filename = url.replace("https://", "").replace("http://", "").replace("/", "_")

    result = scraper.scrape_tables(url)
    
    for i, table in enumerate(result, 1):
        print(f"Table {i}:")
        csv_content = tuple_to_csv.tuples_to_csv_string(table)
        print(csv_content)
        print()

        with open(f"{OUTPUT_DIR}/{filename}_{i}.csv", "w") as f:
            f.write(csv_content)


if __name__ == "__main__":
    main()