<div align="center">

# 动漫角色图片预处理
## <div align="center"><b><a href="README.md">English</a> | <a href="README_CN.md">简体中文</a></b></div>
![License](https://img.shields.io/badge/License-MIT-green)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org)
</div>

## 简介

基于Python的角色图像预处理工具，通过背景透明化、边缘裁剪、智能裁剪、图片标签(Tagger)、图片无损放大等操作，将角色图像转换为可用于训练的数据集。

### 图片处理对比（以下图片均由SD生成）
<div align="center">
    <table>
        <tr>
            <td>原始图片</td>
            <td>边缘裁剪</td>
            <td>智能裁剪 (512 * 512)</td>
        </tr>
        <tr>
            <td><img src="./assets/illust_0.jpeg" width="500px"></td>
            <td><img src="./assets/illust_0_character.jpeg" width="500px"></td>
            <td><img src="./assets/illust_0_smartcrop_0.jpeg" width="500px"></td>
        </tr>
        <tr>
            <td><img src="./assets/illust_1.jpeg" width="500px"></td>
            <td><img src="./assets/illust_1_character.jpeg" width="500px"></td>
            <td><img src="./assets/illust_1_smartcrop_0.jpeg" width="500px"></td>
        </tr>
        <tr>
            <td><img src="./assets/illust_2.jpeg" width="500px"></td>
            <td><img src="./assets/illust_2_character.jpeg" width="500px"></td>
            <td><img src="./assets/illust_2_smartcrop_0.jpeg" width="500px"></td>
        </tr>
    </table>
</div>

## 快速开始

### 方式 A：下载预构建版本（推荐）

从 [Releases](https://github.com/Inupedia/sd-character-image-preprocessing/releases) 下载对应平台的版本：

| 平台 | 文件 |
|---|---|
| Windows x64 | `AnimePreprocessing-windows-x64.zip` |
| macOS (Apple Silicon) | `AnimePreprocessing-macos-arm64.tar.gz` |
| macOS (Intel) | `AnimePreprocessing-macos-x64.tar.gz` |
| Linux x64 | `AnimePreprocessing-linux-x64.tar.gz` |

解压后运行 `AnimePreprocessing` 可执行文件，Web UI 会自动在浏览器中打开。

### 方式 B：从源码运行

需要 [uv](https://docs.astral.sh/uv/)（Python 包管理器）。

1. 克隆仓库：
   ```bash
   git clone https://github.com/Inupedia/sd-character-image-preprocessing
   cd sd-character-image-preprocessing
   ```
2. 安装依赖（自动创建 `.venv`）：
   ```bash
   uv sync
   ```
3. 复制配置模板：
   ```bash
   cp module/config_temp.py module/config.py
   ```
4. 启动 Web UI：
   ```bash
   uv run python app.py
   ```
   在浏览器中打开 http://localhost:7860。

## Web UI（Gradio）

运行 `python app.py` 启动。所有功能通过直观的标签页界面操作，无需命令行知识。

### 背景去除
上传图片并选择模型（推荐动漫角色使用 `isnet-anime`）。背景将被替换为白色。

<div align="center"><img src="./assets/webui_tab_remove_bg.jpg" width="800px"></div>

### 边界裁剪
自动检测角色边界并裁剪多余空白。建议先进行背景去除后再使用，效果更佳。

<div align="center"><img src="./assets/webui_tab_boundary_crop.jpg" width="800px"></div>

### 智能裁剪
基于人脸检测的智能裁剪，支持 YOLO 和 OpenCV Cascade 两种检测方式。支持多人图自动分割（每张人脸生成一张裁剪图）。可调节裁剪比例参数。

<div align="center"><img src="./assets/webui_tab_smart_crop.jpg" width="800px"></div>

### 图片标注
使用 WD Tagger 自动生成 Booru 风格标签，可直接用于 Stable Diffusion 训练。支持置信度阈值调节。

<div align="center"><img src="./assets/webui_tab_tagging.jpg" width="800px"></div>

### 批量重命名
将上传的图片按顺序编号重命名，支持自定义前缀（如 `illust_0.jpg`、`illust_1.jpg`、…）。

<div align="center"><img src="./assets/webui_tab_rename.jpg" width="800px"></div>

### Pixiv 下载器
按画师 ID 或关键词搜索下载作品。需要在 `module/config.py` 中配置有效的 Pixiv Cookie 和用户 ID。

<div align="center"><img src="./assets/webui_tab_pixiv.jpg" width="800px"></div>

## 命令行使用

每个功能也可以通过命令行独立执行，或通过[混合指令](#混合指令)组合使用。

### 要求

- Python 3.11 或更高版本
- [uv](https://docs.astral.sh/uv/)（或使用 `pip install` 配合 `pyproject.toml`）
- Git（可选）
   
### 背景去除
根据人物检测模型进行背景去除，请根据自己的需求选择模型（如isnet-anime对应二次元角色）。
1. 添加模型文件：所有的模型都存储在`.u2net`文件夹中（例如/Users/username/.u2net），以下为参考模型：
   1. u2net ([下载](https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx), [源码](https://github.com/xuebinqin/U-2-Net))：适用于一般用途的预训练模型
   2. u2netp ([下载](https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx), [源码](https://github.com/xuebinqin/U-2-Net))：u2net模型的轻量版
   3. u2net_human_seg ([下载](https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx), [源码](https://github.com/xuebinqin/U-2-Net))：适用于人体分割的预训练模型
   4. u2net_cloth_seg ([下载](https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_cloth_seg.onnx), [源码](https://github.com/levindabhi/cloth-segmentation))：适用于从人像中解析衣物的预训练模型，此处的衣物被解析为三类：上半身、下半身和全身
   5. silueta ([下载](https://github.com/danielgatis/rembg/releases/download/v0.0.0/silueta.onnx), [源码](https://github.com/xuebinqin/U-2-Net/issues/295))：与u2net相同，但大小减少到43Mb
   6. isnet-general-use ([下载](https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-general-use.onnx), [源码](https://github.com/xuebinqin/DIS))：新的适用于一般用途的预训练模型
   7. isnet-anime ([下载](https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-anime.onnx), [源码](https://github.com/SkyTNT/anime-segmentation))：适用于动漫角色的高精度分割模型
   8. sam ([下载编码器](https://github.com/danielgatis/rembg/releases/download/v0.0.0/vit_b-encoder-quant.onnx), [下载解码器](https://github.com/danielgatis/rembg/releases/download/v0.0.0/vit_b-decoder-quant.onnx), [源码](https://github.com/facebookresearch/segment-anything))：适用于任何用途的预训练模型
2. 修改`config.py`中以下配置，格式如下：
   ```python
    IMAGE_CONFIG = {
        # 修改为对应的模型名称，如isnet-anime
        "REMBG_MODEL": "u2net",
    }
   ```
3. 将需要处理的图片放入`src/input`文件夹中
4. 运行`main.py`：
   ```bash
   python main.py --remove-bg
   ```

### 边缘裁剪
普通的裁剪只会将多余的白色背景部分进行最大程度的剪切，需配合背景去除达到人物裁剪的效果。
1. 修改`config.py`中以下配置，格式如下：
   ```python
    IMAGE_CONFIG = {
        # 修改裁剪图片目标的存放路径及保持路径，默认修改src/output下的文件并存储为“原名_crop.png”在同一路径下，如需不同路径请先生成对应路径
        "BOUNDARY_CROP_INPUT_DIR": "./src/rm_bg_output/",
        "BOUNDARY_CROP_OUTPUT_DIR": "./src/boundary_crop_output/",
    }
   ```
2. 运行`main.py`：
   ```bash
   python main.py --boundary-crop
   ```

### 智能裁剪
智能裁剪可以搭配背景去除使用，注意在图像分辨率不高的情况下裁剪的人物会低512x512，因此建议裁剪后进行放大处理。一图多人的情况下会根据脸部特征自动裁剪出多张图片，但不适用太密集的情况。
1. 修改`config.py`中以下配置，格式如下：
   ```python
    IMAGE_CONFIG = {
        # 修改裁剪图片目标的存放路径及保持路径，默认修改src/output下的文件并存储为“原名_smartcrop_数字.png”在同一路径下，如需不同路径请先生成对应路径
        "SMART_CROP_INPUT_DIR": "./src/rm_bg_output/",
        "SMART_CROP_OUTPUT_DIR": "./src/smart_crop_output/",
        # 模型地址，不用改变
        "HF_REPO_ID": "inupedia/anime-character-image-preprocessing",
        "HF_MODEL_DIR": "./module/model/",
    }
   ```
2. 运行`main.py`：
   ```bash
   python main.py --smart-crop auto # 推荐，可调整scale factor参数例如--smart-crop auto 1.5
   python main.py --smart-crop auto-fast #基于lbpcascade_animeface.xml自动裁剪，速度快，但可能会漏掉一些人物
   ```

### 图片标签
| 原始图片 | Tagger (50% Confidence) |
| :--------: | :--------: |
| ![Image](./assets/illust_3.jpeg) [^1] | boat, lily pad, flower, multiple girls, 2girls, water, watercraft, lotus, hanfu, sitting, outdoors, black hair, hair flower, hair ornament, chinese clothes, day, holding, long hair, long sleeves, sash, smile, pink flower, looking at another, bangs, hair bun, sidelocks, braid, single hair bun |

1. 修改`config.py`中以下配置，格式如下：
   ```python
    IMAGE_CONFIG = {
         "IMAGE_TAGGER_INPUT_DIR": "./src/input/", #需要标签的图片目录
         "IMAGE_TAGGER_CONFIDENCE": 0.5, #置信度，越高越准确，但可能会漏掉一些标签
    }
   ```
2. 下载[wd-v1-4-convnextv2-tagger-v2模型](https://huggingface.co/SmilingWolf/wd-v1-4-convnextv2-tagger-v2/blob/main/model.onnx)和[selected_tags](https://huggingface.co/SmilingWolf/wd-v1-4-convnextv2-tagger-v2/blob/main/selected_tags.csv)至`module/image_tagger/model`文件夹中
3. 运行`main.py`：
   ```bash
   python main.py --tag
   ```

### 图片放大
发出了鸽子般的笑声

### 图片命名
1. 修改`config.py`中以下配置，格式如下：
   ```python
    IMAGE_CONFIG = {
        # 修改为对应的前缀名称，如illust，将会生成illust_1.jpg、illust_2.jpg等
        "IMAGE_PREFIX": "illust",
    }
   ```
2. 将需要处理的图片放入`src/input`文件夹中
3. 运行`main.py`：
   ```bash
   python main.py --rename
   ```

### PIXIV图片下载
此功能主要满足两个需求，一通过画师ID下载画师的所有作品，二通过关键字下载相关作品（数量会根据对应页数进行下载）。
1. <strong>爬虫请遵守Pixiv的[相关规定](https://www.pixiv.net/robots.txt)</strong>
2. 修改`config.py`中以下配置，格式如下：
   ```python
    NETWORK_CONFIG = {
        # 代理设置（Clash无需修改，SSR需要修改端口号）
        "PROXY": {"https": "127.0.0.1:7890"},
    }
    USER_CONFIG = {
        "USER_ID": "修改成自己的uid，参考个人资料页面的网址https://www.pixiv.net/users/{UID}",
        "COOKIE": "修改成自己的cookie，获取方式参考以下图文",
    }
   ```
   - 获取cookie的方法：
     1. 登录[pixiv](https://www.pixiv.net/)
     2. 按F12打开开发者工具
     3. 点击Network
     4. 访问排行榜并刷新页面
     5. 找到ranking.php并复制其Request Headers中的cookie
        <div>
            <img src="./assets/Cookie.jpg" width="800px"></img>
        </div>
   
3. 根据画师ID爬取其pixiv的图片：
   ```bash
   python main.py --pixiv-user 画师ID
   ```
4. 根据关键字进行下载：
   1. 修改`config.py`中以下配置，格式如下：
      ```python
       IMAGE_CONFIG = {
            "KEYWORD_ORDER": True,  # True: 按照热度排序，False: 按照最新排序
            "KEYWORD_N_PAGES": 5,  # 1页为60张图片，实际一页数量会大于60因为有些画集会有多张图片
            "KEYWORD_MODE": "safe",  # safe / r18 / all 你懂的
       }
      ```
    2. （PIXIV会员功能）关键字可以通过组合的方式进行精确搜索，如"50000users AND hutao"
        ```bash
        python main.py --pixiv-keyword "关键字"
        ```
   
### 混合指令
混合指令可以满足多任务按先后顺序执行，如果想要同时使用多个指令，可以使用组合如下。
   ```bash
   python main.py --rename --remove-bg --boundary-crop #先重命名，再对图片去除背景并边缘裁剪
   ```

## 构建独立发行版

项目包含 GitHub Actions 工作流，推送版本标签时会自动构建独立可执行文件：

```bash
git tag v1.0.0
git push origin v1.0.0
```

会自动为 Windows、macOS（Intel + Apple Silicon）和 Linux 构建可执行文件，并附加到 GitHub Release。也可以在 Actions 页面手动触发构建。

本地构建：
```bash
uv sync
uv pip install pyinstaller
cp module/config_temp.py module/config.py
uv run pyinstaller AnimePreprocessing.spec --noconfirm
# 输出目录：dist/AnimePreprocessing/
```

## 参考项目
- [PixivCrawler](https://github.com/CWHer/PixivCrawler)
- [rembg](https://github.com/danielgatis/rembg)
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- [anime_object_detection](https://huggingface.co/spaces/deepghs/anime_object_detection)
- [wd-v1-4-convnextv2-tagger-v2](https://huggingface.co/SmilingWolf/wd-v1-4-convnextv2-tagger-v2)

## 许可证
[MIT License](/LICENSE)

[^1]: [误入藕花深处](https://www.liblibai.com/imageinfo/332ef1eda104a78f9132d4c79d9a7f69)