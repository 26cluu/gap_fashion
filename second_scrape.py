import asyncio
from playwright.async_api import async_playwright
import aiofiles
import json
import os
import requests


# ===== CONFIGURATION ===== #
JSON_INPUT_PATH = "gap_products.json"
JSON_OUTPUT_PATH = "gap_products_updated.json"
IMAGE_DIR = "gap_images"
DESCRIPTION_SELECTOR = ".product-description__text"
IMAGE_SELECTOR = "a.brick_product-image"
CONCURRENT_TABS = 5  # Adjust: 3-10 is typically safe

os.makedirs(IMAGE_DIR, exist_ok=True)


# ===== SCRAPE ONE PRODUCT ===== #
async def scrape_product(browser, product):
    page = await browser.new_page()
    try:
        print(f"Scraping: {product['url']}")
        await page.goto(product["url"], timeout=60000)

        # Extract description
        list_items = await page.query_selector_all("ul.product-information-item__list > li.product-information-item__list-item")
        if list_items:
            texts = []
            for li in list_items[:5]:
                text = await li.text_content()
                if text:
                    texts.append(text.strip())
            description = " ".join(texts)
        else:
            description = "Description not found"

        # Extract last high-res image
        img_anchors = await page.query_selector_all("a.brick__product-image")
        if img_anchors:
            last_img_anchor = img_anchors[-1]
            img_url = await last_img_anchor.get_attribute("href")
            if img_url and img_url.startswith("/"):
                img_url = f"https://www.gap.com{img_url}"
        else:
            img_url = None

        if img_url:
            try:
                img_data = requests.get(img_url).content
                img_filename = os.path.join(IMAGE_DIR, f"page{product['page']}_id{product['id']}.jpg")
                async with aiofiles.open(img_filename, 'wb') as f:
                    await f.write(img_data)
            except Exception as e:
                print(f"Image download failed for {product['name']}: {e}")
                img_filename = "Image not found"
        else:
            img_filename = "Image not found"

        # Update product
        product["description"] = description
        product["image_path"] = img_filename

    except Exception as e:
        print(f"Failed to scrape {product['url']}: {e}")
        product["description"] = "Failed to scrape"
        product["image_path"] = "Failed to scrape"
    finally:
        await page.close()



# ===== CONCURRENTLY RUN TASKS ===== #
async def run_in_batches(browser, products, concurrent_tabs):
    semaphore = asyncio.Semaphore(concurrent_tabs)

    async def limited_scrape(product):
        async with semaphore:
            await scrape_product(browser, product)

    await asyncio.gather(*(limited_scrape(p) for p in products))


# ===== MAIN ENTRY POINT ===== #
async def main():
    with open(JSON_INPUT_PATH, "r") as f:
        data = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        await run_in_batches(browser, data["products"], CONCURRENT_TABS)
        await browser.close()

    async with aiofiles.open(JSON_OUTPUT_PATH, "w") as f:
        json_str = json.dumps(data, indent=4)
        await f.write(json_str)


if __name__ == "__main__":
    asyncio.run(main())
                             