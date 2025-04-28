#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: 潘高
LastEditors: 潘高
Date: 2022-03-21 17:01:39
LastEditTime: 2024-09-08 20:28:48
Description: 业务层API，供前端JS调用
usage: 在Javascript中调用window.pywebview.api.<methodname>(<parameters>)
'''

from api.storage import Storage
from api.system import System
from api.merge import Merge
import shutil
import os
import re


# from api.merge import Merge
def copy_file(origin_path, target_path):
    """
    复制文件
    :param origin_path: 源文件路径
    :param target_path: 目标文件路径(包含文件名)
    :return:None
    """
    try:
        # 确保源文件存在
        if not os.path.exists(origin_path):
            raise FileNotFoundError(f"源文件 {origin_path} 不存在")

        # 确保目标文件夹存在
        target_folder_path = os.path.dirname(target_path)
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)

        # 复制文件
        shutil.copy(origin_path, target_path)
        print(f"文件已成功复制到 {target_path}")
    except Exception as e:
        print(f"复制文件时出错: {e}")


class API(System, Storage, Merge):
    """业务层API，供前端JS调用"""
    '''
    前后端衔接测试完成，js代码中缺少返回项属性的衔接python的方法，返回的项应包含顺序和项的名字、完整路径、遮罩高度等信息。
    最后的合并操作需要图片完整路径，否则无法找到图片。因而前端上传图片改为由后端实现，上传的同时附带完整路径信息。
    因为前端不能获取图片真实路径，而在前端排序过程中后端若要同时维护项的顺序等信息会增加复杂度。
    '''

    def __init__(self):
        self.output_path = "./output"
        self.work_path = "./work_dir"
        if not os.path.exists(self.work_path):
            os.makedirs(self.work_path)
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self.merge_mode = True  # 合并模式，当图片宽度不一致时，True为适应最长等比例缩放，False适应对短等比例缩放
        self.work_images_list = []
        self.path_pattern = re.compile('data-path=\"(.*?)\"')
        self.height_pattern = re.compile('data-overlay-height=\"(\d+)\"')

    def setWindow(self, window):
        """获取窗口实例"""
        System._window = window
        self.system = System()

    def joint_function(self):
        if not self.confirm_alert():
            return
        self.work_images_list = []
        self.merge_mode = self.select_mode_alert()
        print(f"合并模式: {self.merge_mode}")
        images_list = self.get_images()
        self.system._window.evaluate_js("newButton.click()")

        if images_list:
            self.copy_image(images_list)
            # 调用合并函数
            self.merge_images(self.work_images_list, self.merge_mode, self.output_path)
            self.system._window.evaluate_js("alert('图片合并完成！')")

        else:
            self.system._window.evaluate_js("alert('请选择图片！')")

    def confirm_alert(self) -> bool:
        """
        后端弹出窗口确认是否开始合并
        """
        result = System._window.create_confirmation_dialog("确认", "确认开始合并？")
        return bool(result)

    def select_mode_alert(self) -> bool:
        """
        后端弹出窗口选择合并模式
        :return: bool True为适应最长等比例缩放，False适应对短等比例缩放
        """
        result = System._window.create_confirmation_dialog("选择合并模式",
                                                           "适应最长等比例缩放（确认）\n适应最短等比例缩放（取消）")
        return bool(result)

    def get_images(self):
        """
        从前端页面获取图片列表
        :return: [('image_path',height),……]
        """
        lis = self.system._window.evaluate_js("itemList.querySelectorAll('li')")
        images_list = []

        for li in lis:
            # image_path=li["data-path"]
            data = (li["outerHTML"])
            image_path = self.path_pattern.findall(data)[0]
            height = self.height_pattern.findall(data)
            if not height:
                height = 0
            else:
                height = int(height[0])
            images_list.append((image_path, height))
            # images_list.append((image_path,height))
        return images_list

    def copy_image(self, images_list):

        for path, height in images_list:
            target_path = os.path.join(self.work_path, os.path.basename(path))
            copy_file(path, target_path)
            self.work_images_list.append((target_path, height))

    def get_files(self):
        """添加图片"""
        image_origin_list = self.system.system_pyCreateFileDialog(['图片文件 (*.jpg;*.png;*.jpeg;*.gif;*.bmp;*.webp)'])
        image_list = []
        for file in image_origin_list:  # 示例文件
            with open(file['path'], "rb") as f:
                image_list.append({
                    "name": file['filename'],
                    "data": list(f.read()),  # 将bytes转为列表便于JSON序列化
                    "path": file['path'],
                    "mime": f"image/{file['ext'][1:]}"
                })
        return image_list


