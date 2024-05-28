from flask import Flask, request, jsonify, render_template, send_from_directory, abort
import os
import json
import random
import configparser
from jinja2 import Environment, FileSystemLoader

# 配置
config = configparser.ConfigParser()
config.read("config.ini")
output_dir = config["DEFAULT"]["OutputDir"]
PORT = int(config["DEFAULT"]["ServerPort"])
ITEMS_PER_PAGE = int(config["DEFAULT"]["ItemsPerPage"])
local_images = config["DEFAULT"]["LocalImages"].lower() == 'true'

app = Flask(__name__)

data = []

def load_image_data():
    print("正在加载图像数据...")
    global data
    data = []
    for root, dirs, files in os.walk(output_dir):
        jsons = [f for f in files if f.endswith('.json')]
        random.shuffle(jsons)
        for json_file in jsons:
            image = None
            with open(os.path.join(root, json_file), 'r') as f:
                json_data = json.load(f)
            if local_images:
                # 在文件系统中查找图像
                image = json_file.replace('.json', '.jpg')
                image_path = os.path.join(root, image)
                if not os.path.isfile(image_path):
                    continue
                image = '/' + os.path.relpath(image_path, start=os.getcwd()).replace('\\', '/')
            elif not json_data.get("url") or not json_data.get('meta'):
                continue
            else:
                image = json_data["url"]
            data.append({'image': image, 'data': json_data})
    print(f"{data} 数据")
    
    print(f"{len(data)} 条图像数据已加载!")

@app.route('/')
def index():
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('web/template.html')
    return render_template(template)

@app.route('/page/<int:page_number>')
def paginate(page_number):
    search_term = request.args.get('search', '')

    start_index = ITEMS_PER_PAGE * (page_number - 1)
    end_index = start_index + ITEMS_PER_PAGE

    if search_term:
        # 根据搜索词过滤数据
        filtered_data = [item for item in data if search_term.lower() in json.dumps(item['data']).lower()]
        page_data = filtered_data[start_index:end_index]
    else:
        page_data = data[start_index:end_index]

    return jsonify(page_data)

@app.route(f'/{output_dir}/<path:filename>')
def serve_files(filename):
    try:
        return send_from_directory(output_dir, filename)
    except FileNotFoundError:
        abort(404, "File not found")

@app.route('/web/<path:filename>')
def serve_static_files(filename):
    try:
        return send_from_directory('web', filename)
    except FileNotFoundError:
        abort(404, "File not found")

if __name__ == '__main__':
    load_image_data()
    app.run(port=PORT)
