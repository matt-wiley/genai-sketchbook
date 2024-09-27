import asyncio
import sys
import os
import re
import openai
from urllib.parse import urlparse, urljoin
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WebScraper:
    def __init__(self, base_url, max_depth=2, output_dir=None):
        self.base_url = base_url
        self.base_hostname = urlparse(base_url).hostname
        self.visited_links = set()
        self.max_depth = max_depth
        # Derive the output directory if not provided
        self.output_dir = output_dir or f".local/output/{self.sanitize_output_dir(base_url)}"
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def sanitize_output_dir(self, url):
        """Sanitize the BASE_URL to create a valid directory name."""
        parsed_url = urlparse(url)
        # Combine the hostname with the path to make the output directory unique
        dir_name = re.sub(r'[^\w\-_]', '_', f"{parsed_url.hostname}{parsed_url.path}")
        return dir_name.strip('_') or "scraped_pages"

    def sanitize_filename(self, url, extension=".txt"):
        """Sanitize the URL to create a valid filename with the specified extension."""
        parsed_url = urlparse(url)
        filename = re.sub(r'[^\w\-_]', '_', parsed_url.path) or "index"
        return os.path.join(self.output_dir, f"{filename}{extension}")

    async def fetch_links(self, url, depth=0):
        if url in self.visited_links or depth > self.max_depth:
            return
        
        self.visited_links.add(url)
        
        # Determine the text file path
        text_file_path = self.sanitize_filename(url, extension=".txt")

        # Check if the text content file already exists and is not empty
        if os.path.exists(text_file_path) and os.path.getsize(text_file_path) > 0:
            print(f"Skipping already cached page: {url}")
            return
        
        print(f"Scraping {url} at depth {depth}")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            try:
                await page.goto(url)
                # Save the text content of the page
                await self.save_page_content(url, page)
                links = await page.eval_on_selector_all("a[href]", "elements => elements.map(el => el.href)")
            except Exception as e:
                print(f"Error accessing {url}: {e}")
                await browser.close()
                return

            await browser.close()
        
        # Filter links that match the original hostname
        filtered_links = [link for link in links if urlparse(link).hostname == self.base_hostname]
        filtered_links = [urljoin(url, link) for link in filtered_links]

        print(f"Found {len(filtered_links)} links on {url}")

        for link in filtered_links:
            await self.fetch_links(link, depth + 1)

    async def save_page_content(self, url, page):
        """Save the text content of the current page to a file."""
        content = await page.inner_text('body')
        text_file_path = self.sanitize_filename(url, extension=".txt")
        
        with open(text_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"Saved text content to {text_file_path}")

    async def start(self):
        await self.fetch_links(self.base_url)

    def process_files_with_openai(self):
        """Process each output file, send content to OpenAI, and retrieve an outline and headline."""
        for root, _, files in os.walk(self.output_dir):
            for filename in files:
                if filename.endswith(".txt"):
                    filepath = os.path.join(root, filename)
                    if os.path.getsize(filepath) == 0:
                        print(f"Skipping empty file: {filepath}")
                        continue
                    
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                    
                    print(f"Processing file: {filepath}")
                    outline, headline = self.get_outline_and_headline(content)
                    
                    # Create a corresponding markdown file with the same name
                    markdown_filename = os.path.splitext(filename)[0] + ".md"
                    markdown_filepath = os.path.join(root, markdown_filename)

                    # Save the headline and outline as markdown
                    with open(markdown_filepath, 'w', encoding='utf-8') as markdown_file:
                        markdown_file.write(f"# {headline}\n\n{outline}")
                    
                    print(f"Saved markdown output to {markdown_filepath}")

    def get_outline_and_headline(self, content):
        """Send the page content to OpenAI and retrieve an outline and headline."""
        messages = [
            {
                "role": "system",
                "content": "\n".join([
                    "You are an expert in summarizing information about companies and organizations.",
                    "You do this to help job seekers understand the key details about a company.",
                    "Given the text content of a webpage, provide an outline that summarizes the key points.",
                    "Include a brief description of each section or topic covered in the content.",
                    "Additionally, create a one-sentence headline that captures the essence of the content.",
                ])
            },
            {
                "role": "user",
                "content": f"Text content:\n{content}\n\n Please summarize this content, in a small paragraph and an outline, and provide a one-sentence headline about the page."
            }
        ]
        
        try:
            response = openai.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4'),  # Read engine from environment variable or use 'gpt-4' as default
                messages=messages,
                max_tokens=1500,  # Adjust this value as needed for detail
                temperature=0.3    # Adjust creativity; 0.3 keeps it concise
            )
            # Extract the outline and headline from the response
            result_text = response.choices[0].message.content.strip().split("\n", 1)
            if len(result_text) == 2:
                headline = result_text[0].strip()
                outline = result_text[1].strip()
                return outline, headline
            else:
                return "No outline available", "No headline available"
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            return "Error generating outline", "Error generating headline"

if __name__ == "__main__":
    # Get parameters from environment variables
    base_url = os.getenv("BASE_URL")
    max_depth = int(os.getenv("MAX_DEPTH", 2))
    
    if not base_url:
        print("Error: Please specify the BASE_URL environment variable.")
        sys.exit(1)
    
    output_dir = os.getenv("OUTPUT_DIR", None)  # If OUTPUT_DIR is not set, it will be derived

    scraper = WebScraper(base_url, max_depth, output_dir)
    asyncio.run(scraper.start())

    # Process the output files with OpenAI
    scraper.process_files_with_openai()
