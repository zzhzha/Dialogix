#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: 潘高
LastEditors: 潘高
Date: 2022-03-23 15:41:46
LastEditTime: 2024-09-08 20:29:41
Description: 生成客户端主程序
usage: 运行前，请确保本机已经搭建Python3开发环境，且已经安装 pywebview 模块。
'''

import argparse
import mimetypes
import os
import sys
import webview
from api.api import API
from pyapp.config.config import Config
from pyapp.db.db import DB

cfg = Config()  # 配置
db = DB()  # 数据库类
api = API()  # 本地接口

cfg.init()


def on_shown():
    # print('程序启动')
    db.init()  # 初始化数据库


def on_loaded():
    # print('DOM加载完毕')
    pass


def on_closing():
    # print('程序关闭')
    pass


def WebViewApp(ifCef=False):
    # 是否为开发环境
    Config.devEnv = sys.flags.dev_mode
    # Config.devEnv = True

    # 视图层页面URL
    if Config.devEnv:
        # 开发环境
        MAIN_DIR = f'http://localhost:{Config.devPort}/'
        template = os.path.join(MAIN_DIR, "")  # 设置页面，指向远程
    else:
        # 生产环境
        MAIN_DIR = os.path.join(".", "web")
        template = os.path.join(MAIN_DIR, "index.html")  # 设置页面，指向本地

        # 修复某些情况下，打包后软件打开白屏的问题
        mimetypes.add_type('application/javascript', '.js')

    # 系统分辨率
    screens = webview.screens
    screens = screens[0]
    width = screens.width
    height = screens.height
    # 程序窗口大小
    initWidth = int(width * 2 / 3)
    initHeight = int(height * 4 / 5)
    minWidth = int(initWidth / 2)
    minHeight = int(initHeight / 2)

    # 创建窗口
    window = webview.create_window(title=Config.appName, url=template, js_api=api, width=initWidth, height=initHeight,
                                   min_size=(minWidth, minHeight))

    # 创建提示窗口
    hint_window = webview.create_window(title='提示', html="""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>对话图片拼接器</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f0f0f0;
            margin: 0 auto;
            max-width: 900px;
            padding: 20px;
        }
        .credits {
            background-color: #d9d9d9;
            padding: 12px 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
            border-left: 4px solid #999;
        }
        .credits a {
            color: #444;
            text-decoration: none;
            font-weight: bold;
        }
        .credits a:hover {
            text-decoration: underline;
        }
        h1 {
            color: #444;
            border-bottom: 1px solid #ccc;
            padding-bottom: 10px;
            margin-top: 0;
        }
        h2 {
            color: #555;
            margin-top: 25px;
        }
        .container {
            background-color: #e6e6e6;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .highlight {
            background-color: #d9d9d9;
            padding: 2px 4px;
            border-radius: 3px;
        }
        .note {
            background-color: #d1d1d1;
            padding: 10px;
            border-left: 4px solid #999;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="credits">
        盛世工作室出品 · 作者：Z在此 · 
        <a href="https://space.bilibili.com/397283120" target="_blank">B站主页</a>
    </div>
    
    <div class="container">
        <h1>对话图片拼接器（暂定）</h1>
        
        <h2>程序功能</h2>
        <p>将多张图片以指定的底部像素高度为基准进行垂直拼接，在你想要某个视频出现的"名人名言"的图片形式的完整版时，就可以事先简单截图，然后使用本程序进行快速拼接的操作，输出为一张完整的图片。当然也可以不输入或者只输入部分图片的高度，只用作将图片进行垂直拼接也是可以的。</p>
        
        <h2>详细说明</h2>
        <p>输入和按钮等控件，鼠标悬停时显示快捷键。而列表中的图片项显示的是完整图片名。</p>
        
        <p>特别提及"输入"控件，按t焦点即可聚焦在输入框内，使得可以输入高度值，输入完成后按回车键或者再次按t（英文输入状态下）焦点则会回到窗口，恢复能够正常使用快捷键快速操作的状态。</p>
        
        <p>点击"添加图片"按钮，可以选择多张图片（仅支持 jpg、jpeg、png、gif、bmp、webp 格式），列表支持拖拽排序图片项，支持shift多选、ctrl单选和del删除操作。</p>
        
        <p>点击列表项，选中项会显示在左侧图片预览区，并分别在图片的右侧，下方显示图片对应的像素高度和宽度。（做完才发现宽度无意义 囧）</p>
        
        <p>点击√按钮或者按下z键，可以选择将该图片切割，并在图片上方显示灰色区域表示要被切割的部分。点击×按钮或者按下x键，可以取消切割，对应的，如果有灰色区域则消失。（也是做完才发现这两个可以合并到一起，但是做都做了 囧）</p>
        
        <p>点击"确认"按钮，提示选择合并模式，分别为适应最长边等比例缩放和适应最短边等比例缩放，根据需要自行选择。</p>
        
        <p>选定合并模式后，程序真正开始切割拼接图片。完成后会出现弹窗提示并将列表清空。</p>
        
        <p>切割后的图片会保存在本地，保存在程序所在目录下的"output"文件夹内。</p>
        
        <div class="note">
            <h3>特别提示</h3>
            <p>因为有适应最短边等比例缩放等的模式的存在，因此截图不用严格按照视频高度，也可以手动粗略截一些，另外一些部分在程序里处理；在输入框中输入的高度会保留，不会随着切换图片项而清空，因而在图片需要裁剪的底部的高度相同的情况下可以通过快捷键快速操作。</p>
        </div>
    </div>
</body>
</html>""")
    # 获取窗口实例
    api.setWindow(window)

    # 绑定事件
    window.events.shown += on_shown
    window.events.loaded += on_loaded
    window.events.closing += on_closing

    # CEF模式
    guiCEF = 'cef' if ifCef else None

    # 启动窗口
    webview.start(debug=Config.devEnv, http_server=True, gui=guiCEF)

    # webview.start(debug=True, http_server=True, gui=guiCEF)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cef", action="store_true", dest="if_cef", help="if_cef")
    args = parser.parse_args()

    ifCef = args.if_cef  # 是否开启cef模式

    WebViewApp(ifCef)
