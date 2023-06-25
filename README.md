<div align="center">

# Character Image Preprocessing

![GitHub](https://img.shields.io/badge/WIP-未完成-brown)

[![License](https://img.shields.io/badge/License-MIT-green)](./license)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org)
</div>

## 简介

基于Python的角色图像预处理工具，通过自动背景透明化、角色裁剪、图片无损放大等操作，将角色图像转换为可用于训练的数据集。

### 图片处理对比（以下图片均由SD生成）
<div align="center">
    <table>
        <tr>
            <td>原始图片</td>
            <td>处理后图片</td>
        </tr>
        <tr>
            <td><img src="./src/input/illust_0.png" width="500px"></td>
            <td><img src="./src/output/illust_0_character.png" width="500px"></td>
        </tr>
        <tr>
            <td><img src="./src/input/illust_1.png" width="500px"></td>
            <td><img src="./src/output/illust_1_character.png" width="500px"></td>
        </tr>
        <tr>
            <td><img src="./src/input/illust_2.png" width="500px"></td>
            <td><img src="./src/output/illust_2_character.png" width="500px"></td>
        </tr>
    </table>
</div>

## 使用方法

### 要求

- Python 3.8或更高版本及其依赖包
- Git (可选)

### 安装
1. 克隆存储库或者[下载zip](https://github.com/Inupedia/sd-character-image-preprocessing/archive/refs/heads/main.zip)：
   ```bash
   git clone https://github.com/Inupedia/sd-character-image-preprocessing
   ```
2. 安装所需的软件包：
   ```bash
   pip install -r requirements.txt 
   ```
### 使用
1. 将需要处理的图片放入`src/input`文件夹中
2. 运行`main.py`：
   ```bash
   python main.py
   ```

## 许可证
[MIT License](./license)