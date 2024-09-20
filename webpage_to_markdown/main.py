import sys
import os
import asyncio
import base64
import hashlib

from PIL import Image
from io import BytesIO
from playwright.async_api import async_playwright
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("OPENAI_MODEL")

def resize_image(image_path, output_path=None, max_dimension=1024) -> str:
    """
    Resizes an image so that its largest dimension does not exceed max_dimension pixels,
    while preserving the aspect ratio. Additionally, returns the resized image encoded as a Base64 string.

    Parameters:
    - image_path (str): Path to the input image file.
    - output_path (str, optional): Path to save the resized image. 
        If not provided, the resized image will be saved as 'resized_<original_filename>' in the same directory.
    - max_dimension (int, optional): Maximum allowed size for the largest dimension (default is 1024).

    Returns:
    - base64_str (str): The resized image encoded as a Base64 string.
    """
    try:
        # Open the image file
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            print(f"Original size: {original_width}x{original_height}")

            # Determine the scaling factor
            if original_width > original_height:
                if original_width <= max_dimension:
                    print("No resizing needed.")
                    resized_img = img.copy()
                else:
                    scaling_factor = max_dimension / float(original_width)
                    new_width = max_dimension
                    new_height = int(original_height * scaling_factor)
                    print(f"Resizing to: {new_width}x{new_height}")
                    resized_img = img.resize((new_width, new_height))
            else:
                if original_height <= max_dimension:
                    print("No resizing needed.")
                    resized_img = img.copy()
                else:
                    scaling_factor = max_dimension / float(original_height)
                    new_height = max_dimension
                    new_width = int(original_width * scaling_factor)
                    print(f"Resizing to: {new_width}x{new_height}")
                    resized_img = img.resize((new_width, new_height))

            # Determine the output path
            if output_path is None:
                directory, filename = os.path.split(image_path)
                name, ext = os.path.splitext(filename)
                resized_filename = f"resized_{name}{ext}"
                output_path = os.path.join(directory, resized_filename)

            # Save the resized image
            resized_img.save(output_path)
            print(f"Resized image saved to: {output_path}")

            # Encode the resized image to Base64
            buffered = BytesIO()
            # Choose format based on original image or specify a format
            format = img.format if img.format else 'JPEG'
            resized_img.save(buffered, format=format)
            img_bytes = buffered.getvalue()
            base64_str = base64.b64encode(img_bytes).decode('utf-8')
            print("Image successfully encoded to Base64.")

            return base64_str

    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
        return None
    except IOError:
        print(f"Error: Cannot open or process the image file '{image_path}'.")
        return None








def secure_url_hash(url: str) -> str:
    """
    Create a cryptographically secure hash of the given URL using SHA-256.

    Args:
        url (str): The URL to be hashed.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash.
    """
    # Ensure the URL is encoded as bytes before hashing
    url_bytes = url.encode('utf-8')

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the bytes of the URL
    hash_object.update(url_bytes)

    # Return the hexadecimal representation of the hash
    return hash_object.hexdigest()



# Function to take a screenshot of a webpage
async def take_screenshot(url, output_path):
    """
    Take a screenshot of a webpage and save it to the specified output path.
    """

    view_width = 1200
    view_height = view_width * 7

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page.set_viewport_size({"width": view_width, "height": view_height})
        await page.goto(url)
        await page.screenshot(path=output_path)
        await browser.close()
        print(f"Screenshot saved at {output_path}")



# Function to convert screenshot to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")



# Function to call OpenAI API and get Markdown structure
def screenshot_to_markdown(image_base64):
    
    client = OpenAI(api_key=API_KEY)



    prompt = (
        "You are given a screenshot of a webpage. "
        "Please analyze the visual elements in the image and provide a "
        "Markdown representation of the page structure. "
        "Break down the structure by identifying key sections like headers, "
        "navigation bars, images, content blocks, and footer."
    )

    # Make the API request
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt.join("\n")},
            {"role": "user", "content": [
                { "type": "text", "text": "Return the information hierachy of the following page, displayed in markdown format" },
                { "type": "image_url", "image_url": { "url": f"data:image/png;base64,{image_base64}" } }
            ]},
        ],
        max_tokens=500
    )

    # Extract the generated Markdown
    markdown_text = response.choices[0].message.content
    return markdown_text.strip()



# Main function to take a screenshot and generate markdown
async def main(url, screenshot_path):
    # Step 1: Take the screenshot
    await take_screenshot(url, screenshot_path)

    # Step 2: Convert the screenshot to base64
    image_base64 = resize_image(screenshot_path)

    # Step 3: Get Markdown representation from OpenAI
    markdown = screenshot_to_markdown(image_base64)

    # Step 4: Print or save the markdown representation
    print("\nGenerated Markdown Representation of the Page Structure:\n")
    print(markdown)



if __name__ == "__main__":
    target = sys.argv[1] or None
    url = target if target is not None else "https://example.com"  # Replace with the target URL
    screenshot_path =  f"screenshots/{secure_url_hash(url)}.png" # Path to save the screenshot

    # Run the async main function
    asyncio.run(main(url, screenshot_path))
