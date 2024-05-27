import os
import json
import requests
import configparser

# Configuration
config = configparser.ConfigParser()
config.read("config.ini")
output_dir = config["DEFAULT"]["OutputDir"]
nsfw_level = config["DEFAULT"]["NSFWLevel"]
api_key = config["DEFAULT"]["ApiKey"]
local_images = config["DEFAULT"]["LocalImages"].lower() == 'true'
cursor = config["DEFAULT"]["Cursor"]
def save_metadata(item, output_dir):
    item_id = item["id"]
    json_filename = os.path.join(output_dir, f"{item_id}.json")
    if os.path.isfile(json_filename):
        print(f"File {json_filename} already exists.")
    else:
        print(f"Saving {json_filename}.")
        with open(json_filename, "w") as f:
            json.dump(item, f, indent=1)

def save_image(item, output_dir):
    if item["meta"] and item["url"] and local_images:
        img_filename = os.path.join(output_dir, f"{item['id']}.jpg")
        image_response = requests.get(item["url"])
        if image_response.status_code == 200:
            with open(img_filename, "wb") as f:
                f.write(image_response.content)
            print("Image saved successfully!")
        else:
            print("Error saving image:", image_response.status_code)

def fetch_images(url):
    print(f"Fetching URL: {url}")
    response = requests.get(url)
    return response

# Initial URL
url = f"https://civitai.com/api/v1/images?token={api_key}&limit=100&sort=Most%20Reactions&nsfw={nsfw_level}&cursor={cursor}"

while url:
    response = fetch_images(url)

    if response.status_code == 200:
        data = response.json()
        next_cursor = data["metadata"].get("nextCursor")
        
        if next_cursor:
            # Convert nextCursor to directory-friendly format
            cursor_dir_name = next_cursor.replace('|', '_')
            # Create a new directory named after converted nextCursor
            page_output_dir = os.path.join(output_dir, cursor_dir_name)
            os.makedirs(page_output_dir, exist_ok=True)

            for item in data["items"]:
                save_metadata(item, page_output_dir)
                save_image(item, page_output_dir)
            
            # Update URL to nextPage if it exists
            url = data["metadata"].get("nextPage", None)
        else:
            break
    else:
        print("Error:", response.status_code)
        break
