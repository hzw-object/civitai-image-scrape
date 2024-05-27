# civitai-web-scraper

Scrape Civitai for AI generated images and prompts.

## Install

Clone the repo with:

```sh
git clone https://github.com/hzw-object/civitai-image-scrape.git
```

Initialise the python environment:

```sh
conda create --name civitai-env
conda activate civitai-env
pip install -r requirements.txt
```

Run the following and then update the config values

```sh
cp config.example.ini config.ini
```

## Usage

Run the script

```sh
python scrape_civitai.py
```

Run the server

```sh
python server.py
```
