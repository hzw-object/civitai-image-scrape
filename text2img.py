import os
import json
import requests
import base64
import glob

# Stable Diffusion API URL
api_url = "http://47.94.82.9:57003/sdapi/v1/txt2img"

# Directory pattern to match all JSON files in subdirectories
json_pattern = "./out/*/*.json"

# Output directory for generated images
output_dir = "./generated/"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Function to call Stable Diffusion API
def call_stable_diffusion_api(metadata, output_filename):
    payload = {
        "prompt": metadata["prompt"],
        "negative_prompt": metadata["negativePrompt"],
        "width": int(metadata["Size"].split('x')[0]),
        "height": int(metadata["Size"].split('x')[1]),
        "steps": metadata["steps"],
        "cfg_scale": metadata["cfgScale"],
        "sampler": metadata["sampler"],
        "seed": metadata["seed"],
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_data = response.json()
        if "images" in response_data:
            for idx, img_data in enumerate(response_data["images"]):
                img_bytes = base64.b64decode(img_data)
                img_output_filename = os.path.join(output_dir, output_filename.replace(".png", f"_{idx}.png"))
                with open(img_output_filename, "wb") as f:
                    f.write(img_bytes)
                print(f"Image saved as {img_output_filename}")
        else:
            print("No images found in the response.")
    else:
        print(f"Failed to generate image for {output_filename}. Status code: {response.status_code}")
        print("Response:", response.text)

# Iterate over all JSON files matching the pattern
for filepath in glob.glob(json_pattern):
    with open(filepath, "r") as json_file:
        metadata = json.load(json_file)
        image_filename = os.path.basename(filepath).replace(".json", "_generated.png")
        call_stable_diffusion_api(metadata["meta"], image_filename)
