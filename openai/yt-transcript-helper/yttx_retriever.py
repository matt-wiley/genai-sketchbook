import re
import sys
import os
import asyncio

from urllib.parse import urlparse, parse_qs
from typing import List

from playwright.async_api import async_playwright


OUTPUT_DIR=".local/output/yttx"

async def get_transcript(url: str) -> List[str]:
    """Retrieve the transcript text from a YouTube video URL."""
    
    transcript = None
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url)

            print("Waiting 5 seconds for the page to load...")
            # Sleep for a few seconds to allow the page to load
            await page.wait_for_timeout(5000)

            print("Clicking on the 'Show transcript' button")
            await page.eval_on_selector_all("button[aria-label='Show transcript']", "elements => elements.map(e => e.click())")

            print("Waiting for the transcript to load...")
            await page.wait_for_timeout(5000) # Wait for the transcript to load

            transcript = await page.eval_on_selector_all("ytd-transcript-renderer", "elements => elements.map(e => e.innerText)")
            


            # for line in transcript_text:
            #     line = re.sub(r"\s+", " ", line)
            #     line.strip()
            #     print(line)
                

        except Exception as e:
            print(f"Error accessing {url}: {e}")
            await browser.close()

        await browser.close()

    return transcript


def main():
    url = sys.argv[1]

    # extract the video ID from the URL
    parsed_url = urlparse(url)
    # Extract the query part of the URL
    query_string = parsed_url.query
    # Convert the query string into a dictionary
    query_params = parse_qs(query_string)

    # Get the 'v' parameter from the query string
    v_id = query_params.get('v', None)[0]
    
    if not v_id:
        print("Invalid YouTube video URL. Please provide a valid URL.")
        sys.exit(1)



    output_dir = f"{OUTPUT_DIR}/{v_id}"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{OUTPUT_DIR}/{v_id}/initial_scrape.txt"

    if not os.path.exists(output_file):
        print(f"Retrieving transcript for {url}...")
        transcript = asyncio.run(get_transcript(url))
        with open(output_file, 'w') as file:
            file.write("\n".join(transcript))
    
    with open(output_file, 'r') as file:
        transcript = file.readlines()

    ## Clean up the transcript text

    cleaned_transcript = []
    for line in transcript:
        line = line.strip()
        
        # Skip empty lines
        if len(line) == 0:
            break # Do not include in the cleaned transcript

        if re.match(r"English \(auto-generated\)", line):
            break # Do not include in the cleaned transcript

        # Keep lines that don't start with a digit or a square bracket
        if re.match(r"^[^\d\[]+", line):
            cleaned_transcript.append(line)

        
    with open(f"{OUTPUT_DIR}/{v_id}/cleaned_transcript.txt", 'w') as file:
        file.write("\n".join(cleaned_transcript))


if __name__ == "__main__":
    main()