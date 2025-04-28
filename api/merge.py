#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os
from PIL import Image
import time
from pathlib import Path


def clear_with_pathlib(dir_path):
    """使用现代Pathlib接口"""
    path = Path(dir_path)
    if not path.is_dir():
        raise ValueError("路径无效")

    [f.unlink() for f in path.glob("*") if f.is_file()]  # 删除所有文件
    # 如需删除子目录: [shutil.rmtree(d) for d in path.glob("*") if d.is_dir()]


def crop_and_save_bottom_and_return_width(image_path, keep_height):
    """
    裁剪图片：只保留下半部分的指定高度
    :param image_path: 输入图片路径
    :param keep_height: 要保留的下半部分高度（像素）
    :param output_path: 输出图片路径
    """
    # 加载图片
    img = Image.open(image_path).convert('RGBA')
    width, height = img.size

    # # 验证保留高度是否合法
    # if keep_height <= 0:
    #     raise ValueError("保留高度必须大于0")
    # if keep_height > height:
    #     raise ValueError("保留高度不能超过原图高度")


    # 计算裁剪区域（保留下半部分）
    top = keep_height
    bottom = height
    left = 0
    right = width

    if keep_height == 0:
        top = 0

    # 使用crop方法直接裁剪
    cropped_img = img.crop((left, top, right, bottom))
    str(hash(time.time())) + '.png'
    temp_path = os.path.dirname(image_path) +'/' + str(hash(time.time())) + '.png'

    cropped_img.save(temp_path)

    os.remove(image_path)

    return temp_path,width


def resize_safely(image_path, target_width=None, target_height=None):
    """等比缩放"""
    img = Image.open(image_path)
    original_width, original_height = img.size

    # 如果目标宽度和指定宽度相同，则不缩放
    if target_width and original_width == target_width:
        temp_path=os.path.splitext(image_path)[0] + '_' + '.png'
        img.save(temp_path)
        return temp_path

    # 计算缩放比例
    if target_width and not target_height:  # 按宽度缩放
        ratio = target_width / original_width
        new_width = target_width
        new_height = int(original_height * ratio)
    elif target_height and not target_width:  # 按高度缩放
        ratio = target_height / original_height
        new_height = target_height
        new_width = int(original_width * ratio)
    else:  # 如果同时指定宽高，则按比例缩放至不超过目标尺寸
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

    # 缩放图片
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)

    # 先保存到临时文件
    temp_path = os.path.splitext(image_path)[0] + '_' + '.png'
    resized_img.save(temp_path)

    # 删除原文件，并将临时文件重命名为原文件名
    os.remove(image_path)
    return temp_path


def merge_images_pillow(image_paths, output_path, direction='vertical'):
    """
    使用Pillow内置方法合并图片（自动处理RGBA通道）
    :param image_paths: 图片路径列表
    :param output_path: 输出路径
    :param direction: 'vertical'（垂直）或 'horizontal'（水平）
    """
    # 打开所有图片并计算总尺寸
    images = [Image.open(path) for path in image_paths]
    widths, heights = zip(*(img.size for img in images))

    if direction == 'vertical':
        total_width = max(widths)
        total_height = sum(heights)
        new_img = Image.new('RGBA', (total_width, total_height))
        y_offset = 0
        for img in images:
            new_img.paste(img, (0, y_offset))
            y_offset += img.height
    else:
        total_width = sum(widths)
        total_height = max(heights)
        new_img = Image.new('RGBA', (total_width, total_height))
        x_offset = 0
        for img in images:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.width

    output_path = os.path.join(output_path, str(hash(time.time())) + '.png')
    new_img.save(output_path)
    print(image_paths)

    clear_with_pathlib(dir_path=os.path.dirname(image_paths[0]))


class Merge:

    @staticmethod
    def merge_images(images_list: list[tuple[str, int]], merge_mode: bool, output_path):
        """
        合并图片。处理流程：
        1. 裁剪图片，流程中收集每张图片的宽度
        2. 根据合并模式，从收集的图片宽度中获取最大值或最小值，并将所有图片按该宽度进行等比缩放
        3. 合并图片
        4. 保存图片
        :param images_list: 图片列表
        :param merge_mode: 合并模式
        :return: None
        """
        width_list = []
        path_list = []

        for path, height in images_list:
            path_,width = crop_and_save_bottom_and_return_width(path, height)
            path_list.append(path_)
            width_list.append(width)

        if merge_mode:
            required_width = max(width_list)
        else:
            required_width = min(width_list)
        new_path_list = []
        print(path_list)

        for path in path_list:
            new_path_list.append(resize_safely(path, target_width=required_width))
        print(new_path_list)
        # merge_images_pillow(path_list, output_path, direction='horizontal')
        merge_images_pillow(new_path_list, output_path)
