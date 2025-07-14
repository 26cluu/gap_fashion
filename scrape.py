from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
from datetime import datetime

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# List to store all product data
all_products = []

# Manually specify category and page number
category = "men"  # Change this to: "men", "women", "kids", "baby"
page_number = 6  # Change this to the page number you want to scrape

# URL to scrape
url = "https://www.gap.com/browse/men/shop-all-styles?cid=1127944&nav=meganav%3AMen%3ACategories%3AShop+All+Styles#pageId=5"

driver.get(url)

time.sleep(10)

product_cards = driver.find_elements(By.CLASS_NAME, "plp_product-card")

print(f"Found {len(product_cards)} product cards")

for i, product_card in enumerate(product_cards):
    try:
        print(f"\n--- Processing Product {i+1}/{len(product_cards)} ---")

        # Extract product name
        try:
            name_element = product_card.find_element(
                By.CLASS_NAME, "plp_product-card-name"
            )
            product_name = (
                name_element.get_attribute("title") or name_element.text.strip()
            )
            print(f"Name: {product_name}")
        except:
            print("Name: Not found")
            product_name = "Unknown"

        # Extract price
        try:
            price_element = product_card.find_element(
                By.CLASS_NAME, "plp_product-card-price"
            )
            price = price_element.text.strip()
            print(f"Price: {price}")
        except:
            print("Price: Not found")
            price = "Price not available"

        # Extract product URL
        try:
            url_element = product_card.find_element(By.CLASS_NAME, "plp_product-info")
            product_url = url_element.get_attribute("href")
            print(f"URL: {product_url}")
        except:
            print("URL: Not found")
            product_url = None

        # Create product dictionary
        product_data = {
            "id": i + 1,
            "name": product_name,
            "price": price,
            "url": product_url,
            "category": category,
            "page": page_number,
            "category_page": f"{category}-pg{page_number}",
            "scraped_at": datetime.now().isoformat(),
        }

        # Add to our collection
        all_products.append(product_data)
        print(f"✅ Added product {i+1} to collection")

        time.sleep(1)

        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.5)  # Brief pause to let the scroll complete

    except Exception as e:
        print(f"❌ Error processing product {i+1}: {e}")
        continue

# Load existing data or create new structure
filename = "gap_products.json"
try:
    with open(filename, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
    print(f"📖 Loaded existing data from {filename}")
except FileNotFoundError:
    existing_data = {
        "scraped_at": datetime.now().isoformat(),
        "total_products": 0,
        "products": [],
    }
    print(f"📝 Creating new data file: {filename}")

# Add new products to existing data
existing_data["products"].extend(all_products)
existing_data["total_products"] = len(existing_data["products"])
existing_data["last_updated"] = datetime.now().isoformat()

# Save updated data back to file
with open(filename, "w", encoding="utf-8") as f:
    json.dump(existing_data, f, indent=2, ensure_ascii=False)

print(f"\n🎉 Successfully scraped {len(all_products)} products!")
print(f"📁 Data saved to: {filename}")

time.sleep(5)

driver.quit()
print("Browser closed")
