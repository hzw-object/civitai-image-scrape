# civitai-images-scraper

获取 Civitai AI 生成的图片和提示信息。

## 安装

使用以下命令克隆仓库：

sh

```sh
git clone https://github.com/hzw-object/civitai-image-scrape.git
```

初始化 Python 环境：

sh

```sh
conda create --name civitai-env 
conda activate civitai-env 
pip install -r requirements.txt
```

运行以下命令，然后更新配置文件中的值：


```sh
cp config.example.ini config.ini
```

## 使用方法

运行脚本：

```sh
python scrape_civitai.py
```

运行服务器：


```sh
python server.py
```