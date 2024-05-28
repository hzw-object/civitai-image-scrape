import http.server
import socketserver
import os
import json
import random
import configparser
from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, FileSystemLoader

# 配置
config = configparser.ConfigParser()
config.read("config.ini")
output_dir = config["DEFAULT"]["OutputDir"]
PORT = int(config["DEFAULT"]["ServerPort"])
ITEMS_PER_PAGE = int(config["DEFAULT"]["ItemsPerPage"])
local_images = config["DEFAULT"]["LocalImages"].lower() == 'true'

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
    print(f"{len(data)} 条图像数据已加载!")

# 创建一个自定义的 HTTP 请求处理程序
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global data

        url_parts = urlparse(self.path)
        path = url_parts.path
        query = parse_qs(url_parts.query)
        search_term = query.get('search', [''])[0]  # 从查询参数获取搜索词

        if path == '/':
            # 返回 HTML 页面
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template('web/template.html')
            output = template.render()
            self.wfile.write(output.encode('utf-8'))

        elif path.startswith("/page/"):
            # 分页处理
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            page_number = int(path.split("/")[2])
            start_index = ITEMS_PER_PAGE * (page_number - 1)
            end_index = start_index + ITEMS_PER_PAGE

            if search_term:
                # 根据搜索词过滤数据
                filtered_data = [item for item in data if search_term.lower() in json.dumps(item['data']).lower()]
                page_data = filtered_data[start_index:end_index]
            else:
                page_data = data[start_index:end_index]

            self.wfile.write(json.dumps(page_data).encode('utf-8'))

        elif path.startswith(f"/{output_dir}/") or path.startswith('/web/'):
            # 返回其他静态文件
            try:
                with open('.' + path, 'rb') as f:
                    self.send_response(200)
                    if path.endswith('.json'):
                        self.send_header('Content-type', 'application/json')

                    elif path.endswith('.css'):
                        self.send_header('Content-type', 'text/css')
                        self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, "File not found")

        else:
            # 404 处理
            self.send_error(404, "File not found")

load_image_data()

# 启动服务器
with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"服务器正在 http://localhost:{PORT} 提供服务")
    httpd.serve_forever()
